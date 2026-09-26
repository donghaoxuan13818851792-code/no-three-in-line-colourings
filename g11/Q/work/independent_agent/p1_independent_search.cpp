#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr int kSide = 11;
constexpr int kPointCount = kSide * kSide;
constexpr std::uint64_t kHighMask = (std::uint64_t{1} << 57) - 1;
constexpr std::array<std::size_t, 6> kPartSizes{
    35563, 33447, 64283, 86528, 213982, 152034};

// This intentionally uses two machine words rather than unsigned __int128,
// unlike the implementation under audit.
struct Mask {
  std::uint64_t low = 0;
  std::uint64_t high = 0;

  friend bool operator==(Mask a, Mask b) {
    return a.low == b.low && a.high == b.high;
  }
  friend bool operator<(Mask a, Mask b) {
    return a.high != b.high ? a.high < b.high : a.low < b.low;
  }
};

Mask operator|(Mask a, Mask b) {
  return {a.low | b.low, a.high | b.high};
}

Mask operator&(Mask a, Mask b) {
  return {a.low & b.low, a.high & b.high};
}

Mask operator^(Mask a, Mask b) {
  return {a.low ^ b.low, a.high ^ b.high};
}

bool Any(Mask value) { return value.low != 0 || value.high != 0; }

int Count(Mask value) {
  return std::popcount(value.low) + std::popcount(value.high);
}

bool Test(Mask value, int point) {
  return point < 64 ? ((value.low >> point) & 1)
                    : ((value.high >> (point - 64)) & 1);
}

void Set(Mask& value, int point) {
  if (point < 64)
    value.low |= std::uint64_t{1} << point;
  else
    value.high |= std::uint64_t{1} << (point - 64);
}

Mask Parse(const std::string& token) {
  if (token.size() != 31)
    throw std::runtime_error("input mask is not 31 hex digits");
  Mask result;
  for (char ch : token) {
    unsigned nibble;
    if (ch >= '0' && ch <= '9')
      nibble = static_cast<unsigned>(ch - '0');
    else if (ch >= 'a' && ch <= 'f')
      nibble = static_cast<unsigned>(ch - 'a' + 10);
    else
      throw std::runtime_error("input mask is not lowercase hexadecimal");
    result.high = (result.high << 4) | (result.low >> 60);
    result.low = (result.low << 4) | nibble;
  }
  if (result.high & ~kHighMask)
    throw std::runtime_error("input bit lies outside the grid");
  return result;
}

std::string Hex(Mask value) {
  constexpr char kDigits[] = "0123456789abcdef";
  std::string result(31, '0');
  for (int place = 0; place < 31; ++place) {
    const unsigned nibble =
        place < 16
            ? static_cast<unsigned>((value.low >> (4 * place)) & 15)
            : static_cast<unsigned>(
                  (value.high >> (4 * (place - 16))) & 15);
    result[30 - place] = kDigits[nibble];
  }
  return result;
}

std::pair<int, int> D4Image(int row, int column, int symmetry) {
  switch (symmetry) {
    case 0: return {row, column};
    case 1: return {row, kSide - 1 - column};
    case 2: return {kSide - 1 - row, column};
    case 3:
      return {kSide - 1 - row, kSide - 1 - column};
    case 4: return {column, row};
    case 5: return {column, kSide - 1 - row};
    case 6: return {kSide - 1 - column, row};
    case 7:
      return {kSide - 1 - column, kSide - 1 - row};
    default: throw std::runtime_error("invalid D4 element");
  }
}

Mask Transform(Mask value, int symmetry) {
  Mask image;
  for (int point = 0; point < kPointCount; ++point) {
    if (!Test(value, point)) continue;
    const auto [row, column] =
        D4Image(point / kSide, point % kSide, symmetry);
    Set(image, kSide * row + column);
  }
  return image;
}

struct Cap {
  Mask points;
  std::uint8_t singleton_row;
  std::uint8_t singleton_column;
};

struct Line {
  Mask points;
  std::uint8_t size;
};

std::vector<Mask> ReadMasks(const std::filesystem::path& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot read " + path.string());
  std::vector<Mask> result;
  std::string token;
  while (input >> token) result.push_back(Parse(token));
  return result;
}

std::pair<int, int> ValidateMultiplicity(Mask points) {
  if (Count(points) != 21)
    throw std::runtime_error("input cap size is not 21");
  int singleton_row = -1;
  int singleton_column = -1;
  for (int row = 0; row < kSide; ++row) {
    int count = 0;
    for (int column = 0; column < kSide; ++column)
      count += Test(points, kSide * row + column);
    if (count == 1) {
      if (singleton_row >= 0)
        throw std::runtime_error("multiple singleton rows");
      singleton_row = row;
    } else if (count != 2) {
      throw std::runtime_error("bad row multiplicity");
    }
  }
  for (int column = 0; column < kSide; ++column) {
    int count = 0;
    for (int row = 0; row < kSide; ++row)
      count += Test(points, kSide * row + column);
    if (count == 1) {
      if (singleton_column >= 0)
        throw std::runtime_error("multiple singleton columns");
      singleton_column = column;
    } else if (count != 2) {
      throw std::runtime_error("bad column multiplicity");
    }
  }
  if (singleton_row < 0 || singleton_column < 0)
    throw std::runtime_error("missing singleton row/column");

  bool main_diagonal = false;
  bool anti_diagonal = false;
  for (int coordinate = 0; coordinate < kSide; ++coordinate) {
    main_diagonal |= Test(
        points, kSide * coordinate + coordinate);
    anti_diagonal |= Test(
        points, kSide * coordinate + kSide - 1 - coordinate);
  }
  if (!main_diagonal || !anti_diagonal)
    throw std::runtime_error("cap misses a long diagonal");
  return {singleton_row, singleton_column};
}

std::vector<Cap> LoadCaps(const std::filesystem::path& directory) {
  std::vector<Mask> masks;
  masks.reserve(1019640);
  for (int row = 0; row <= 5; ++row) {
    const auto path =
        directory /
        ("caps21_r" + std::to_string(row) + "_diag.hex");
    const std::vector<Mask> part = ReadMasks(path);
    if (part.size() != kPartSizes[row])
      throw std::runtime_error("unexpected cap-file length");
    masks.insert(masks.end(), part.begin(), part.end());
    if (row != 5)
      for (Mask mask : part) masks.push_back(Transform(mask, 2));
  }
  if (masks.size() != 1019640)
    throw std::runtime_error("unexpected reconstructed cap count");
  std::sort(masks.begin(), masks.end());
  if (std::adjacent_find(masks.begin(), masks.end()) != masks.end())
    throw std::runtime_error("duplicate reconstructed cap");

  std::vector<Cap> caps;
  caps.reserve(masks.size());
  for (Mask mask : masks) {
    const auto [row, column] = ValidateMultiplicity(mask);
    caps.push_back(
        {mask, static_cast<std::uint8_t>(row),
         static_cast<std::uint8_t>(column)});
  }
  return caps;
}

// Independent construction: every pair of grid points determines its complete
// grid line.  A set removes duplicates.  This does not use primitive directions.
std::vector<Line> BuildLines() {
  std::set<Mask> unique;
  for (int first = 0; first < kPointCount; ++first) {
    const int r1 = first / kSide;
    const int c1 = first % kSide;
    for (int second = first + 1; second < kPointCount; ++second) {
      const int r2 = second / kSide;
      const int c2 = second % kSide;
      Mask line;
      for (int point = 0; point < kPointCount; ++point) {
        const int r = point / kSide;
        const int c = point % kSide;
        if ((r2 - r1) * (c - c1) == (c2 - c1) * (r - r1))
          Set(line, point);
      }
      if (Count(line) >= 3) unique.insert(line);
    }
  }
  std::vector<Line> lines;
  std::array<int, 12> distribution{};
  for (Mask line : unique) {
    const int size = Count(line);
    ++distribution[size];
    lines.push_back({line, static_cast<std::uint8_t>(size)});
  }
  std::array<int, 12> expected{};
  expected[3] = 396;
  expected[4] = 124;
  expected[5] = 40;
  expected[6] = 28;
  expected[7] = expected[8] = expected[9] = expected[10] = 4;
  expected[11] = 24;
  if (lines.size() != 628 || distribution != expected)
    throw std::runtime_error("independent line construction failed");
  return lines;
}

bool Compatible(const Cap& first, const Cap& second) {
  return first.singleton_row != second.singleton_row &&
         first.singleton_column != second.singleton_column &&
         !Any(first.points & second.points);
}

class PackingSearch {
 public:
  PackingSearch(std::vector<Cap> caps, std::vector<Line> lines)
      : caps_(std::move(caps)),
        lines_(std::move(lines)),
        word_count_((caps_.size() + 63) / 64),
        point_occurrence_(kPointCount,
                          std::vector<std::uint64_t>(word_count_)),
        row_occurrence_(kSide,
                        std::vector<std::uint64_t>(word_count_)),
        column_occurrence_(kSide,
                           std::vector<std::uint64_t>(word_count_)) {
    for (std::size_t id = 0; id < caps_.size(); ++id) {
      const std::size_t word = id / 64;
      const std::uint64_t bit = std::uint64_t{1} << (id % 64);
      for (int point = 0; point < kPointCount; ++point)
        if (Test(caps_[id].points, point))
          point_occurrence_[point][word] |= bit;
      row_occurrence_[caps_[id].singleton_row][word] |= bit;
      column_occurrence_[caps_[id].singleton_column][word] |= bit;
    }

    for (int chosen = 2; chosen <= 4; ++chosen) {
      const int remaining_capacity = 2 * (6 - chosen);
      for (std::size_t line = 0; line < lines_.size(); ++line)
        if (lines_[line].size > remaining_capacity)
          active_[chosen].push_back(line);
    }

    for (std::size_t id = 0; id < caps_.size(); ++id) {
      Mask minimum = caps_[id].points;
      for (int symmetry = 1; symmetry < 8; ++symmetry)
        minimum = std::min(minimum, Transform(caps_[id].points, symmetry));
      if (caps_[id].points == minimum) representatives_.push_back(id);
    }
    if (representatives_.size() != 127491)
      throw std::runtime_error("independent D4 representative count failed");
    std::cerr << "independent_caps " << caps_.size()
              << " independent_lines " << lines_.size()
              << " d4_representatives " << representatives_.size()
              << '\n';
  }

  bool Run(std::size_t shard, std::size_t shard_count) {
    if (shard_count == 0 || shard >= shard_count)
      throw std::runtime_error("invalid shard");
    const auto started = std::chrono::steady_clock::now();
    for (std::size_t rep = shard; rep < representatives_.size();
         rep += shard_count) {
      const std::size_t first_id = representatives_[rep];
      const Cap& first = caps_[first_id];
      std::vector<std::uint64_t> bits(word_count_, ~std::uint64_t{0});
      if (caps_.size() % 64)
        bits.back() &=
            (std::uint64_t{1} << (caps_.size() % 64)) - 1;
      Exclude(bits, row_occurrence_[first.singleton_row]);
      Exclude(bits, column_occurrence_[first.singleton_column]);
      for (int point = 0; point < kPointCount; ++point)
        if (Test(first.points, point))
          Exclude(bits, point_occurrence_[point]);
      ClearAtMost(bits, first_id);

      std::vector<std::size_t> seconds;
      Visit(bits, [&](std::size_t id) {
        ++examined_[2];
        if (PrefixPossible(first.points | caps_[id].points, 2)) {
          ++accepted_[2];
          seconds.push_back(id);
        }
      });
      choice_[0] = first_id;
      ++first_caps_;
      if (AfterFirst(first_id, seconds)) {
        std::cout << "SOLUTION";
        Mask selected;
        for (std::size_t id : choice_) {
          std::cout << ' ' << id;
          selected = selected | caps_[id].points;
        }
        std::cout << '\n';
        for (std::size_t id : choice_)
          std::cout << Hex(caps_[id].points) << '\n';
        const Mask full{~std::uint64_t{0}, kHighMask};
        std::cout << "COMPLEMENT " << Hex(full ^ selected) << '\n';
        return true;
      }
      if (first_caps_ % 100 == 0) {
        const double elapsed =
            std::chrono::duration<double>(
                std::chrono::steady_clock::now() - started)
                .count();
        std::cerr << "independent_progress " << shard << '/'
                  << shard_count << " first_caps " << first_caps_
                  << " rep " << rep;
        PrintCounters(std::cerr);
        std::cerr << " seconds " << elapsed << '\n';
      }
    }
    std::cout << "INDEPENDENT_UNSAT_SHARD " << shard << ' '
              << shard_count << " first_caps " << first_caps_;
    PrintCounters(std::cout);
    std::cout << '\n';
    return false;
  }

 private:
  static void Exclude(std::vector<std::uint64_t>& destination,
                      const std::vector<std::uint64_t>& forbidden) {
    for (std::size_t word = 0; word < destination.size(); ++word)
      destination[word] &= ~forbidden[word];
  }

  static void ClearAtMost(std::vector<std::uint64_t>& bits,
                          std::size_t id) {
    const std::size_t word = id / 64;
    std::fill(bits.begin(), bits.begin() + word, std::uint64_t{0});
    const unsigned offset = static_cast<unsigned>(id % 64);
    bits[word] &=
        offset == 63
            ? std::uint64_t{0}
            : ~((std::uint64_t{1} << (offset + 1)) - 1);
  }

  template <class Function>
  static void Visit(const std::vector<std::uint64_t>& bits,
                    Function function) {
    for (std::size_t word = 0; word < bits.size(); ++word) {
      std::uint64_t value = bits[word];
      while (value) {
        const unsigned offset = std::countr_zero(value);
        function(64 * word + offset);
        value &= value - 1;
      }
    }
  }

  bool PrefixPossible(Mask selected, int chosen) const {
    const int capacity = 2 * (6 - chosen);
    for (std::size_t line_id : active_[chosen]) {
      const Line& line = lines_[line_id];
      if (Count(selected & line.points) + capacity < line.size)
        return false;
    }
    return true;
  }

  bool ComplementIsCap(Mask selected) const {
    const Mask full{~std::uint64_t{0}, kHighMask};
    const Mask complement = full ^ selected;
    if (Count(complement) != 16)
      throw std::runtime_error("terminal complement size is not 16");
    for (const Line& line : lines_)
      if (Count(complement & line.points) >= 3) return false;
    return true;
  }

  bool AfterFirst(std::size_t first_id,
                  const std::vector<std::size_t>& seconds) {
    const Cap& first = caps_[first_id];
    for (std::size_t si = 0; si < seconds.size(); ++si) {
      const std::size_t second_id = seconds[si];
      const Cap& second = caps_[second_id];
      const Mask selected_two = first.points | second.points;

      std::vector<std::size_t> thirds;
      for (std::size_t index = si + 1; index < seconds.size(); ++index) {
        const std::size_t id = seconds[index];
        ++examined_[3];
        if (!Compatible(second, caps_[id])) continue;
        if (!PrefixPossible(selected_two | caps_[id].points, 3)) continue;
        ++accepted_[3];
        thirds.push_back(id);
      }

      for (std::size_t ti = 0; ti < thirds.size(); ++ti) {
        const std::size_t third_id = thirds[ti];
        const Cap& third = caps_[third_id];
        const Mask selected_three = selected_two | third.points;

        std::vector<std::size_t> fourths;
        for (std::size_t index = ti + 1; index < thirds.size(); ++index) {
          const std::size_t id = thirds[index];
          ++examined_[4];
          if (!Compatible(third, caps_[id])) continue;
          if (!PrefixPossible(selected_three | caps_[id].points, 4))
            continue;
          ++accepted_[4];
          fourths.push_back(id);
        }

        for (std::size_t fi = 0; fi < fourths.size(); ++fi) {
          const std::size_t fourth_id = fourths[fi];
          const Cap& fourth = caps_[fourth_id];
          const Mask selected_four = selected_three | fourth.points;
          for (std::size_t index = fi + 1; index < fourths.size();
               ++index) {
            const std::size_t fifth_id = fourths[index];
            ++examined_[5];
            if (!Compatible(fourth, caps_[fifth_id])) continue;
            if (!ComplementIsCap(
                    selected_four | caps_[fifth_id].points))
              continue;
            ++accepted_[5];
            choice_ = {
                first_id, second_id, third_id, fourth_id, fifth_id};
            return true;
          }
        }
      }
    }
    return false;
  }

  void PrintCounters(std::ostream& output) const {
    for (int depth = 2; depth <= 5; ++depth)
      output << " examined" << depth << ' ' << examined_[depth]
             << " accepted" << depth << ' ' << accepted_[depth];
  }

  std::vector<Cap> caps_;
  std::vector<Line> lines_;
  std::size_t word_count_;
  std::vector<std::vector<std::uint64_t>> point_occurrence_;
  std::vector<std::vector<std::uint64_t>> row_occurrence_;
  std::vector<std::vector<std::uint64_t>> column_occurrence_;
  std::array<std::vector<std::size_t>, 5> active_;
  std::vector<std::size_t> representatives_;
  std::array<std::size_t, 5> choice_{};
  std::array<std::uint64_t, 6> examined_{};
  std::array<std::uint64_t, 6> accepted_{};
  std::uint64_t first_caps_ = 0;
};

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 3 && argc != 4)
      throw std::runtime_error(
          "usage: p1_independent_search SHARD SHARDS [CAP_DIRECTORY]");
    const std::size_t shard = std::stoull(argv[1]);
    const std::size_t shards = std::stoull(argv[2]);
    const std::filesystem::path directory =
        argc == 4 ? argv[3] : "work/math_agent";
    std::vector<Cap> caps = LoadCaps(directory);
    std::vector<Line> lines = BuildLines();
    PackingSearch search(std::move(caps), std::move(lines));
    return search.Run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "INDEPENDENT_ERROR " << error.what() << '\n';
    return 2;
  }
}
