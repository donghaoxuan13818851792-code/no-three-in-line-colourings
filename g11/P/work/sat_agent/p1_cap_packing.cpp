#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <utility>
#include <vector>

using U128 = unsigned __int128;
constexpr int N = 11;
constexpr int POINTS = N * N;

struct Cap {
  U128 mask;
  uint8_t singleton_row;
  uint8_t singleton_col;
};

struct Line {
  U128 mask;
  uint8_t length;
};

U128 parse_hex(const std::string& text) {
  U128 value = 0;
  for (char ch : text) {
    value <<= 4;
    if ('0' <= ch && ch <= '9') value |= ch - '0';
    else if ('a' <= ch && ch <= 'f') value |= ch - 'a' + 10;
    else if ('A' <= ch && ch <= 'F') value |= ch - 'A' + 10;
    else throw std::runtime_error("invalid hexadecimal mask");
  }
  return value;
}

std::string to_hex(U128 value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result(31, '0');
  for (int index = 30; index >= 0; --index) {
    result[index] = digits[static_cast<unsigned>(value & 15)];
    value >>= 4;
  }
  return result;
}

int popcount(U128 value) {
  return std::popcount(static_cast<uint64_t>(value)) +
         std::popcount(static_cast<uint64_t>(value >> 64));
}

U128 transform(U128 mask, int symmetry) {
  U128 result = 0;
  for (int point = 0; point < POINTS; ++point) {
    if (!((mask >> point) & 1)) continue;
    int x = point / N, y = point % N;
    std::array<std::pair<int, int>, 8> images{{
        {x, y},
        {x, N - 1 - y},
        {N - 1 - x, y},
        {N - 1 - x, N - 1 - y},
        {y, x},
        {y, N - 1 - x},
        {N - 1 - y, x},
        {N - 1 - y, N - 1 - x},
    }};
    auto [xx, yy] = images[symmetry];
    result |= U128(1) << (N * xx + yy);
  }
  return result;
}

int singleton_row(U128 mask) {
  U128 row_mask = (U128(1) << N) - 1;
  int singleton = -1;
  for (int row = 0; row < N; ++row) {
    int count = popcount((mask >> (N * row)) & row_mask);
    if (count == 1) {
      if (singleton >= 0) throw std::runtime_error("two singleton rows");
      singleton = row;
    } else if (count != 2) {
      throw std::runtime_error("bad row multiplicity");
    }
  }
  if (singleton < 0) throw std::runtime_error("no singleton row");
  return singleton;
}

int singleton_col(U128 mask) {
  int singleton = -1;
  for (int column = 0; column < N; ++column) {
    int count = 0;
    for (int row = 0; row < N; ++row)
      count += static_cast<int>((mask >> (N * row + column)) & 1);
    if (count == 1) {
      if (singleton >= 0) throw std::runtime_error("two singleton columns");
      singleton = column;
    } else if (count != 2) {
      throw std::runtime_error("bad column multiplicity");
    }
  }
  if (singleton < 0) throw std::runtime_error("no singleton column");
  return singleton;
}

std::vector<U128> load_masks(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open " + path);
  std::vector<U128> result;
  std::string text;
  while (input >> text) result.push_back(parse_hex(text));
  return result;
}

std::vector<Cap> load_all_caps(const std::string& directory) {
  std::vector<U128> masks;
  for (int row = 0; row <= 5; ++row) {
    auto part = load_masks(
        directory + "/caps21_r" + std::to_string(row) + "_diag.hex");
    masks.insert(masks.end(), part.begin(), part.end());
    if (row < 5) {
      for (U128 mask : part) masks.push_back(transform(mask, 2));
    }
  }
  std::sort(masks.begin(), masks.end());
  auto unique_end = std::unique(masks.begin(), masks.end());
  if (unique_end != masks.end())
    throw std::runtime_error("duplicate cap after reflection");
  if (masks.size() != 1019640)
    throw std::runtime_error("expected 1,019,640 caps");

  U128 main_diagonal = 0, anti_diagonal = 0;
  for (int i = 0; i < N; ++i) {
    main_diagonal |= U128(1) << (N * i + i);
    anti_diagonal |= U128(1) << (N * i + (N - 1 - i));
  }
  std::vector<Cap> caps;
  caps.reserve(masks.size());
  for (U128 mask : masks) {
    if (popcount(mask) != 21 || !(mask & main_diagonal) ||
        !(mask & anti_diagonal))
      throw std::runtime_error("invalid cap mask");
    caps.push_back({
        mask,
        static_cast<uint8_t>(singleton_row(mask)),
        static_cast<uint8_t>(singleton_col(mask)),
    });
  }
  return caps;
}

std::vector<Line> make_lines() {
  std::vector<Line> lines;
  for (int dx = 0; dx < N; ++dx) {
    for (int dy = -(N - 1); dy < N; ++dy) {
      if (dx == 0) {
        if (dy != 1) continue;
      } else if (std::gcd(dx, std::abs(dy)) != 1) {
        continue;
      }
      for (int x = 0; x < N; ++x) {
        for (int y = 0; y < N; ++y) {
          if (0 <= x - dx && x - dx < N &&
              0 <= y - dy && y - dy < N)
            continue;
          U128 mask = 0;
          int xx = x, yy = y;
          while (0 <= xx && xx < N && 0 <= yy && yy < N) {
            mask |= U128(1) << (N * xx + yy);
            xx += dx;
            yy += dy;
          }
          int length = popcount(mask);
          if (length >= 3)
            lines.push_back({mask, static_cast<uint8_t>(length)});
        }
      }
    }
  }
  std::sort(lines.begin(), lines.end(), [](const Line& a, const Line& b) {
    return a.mask < b.mask;
  });
  auto duplicate = std::adjacent_find(
      lines.begin(), lines.end(),
      [](const Line& a, const Line& b) { return a.mask == b.mask; });
  if (duplicate != lines.end() || lines.size() != 628)
    throw std::runtime_error("expected 628 distinct relevant lines");
  std::array<int, 12> distribution{};
  for (const Line& line : lines) ++distribution[line.length];
  std::array<int, 12> expected{};
  expected[3] = 396;
  expected[4] = 124;
  expected[5] = 40;
  expected[6] = 28;
  expected[7] = expected[8] = expected[9] = expected[10] = 4;
  expected[11] = 24;
  if (distribution != expected)
    throw std::runtime_error("unexpected line-length distribution");
  return lines;
}

class Search {
 public:
  Search(std::vector<Cap> caps, std::vector<Line> lines)
      : caps_(std::move(caps)), lines_(std::move(lines)),
        words_((caps_.size() + 63) / 64),
        point_index_(POINTS, std::vector<uint64_t>(words_)),
        row_index_(N, std::vector<uint64_t>(words_)),
        col_index_(N, std::vector<uint64_t>(words_)) {
    for (size_t id = 0; id < caps_.size(); ++id) {
      uint64_t bit = uint64_t(1) << (id & 63);
      size_t word = id >> 6;
      U128 mask = caps_[id].mask;
      for (int point = 0; point < POINTS; ++point)
        if ((mask >> point) & 1) point_index_[point][word] |= bit;
      row_index_[caps_[id].singleton_row][word] |= bit;
      col_index_[caps_[id].singleton_col][word] |= bit;
    }
    for (int depth = 1; depth <= 5; ++depth) {
      int complement_classes = 6 - depth;
      int capacity = 2 * complement_classes;
      for (size_t line = 0; line < lines_.size(); ++line)
        if (lines_[line].length > capacity)
          active_lines_[depth].push_back(line);
    }
    for (size_t id = 0; id < caps_.size(); ++id) {
      U128 canonical = caps_[id].mask;
      for (int symmetry = 1; symmetry < 8; ++symmetry)
        canonical = std::min(canonical, transform(caps_[id].mask, symmetry));
      if (caps_[id].mask == canonical) first_representatives_.push_back(id);
    }
    std::cerr << "caps " << caps_.size()
              << " d4_representatives " << first_representatives_.size()
              << " words " << words_ << '\n';
  }

  bool line_capacity(U128 selected_union, int depth) const {
    int required_capacity = 2 * (6 - depth);
    for (size_t line_id : active_lines_[depth]) {
      const Line& line = lines_[line_id];
      if (popcount(selected_union & line.mask) <
          static_cast<int>(line.length) - required_capacity)
        return false;
    }
    return true;
  }

  std::vector<uint64_t> compatible_with(const Cap& cap) const {
    std::vector<uint64_t> result(words_, ~uint64_t(0));
    if (caps_.size() & 63)
      result.back() &= (uint64_t(1) << (caps_.size() & 63)) - 1;
    and_not(result, row_index_[cap.singleton_row]);
    and_not(result, col_index_[cap.singleton_col]);
    U128 mask = cap.mask;
    while (mask) {
      int point = std::countr_zero(static_cast<uint64_t>(mask));
      if ((mask & ((U128(1) << 64) - 1)) == 0)
        point = 64 + std::countr_zero(static_cast<uint64_t>(mask >> 64));
      and_not(result, point_index_[point]);
      mask &= mask - 1;
    }
    return result;
  }

  void stats(size_t limit) {
    limit = std::min(limit, first_representatives_.size());
    uint64_t raw_total = 0, capacity_total = 0;
    auto started = std::chrono::steady_clock::now();
    for (size_t index = 0; index < limit; ++index) {
      size_t first_id = first_representatives_[index];
      const Cap& first = caps_[first_id];
      auto candidates = compatible_with(first);
      clear_through(candidates, first_id);
      uint64_t raw = bit_count(candidates);
      uint64_t capacity = 0;
      for_each_bit(candidates, [&](size_t second_id) {
        if (line_capacity(first.mask | caps_[second_id].mask, 2))
          ++capacity;
      });
      raw_total += raw;
      capacity_total += capacity;
      std::cout << index << ' ' << first_id << ' ' << raw << ' '
                << capacity << '\n';
    }
    double seconds = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    std::cerr << "stats_first " << limit << " raw_total " << raw_total
              << " capacity_total " << capacity_total
              << " seconds " << seconds << '\n';
  }

  void stats3(size_t representative_index, size_t second_limit) {
    if (representative_index >= first_representatives_.size())
      throw std::runtime_error("representative index out of range");
    size_t first_id = first_representatives_[representative_index];
    const Cap& first = caps_[first_id];
    auto candidate_bits = compatible_with(first);
    clear_through(candidate_bits, first_id);
    std::vector<size_t> seconds;
    for_each_bit(candidate_bits, [&](size_t id) {
      if (line_capacity(first.mask | caps_[id].mask, 2))
        seconds.push_back(id);
    });
    second_limit = std::min(second_limit, seconds.size());
    uint64_t disjoint_thirds = 0, capacity_thirds = 0;
    auto started = std::chrono::steady_clock::now();
    for (size_t index = 0; index < second_limit; ++index) {
      size_t second_id = seconds[index];
      const Cap& second = caps_[second_id];
      uint64_t raw = 0, capacity = 0;
      for (size_t later = index + 1; later < seconds.size(); ++later) {
        const Cap& third = caps_[seconds[later]];
        if ((second.mask & third.mask) ||
            second.singleton_row == third.singleton_row ||
            second.singleton_col == third.singleton_col)
          continue;
        ++raw;
        if (line_capacity(first.mask | second.mask | third.mask, 3))
          ++capacity;
      }
      disjoint_thirds += raw;
      capacity_thirds += capacity;
      std::cout << index << ' ' << second_id << ' ' << raw << ' '
                << capacity << '\n';
    }
    double seconds_elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    std::cerr << "stats3 representative_index " << representative_index
              << " first_id " << first_id
              << " seconds_total " << seconds.size()
              << " sampled " << second_limit
              << " disjoint_thirds " << disjoint_thirds
              << " capacity_thirds " << capacity_thirds
              << " elapsed_seconds " << seconds_elapsed << '\n';
  }

  bool run(size_t shard, size_t shards) {
    if (shard >= shards || shards == 0)
      throw std::runtime_error("bad shard");
    auto started = std::chrono::steady_clock::now();
    for (size_t rep_index = shard;
         rep_index < first_representatives_.size();
         rep_index += shards) {
      size_t first_id = first_representatives_[rep_index];
      const Cap& first = caps_[first_id];
      auto candidate_bits = compatible_with(first);
      clear_through(candidate_bits, first_id);
      std::vector<size_t> seconds;
      for_each_bit(candidate_bits, [&](size_t id) {
        ++tested_[2];
        if (line_capacity(first.mask | caps_[id].mask, 2)) {
          ++passed_[2];
          seconds.push_back(id);
        }
      });
      chosen_[0] = first_id;
      ++first_caps_;
      if (search_after_first(first_id, seconds)) {
        std::cout << "SOLUTION";
        for (size_t id : chosen_) std::cout << ' ' << id;
        std::cout << '\n';
        for (size_t id : chosen_)
          std::cout << to_hex(caps_[id].mask) << '\n';
        U128 union_mask = 0;
        for (size_t id : chosen_) union_mask |= caps_[id].mask;
        U128 full = (U128(1) << POINTS) - 1;
        std::cout << "COMPLEMENT " << to_hex(full ^ union_mask) << '\n';
        return true;
      }
      if ((first_caps_ % 100) == 0) {
        double seconds = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started).count();
        std::cerr << "progress shard " << shard << '/' << shards
                  << " first_caps " << first_caps_
                  << " rep_index " << rep_index
                  << " tested2 " << tested_[2]
                  << " passed2 " << passed_[2]
                  << " tested3 " << tested_[3]
                  << " passed3 " << passed_[3]
                  << " tested4 " << tested_[4]
                  << " passed4 " << passed_[4]
                  << " tested5 " << tested_[5]
                  << " passed5 " << passed_[5]
                  << " seconds " << seconds << '\n';
      }
    }
    std::cout << "UNSAT_SHARD " << shard << ' ' << shards
              << " first_caps " << first_caps_;
    for (int depth = 2; depth <= 5; ++depth) {
      std::cout << " tested" << depth << ' ' << tested_[depth]
                << " passed" << depth << ' ' << passed_[depth];
    }
    std::cout << '\n';
    return false;
  }

 private:
  static void and_not(
      std::vector<uint64_t>& destination,
      const std::vector<uint64_t>& excluded) {
    for (size_t word = 0; word < destination.size(); ++word)
      destination[word] &= ~excluded[word];
  }

  static uint64_t bit_count(const std::vector<uint64_t>& bits) {
    uint64_t result = 0;
    for (uint64_t word : bits) result += std::popcount(word);
    return result;
  }

  template <class Function>
  static void for_each_bit(
      const std::vector<uint64_t>& bits, Function function) {
    for (size_t word_index = 0; word_index < bits.size(); ++word_index) {
      uint64_t word = bits[word_index];
      while (word) {
        unsigned offset = std::countr_zero(word);
        function((word_index << 6) + offset);
        word &= word - 1;
      }
    }
  }

  void clear_through(std::vector<uint64_t>& bits, size_t id) const {
    size_t word = id >> 6;
    std::fill(bits.begin(), bits.begin() + word, uint64_t(0));
    uint64_t keep_above =
        (id & 63) == 63 ? uint64_t(0)
                        : ~((uint64_t(1) << ((id & 63) + 1)) - 1);
    bits[word] &= keep_above;
  }

  bool dfs(int selected, U128 selected_union,
           const std::vector<uint64_t>& candidates, size_t last_id) {
    if (selected == 5) return true;
    int next_depth = selected + 1;
    int remaining_after = 5 - next_depth;
    bool found = false;
    for_each_bit(candidates, [&](size_t id) {
      if (found) return;
      U128 next_union = selected_union | caps_[id].mask;
      ++nodes_[next_depth];
      if (!line_capacity(next_union, next_depth)) return;
      chosen_[selected] = id;
      if (next_depth == 5) {
        found = true;
        return;
      }
      std::vector<uint64_t> next = candidates;
      clear_through(next, id);
      auto compatible = compatible_with(caps_[id]);
      for (size_t word = 0; word < words_; ++word)
        next[word] &= compatible[word];
      if (bit_count(next) < static_cast<uint64_t>(remaining_after)) return;
      if (dfs(next_depth, next_union, next, id)) found = true;
    });
    return found;
  }

  bool search_after_first(
      size_t first_id, const std::vector<size_t>& seconds) {
    const Cap& first = caps_[first_id];
    for (size_t second_index = 0;
         second_index < seconds.size(); ++second_index) {
      size_t second_id = seconds[second_index];
      const Cap& second = caps_[second_id];
      U128 union2 = first.mask | second.mask;

      std::vector<size_t> thirds;
      for (size_t index = second_index + 1;
           index < seconds.size(); ++index) {
        const Cap& third = caps_[seconds[index]];
        ++tested_[3];
        if ((second.mask & third.mask) ||
            second.singleton_row == third.singleton_row ||
            second.singleton_col == third.singleton_col)
          continue;
        if (!line_capacity(union2 | third.mask, 3)) continue;
        ++passed_[3];
        thirds.push_back(seconds[index]);
      }

      for (size_t third_index = 0;
           third_index < thirds.size(); ++third_index) {
        size_t third_id = thirds[third_index];
        const Cap& third = caps_[third_id];
        U128 union3 = union2 | third.mask;

        std::vector<size_t> fourths;
        for (size_t index = third_index + 1;
             index < thirds.size(); ++index) {
          const Cap& fourth = caps_[thirds[index]];
          ++tested_[4];
          if ((third.mask & fourth.mask) ||
              third.singleton_row == fourth.singleton_row ||
              third.singleton_col == fourth.singleton_col)
            continue;
          if (!line_capacity(union3 | fourth.mask, 4)) continue;
          ++passed_[4];
          fourths.push_back(thirds[index]);
        }

        for (size_t fourth_index = 0;
             fourth_index < fourths.size(); ++fourth_index) {
          size_t fourth_id = fourths[fourth_index];
          const Cap& fourth = caps_[fourth_id];
          U128 union4 = union3 | fourth.mask;
          for (size_t index = fourth_index + 1;
               index < fourths.size(); ++index) {
            const Cap& fifth = caps_[fourths[index]];
            ++tested_[5];
            if ((fourth.mask & fifth.mask) ||
                fourth.singleton_row == fifth.singleton_row ||
                fourth.singleton_col == fifth.singleton_col)
              continue;
            if (!line_capacity(union4 | fifth.mask, 5)) continue;
            ++passed_[5];
            chosen_[0] = first_id;
            chosen_[1] = second_id;
            chosen_[2] = third_id;
            chosen_[3] = fourth_id;
            chosen_[4] = fourths[index];
            return true;
          }
        }
      }
    }
    return false;
  }

  std::vector<Cap> caps_;
  std::vector<Line> lines_;
  size_t words_;
  std::vector<std::vector<uint64_t>> point_index_;
  std::vector<std::vector<uint64_t>> row_index_;
  std::vector<std::vector<uint64_t>> col_index_;
  std::array<std::vector<size_t>, 6> active_lines_;
  std::vector<size_t> first_representatives_;
  std::array<size_t, 5> chosen_{};
  std::array<uint64_t, 6> nodes_{};
  std::array<uint64_t, 6> tested_{};
  std::array<uint64_t, 6> passed_{};
  uint64_t first_caps_ = 0;
};

int main(int argc, char** argv) {
  try {
    std::string directory = "work/math_agent";
    std::string mode = "stats";
    size_t first = 10, representative = 0, second_limit = 100;
    size_t shard = 0, shards = 1;
    for (int index = 1; index < argc; ++index) {
      std::string argument = argv[index];
      if (argument == "--directory" && index + 1 < argc)
        directory = argv[++index];
      else if (argument == "--stats" && index + 1 < argc) {
        mode = "stats";
        first = std::stoull(argv[++index]);
      } else if (argument == "--stats3" && index + 2 < argc) {
        mode = "stats3";
        representative = std::stoull(argv[++index]);
        second_limit = std::stoull(argv[++index]);
      } else if (argument == "--search") {
        mode = "search";
      } else if (argument == "--shard" && index + 2 < argc) {
        shard = std::stoull(argv[++index]);
        shards = std::stoull(argv[++index]);
      } else {
        throw std::runtime_error("bad command-line argument " + argument);
      }
    }
    auto caps = load_all_caps(directory);
    auto lines = make_lines();
    Search search(std::move(caps), std::move(lines));
    if (mode == "stats") {
      search.stats(first);
      return 0;
    }
    if (mode == "stats3") {
      search.stats3(representative, second_limit);
      return 0;
    }
    return search.run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "ERROR " << error.what() << '\n';
    return 2;
  }
}
