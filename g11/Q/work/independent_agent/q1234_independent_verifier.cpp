// Independent replay of the Q1--Q4 fixed-cap packing computation.
//
// The two-word cap loader and pair-defined line construction come from the
// independently authored P1 checker.  This file does not include or call the
// implementation under audit.  It independently re-enumerates every
// fixed-cap/three-cap prefix and solves each 36-point residual through
// explicit NAE triples rather than the primary line-count solver.
#define main p1_independent_unused_main
#include "p1_independent_search.cpp"
#undef main

#include <optional>

namespace {

class TripleResidual36 {
 public:
  explicit TripleResidual36(const std::vector<Line>& lines)
      : lines_(lines) {}

  bool Solve(Mask residual) {
    ++instances_;
    if (Count(residual) != 36)
      throw std::runtime_error("residual size is not 36");

    std::array<std::int8_t, kPointCount> local{};
    local.fill(-1);
    std::array<int, 36> global{};
    int variables = 0;
    for (int point = 0; point < kPointCount; ++point) {
      if (!Test(residual, point)) continue;
      local[point] = static_cast<std::int8_t>(variables);
      global[variables++] = point;
    }
    if (variables != 36)
      throw std::runtime_error("bad residual-variable map");

    triples_.clear();
    occurrences_.fill(0);
    for (const Line& line : lines_) {
      std::array<int, 4> members{};
      int count = 0;
      for (int point = 0; point < kPointCount; ++point) {
        if (!Test(residual, point) || !Test(line.points, point)) continue;
        if (count == 4)
          throw std::runtime_error("residual line has more than four points");
        members[count++] = local[point];
      }
      for (int first = 0; first < count; ++first) {
        for (int second = first + 1; second < count; ++second) {
          for (int third = second + 1; third < count; ++third) {
            triples_.push_back({
                static_cast<std::uint8_t>(members[first]),
                static_cast<std::uint8_t>(members[second]),
                static_cast<std::uint8_t>(members[third]),
            });
            ++occurrences_[members[first]];
            ++occurrences_[members[second]];
            ++occurrences_[members[third]];
          }
        }
      }
    }

    std::array<std::int8_t, 36> values{};
    values.fill(-1);
    values[0] = 0;  // One representative under residual-colour interchange.
    std::array<std::int8_t, 36> model{};
    if (!Search(values, model)) return false;

    Mask zero;
    Mask one;
    for (int variable = 0; variable < 36; ++variable) {
      if (model[variable] == 0)
        Set(zero, global[variable]);
      else if (model[variable] == 1)
        Set(one, global[variable]);
      else
        throw std::runtime_error("incomplete residual model");
    }
    if (Any(zero & one) || (zero | one) != residual ||
        Count(zero) > 21 || Count(one) > 21)
      throw std::runtime_error("invalid residual model");
    for (const Line& line : lines_) {
      if (Count(zero & line.points) > 2 ||
          Count(one & line.points) > 2)
        throw std::runtime_error("residual model is not a pair of caps");
    }
    ++satisfiable_;
    return true;
  }

  std::uint64_t instances() const { return instances_; }
  std::uint64_t nodes() const { return nodes_; }
  std::uint64_t conflicts() const { return conflicts_; }
  std::uint64_t satisfiable() const { return satisfiable_; }

 private:
  struct Triple {
    std::uint8_t first;
    std::uint8_t second;
    std::uint8_t third;
  };

  bool Propagate(std::array<std::int8_t, 36>& values) {
    for (;;) {
      bool changed = false;
      int zeros = 0;
      int ones = 0;
      for (int value : values) {
        zeros += value == 0;
        ones += value == 1;
      }
      if (zeros > 21 || ones > 21) {
        ++conflicts_;
        return false;
      }
      if (zeros == 21 || ones == 21) {
        const int forced = zeros == 21 ? 1 : 0;
        for (std::int8_t& value : values) {
          if (value >= 0) continue;
          value = static_cast<std::int8_t>(forced);
          changed = true;
        }
      }

      for (const Triple& triple : triples_) {
        const std::array<int, 3> variables{
            triple.first, triple.second, triple.third};
        int free_variable = -1;
        int free_count = 0;
        int first_value = -1;
        bool assigned_differ = false;
        for (int variable : variables) {
          const int value = values[variable];
          if (value < 0) {
            free_variable = variable;
            ++free_count;
          } else if (first_value < 0) {
            first_value = value;
          } else if (value != first_value) {
            assigned_differ = true;
          }
        }
        if (assigned_differ) continue;
        if (free_count == 0) {
          ++conflicts_;
          return false;
        }
        if (free_count == 1) {
          const int forced = 1 - first_value;
          if (values[free_variable] >= 0 &&
              values[free_variable] != forced) {
            ++conflicts_;
            return false;
          }
          if (values[free_variable] < 0) {
            values[free_variable] = static_cast<std::int8_t>(forced);
            changed = true;
          }
        }
      }
      if (!changed) return true;
    }
  }

  bool Search(std::array<std::int8_t, 36> values,
              std::array<std::int8_t, 36>& model) {
    ++nodes_;
    if (!Propagate(values)) return false;
    int zeros = 0;
    int ones = 0;
    int chosen = -1;
    int best = -1;
    for (int variable = 0; variable < 36; ++variable) {
      zeros += values[variable] == 0;
      ones += values[variable] == 1;
      if (values[variable] < 0 && occurrences_[variable] > best) {
        chosen = variable;
        best = occurrences_[variable];
      }
    }
    if (chosen < 0) {
      if (zeros <= 21 && ones <= 21) {
        model = values;
        return true;
      }
      ++conflicts_;
      return false;
    }
    const int preferred = zeros < ones ? 0 : 1;
    for (int value : {preferred, 1 - preferred}) {
      auto child = values;
      child[chosen] = static_cast<std::int8_t>(value);
      if (Search(child, model)) return true;
    }
    return false;
  }

  const std::vector<Line>& lines_;
  std::vector<Triple> triples_;
  std::array<int, 36> occurrences_{};
  std::uint64_t instances_ = 0;
  std::uint64_t nodes_ = 0;
  std::uint64_t conflicts_ = 0;
  std::uint64_t satisfiable_ = 0;
};

class LocalIndex {
 public:
  LocalIndex(const std::vector<Cap>& caps,
             std::vector<std::size_t> global_ids)
      : caps_(caps),
        global_ids_(std::move(global_ids)),
        words_((global_ids_.size() + 63) / 64),
        by_point_(kPointCount, std::vector<std::uint64_t>(words_)),
        by_row_(kSide, std::vector<std::uint64_t>(words_)),
        by_column_(kSide, std::vector<std::uint64_t>(words_)),
        cache_(global_ids_.size()),
        ready_(global_ids_.size(), false) {
    for (std::size_t local = 0; local < global_ids_.size(); ++local) {
      const std::size_t word = local / 64;
      const std::uint64_t bit =
          std::uint64_t{1} << static_cast<unsigned>(local % 64);
      const Cap& cap = caps_[global_ids_[local]];
      for (int point = 0; point < kPointCount; ++point)
        if (Test(cap.points, point)) by_point_[point][word] |= bit;
      by_row_[cap.singleton_row][word] |= bit;
      by_column_[cap.singleton_column][word] |= bit;
    }
  }

  std::size_t size() const { return global_ids_.size(); }
  std::size_t global(std::size_t local) const {
    return global_ids_[local];
  }

  const std::vector<std::uint64_t>& CompatibleBits(std::size_t local) {
    if (ready_[local]) return cache_[local];
    std::vector<std::uint64_t> result(words_, ~std::uint64_t{0});
    if (global_ids_.size() % 64)
      result.back() &=
          (std::uint64_t{1} << (global_ids_.size() % 64)) - 1;
    const Cap& cap = caps_[global_ids_[local]];
    Exclude(result, by_row_[cap.singleton_row]);
    Exclude(result, by_column_[cap.singleton_column]);
    for (int point = 0; point < kPointCount; ++point)
      if (Test(cap.points, point)) Exclude(result, by_point_[point]);
    cache_[local] = std::move(result);
    ready_[local] = true;
    return cache_[local];
  }

  static void Intersect(std::vector<std::uint64_t>& destination,
                        const std::vector<std::uint64_t>& other) {
    for (std::size_t word = 0; word < destination.size(); ++word)
      destination[word] &= other[word];
  }

  static void ClearThrough(std::vector<std::uint64_t>& bits,
                           std::size_t local) {
    const std::size_t word = local / 64;
    std::fill(bits.begin(), bits.begin() + word, std::uint64_t{0});
    const unsigned offset = static_cast<unsigned>(local % 64);
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

 private:
  static void Exclude(std::vector<std::uint64_t>& destination,
                      const std::vector<std::uint64_t>& excluded) {
    for (std::size_t word = 0; word < destination.size(); ++word)
      destination[word] &= ~excluded[word];
  }

  const std::vector<Cap>& caps_;
  std::vector<std::size_t> global_ids_;
  std::size_t words_;
  std::vector<std::vector<std::uint64_t>> by_point_;
  std::vector<std::vector<std::uint64_t>> by_row_;
  std::vector<std::vector<std::uint64_t>> by_column_;
  std::vector<std::vector<std::uint64_t>> cache_;
  std::vector<bool> ready_;
};

class IndependentQ1234 {
 public:
  IndependentQ1234(std::vector<Cap> caps,
                   std::vector<Mask> fixed,
                   std::vector<Line> lines,
                   const std::filesystem::path& residual_path)
      : caps_(std::move(caps)),
        fixed_(std::move(fixed)),
        lines_(std::move(lines)),
        residual_(lines_),
        residual_output_(residual_path) {
    if (!residual_output_)
      throw std::runtime_error("cannot create residual stream");
    if (fixed_.size() != 89)
      throw std::runtime_error("fixed table does not have 89 entries");
    std::sort(fixed_.begin(), fixed_.end());
    if (std::adjacent_find(fixed_.begin(), fixed_.end()) != fixed_.end())
      throw std::runtime_error("duplicate fixed cap");
    for (Mask cap : fixed_) ValidateFixed(cap);
    for (int remaining = 2; remaining <= 4; ++remaining) {
      const int capacity = 2 * remaining;
      for (std::size_t line = 0; line < lines_.size(); ++line)
        if (lines_[line].size > capacity)
          active_[remaining].push_back(line);
    }
  }

  bool Run(std::size_t shard, std::size_t shards) {
    if (shards == 0 || shard >= shards)
      throw std::runtime_error("bad shard");
    for (std::size_t fixed_index = shard;
         fixed_index < fixed_.size(); fixed_index += shards) {
      const auto before_tested = tested_;
      const auto before_passed = passed_;
      const std::uint64_t before_instances = residual_.instances();
      const std::uint64_t before_nodes = residual_.nodes();
      const std::uint64_t before_conflicts = residual_.conflicts();
      const std::uint64_t before_sat = residual_.satisfiable();

      std::vector<std::size_t> candidates;
      for (std::size_t id = 0; id < caps_.size(); ++id)
        if (!Any(fixed_[fixed_index] & caps_[id].points))
          candidates.push_back(id);
      LocalIndex local(caps_, std::move(candidates));
      ++fixed_processed_;
      if (SearchFixed(
              fixed_index, fixed_[fixed_index], local)) return true;

      std::cout
          << "INDEPENDENT_FIXED " << fixed_index
          << " candidates " << local.size();
      for (int depth = 1; depth <= 3; ++depth) {
        std::cout
            << " tested" << depth << ' '
            << tested_[depth] - before_tested[depth]
            << " passed" << depth << ' '
            << passed_[depth] - before_passed[depth];
      }
      std::cout
          << " residual_instances "
          << residual_.instances() - before_instances
          << " residual_nodes " << residual_.nodes() - before_nodes
          << " residual_conflicts "
          << residual_.conflicts() - before_conflicts
          << " residual_sat " << residual_.satisfiable() - before_sat
          << '\n';
    }
    std::cout
        << "INDEPENDENT_UNSAT_Q1234_SHARD " << shard << ' ' << shards
        << " fixed_processed " << fixed_processed_;
    for (int depth = 1; depth <= 3; ++depth)
      std::cout << " tested" << depth << ' ' << tested_[depth]
                << " passed" << depth << ' ' << passed_[depth];
    std::cout
        << " residual_instances " << residual_.instances()
        << " residual_nodes " << residual_.nodes()
        << " residual_conflicts " << residual_.conflicts()
        << " residual_sat " << residual_.satisfiable() << '\n';
    return false;
  }

 private:
  void ValidateFixed(Mask cap) const {
    if (Count(cap) != 22)
      throw std::runtime_error("fixed cap size is not 22");
    for (const Line& line : lines_)
      if (Count(cap & line.points) > 2)
        throw std::runtime_error("fixed mask is not a cap");
    for (int row = 0; row < kSide; ++row) {
      int count = 0;
      for (int column = 0; column < kSide; ++column)
        count += Test(cap, kSide * row + column);
      if (count != 2)
        throw std::runtime_error("fixed cap row multiplicity is not two");
    }
    for (int column = 0; column < kSide; ++column) {
      int count = 0;
      for (int row = 0; row < kSide; ++row)
        count += Test(cap, kSide * row + column);
      if (count != 2)
        throw std::runtime_error("fixed cap column multiplicity is not two");
    }
  }

  bool PrefixPossible(Mask selected, int remaining) const {
    const int capacity = 2 * remaining;
    for (std::size_t line_id : active_[remaining]) {
      const Line& line = lines_[line_id];
      if (Count(selected & line.points) + capacity < line.size)
        return false;
    }
    return true;
  }

  bool SearchFixed(std::size_t fixed_index, Mask fixed,
                   LocalIndex& local) {
    for (std::size_t first = 0; first < local.size(); ++first) {
      ++tested_[1];
      Mask union1 = fixed | caps_[local.global(first)].points;
      if (!PrefixPossible(union1, 4)) continue;
      ++passed_[1];
      std::vector<std::uint64_t> seconds =
          local.CompatibleBits(first);
      LocalIndex::ClearThrough(seconds, first);
      bool found = false;
      LocalIndex::Visit(seconds, [&](std::size_t second) {
        if (found) return;
        ++tested_[2];
        Mask union2 = union1 | caps_[local.global(second)].points;
        if (!PrefixPossible(union2, 3)) return;
        ++passed_[2];
        std::vector<std::uint64_t> thirds = seconds;
        LocalIndex::ClearThrough(thirds, second);
        LocalIndex::Intersect(
            thirds, local.CompatibleBits(second));
        LocalIndex::Visit(thirds, [&](std::size_t third) {
          if (found) return;
          ++tested_[3];
          Mask union3 = union2 | caps_[local.global(third)].points;
          if (!PrefixPossible(union3, 2)) return;
          ++passed_[3];
          const Mask full{~std::uint64_t{0}, kHighMask};
          const Mask residual = full ^ union3;
          residual_output_
              << fixed_index << ' '
              << Hex(caps_[local.global(first)].points) << ' '
              << Hex(caps_[local.global(second)].points) << ' '
              << Hex(caps_[local.global(third)].points) << ' '
              << Hex(residual) << '\n';
          if (residual_.Solve(residual)) {
            std::cout << "INDEPENDENT_SOLUTION fixed "
                      << fixed_index << " residual " << Hex(residual)
                      << '\n';
            found = true;
          }
        });
      });
      if (found) return true;
    }
    return false;
  }

  std::vector<Cap> caps_;
  std::vector<Mask> fixed_;
  std::vector<Line> lines_;
  std::array<std::vector<std::size_t>, 5> active_;
  TripleResidual36 residual_;
  std::ofstream residual_output_;
  std::array<std::uint64_t, 4> tested_{};
  std::array<std::uint64_t, 4> passed_{};
  std::uint64_t fixed_processed_ = 0;
};

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 5 && argc != 6)
      throw std::runtime_error(
          "usage: q1234_independent_verifier "
          "SHARD SHARDS RESIDUAL_OUTPUT CAP_DIRECTORY [FIXED_TABLE]");
    const std::size_t shard = std::stoull(argv[1]);
    const std::size_t shards = std::stoull(argv[2]);
    const std::filesystem::path residual_path = argv[3];
    const std::filesystem::path directory = argv[4];
    const std::filesystem::path fixed_path =
        argc == 6 ? argv[5] : directory / "caps22_d4.hex";
    IndependentQ1234 verifier(
        LoadCaps(directory), ReadMasks(fixed_path), BuildLines(),
        residual_path);
    return verifier.Run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "INDEPENDENT_Q1234_ERROR " << error.what() << '\n';
    return 2;
  }
}
