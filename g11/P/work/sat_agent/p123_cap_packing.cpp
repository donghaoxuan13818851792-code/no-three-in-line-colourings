// Exact cap-level search for the three profiles with at least four 21-caps.
//
// Reuse the independently audited cap loader, geometry, mask operations, and
// D4 implementation from the frozen P1 search without modifying that source.
#define main p1_cap_packing_unused_main
#include "p1_cap_packing.cpp"
#undef main

struct ResidualConstraint {
  uint64_t variables;
  uint8_t length;
};

class TwoCapResidualChecker {
 public:
  explicit TwoCapResidualChecker(const std::vector<Line>& lines)
      : lines_(lines) {}

  bool solve(U128 selected_union, U128& first_colour, U128& second_colour) {
    ++instances_;
    constexpr U128 full_grid = (U128(1) << POINTS) - 1;
    U128 residual = full_grid ^ selected_union;
    if (popcount(residual) != 37)
      throw std::runtime_error("four caps must leave 37 points");

    std::array<int8_t, POINTS> local_id;
    local_id.fill(-1);
    std::array<int, 37> global_point{};
    int local_count = 0;
    for (int point = 0; point < POINTS; ++point) {
      if (!((residual >> point) & 1)) continue;
      local_id[point] = static_cast<int8_t>(local_count);
      global_point[local_count++] = point;
    }
    if (local_count != 37) throw std::runtime_error("bad residual mapping");

    constraint_count_ = 0;
    degrees_.fill(0);
    for (const Line& line : lines_) {
      U128 on_line = residual & line.mask;
      int length = popcount(on_line);
      if (length > 4)
        throw std::runtime_error("depth-four capacity invariant failed");
      if (length < 3) continue;
      uint64_t variables = 0;
      while (on_line) {
        int point;
        uint64_t low = static_cast<uint64_t>(on_line);
        if (low)
          point = std::countr_zero(low);
        else
          point = 64 + std::countr_zero(
              static_cast<uint64_t>(on_line >> 64));
        int local = local_id[point];
        if (local < 0) throw std::runtime_error("bad local point");
        variables |= uint64_t(1) << local;
        on_line &= on_line - 1;
      }
      constraints_[constraint_count_++] = {
          variables, static_cast<uint8_t>(length)};
      uint64_t scan = variables;
      while (scan) {
        int local = std::countr_zero(scan);
        ++degrees_[local];
        scan &= scan - 1;
      }
    }

    // Swapping the two residual colours is a symmetry.
    uint64_t assigned = 1;
    uint64_t ones = 0;
    uint64_t model_ones = 0;
    if (!search(assigned, ones, model_ones)) return false;

    first_colour = 0;
    second_colour = 0;
    for (int local = 0; local < 37; ++local) {
      U128 point_mask = U128(1) << global_point[local];
      if ((model_ones >> local) & 1)
        second_colour |= point_mask;
      else
        first_colour |= point_mask;
    }
    if (popcount(first_colour) > 21 || popcount(second_colour) > 21 ||
        (first_colour | second_colour) != residual ||
        (first_colour & second_colour))
      throw std::runtime_error("invalid residual model cardinality");
    for (const Line& line : lines_) {
      if (popcount(first_colour & line.mask) > 2 ||
          popcount(second_colour & line.mask) > 2)
        throw std::runtime_error("invalid residual model geometry");
    }
    ++satisfiable_instances_;
    return true;
  }

  uint64_t instances() const { return instances_; }
  uint64_t nodes() const { return nodes_; }
  uint64_t propagation_conflicts() const {
    return propagation_conflicts_;
  }
  uint64_t satisfiable_instances() const {
    return satisfiable_instances_;
  }

 private:
  static constexpr uint64_t FULL37 = (uint64_t(1) << 37) - 1;

  bool force(uint64_t variables, bool value,
             uint64_t& assigned, uint64_t& ones) const {
    uint64_t already = variables & assigned;
    if (value) {
      if (already & ~ones) return false;
      ones |= variables;
    } else {
      if (already & ones) return false;
      ones &= ~variables;
    }
    assigned |= variables;
    return true;
  }

  bool propagate(uint64_t& assigned, uint64_t& ones) {
    for (;;) {
      bool changed = false;
      int one_count = std::popcount(ones);
      int zero_count = std::popcount(assigned) - one_count;
      if (one_count > 21 || zero_count > 21) {
        ++propagation_conflicts_;
        return false;
      }
      uint64_t unassigned = FULL37 & ~assigned;
      if (unassigned) {
        if (one_count == 21) {
          if (!force(unassigned, false, assigned, ones)) {
            ++propagation_conflicts_;
            return false;
          }
          changed = true;
        } else if (zero_count == 21) {
          if (!force(unassigned, true, assigned, ones)) {
            ++propagation_conflicts_;
            return false;
          }
          changed = true;
        }
      }

      for (int index = 0; index < constraint_count_; ++index) {
        const ResidualConstraint& constraint = constraints_[index];
        uint64_t present = constraint.variables & assigned;
        int one = std::popcount(constraint.variables & ones);
        int zero = std::popcount(present) - one;
        if (one > 2 || zero > 2) {
          ++propagation_conflicts_;
          return false;
        }
        uint64_t free = constraint.variables & ~assigned;
        if (!free) continue;
        if (one == 2) {
          if (!force(free, false, assigned, ones)) {
            ++propagation_conflicts_;
            return false;
          }
          changed = true;
        } else if (zero == 2) {
          if (!force(free, true, assigned, ones)) {
            ++propagation_conflicts_;
            return false;
          }
          changed = true;
        }
      }
      if (!changed) return true;
    }
  }

  bool search(uint64_t assigned, uint64_t ones, uint64_t& model_ones) {
    ++nodes_;
    if (!propagate(assigned, ones)) return false;
    if (assigned == FULL37) {
      int one_count = std::popcount(ones);
      int zero_count = 37 - one_count;
      if (one_count <= 21 && zero_count <= 21) {
        model_ones = ones;
        return true;
      }
      return false;
    }

    uint64_t free = FULL37 & ~assigned;
    int chosen = -1;
    int best_score = -1;
    uint64_t scan = free;
    while (scan) {
      int variable = std::countr_zero(scan);
      int score = degrees_[variable];
      // Prefer variables on constraints that are close to forcing.
      uint64_t bit = uint64_t(1) << variable;
      for (int index = 0; index < constraint_count_; ++index) {
        const ResidualConstraint& constraint = constraints_[index];
        if (!(constraint.variables & bit)) continue;
        int assigned_here =
            std::popcount(constraint.variables & assigned);
        if (assigned_here >= 2) score += 4;
        else if (assigned_here == 1) score += 1;
      }
      if (score > best_score) {
        best_score = score;
        chosen = variable;
      }
      scan &= scan - 1;
    }
    if (chosen < 0) throw std::runtime_error("failed to branch");
    uint64_t bit = uint64_t(1) << chosen;
    int one_count = std::popcount(ones);
    int zero_count = std::popcount(assigned) - one_count;
    bool first_value = one_count < zero_count;
    for (bool value : {first_value, !first_value}) {
      uint64_t next_assigned = assigned;
      uint64_t next_ones = ones;
      if (!force(bit, value, next_assigned, next_ones)) continue;
      if (search(next_assigned, next_ones, model_ones)) return true;
    }
    return false;
  }

  const std::vector<Line>& lines_;
  std::array<ResidualConstraint, 628> constraints_{};
  std::array<uint16_t, 37> degrees_{};
  int constraint_count_ = 0;
  uint64_t instances_ = 0;
  uint64_t nodes_ = 0;
  uint64_t propagation_conflicts_ = 0;
  uint64_t satisfiable_instances_ = 0;
};

class P123Search {
 public:
  P123Search(std::vector<Cap> caps, std::vector<Line> lines)
      : caps_(std::move(caps)), lines_(std::move(lines)),
        words_((caps_.size() + 63) / 64),
        point_index_(POINTS, std::vector<uint64_t>(words_)),
        row_index_(N, std::vector<uint64_t>(words_)),
        col_index_(N, std::vector<uint64_t>(words_)),
        residual_checker_(lines_) {
    for (size_t id = 0; id < caps_.size(); ++id) {
      uint64_t bit = uint64_t(1) << (id & 63);
      size_t word = id >> 6;
      U128 mask = caps_[id].mask;
      for (int point = 0; point < POINTS; ++point)
        if ((mask >> point) & 1) point_index_[point][word] |= bit;
      row_index_[caps_[id].singleton_row][word] |= bit;
      col_index_[caps_[id].singleton_col][word] |= bit;
    }
    for (int depth = 2; depth <= 4; ++depth) {
      int capacity = 2 * (6 - depth);
      for (size_t line = 0; line < lines_.size(); ++line)
        if (lines_[line].length > capacity)
          active_lines_[depth].push_back(line);
    }
    for (size_t id = 0; id < caps_.size(); ++id) {
      U128 canonical = caps_[id].mask;
      for (int symmetry = 1; symmetry < 8; ++symmetry)
        canonical = std::min(
            canonical, transform(caps_[id].mask, symmetry));
      if (caps_[id].mask == canonical) first_representatives_.push_back(id);
    }
    if (first_representatives_.size() != 127491)
      throw std::runtime_error("expected 127,491 D4 representatives");
    std::cerr << "caps " << caps_.size()
              << " d4_representatives " << first_representatives_.size()
              << " words " << words_ << '\n';
  }

  bool run(size_t shard, size_t shards) {
    if (!shards || shard >= shards)
      throw std::runtime_error("bad shard");
    auto started = std::chrono::steady_clock::now();
    for (size_t representative_index = shard;
         representative_index < first_representatives_.size();
         representative_index += shards) {
      size_t first_id = first_representatives_[representative_index];
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
        std::cout << "SOLUTION123";
        for (size_t id : chosen_) std::cout << ' ' << id;
        std::cout << '\n';
        for (size_t id : chosen_)
          std::cout << to_hex(caps_[id].mask) << '\n';
        std::cout << "RESIDUAL_A " << to_hex(residual_a_) << '\n';
        std::cout << "RESIDUAL_B " << to_hex(residual_b_) << '\n';
        std::cout << "SIZES 21 21 21 21 "
                  << popcount(residual_a_) << ' '
                  << popcount(residual_b_) << '\n';
        return true;
      }
      if ((first_caps_ % 100) == 0) {
        double seconds_elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started).count();
        std::cerr
            << "progress shard " << shard << '/' << shards
            << " first_caps " << first_caps_
            << " rep_index " << representative_index
            << " tested2 " << tested_[2] << " passed2 " << passed_[2]
            << " tested3 " << tested_[3] << " passed3 " << passed_[3]
            << " tested4 " << tested_[4] << " passed4 " << passed_[4]
            << " residual_instances " << residual_checker_.instances()
            << " residual_nodes " << residual_checker_.nodes()
            << " residual_sat "
            << residual_checker_.satisfiable_instances()
            << " seconds " << seconds_elapsed << '\n';
      }
    }
    std::cout
        << "UNSAT123_SHARD " << shard << ' ' << shards
        << " first_caps " << first_caps_
        << " tested2 " << tested_[2] << " passed2 " << passed_[2]
        << " tested3 " << tested_[3] << " passed3 " << passed_[3]
        << " tested4 " << tested_[4] << " passed4 " << passed_[4]
        << " residual_instances " << residual_checker_.instances()
        << " residual_nodes " << residual_checker_.nodes()
        << " residual_conflicts "
        << residual_checker_.propagation_conflicts()
        << " residual_sat "
        << residual_checker_.satisfiable_instances() << '\n';
    return false;
  }

 private:
  bool line_capacity(U128 selected_union, int depth) const {
    int residual_capacity = 2 * (6 - depth);
    for (size_t line_id : active_lines_[depth]) {
      const Line& line = lines_[line_id];
      if (popcount(selected_union & line.mask) <
          static_cast<int>(line.length) - residual_capacity)
        return false;
    }
    return true;
  }

  static void and_not(
      std::vector<uint64_t>& destination,
      const std::vector<uint64_t>& excluded) {
    for (size_t word = 0; word < destination.size(); ++word)
      destination[word] &= ~excluded[word];
  }

  std::vector<uint64_t> compatible_with(const Cap& cap) const {
    std::vector<uint64_t> result(words_, ~uint64_t(0));
    if (caps_.size() & 63)
      result.back() &= (uint64_t(1) << (caps_.size() & 63)) - 1;
    and_not(result, row_index_[cap.singleton_row]);
    and_not(result, col_index_[cap.singleton_col]);
    U128 mask = cap.mask;
    while (mask) {
      int point;
      uint64_t low = static_cast<uint64_t>(mask);
      if (low)
        point = std::countr_zero(low);
      else
        point = 64 + std::countr_zero(static_cast<uint64_t>(mask >> 64));
      and_not(result, point_index_[point]);
      mask &= mask - 1;
    }
    return result;
  }

  static void clear_through(std::vector<uint64_t>& bits, size_t id) {
    size_t word = id >> 6;
    std::fill(bits.begin(), bits.begin() + word, uint64_t(0));
    uint64_t keep_above =
        (id & 63) == 63 ? uint64_t(0)
                        : ~((uint64_t(1) << ((id & 63) + 1)) - 1);
    bits[word] &= keep_above;
  }

  template <class Function>
  static void for_each_bit(
      const std::vector<uint64_t>& bits, Function function) {
    for (size_t word_index = 0; word_index < bits.size(); ++word_index) {
      uint64_t word = bits[word_index];
      while (word) {
        int offset = std::countr_zero(word);
        function((word_index << 6) + offset);
        word &= word - 1;
      }
    }
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
        for (size_t index = third_index + 1;
             index < thirds.size(); ++index) {
          size_t fourth_id = thirds[index];
          const Cap& fourth = caps_[fourth_id];
          ++tested_[4];
          if ((third.mask & fourth.mask) ||
              third.singleton_row == fourth.singleton_row ||
              third.singleton_col == fourth.singleton_col)
            continue;
          U128 union4 = union3 | fourth.mask;
          if (!line_capacity(union4, 4)) continue;
          ++passed_[4];
          if (!residual_checker_.solve(
                  union4, residual_a_, residual_b_))
            continue;
          chosen_[0] = first_id;
          chosen_[1] = second_id;
          chosen_[2] = third_id;
          chosen_[3] = fourth_id;
          return true;
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
  std::array<std::vector<size_t>, 5> active_lines_;
  std::vector<size_t> first_representatives_;
  TwoCapResidualChecker residual_checker_;
  std::array<size_t, 4> chosen_{};
  std::array<uint64_t, 5> tested_{};
  std::array<uint64_t, 5> passed_{};
  uint64_t first_caps_ = 0;
  U128 residual_a_ = 0;
  U128 residual_b_ = 0;
};

int main(int argc, char** argv) {
  try {
    std::string directory = "work/math_agent";
    size_t shard = 0, shards = 1;
    for (int index = 1; index < argc; ++index) {
      std::string argument = argv[index];
      if (argument == "--directory" && index + 1 < argc)
        directory = argv[++index];
      else if (argument == "--shard" && index + 2 < argc) {
        shard = std::stoull(argv[++index]);
        shards = std::stoull(argv[++index]);
      } else {
        throw std::runtime_error("bad command-line argument " + argument);
      }
    }
    auto caps = load_all_caps(directory);
    auto lines = make_lines();
    P123Search search(std::move(caps), std::move(lines));
    return search.run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "ERROR " << error.what() << '\n';
    return 2;
  }
}
