// Exact join solver for a complete catalogue of anchor-compatible 20-caps.
//
// Given one fixed size-22 anchor A and a sorted unique list F of every
// compatible size-20 cap, Q10 exists over this anchor iff there are four
// pairwise-disjoint members of F whose 19-point complement is a cap.
//
// The four equal classes are canonically ordered by their (distinct) pair of
// singleton rows.  At depth q, every line must leave at most 2*(5-q) points
// for the remaining colours.  Candidate-set bitsets implement all filtering;
// the search itself is a transparent four-level exhaustive join.
#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using U128 = unsigned __int128;
constexpr int N = 11;
constexpr int P = 121;
constexpr int NLINES = 628;
constexpr U128 FULL = (U128(1) << P) - 1;

int popcount(U128 x) {
  return std::popcount(static_cast<uint64_t>(x)) +
         std::popcount(static_cast<uint64_t>(x >> 64));
}

int lowbit(U128 x) {
  const uint64_t lo = static_cast<uint64_t>(x);
  if (lo) return std::countr_zero(lo);
  const uint64_t hi = static_cast<uint64_t>(x >> 64);
  return hi ? 64 + std::countr_zero(hi) : -1;
}

U128 parse_hex(const std::string& text) {
  if (text.size() != 31) throw std::runtime_error("mask must have exactly 31 hex digits");
  U128 value = 0;
  for (char ch : text) {
    int digit = -1;
    if ('0' <= ch && ch <= '9') digit = ch - '0';
    if ('a' <= ch && ch <= 'f') digit = ch - 'a' + 10;
    if ('A' <= ch && ch <= 'F') digit = ch - 'A' + 10;
    if (digit < 0) throw std::runtime_error("invalid hex digit");
    value = (value << 4) | static_cast<unsigned>(digit);
  }
  if (value & ~FULL) throw std::runtime_error("mask has bits outside the 11x11 grid");
  return value;
}

std::string to_hex(U128 value) {
  static constexpr char digits[] = "0123456789abcdef";
  std::string result(31, '0');
  for (int i = 30; i >= 0; --i) {
    result[i] = digits[static_cast<unsigned>(value & 15)];
    value >>= 4;
  }
  return result;
}

struct Geometry {
  std::array<U128, NLINES> lines{};
  std::array<uint8_t, NLINES> lengths{};
  std::array<std::pair<uint8_t, uint8_t>, 55> pairs{};

  Geometry() {
    std::set<U128> unique;
    for (int a = 0; a < P; ++a) {
      const int ar = a / N, ac = a % N;
      for (int b = a + 1; b < P; ++b) {
        const int br = b / N, bc = b % N;
        U128 line = 0;
        for (int p = 0; p < P; ++p) {
          const int r = p / N, c = p % N;
          if ((br - ar) * (c - ac) == (bc - ac) * (r - ar)) line |= U128(1) << p;
        }
        if (popcount(line) >= 3) unique.insert(line);
      }
    }
    if (unique.size() != NLINES) throw std::runtime_error("geometry is not 628 maximal lines");
    int li = 0;
    for (U128 line : unique) {
      lines[li] = line;
      lengths[li] = static_cast<uint8_t>(popcount(line));
      ++li;
    }
    int pi = 0;
    for (int a = 0; a < N; ++a)
      for (int b = a + 1; b < N; ++b)
        pairs[pi++] = {static_cast<uint8_t>(a), static_cast<uint8_t>(b)};
  }
};

struct Candidate {
  U128 mask = 0;
  uint8_t row_pair = 0;
  uint8_t col_pair = 0;
};

struct Filter {
  const uint64_t* words = nullptr;
  bool invert = false;
  uint64_t allowed_count = 0;
};

struct Pool {
  std::vector<uint64_t> bits;
  std::vector<uint32_t> active;

  explicit Pool(size_t word_count) : bits(word_count), active() {
    active.reserve(word_count);
  }

  void make_full(size_t candidate_count) {
    const size_t words = bits.size();
    active.resize(words);
    std::iota(active.begin(), active.end(), 0);
    std::fill(bits.begin(), bits.end(), ~uint64_t(0));
    if (candidate_count % 64) bits.back() = (uint64_t(1) << (candidate_count % 64)) - 1;
  }

  void copy_from(const Pool& parent) {
    active = parent.active;
    for (uint32_t word : active) bits[word] = parent.bits[word];
  }

  bool apply(std::vector<Filter>& filters) {
    std::sort(filters.begin(), filters.end(), [](const Filter& a, const Filter& b) {
      return a.allowed_count < b.allowed_count;
    });
    for (const Filter& filter : filters) {
      size_t out = 0;
      for (uint32_t word : active) {
        uint64_t allowed = filter.words[word];
        if (filter.invert) allowed = ~allowed;
        const uint64_t value = bits[word] & allowed;
        bits[word] = value;
        if (value) active[out++] = word;
      }
      active.resize(out);
      if (active.empty()) return false;
    }
    return true;
  }

  template <class Function>
  bool each(size_t candidate_count, Function function) const {
    for (uint32_t word : active) {
      uint64_t value = bits[word];
      while (value) {
        const unsigned offset = std::countr_zero(value);
        const size_t index = size_t(word) * 64 + offset;
        value &= value - 1;
        if (index < candidate_count && !function(index)) return false;
      }
    }
    return true;
  }

  size_t count() const {
    size_t result = 0;
    for (uint32_t word : active) result += std::popcount(bits[word]);
    return result;
  }
};

struct Solver {
  Geometry geometry;
  U128 anchor;
  std::vector<Candidate> candidates;
  std::vector<uint8_t> line_counts;  // candidate-major, exactly 628 bytes each
  size_t word_count = 0;
  std::vector<uint64_t> contains;     // [point][word]
  std::vector<uint64_t> line_ge1;     // [line][word]
  std::vector<uint64_t> line_ge2;     // [line][word]
  std::array<std::vector<uint64_t>, 55> row_future;
  std::array<std::vector<uint64_t>, 55> col_disjoint;
  std::array<uint64_t, P> point_frequency{};
  std::array<uint64_t, NLINES> line_ge1_frequency{};
  std::array<uint64_t, NLINES> line_ge2_frequency{};
  std::array<uint64_t, 55> row_future_frequency{};
  std::array<uint64_t, 55> col_disjoint_frequency{};
  std::array<uint8_t, NLINES> initial_remaining{};

  int root_pair_filter = -1;
  double seconds_limit = 0;
  std::chrono::steady_clock::time_point started;
  bool stopped = false;
  bool found = false;
  std::array<size_t, 4> witness_indices{};
  U128 witness_complement = 0;

  uint64_t roots_examined = 0;
  uint64_t pair_candidates = 0;
  uint64_t triple_candidates = 0;
  uint64_t final_pool_candidates = 0;
  uint64_t pair_pools_built = 0;
  uint64_t triple_pools_built = 0;
  uint64_t final_pools_built = 0;

  Solver(U128 fixed_anchor, const std::string& cap_path, int root_pair, double limit)
      : anchor(fixed_anchor), root_pair_filter(root_pair), seconds_limit(limit) {
    if (popcount(anchor) != 22) throw std::runtime_error("anchor does not have size 22");
    for (int li = 0; li < NLINES; ++li) {
      initial_remaining[li] = geometry.lengths[li] - popcount(anchor & geometry.lines[li]);
      if (initial_remaining[li] > 10) throw std::runtime_error("anchor violates five-colour line capacity");
    }
    read_and_validate_candidates(cap_path);
    build_indexes();
  }

  uint8_t count_at(size_t candidate, int line) const {
    return line_counts[candidate * NLINES + line];
  }

  int pair_id(const std::array<uint8_t, N>& counts) const {
    std::array<int, 2> deficits{-1, -1};
    int used = 0;
    for (int i = 0; i < N; ++i) {
      if (counts[i] == 1) {
        if (used >= 2) return -1;
        deficits[used++] = i;
      } else if (counts[i] != 2) {
        return -1;
      }
    }
    if (used != 2) return -1;
    for (int id = 0; id < 55; ++id)
      if (geometry.pairs[id].first == deficits[0] && geometry.pairs[id].second == deficits[1]) return id;
    return -1;
  }

  void read_and_validate_candidates(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open cap catalogue");
    std::string token;
    U128 previous = 0;
    bool have_previous = false;
    while (input >> token) {
      if (!token.empty() && token[0] == '#') {
        std::string rest;
        std::getline(input, rest);
        continue;
      }
      const U128 mask = parse_hex(token);
      if (have_previous && mask <= previous)
        throw std::runtime_error("cap catalogue is not strictly increasing and unique");
      have_previous = true;
      previous = mask;
      if (popcount(mask) != 20) throw std::runtime_error("candidate does not have size 20");
      if (mask & anchor) throw std::runtime_error("candidate intersects anchor");

      std::array<uint8_t, N> rows{}, cols{};
      U128 points = mask;
      while (points) {
        const int p = lowbit(points);
        points &= points - 1;
        ++rows[p / N];
        ++cols[p % N];
      }
      const int rp = pair_id(rows), cp = pair_id(cols);
      if (rp < 0 || cp < 0) throw std::runtime_error("candidate lacks Q10 row/column deficit structure");

      const size_t index = candidates.size();
      candidates.push_back({mask, static_cast<uint8_t>(rp), static_cast<uint8_t>(cp)});
      line_counts.resize((index + 1) * NLINES);
      for (int li = 0; li < NLINES; ++li) {
        const int count = popcount(mask & geometry.lines[li]);
        if (count > 2) throw std::runtime_error("candidate contains a collinear triple");
        if (initial_remaining[li] - count > 8)
          throw std::runtime_error("candidate violates four-colour residual line capacity");
        line_counts[index * NLINES + li] = static_cast<uint8_t>(count);
      }
    }
    if (candidates.empty()) throw std::runtime_error("empty cap catalogue");
  }

  static bool pairs_disjoint(const std::pair<uint8_t, uint8_t>& a,
                             const std::pair<uint8_t, uint8_t>& b) {
    return a.first != b.first && a.first != b.second &&
           a.second != b.first && a.second != b.second;
  }

  void set_bit(std::vector<uint64_t>& table, size_t row, size_t index) {
    table[row * word_count + index / 64] |= uint64_t(1) << (index % 64);
  }

  void build_indexes() {
    const size_t count = candidates.size();
    word_count = (count + 63) / 64;
    contains.assign(P * word_count, 0);
    line_ge1.assign(NLINES * word_count, 0);
    line_ge2.assign(NLINES * word_count, 0);
    for (auto& bits : row_future) bits.assign(word_count, 0);
    for (auto& bits : col_disjoint) bits.assign(word_count, 0);

    for (size_t i = 0; i < count; ++i) {
      U128 points = candidates[i].mask;
      while (points) {
        const int p = lowbit(points);
        points &= points - 1;
        set_bit(contains, p, i);
        ++point_frequency[p];
      }
      for (int li = 0; li < NLINES; ++li) {
        const int hits = count_at(i, li);
        if (hits >= 1) {
          set_bit(line_ge1, li, i);
          ++line_ge1_frequency[li];
        }
        if (hits >= 2) {
          set_bit(line_ge2, li, i);
          ++line_ge2_frequency[li];
        }
      }
      for (int rp = 0; rp < 55; ++rp) {
        if (candidates[i].row_pair > rp &&
            pairs_disjoint(geometry.pairs[candidates[i].row_pair], geometry.pairs[rp])) {
          row_future[rp][i / 64] |= uint64_t(1) << (i % 64);
          ++row_future_frequency[rp];
        }
      }
      for (int cp = 0; cp < 55; ++cp) {
        if (pairs_disjoint(geometry.pairs[candidates[i].col_pair], geometry.pairs[cp])) {
          col_disjoint[cp][i / 64] |= uint64_t(1) << (i % 64);
          ++col_disjoint_frequency[cp];
        }
      }
    }
  }

  const uint64_t* row_ptr(const std::vector<uint64_t>& table, size_t row) const {
    return table.data() + row * word_count;
  }

  void filters_for_selection(std::vector<Filter>& filters, size_t selected) const {
    U128 points = candidates[selected].mask;
    while (points) {
      const int p = lowbit(points);
      points &= points - 1;
      filters.push_back({row_ptr(contains, p), true, candidates.size() - point_frequency[p]});
    }
    const int rp = candidates[selected].row_pair;
    const int cp = candidates[selected].col_pair;
    filters.push_back({row_future[rp].data(), false, row_future_frequency[rp]});
    filters.push_back({col_disjoint[cp].data(), false, col_disjoint_frequency[cp]});
  }

  void line_filters(std::vector<Filter>& filters,
                    const std::array<uint8_t, NLINES>& remaining,
                    int threshold) const {
    for (int li = 0; li < NLINES; ++li) {
      const int need = int(remaining[li]) - threshold;
      if (need <= 0) continue;
      if (need == 1)
        filters.push_back({row_ptr(line_ge1, li), false, line_ge1_frequency[li]});
      else if (need == 2)
        filters.push_back({row_ptr(line_ge2, li), false, line_ge2_frequency[li]});
      else
        filters.push_back({nullptr, false, 0});
    }
  }

  bool apply_filters(Pool& pool, std::vector<Filter>& filters) {
    for (const Filter& filter : filters)
      if (filter.words == nullptr) {
        pool.active.clear();
        return false;
      }
    return pool.apply(filters);
  }

  void subtract_candidate(const std::array<uint8_t, NLINES>& before,
                          size_t candidate,
                          std::array<uint8_t, NLINES>& after) const {
    for (int li = 0; li < NLINES; ++li) after[li] = before[li] - count_at(candidate, li);
  }

  bool time_exhausted() {
    if (seconds_limit <= 0) return false;
    const double elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    if (elapsed < seconds_limit) return false;
    stopped = true;
    return true;
  }

  bool verify_witness(size_t a, size_t b, size_t c, size_t d) {
    const std::array<size_t, 4> indices{a, b, c, d};
    U128 occupied = anchor;
    for (size_t index : indices) {
      if (occupied & candidates[index].mask) return false;
      occupied |= candidates[index].mask;
    }
    const U128 complement = FULL & ~occupied;
    if (popcount(complement) != 19) return false;
    for (U128 line : geometry.lines)
      if (popcount(complement & line) > 2) return false;
    witness_indices = indices;
    witness_complement = complement;
    return true;
  }

  void solve() {
    started = std::chrono::steady_clock::now();
    Pool full(word_count), pair_pool(word_count), triple_pool(word_count), final_pool(word_count);
    full.make_full(candidates.size());
    std::array<uint8_t, NLINES> remaining1{}, remaining2{}, remaining3{};
    std::vector<Filter> filters;
    filters.reserve(P + NLINES + 4);

    for (size_t a = 0; a < candidates.size(); ++a) {
      if (root_pair_filter >= 0 && candidates[a].row_pair != root_pair_filter) continue;
      if (time_exhausted()) return;
      ++roots_examined;
      subtract_candidate(initial_remaining, a, remaining1);
      pair_pool.copy_from(full);
      filters.clear();
      filters_for_selection(filters, a);
      line_filters(filters, remaining1, 6);
      ++pair_pools_built;
      if (!apply_filters(pair_pool, filters)) continue;

      bool keep_searching_pairs = pair_pool.each(candidates.size(), [&](size_t b) {
        if (stopped || found) return false;
        if (((++pair_candidates) & 4095) == 0 && time_exhausted()) return false;
        subtract_candidate(remaining1, b, remaining2);
        triple_pool.copy_from(pair_pool);
        filters.clear();
        filters_for_selection(filters, b);
        line_filters(filters, remaining2, 4);
        ++triple_pools_built;
        if (!apply_filters(triple_pool, filters)) return true;

        bool keep_searching_triples = triple_pool.each(candidates.size(), [&](size_t c) {
          if (stopped || found) return false;
          if (((++triple_candidates) & 4095) == 0 && time_exhausted()) return false;
          subtract_candidate(remaining2, c, remaining3);
          final_pool.copy_from(triple_pool);
          filters.clear();
          filters_for_selection(filters, c);
          line_filters(filters, remaining3, 2);
          ++final_pools_built;
          if (!apply_filters(final_pool, filters)) return true;
          final_pool_candidates += final_pool.count();
          bool keep_searching_final = final_pool.each(candidates.size(), [&](size_t d) {
            if (!verify_witness(a, b, c, d))
              throw std::runtime_error("internal final-pool witness verification failed");
            found = true;
            return false;
          });
          return keep_searching_final && !found;
        });
        return keep_searching_triples && !found && !stopped;
      });
      if (!keep_searching_pairs || found || stopped) return;
    }
  }

  int report(const std::string& witness_path) const {
    const double elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started).count();
    const char* status = found ? "SAT" : stopped ? "INCOMPLETE" : "COMPLETE_NO_WITNESS";
    std::cout << "status " << status << '\n';
    std::cout << "anchor " << to_hex(anchor) << '\n';
    std::cout << "candidate_count " << candidates.size() << '\n';
    std::cout << "root_row_pair " << root_pair_filter << '\n';
    std::cout << "roots_examined " << roots_examined << '\n';
    std::cout << "pair_candidates " << pair_candidates << '\n';
    std::cout << "triple_candidates " << triple_candidates << '\n';
    std::cout << "final_pool_candidates " << final_pool_candidates << '\n';
    std::cout << "pair_pools_built " << pair_pools_built << '\n';
    std::cout << "triple_pools_built " << triple_pools_built << '\n';
    std::cout << "final_pools_built " << final_pools_built << '\n';
    std::cout << "seconds " << elapsed << '\n';
    if (found) {
      std::cout << "anchor_mask " << to_hex(anchor) << '\n';
      for (int i = 0; i < 4; ++i)
        std::cout << "cap20_" << i << ' ' << to_hex(candidates[witness_indices[i]].mask) << '\n';
      std::cout << "cap19 " << to_hex(witness_complement) << '\n';
      if (!witness_path.empty()) {
        std::ofstream output(witness_path);
        if (!output) throw std::runtime_error("cannot open witness output");
        output << to_hex(anchor) << '\n';
        for (size_t index : witness_indices) output << to_hex(candidates[index].mask) << '\n';
        output << to_hex(witness_complement) << '\n';
      }
    }
    if (found) return 10;
    if (stopped) return 30;
    return 20;
  }
};

int main(int argc, char** argv) try {
  std::string anchor_text, caps_path, witness_path;
  int root_pair = -1;
  double seconds = 0;
  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    auto value = [&]() {
      if (++i >= argc) throw std::runtime_error("missing option value");
      return std::string(argv[i]);
    };
    if (arg == "--anchor") anchor_text = value();
    else if (arg == "--caps") caps_path = value();
    else if (arg == "--root-row-pair") root_pair = std::stoi(value());
    else if (arg == "--seconds") seconds = std::stod(value());
    else if (arg == "--witness") witness_path = value();
    else throw std::runtime_error("unknown option: " + arg);
  }
  if (anchor_text.empty() || caps_path.empty())
    throw std::runtime_error("usage: capset_join --anchor HEX --caps FILE [--root-row-pair 0..54] [--seconds S] [--witness FILE]");
  if (root_pair < -1 || root_pair >= 55) throw std::runtime_error("bad root row-pair shard");
  Solver solver(parse_hex(anchor_text), caps_path, root_pair, seconds);
  solver.solve();
  return solver.report(witness_path);
} catch (const std::exception& error) {
  std::cerr << "ERROR " << error.what() << '\n';
  return 50;
}
