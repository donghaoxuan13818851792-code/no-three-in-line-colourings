// Exact cap-level search for all one-max profiles Q1--Q4.
//
// Fix the unique size-22 class to one of the 89 audited D4 orbit
// representatives.  Choose three pairwise-disjoint size-21 caps in
// increasing numeric-mask order.  Their complement has 36 points and is
// split exhaustively into two caps, each of size at most 21.  Up to
// interchange, the only possible residual sizes are
//
//     21+15, 20+16, 19+17, 18+18,
//
// exactly Q1, Q2, Q3, and Q4.
//
// Completeness: D4 sends the unique 22-cap of every Q1--Q4 colouring to
// one fixed representative.  Q2--Q4 have exactly three 21-caps; Q1 has
// four, from which any three may be chosen.  Ordering the chosen masks
// removes their colour permutations without removing a set.  Every
// prefix passes the necessary line-capacity tests because its unselected
// colour classes cover the complement.  The final Boolean search tries
// every residual bipartition modulo interchange.
//
// Soundness: all fixed/selected masks are audited caps and are disjoint.
// The Boolean checker verifies that both residual parts are caps and
// have size at most 21.  The six masks partition all 121 grid points.

#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Reuse the frozen P1 geometry, cap loader, D4 transform, and U128 helpers.
#define main p1_cap_packing_unused_main
#include "p1_cap_packing.cpp"
#undef main

struct ResidualLineConstraint36 {
  uint64_t variables;
  uint8_t length;
};

class TwoCapResidual36 {
 public:
  explicit TwoCapResidual36(const std::vector<Line>& lines)
      : lines_(lines) {}

  bool solve(U128 selected_union, U128& first, U128& second) {
    ++instances_;
    constexpr U128 full = (U128(1) << POINTS) - 1;
    U128 residual = full ^ selected_union;
    if (popcount(residual) != 36)
      throw std::runtime_error("22+3*21 must leave 36 points");

    std::array<int8_t, POINTS> local_id;
    local_id.fill(-1);
    std::array<int, 36> global_point{};
    int count = 0;
    for (int point = 0; point < POINTS; ++point) {
      if (!((residual >> point) & 1)) continue;
      local_id[point] = static_cast<int8_t>(count);
      global_point[count++] = point;
    }
    if (count != 36) throw std::runtime_error("bad residual mapping");

    constraint_count_ = 0;
    degrees_.fill(0);
    for (const Line& line : lines_) {
      U128 on_line = residual & line.mask;
      int length = popcount(on_line);
      if (length > 4)
        throw std::runtime_error("depth-three capacity invariant failed");
      if (length < 3) continue;
      uint64_t variables = 0;
      while (on_line) {
        int point;
        uint64_t low = static_cast<uint64_t>(on_line);
        if (low) {
          point = std::countr_zero(low);
        } else {
          point = 64 + std::countr_zero(
              static_cast<uint64_t>(on_line >> 64));
        }
        int local = local_id[point];
        if (local < 0) throw std::runtime_error("bad local point");
        variables |= uint64_t(1) << local;
        on_line &= on_line - 1;
      }
      if (constraint_count_ >= static_cast<int>(constraints_.size()))
        throw std::runtime_error("too many residual constraints");
      constraints_[constraint_count_++] = {
          variables, static_cast<uint8_t>(length)};
      uint64_t scan = variables;
      while (scan) {
        int local = std::countr_zero(scan);
        ++degrees_[local];
        scan &= scan - 1;
      }
    }

    // The least residual point is assigned zero.  Every bipartition has
    // exactly one orientation satisfying this colour-swap convention.
    uint64_t assigned = 1;
    uint64_t ones = 0;
    uint64_t model = 0;
    if (!search(assigned, ones, model)) return false;

    first = second = 0;
    for (int local = 0; local < 36; ++local) {
      U128 point = U128(1) << global_point[local];
      if ((model >> local) & 1)
        second |= point;
      else
        first |= point;
    }
    if ((first | second) != residual || (first & second) ||
        popcount(first) > 21 || popcount(second) > 21)
      throw std::runtime_error("invalid residual model");
    for (const Line& line : lines_) {
      if (popcount(first & line.mask) > 2 ||
          popcount(second & line.mask) > 2)
        throw std::runtime_error("residual model contains a triple");
    }
    ++satisfiable_instances_;
    return true;
  }

  uint64_t instances() const { return instances_; }
  uint64_t nodes() const { return nodes_; }
  uint64_t conflicts() const { return conflicts_; }
  uint64_t satisfiable_instances() const {
    return satisfiable_instances_;
  }

 private:
  static constexpr uint64_t FULL36 = (uint64_t(1) << 36) - 1;

  static bool force(
      uint64_t variables, bool value,
      uint64_t& assigned, uint64_t& ones) {
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
        ++conflicts_;
        return false;
      }
      uint64_t unassigned = FULL36 & ~assigned;
      if (unassigned) {
        if (one_count == 21) {
          if (!force(unassigned, false, assigned, ones)) {
            ++conflicts_;
            return false;
          }
          changed = true;
        } else if (zero_count == 21) {
          if (!force(unassigned, true, assigned, ones)) {
            ++conflicts_;
            return false;
          }
          changed = true;
        }
      }

      for (int index = 0; index < constraint_count_; ++index) {
        const auto& constraint = constraints_[index];
        uint64_t present = constraint.variables & assigned;
        int one = std::popcount(constraint.variables & ones);
        int zero = std::popcount(present) - one;
        if (one > 2 || zero > 2) {
          ++conflicts_;
          return false;
        }
        uint64_t free = constraint.variables & ~assigned;
        if (!free) continue;
        if (one == 2) {
          if (!force(free, false, assigned, ones)) {
            ++conflicts_;
            return false;
          }
          changed = true;
        } else if (zero == 2) {
          if (!force(free, true, assigned, ones)) {
            ++conflicts_;
            return false;
          }
          changed = true;
        }
      }
      if (!changed) return true;
    }
  }

  bool search(uint64_t assigned, uint64_t ones, uint64_t& model) {
    ++nodes_;
    if (!propagate(assigned, ones)) return false;
    if (assigned == FULL36) {
      int one_count = std::popcount(ones);
      int zero_count = 36 - one_count;
      if (one_count <= 21 && zero_count <= 21) {
        model = ones;
        return true;
      }
      return false;
    }

    uint64_t free = FULL36 & ~assigned;
    int chosen = -1;
    int best_score = -1;
    uint64_t scan = free;
    while (scan) {
      int variable = std::countr_zero(scan);
      int score = degrees_[variable];
      uint64_t bit = uint64_t(1) << variable;
      for (int index = 0; index < constraint_count_; ++index) {
        const auto& constraint = constraints_[index];
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
      if (search(next_assigned, next_ones, model)) return true;
    }
    return false;
  }

  const std::vector<Line>& lines_;
  std::array<ResidualLineConstraint36, 628> constraints_{};
  std::array<uint16_t, 36> degrees_{};
  int constraint_count_ = 0;
  uint64_t instances_ = 0;
  uint64_t nodes_ = 0;
  uint64_t conflicts_ = 0;
  uint64_t satisfiable_instances_ = 0;
};

class LocalCompatibility {
 public:
  LocalCompatibility(
      const std::vector<Cap>& caps, std::vector<size_t> global_ids)
      : caps_(caps), global_ids_(std::move(global_ids)),
        words_((global_ids_.size() + 63) / 64),
        point_index_(POINTS, std::vector<uint64_t>(words_)),
        row_index_(N, std::vector<uint64_t>(words_)),
        col_index_(N, std::vector<uint64_t>(words_)),
        cache_(global_ids_.size()), ready_(global_ids_.size(), false) {
    for (size_t local = 0; local < global_ids_.size(); ++local) {
      const Cap& cap = caps_[global_ids_[local]];
      size_t word = local >> 6;
      uint64_t bit = uint64_t(1) << (local & 63);
      U128 mask = cap.mask;
      while (mask) {
        int point;
        uint64_t low = static_cast<uint64_t>(mask);
        if (low) {
          point = std::countr_zero(low);
        } else {
          point = 64 + std::countr_zero(
              static_cast<uint64_t>(mask >> 64));
        }
        point_index_[point][word] |= bit;
        mask &= mask - 1;
      }
      row_index_[cap.singleton_row][word] |= bit;
      col_index_[cap.singleton_col][word] |= bit;
    }
  }

  size_t size() const { return global_ids_.size(); }
  size_t global(size_t local) const { return global_ids_[local]; }

  const std::vector<uint64_t>& compatible(size_t local) {
    if (ready_[local]) return cache_[local];
    std::vector<uint64_t> result(words_, ~uint64_t(0));
    if (global_ids_.size() & 63) {
      result.back() &=
          (uint64_t(1) << (global_ids_.size() & 63)) - 1;
    }
    const Cap& cap = caps_[global_ids_[local]];
    and_not(result, row_index_[cap.singleton_row]);
    and_not(result, col_index_[cap.singleton_col]);
    U128 mask = cap.mask;
    while (mask) {
      int point;
      uint64_t low = static_cast<uint64_t>(mask);
      if (low) {
        point = std::countr_zero(low);
      } else {
        point = 64 + std::countr_zero(
            static_cast<uint64_t>(mask >> 64));
      }
      and_not(result, point_index_[point]);
      mask &= mask - 1;
    }
    cache_[local] = std::move(result);
    ready_[local] = true;
    return cache_[local];
  }

  static void clear_through(
      std::vector<uint64_t>& bits, size_t local) {
    size_t word = local >> 6;
    std::fill(bits.begin(), bits.begin() + word, uint64_t(0));
    uint64_t keep =
        (local & 63) == 63
        ? uint64_t(0)
        : ~((uint64_t(1) << ((local & 63) + 1)) - 1);
    bits[word] &= keep;
  }

  static void intersect(
      std::vector<uint64_t>& destination,
      const std::vector<uint64_t>& other) {
    for (size_t word = 0; word < destination.size(); ++word)
      destination[word] &= other[word];
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

 private:
  static void and_not(
      std::vector<uint64_t>& destination,
      const std::vector<uint64_t>& excluded) {
    for (size_t word = 0; word < destination.size(); ++word)
      destination[word] &= ~excluded[word];
  }

  const std::vector<Cap>& caps_;
  std::vector<size_t> global_ids_;
  size_t words_;
  std::vector<std::vector<uint64_t>> point_index_;
  std::vector<std::vector<uint64_t>> row_index_;
  std::vector<std::vector<uint64_t>> col_index_;
  std::vector<std::vector<uint64_t>> cache_;
  std::vector<bool> ready_;
};

class Q1234Search {
 public:
  Q1234Search(
      std::vector<Cap> caps21, std::vector<U128> caps22,
      std::vector<Line> lines)
      : caps21_(std::move(caps21)), caps22_(std::move(caps22)),
        lines_(std::move(lines)), residual_(lines_) {
    if (caps22_.size() != 89)
      throw std::runtime_error("expected 89 fixed size-22 caps");
    for (int remaining = 2; remaining <= 4; ++remaining) {
      int capacity = 2 * remaining;
      for (size_t line = 0; line < lines_.size(); ++line) {
        if (lines_[line].length > capacity)
          active_lines_[remaining].push_back(line);
      }
    }
    for (U128 fixed : caps22_) {
      if (popcount(fixed) != 22)
        throw std::runtime_error("bad fixed cap size");
      for (const Line& line : lines_) {
        if (popcount(fixed & line.mask) > 2)
          throw std::runtime_error("fixed table contains a non-cap");
      }
    }
  }

  bool run(size_t shard, size_t shards) {
    if (!shards || shard >= shards)
      throw std::runtime_error("bad shard");
    auto started = std::chrono::steady_clock::now();
    for (size_t fixed_index = shard;
         fixed_index < caps22_.size(); fixed_index += shards) {
      ++fixed_processed_;
      U128 fixed = caps22_[fixed_index];
      std::vector<size_t> ids;
      for (size_t id = 0; id < caps21_.size(); ++id) {
        if (!(fixed & caps21_[id].mask)) ids.push_back(id);
      }
      LocalCompatibility local(caps21_, std::move(ids));
      std::cerr << "fixed " << fixed_index
                << " candidates " << local.size() << '\n';
      if (search_fixed(fixed_index, fixed, local)) {
        std::cout << "SOLUTION_Q1234 fixed_index " << fixed_index << '\n';
        std::cout << "CAP22 " << to_hex(fixed) << '\n';
        for (int index = 0; index < 3; ++index) {
          std::cout << "CAP21_" << index + 1 << ' '
                    << to_hex(caps21_[chosen_[index]].mask) << '\n';
        }
        std::cout << "RESIDUAL_A " << to_hex(residual_a_) << '\n';
        std::cout << "RESIDUAL_B " << to_hex(residual_b_) << '\n';
        int a = popcount(residual_a_), b = popcount(residual_b_);
        if (a < b) std::swap(a, b);
        const char* profile =
            a == 21 ? "Q1" :
            a == 20 ? "Q2" :
            a == 19 ? "Q3" :
            a == 18 ? "Q4" : "ERROR";
        std::cout << "PROFILE " << profile
                  << " SIZES 22 21 21 21 " << a << ' ' << b << '\n';
        return true;
      }
      double elapsed = std::chrono::duration<double>(
          std::chrono::steady_clock::now() - started).count();
      std::cerr
          << "completed_fixed " << fixed_index
          << " tested1 " << tested_[1] << " passed1 " << passed_[1]
          << " tested2 " << tested_[2] << " passed2 " << passed_[2]
          << " tested3 " << tested_[3] << " passed3 " << passed_[3]
          << " residual_instances " << residual_.instances()
          << " residual_nodes " << residual_.nodes()
          << " residual_sat " << residual_.satisfiable_instances()
          << " seconds " << elapsed << '\n';
    }
    std::cout
        << "UNSAT_Q1234_SHARD " << shard << ' ' << shards
        << " fixed_processed " << fixed_processed_
        << " tested1 " << tested_[1] << " passed1 " << passed_[1]
        << " tested2 " << tested_[2] << " passed2 " << passed_[2]
        << " tested3 " << tested_[3] << " passed3 " << passed_[3]
        << " residual_instances " << residual_.instances()
        << " residual_nodes " << residual_.nodes()
        << " residual_conflicts " << residual_.conflicts()
        << " residual_sat " << residual_.satisfiable_instances() << '\n';
    return false;
  }

 private:
  bool line_capacity(
      U128 selected_union, int remaining_colours) const {
    for (size_t line_id : active_lines_[remaining_colours]) {
      const Line& line = lines_[line_id];
      if (popcount(selected_union & line.mask) <
          static_cast<int>(line.length) - 2 * remaining_colours)
        return false;
    }
    return true;
  }

  bool search_fixed(
      size_t, U128 fixed, LocalCompatibility& local) {
    for (size_t first = 0; first < local.size(); ++first) {
      ++tested_[1];
      size_t first_id = local.global(first);
      U128 union1 = fixed | caps21_[first_id].mask;
      if (!line_capacity(union1, 4)) continue;
      ++passed_[1];
      std::vector<uint64_t> seconds = local.compatible(first);
      LocalCompatibility::clear_through(seconds, first);
      bool found = false;
      LocalCompatibility::for_each_bit(seconds, [&](size_t second) {
        if (found) return;
        ++tested_[2];
        size_t second_id = local.global(second);
        U128 union2 = union1 | caps21_[second_id].mask;
        if (!line_capacity(union2, 3)) return;
        ++passed_[2];
        std::vector<uint64_t> thirds = seconds;
        LocalCompatibility::clear_through(thirds, second);
        LocalCompatibility::intersect(
            thirds, local.compatible(second));
        LocalCompatibility::for_each_bit(thirds, [&](size_t third) {
          if (found) return;
          ++tested_[3];
          size_t third_id = local.global(third);
          U128 union3 = union2 | caps21_[third_id].mask;
          if (!line_capacity(union3, 2)) return;
          ++passed_[3];
          if (!residual_.solve(union3, residual_a_, residual_b_))
            return;
          chosen_ = {first_id, second_id, third_id};
          found = true;
        });
      });
      if (found) return true;
    }
    return false;
  }

  std::vector<Cap> caps21_;
  std::vector<U128> caps22_;
  std::vector<Line> lines_;
  std::array<std::vector<size_t>, 5> active_lines_;
  TwoCapResidual36 residual_;
  std::array<size_t, 3> chosen_{};
  std::array<uint64_t, 4> tested_{};
  std::array<uint64_t, 4> passed_{};
  uint64_t fixed_processed_ = 0;
  U128 residual_a_ = 0;
  U128 residual_b_ = 0;
};

int main(int argc, char** argv) {
  try {
    std::string directory = "work/math_agent";
    std::string fixed_table = "work/math_agent/caps22_d4.hex";
    size_t shard = 0, shards = 1;
    for (int index = 1; index < argc; ++index) {
      std::string argument = argv[index];
      if (argument == "--directory" && index + 1 < argc) {
        directory = argv[++index];
      } else if (argument == "--fixed-table" && index + 1 < argc) {
        fixed_table = argv[++index];
      } else if (argument == "--shard" && index + 2 < argc) {
        shard = std::stoull(argv[++index]);
        shards = std::stoull(argv[++index]);
      } else {
        throw std::runtime_error(
            "bad command-line argument " + argument);
      }
    }
    auto caps21 = load_all_caps(directory);
    auto caps22 = load_masks(fixed_table);
    std::sort(caps22.begin(), caps22.end());
    if (std::adjacent_find(caps22.begin(), caps22.end()) != caps22.end())
      throw std::runtime_error("duplicate fixed cap");
    auto lines = make_lines();
    Q1234Search search(
        std::move(caps21), std::move(caps22), std::move(lines));
    return search.run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "ERROR " << error.what() << '\n';
    return 2;
  }
}
