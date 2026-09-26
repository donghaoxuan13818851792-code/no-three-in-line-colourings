// Exact residual search for Q5--Q7 after fixing caps of sizes 22,21,21.
//
// The input TSV is the independently audited prefix ledger produced by
// q567_cap_packing --prefix-only --residual-log.  A 20-cap is enumerated for
// Q5/Q6, using only the Q1--Q4-licensed extension rule, and its complement is
// solved as an exact two-colour problem.  Q7 enumerates a 19-cap without any
// dominance premise and likewise solves the remaining 19+19 split.

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using U128 = unsigned __int128;

namespace {
constexpr int N = 11;
constexpr int POINTS = 121;
constexpr U128 FULL = (U128(1) << POINTS) - 1;

int popcount(U128 value) {
  return std::popcount(static_cast<uint64_t>(value)) +
         std::popcount(static_cast<uint64_t>(value >> 64));
}

int least_point(U128 value) {
  const uint64_t low = static_cast<uint64_t>(value);
  if (low) return std::countr_zero(low);
  return 64 + std::countr_zero(static_cast<uint64_t>(value >> 64));
}

U128 parse_hex(const std::string& word) {
  U128 value = 0;
  for (char ch : word) {
    value <<= 4;
    if ('0' <= ch && ch <= '9') value |= ch - '0';
    else if ('a' <= ch && ch <= 'f') value |= ch - 'a' + 10;
    else if ('A' <= ch && ch <= 'F') value |= ch - 'A' + 10;
    else throw std::runtime_error("bad hexadecimal mask");
  }
  return value;
}

std::string to_hex(U128 value) {
  static constexpr char digits[] = "0123456789abcdef";
  if (!value) return "0";
  std::string result;
  while (value) {
    result.push_back(digits[static_cast<unsigned>(value & 15)]);
    value >>= 4;
  }
  std::reverse(result.begin(), result.end());
  return result;
}

bool collinear(int a, int b, int c) {
  const int ax = a % N, ay = a / N;
  const int bx = b % N, by = b / N;
  const int cx = c % N, cy = c / N;
  return (bx - ax) * (cy - ay) == (by - ay) * (cx - ax);
}

struct Prefix {
  size_t fixed_index = 0;
  size_t first_id = 0;
  size_t second_id = 0;
  U128 first = 0;
  U128 second = 0;
  U128 residual = 0;
};

std::vector<Prefix> load_prefixes(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open prefix ledger " + path);
  std::vector<Prefix> result;
  std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) continue;
    std::istringstream words(line);
    Prefix prefix;
    std::string first, second, residual;
    if (!(words >> prefix.fixed_index >> prefix.first_id >> prefix.second_id
                >> first >> second >> residual))
      throw std::runtime_error("malformed prefix ledger row");
    prefix.first = parse_hex(first);
    prefix.second = parse_hex(second);
    prefix.residual = parse_hex(residual);
    result.push_back(prefix);
  }
  return result;
}

class Search {
 public:
  Search(uint64_t node_limit, uint64_t progress_every,
         bool search_q56, bool search_q7)
      : node_limit_(node_limit), progress_every_(progress_every),
        search_q56_(search_q56), search_q7_(search_q7) {
    for (int a = 0; a < POINTS; ++a) {
      for (int b = a + 1; b < POINTS; ++b) {
        U128 line = 0;
        for (int c = 0; c < POINTS; ++c)
          if (collinear(a, b, c)) line |= U128(1) << c;
        pair_line_[a][b] = pair_line_[b][a] = line;
        if (popcount(line) >= 3) maximal_lines_set_.insert(line);
      }
    }
    lines_.assign(maximal_lines_set_.begin(), maximal_lines_set_.end());
    if (lines_.size() != 628)
      throw std::runtime_error("geometry did not produce 628 maximal lines");
  }

  // 10=SAT, 20=all requested prefixes UNSAT, 30=node-limited.
  int run(const std::vector<Prefix>& prefixes, size_t start, size_t count) {
    const size_t end = std::min(prefixes.size(), start + count);
    if (start > end) throw std::runtime_error("bad prefix range");
    for (size_t index = start; index < end; ++index) {
      current_prefix_index_ = index;
      if (!prepare(prefixes[index])) throw std::runtime_error("bad prefix row");
      if (search_q56_) {
        if (enumerate_target(20)) return 10;
        if (incomplete_) return 30;
      }
      if (search_q7_) {
        if (enumerate_target(19)) return 10;
        if (incomplete_) return 30;
      }
      ++prefixes_completed_;
      if (progress_every_ && prefixes_completed_ % progress_every_ == 0)
        std::cerr << "progress prefixes_completed " << prefixes_completed_
                  << " cap_nodes " << cap_nodes_
                  << " cap_leaves " << cap_leaves_
                  << " two_colour_nodes " << two_colour_nodes_ << '\n';
    }
    return 20;
  }

  void print_stats(int result) const {
    std::cout << (result == 10 ? "SAT_Q567_RESIDUAL" :
                  result == 20 ? "UNSAT_Q567_RESIDUAL_RANGE" :
                                 "INCOMPLETE_Q567_RESIDUAL")
              << " prefixes_completed " << prefixes_completed_
              << " current_prefix " << current_prefix_index_
              << " cap_nodes " << cap_nodes_
              << " cap_leaves " << cap_leaves_
              << " dominance_rejects " << dominance_rejects_
              << " complement_capacity_rejects "
              << complement_capacity_rejects_
              << " two_colour_instances " << two_colour_instances_
              << " two_colour_nodes " << two_colour_nodes_ << '\n';
    if (result == 10) {
      std::cout << "PREFIX " << current_prefix_index_
                << " FIXED_INDEX " << current_.fixed_index
                << " FIRST_ID " << current_.first_id
                << " SECOND_ID " << current_.second_id << '\n';
      std::cout << "SELECTED22_21_21 " << to_hex(selected_union_) << '\n';
      std::cout << "CAP_FIRST " << to_hex(solution_first_) << '\n';
      std::cout << "CAP_SECOND " << to_hex(solution_second_) << '\n';
      std::cout << "CAP_THIRD " << to_hex(solution_third_) << '\n';
      std::cout << "PROFILE " << solution_profile_ << '\n';
    }
  }

 private:
  bool prepare(const Prefix& prefix) {
    current_ = prefix;
    if (popcount(prefix.first) != 21 || popcount(prefix.second) != 21 ||
        popcount(prefix.residual) != 57)
      return false;
    if ((prefix.first & prefix.second) != 0) return false;
    selected_union_ = FULL ^ prefix.residual;
    if (popcount(selected_union_) != 64) return false;
    if ((prefix.first | prefix.second) & prefix.residual) return false;
    const U128 fixed = selected_union_ ^ prefix.first ^ prefix.second;
    if (popcount(fixed) != 22 ||
        (fixed & (prefix.first | prefix.second)) != 0)
      return false;
    for (U128 cap : {fixed, prefix.first, prefix.second})
      for (U128 line : lines_)
        if (popcount(cap & line) > 2) return false;
    for (U128 line : lines_)
      if (popcount(prefix.residual & line) > 6) return false;
    critical_lines_.clear();
    for (U128 line : lines_) {
      const U128 residual_line = prefix.residual & line;
      const int length = popcount(residual_line);
      if (length >= 5)
        critical_lines_.push_back({residual_line, length - 4});
    }
    std::array<int, N> row_scores{};
    for (const auto& [line, lower] : critical_lines_) {
      (void) lower;
      U128 scan = line;
      while (scan) {
        const int point = least_point(scan);
        row_scores[point / N] += 8;
        scan &= scan - 1;
      }
    }
    for (int row = 0; row < N; ++row) {
      row_order_[row] = row;
      U128 row_mask = ((U128(1) << N) - 1) << (row * N);
      // Shorter residual rows have fewer local choices.
      row_scores[row] += 20 * (6 - popcount(prefix.residual & row_mask));
    }
    std::stable_sort(row_order_.begin(), row_order_.end(),
                     [&](int a, int b) { return row_scores[a] > row_scores[b]; });
    return true;
  }

  bool enumerate_target(int target) {
    target_ = target;
    singleton_rows_left_ = 22 - target;
    column_degree_.fill(0);
    selected_points_.clear();
    return cap_recurse(0, 0, 0);
  }

  bool cap_recurse(int depth, U128 selected, U128 blocked) {
    if (node_limit_ && cap_nodes_ + two_colour_nodes_ >= node_limit_) {
      incomplete_ = true;
      return false;
    }
    ++cap_nodes_;
    if (depth == N) {
      if (singleton_rows_left_ != 0 || popcount(selected) != target_) return false;
      int singleton_columns = 0;
      for (int column = 0; column < N; ++column) {
        if (column_degree_[column] == 1) ++singleton_columns;
        else if (column_degree_[column] != 2) return false;
      }
      if (singleton_columns != 22 - target_) return false;
      if (!meets_long_diagonals(selected)) return false;
      ++cap_leaves_;
      if (target_ == 20 && !passes_size20_dominance(selected, blocked)) {
        ++dominance_rejects_;
        return false;
      }
      return test_complement(selected);
    }

    U128 future_mask = 0;
    for (int column = 0; column < N; ++column) {
      if (column_degree_[column] > 2) return false;
      int future = 0;
      for (int future_depth = depth; future_depth < N; ++future_depth) {
        const int future_row = row_order_[future_depth];
        const int point = future_row * N + column;
        const bool available = ((current_.residual >> point) & 1) &&
                               !((blocked >> point) & 1) &&
                               column_degree_[column] < 2;
        future += available;
        if (available) future_mask |= U128(1) << point;
      }
      if (column_degree_[column] + future < 1) return false;
    }
    // Once this cap is removed, two colours remain and cover at most four
    // points of any line.  A residual line of length m=5 or 6 therefore
    // requires this cap to take at least m-4 points.  Reject as soon as the
    // selected plus still geometrically available support cannot reach that
    // lower bound.
    for (const auto& [line, lower] : critical_lines_)
      if (popcount(selected & line) + popcount(future_mask & line) < lower)
        return false;

    const int row = row_order_[depth];
    const int rows_after = N - depth - 1;
    for (int need : {1, 2}) {
      if (need == 1 && singleton_rows_left_ == 0) continue;
      if (need == 2 && singleton_rows_left_ > rows_after) continue;
      if (need == 1) --singleton_rows_left_;
      std::array<int, N> available{};
      int available_count = 0;
      for (int column = 0; column < N; ++column) {
        const int point = row * N + column;
        if (((current_.residual >> point) & 1) &&
            !((blocked >> point) & 1) && column_degree_[column] < 2)
          available[available_count++] = point;
      }
      for (int i = 0; i < available_count; ++i) {
        const int p = available[i];
        const int j_begin = need == 1 ? i : i + 1;
        const int j_end = need == 1 ? i + 1 : available_count;
        for (int j = j_begin; j < j_end; ++j) {
          const int q = available[j];
          U128 next_blocked = blocked;
          for (int old : selected_points_) {
            next_blocked |= pair_line_[p][old];
            if (need == 2) next_blocked |= pair_line_[q][old];
          }
          selected_points_.push_back(p);
          ++column_degree_[p % N];
          U128 next_selected = selected | (U128(1) << p);
          if (need == 2) {
            selected_points_.push_back(q);
            ++column_degree_[q % N];
            next_selected |= U128(1) << q;
          }
          if (cap_recurse(depth + 1, next_selected, next_blocked)) return true;
          if (need == 2) {
            --column_degree_[q % N];
            selected_points_.pop_back();
          }
          --column_degree_[p % N];
          selected_points_.pop_back();
          if (incomplete_) return false;
        }
      }
      if (need == 1) ++singleton_rows_left_;
    }
    return false;
  }

  bool meets_long_diagonals(U128 cap) const {
    U128 main = 0, anti = 0;
    for (int index = 0; index < N; ++index) {
      main |= U128(1) << (index * N + index);
      anti |= U128(1) << (index * N + N - 1 - index);
    }
    return (cap & main) && (cap & anti);
  }

  bool passes_size20_dominance(U128 cap, U128 blocked) const {
    std::array<int, 2> rows{}, columns{};
    int row_count = 0, column_count = 0;
    for (int row = 0; row < N; ++row) {
      U128 row_mask = ((U128(1) << N) - 1) << (row * N);
      if (popcount(cap & row_mask) == 1) rows[row_count++] = row;
    }
    for (int column = 0; column < N; ++column) {
      int count = 0;
      for (int row = 0; row < N; ++row)
        count += static_cast<int>((cap >> (row * N + column)) & 1);
      if (count == 1) columns[column_count++] = column;
    }
    if (row_count != 2 || column_count != 2)
      throw std::runtime_error("bad size-20 singleton coordinates");
    for (int row : rows) for (int column : columns) {
      const U128 point = U128(1) << (row * N + column);
      if ((cap | selected_union_ | blocked) & point) continue;
      return false;
    }
    return true;
  }

  struct BinaryConstraint {
    std::array<uint8_t, 4> variables{};
    uint8_t length = 0;
  };

  bool test_complement(U128 first) {
    const U128 complement = current_.residual ^ first;
    const int complement_size = popcount(complement);
    int target_one = 0;
    const char* profile = nullptr;
    if (target_ == 20) {
      // The same enumerated 20-cap covers Q5 and Q6.
      if (solve_binary(complement, 20, first)) {
        profile = "Q5";
        target_one = 20;
      } else if (solve_binary(complement, 19, first)) {
        profile = "Q6";
        target_one = 19;
      }
    } else if (target_ == 19 && complement_size == 38 &&
               solve_binary(complement, 19, first)) {
      profile = "Q7";
      target_one = 19;
    }
    if (!profile) return false;
    solution_first_ = first;
    solution_second_ = binary_solution_one_;
    solution_third_ = complement ^ binary_solution_one_;
    solution_profile_ = profile;
    if (popcount(solution_second_) != target_one)
      throw std::runtime_error("bad binary solution size");
    validate_solution();
    return true;
  }

  bool solve_binary(U128 points, int target_one, U128 first_cap) {
    ++two_colour_instances_;
    binary_point_count_ = 0;
    local_id_.fill(-1);
    U128 scan = points;
    while (scan) {
      const int point = least_point(scan);
      local_id_[point] = binary_point_count_;
      global_point_[binary_point_count_++] = point;
      scan &= scan - 1;
    }
    binary_constraint_count_ = 0;
    binary_degree_.fill(0);
    for (U128 line : lines_) {
      U128 on_line = points & line;
      const int length = popcount(on_line);
      if (length > 4) {
        ++complement_capacity_rejects_;
        return false;
      }
      if (length < 3) continue;
      BinaryConstraint constraint;
      constraint.length = length;
      int index = 0;
      while (on_line) {
        const int point = least_point(on_line);
        const int local = local_id_[point];
        constraint.variables[index++] = local;
        ++binary_degree_[local];
        on_line &= on_line - 1;
      }
      binary_constraints_[binary_constraint_count_++] = constraint;
    }
    binary_target_ = target_one;
    binary_points_mask_ = points;
    binary_first_cap_ = first_cap;
    std::array<int8_t, 38> assignment;
    assignment.fill(-1);
    if (points == 0) return false;
    // For Q7 the two remaining size-19 colours are interchangeable.
    if (binary_point_count_ == 38 && target_one == 19) assignment[0] = 1;
    return binary_recurse(assignment);
  }

  bool binary_propagate(std::array<int8_t, 38>& assignment) {
    for (;;) {
      bool changed = false;
      int ones = 0, unknown = 0;
      for (int i = 0; i < binary_point_count_; ++i) {
        ones += assignment[i] == 1;
        unknown += assignment[i] < 0;
      }
      if (ones > binary_target_ || ones + unknown < binary_target_) return false;
      if (ones == binary_target_ || ones + unknown == binary_target_) {
        const int force = ones == binary_target_ ? 0 : 1;
        for (int i = 0; i < binary_point_count_; ++i)
          if (assignment[i] < 0) assignment[i] = force, changed = true;
      }
      for (int c = 0; c < binary_constraint_count_; ++c) {
        const BinaryConstraint& constraint = binary_constraints_[c];
        int line_ones = 0, line_unknown = 0;
        for (int j = 0; j < constraint.length; ++j) {
          const int value = assignment[constraint.variables[j]];
          line_ones += value == 1;
          line_unknown += value < 0;
        }
        const int lower = constraint.length - 2;
        constexpr int upper = 2;
        if (line_ones > upper || line_ones + line_unknown < lower) return false;
        if (line_ones == upper || line_ones + line_unknown == lower) {
          const int force = line_ones == upper ? 0 : 1;
          for (int j = 0; j < constraint.length; ++j) {
            int8_t& value = assignment[constraint.variables[j]];
            if (value < 0) value = force, changed = true;
          }
        }
      }
      if (!changed) return true;
    }
  }

  bool binary_recurse(std::array<int8_t, 38> assignment) {
    if (node_limit_ && cap_nodes_ + two_colour_nodes_ >= node_limit_) {
      incomplete_ = true;
      return false;
    }
    ++two_colour_nodes_;
    if (!binary_propagate(assignment)) return false;
    int chosen = -1, best_degree = -1;
    int assigned_ones = 0;
    for (int i = 0; i < binary_point_count_; ++i) {
      assigned_ones += assignment[i] == 1;
      if (assignment[i] < 0 && binary_degree_[i] > best_degree) {
        best_degree = binary_degree_[i];
        chosen = i;
      }
    }
    if (chosen < 0) {
      U128 cap = 0;
      for (int i = 0; i < binary_point_count_; ++i)
        if (assignment[i] == 1) cap |= U128(1) << global_point_[i];
      binary_solution_one_ = cap;
      return true;
    }
    const int preferred = assigned_ones < binary_target_ / 2 ? 1 : 0;
    for (int value : {preferred, 1 - preferred}) {
      auto child = assignment;
      child[chosen] = value;
      if (binary_recurse(child)) return true;
      if (incomplete_) return false;
    }
    return false;
  }

  void validate_solution() const {
    U128 union_mask = selected_union_;
    for (U128 cap : {solution_first_, solution_second_, solution_third_}) {
      if (union_mask & cap) throw std::runtime_error("solution caps overlap");
      union_mask |= cap;
      for (U128 line : lines_)
        if (popcount(cap & line) > 2)
          throw std::runtime_error("solution contains collinear triple");
    }
    if (union_mask != FULL) throw std::runtime_error("solution does not cover grid");
  }

  uint64_t node_limit_ = 0, progress_every_ = 0;
  bool incomplete_ = false;
  bool search_q56_ = true, search_q7_ = true;
  std::array<std::array<U128, POINTS>, POINTS> pair_line_{};
  std::set<U128> maximal_lines_set_;
  std::vector<U128> lines_;
  std::vector<std::pair<U128, int>> critical_lines_;
  std::array<int, N> row_order_{};
  Prefix current_;
  size_t current_prefix_index_ = 0, prefixes_completed_ = 0;
  U128 selected_union_ = 0;
  int target_ = 0, singleton_rows_left_ = 0;
  std::array<uint8_t, N> column_degree_{};
  std::vector<int> selected_points_;

  std::array<int8_t, POINTS> local_id_{};
  std::array<int, 38> global_point_{};
  std::array<uint8_t, 38> binary_degree_{};
  std::array<BinaryConstraint, 628> binary_constraints_{};
  int binary_point_count_ = 0, binary_constraint_count_ = 0, binary_target_ = 0;
  U128 binary_points_mask_ = 0, binary_first_cap_ = 0;
  U128 binary_solution_one_ = 0;

  U128 solution_first_ = 0, solution_second_ = 0, solution_third_ = 0;
  const char* solution_profile_ = nullptr;
  uint64_t cap_nodes_ = 0, cap_leaves_ = 0, dominance_rejects_ = 0;
  uint64_t complement_capacity_rejects_ = 0;
  uint64_t two_colour_instances_ = 0, two_colour_nodes_ = 0;
};
}  // namespace

int main(int argc, char** argv) {
  try {
    std::string input;
    size_t start = 0, count = ~size_t(0);
    uint64_t node_limit = 0, progress_every = 100;
    std::string profiles = "all";
    for (int i = 1; i < argc; ++i) {
      const std::string arg = argv[i];
      if (arg == "--input" && i + 1 < argc) input = argv[++i];
      else if (arg == "--start" && i + 1 < argc) start = std::stoull(argv[++i]);
      else if (arg == "--count" && i + 1 < argc) count = std::stoull(argv[++i]);
      else if (arg == "--node-limit" && i + 1 < argc)
        node_limit = std::stoull(argv[++i]);
      else if (arg == "--progress-every" && i + 1 < argc)
        progress_every = std::stoull(argv[++i]);
      else if (arg == "--profiles" && i + 1 < argc)
        profiles = argv[++i];
      else throw std::runtime_error("bad argument " + arg);
    }
    if (input.empty()) throw std::runtime_error("--input is required");
    if (profiles != "all" && profiles != "q56" && profiles != "q7")
      throw std::runtime_error("--profiles must be all, q56, or q7");
    const auto prefixes = load_prefixes(input);
    const auto begin = std::chrono::steady_clock::now();
    Search search(node_limit, progress_every,
                  profiles != "q7", profiles != "q56");
    const int result = search.run(prefixes, start, count);
    search.print_stats(result);
    std::cerr << "elapsed_seconds "
              << std::chrono::duration<double>(
                     std::chrono::steady_clock::now() - begin).count()
              << '\n';
    return result;
  } catch (const std::exception& error) {
    std::cerr << "ERROR " << error.what() << '\n';
    return 2;
  }
}
