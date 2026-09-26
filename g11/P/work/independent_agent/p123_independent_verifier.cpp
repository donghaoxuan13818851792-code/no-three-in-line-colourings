// Independent verifier for the P1/P2/P3 four-cap computation.
//
// Reuse only the independently authored two-word cap loader and point-pair
// geometry.  The residual solver below is new: it expands every residual
// line to explicit NAE triples and applies a triple-level DPLL, rather than
// the line-count propagator in the implementation under audit.
#define main p1_independent_unused_main
#include "p1_independent_search.cpp"
#undef main

#include <optional>

namespace {

struct NAETriple {
  std::uint8_t first;
  std::uint8_t second;
  std::uint8_t third;
};

class TripleResidualSolver {
 public:
  explicit TripleResidualSolver(const std::vector<Line>& lines)
      : lines_(lines) {}

  bool Solve(Mask residual, Mask& zero_colour, Mask& one_colour) {
    ++instances_;
    if (Count(residual) != 37)
      throw std::runtime_error("residual does not have 37 points");

    std::array<std::int8_t, kPointCount> local;
    local.fill(-1);
    std::array<int, 37> global{};
    int variables = 0;
    for (int point = 0; point < kPointCount; ++point) {
      if (!Test(residual, point)) continue;
      local[point] = static_cast<std::int8_t>(variables);
      global[variables++] = point;
    }
    if (variables != 37)
      throw std::runtime_error("wrong residual-variable count");

    triples_.clear();
    occurrences_.fill(0);
    for (const Line& line : lines_) {
      std::array<int, 4> members{};
      int count = 0;
      for (int point = 0; point < kPointCount; ++point) {
        if (!Test(residual, point) || !Test(line.points, point)) continue;
        if (count == 4)
          throw std::runtime_error("residual line exceeds capacity four");
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

    std::array<std::int8_t, 37> values;
    values.fill(-1);
    values[0] = 0;  // Break interchange of the two residual colours.
    std::array<std::int8_t, 37> model{};
    if (!Search(values, model)) return false;

    zero_colour = {};
    one_colour = {};
    for (int variable = 0; variable < 37; ++variable) {
      if (model[variable] == 0)
        Set(zero_colour, global[variable]);
      else if (model[variable] == 1)
        Set(one_colour, global[variable]);
      else
        throw std::runtime_error("incomplete residual model");
    }
    if (Count(zero_colour) > 21 || Count(one_colour) > 21 ||
        Any(zero_colour & one_colour) ||
        (zero_colour | one_colour) != residual)
      throw std::runtime_error("bad residual model partition");
    for (const Line& line : lines_)
      if (Count(zero_colour & line.points) > 2 ||
          Count(one_colour & line.points) > 2)
        throw std::runtime_error("bad residual model line");
    ++satisfiable_;
    return true;
  }

  std::uint64_t instances() const { return instances_; }
  std::uint64_t nodes() const { return nodes_; }
  std::uint64_t conflicts() const { return conflicts_; }
  std::uint64_t satisfiable() const { return satisfiable_; }

 private:
  bool Assign(std::array<std::int8_t, 37>& values,
              int variable, int value) const {
    if (values[variable] >= 0) return values[variable] == value;
    values[variable] = static_cast<std::int8_t>(value);
    return true;
  }

  bool Propagate(std::array<std::int8_t, 37>& values) {
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
        for (int variable = 0; variable < 37; ++variable) {
          if (values[variable] >= 0) continue;
          values[variable] = static_cast<std::int8_t>(forced);
          changed = true;
        }
      }

      for (const NAETriple& triple : triples_) {
        const std::array<int, 3> variables{
            triple.first, triple.second, triple.third};
        int free_variable = -1;
        int free_count = 0;
        int assigned_count = 0;
        int assigned_value = -1;
        bool assigned_differ = false;
        for (int variable : variables) {
          const int value = values[variable];
          if (value < 0) {
            free_variable = variable;
            ++free_count;
          } else {
            if (assigned_count && value != assigned_value)
              assigned_differ = true;
            assigned_value = value;
            ++assigned_count;
          }
        }
        if (free_count == 0) {
          if (!assigned_differ) {
            ++conflicts_;
            return false;
          }
          continue;
        }
        if (free_count == 1 && !assigned_differ &&
            assigned_count == 2) {
          if (!Assign(values, free_variable, 1 - assigned_value)) {
            ++conflicts_;
            return false;
          }
          changed = true;
        }
      }
      if (!changed) return true;
    }
  }

  bool Search(std::array<std::int8_t, 37> values,
              std::array<std::int8_t, 37>& model) {
    ++nodes_;
    if (!Propagate(values)) return false;
    int zeros = 0;
    int ones = 0;
    int chosen = -1;
    int best_score = -1;
    for (int variable = 0; variable < 37; ++variable) {
      zeros += values[variable] == 0;
      ones += values[variable] == 1;
      if (values[variable] < 0 &&
          occurrences_[variable] > best_score) {
        chosen = variable;
        best_score = occurrences_[variable];
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
  std::vector<NAETriple> triples_;
  std::array<int, 37> occurrences_{};
  std::uint64_t instances_ = 0;
  std::uint64_t nodes_ = 0;
  std::uint64_t conflicts_ = 0;
  std::uint64_t satisfiable_ = 0;
};

class IndependentP123Verifier {
 public:
  IndependentP123Verifier(std::vector<Cap> caps,
                          std::vector<Line> lines,
                          const std::filesystem::path& residual_path)
      : caps_(std::move(caps)),
        lines_(std::move(lines)),
        word_count_((caps_.size() + 63) / 64),
        point_occurrence_(kPointCount,
                          std::vector<std::uint64_t>(word_count_)),
        row_occurrence_(kSide,
                        std::vector<std::uint64_t>(word_count_)),
        column_occurrence_(kSide,
                           std::vector<std::uint64_t>(word_count_)),
        residual_solver_(lines_),
        residual_output_(residual_path) {
    if (!residual_output_)
      throw std::runtime_error("cannot open residual output");
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
      const int capacity = 2 * (6 - chosen);
      for (std::size_t line = 0; line < lines_.size(); ++line)
        if (lines_[line].size > capacity)
          active_[chosen].push_back(line);
    }
    for (std::size_t id = 0; id < caps_.size(); ++id) {
      Mask minimum = caps_[id].points;
      for (int symmetry = 1; symmetry < 8; ++symmetry)
        minimum = std::min(
            minimum, Transform(caps_[id].points, symmetry));
      if (caps_[id].points == minimum) representatives_.push_back(id);
    }
    if (representatives_.size() != 127491)
      throw std::runtime_error("D4 representative count mismatch");
    std::cerr << "independent_caps " << caps_.size()
              << " independent_lines " << lines_.size()
              << " d4_representatives " << representatives_.size()
              << '\n';
  }

  bool Run(std::size_t shard, std::size_t shards) {
    if (!shards || shard >= shards)
      throw std::runtime_error("invalid shard");
    const auto started = std::chrono::steady_clock::now();
    for (std::size_t representative = shard;
         representative < representatives_.size();
         representative += shards) {
      const std::size_t first_id = representatives_[representative];
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
      ++first_caps_;
      if (AfterFirst(first_id, seconds)) {
        std::cout << "INDEPENDENT_SOLUTION123";
        Mask selected;
        for (std::size_t id : choice_) {
          std::cout << ' ' << id;
          selected = selected | caps_[id].points;
        }
        std::cout << '\n';
        for (std::size_t id : choice_)
          std::cout << Hex(caps_[id].points) << '\n';
        std::cout << "RESIDUAL_ZERO " << Hex(solution_zero_) << '\n';
        std::cout << "RESIDUAL_ONE " << Hex(solution_one_) << '\n';
        return true;
      }
      if (first_caps_ % 100 == 0) {
        const double elapsed =
            std::chrono::duration<double>(
                std::chrono::steady_clock::now() - started)
                .count();
        std::cerr << "independent_progress " << shard << '/' << shards
                  << " first_caps " << first_caps_
                  << " representative " << representative;
        PrintCounters(std::cerr);
        std::cerr << " residual_instances "
                  << residual_solver_.instances()
                  << " residual_nodes " << residual_solver_.nodes()
                  << " residual_sat " << residual_solver_.satisfiable()
                  << " seconds " << elapsed << '\n';
      }
    }
    residual_output_.flush();
    if (!residual_output_)
      throw std::runtime_error("failed writing residual stream");
    std::cout << "INDEPENDENT_UNSAT123_SHARD " << shard << ' ' << shards
              << " first_caps " << first_caps_;
    PrintCounters(std::cout);
    std::cout << " residual_instances " << residual_solver_.instances()
              << " residual_nodes " << residual_solver_.nodes()
              << " residual_conflicts " << residual_solver_.conflicts()
              << " residual_sat " << residual_solver_.satisfiable()
              << '\n';
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
        for (std::size_t index = ti + 1; index < thirds.size(); ++index) {
          const std::size_t fourth_id = thirds[index];
          const Cap& fourth = caps_[fourth_id];
          ++examined_[4];
          if (!Compatible(third, fourth)) continue;
          const Mask selected_four = selected_three | fourth.points;
          if (!PrefixPossible(selected_four, 4)) continue;
          ++accepted_[4];
          const Mask full{~std::uint64_t{0}, kHighMask};
          const Mask residual = full ^ selected_four;
          residual_output_ << Hex(residual) << '\n';
          if (!residual_solver_.Solve(
                  residual, solution_zero_, solution_one_))
            continue;
          choice_ = {first_id, second_id, third_id, fourth_id};
          return true;
        }
      }
    }
    return false;
  }

  void PrintCounters(std::ostream& output) const {
    for (int depth = 2; depth <= 4; ++depth)
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
  TripleResidualSolver residual_solver_;
  std::ofstream residual_output_;
  std::array<std::size_t, 4> choice_{};
  std::array<std::uint64_t, 5> examined_{};
  std::array<std::uint64_t, 5> accepted_{};
  std::uint64_t first_caps_ = 0;
  Mask solution_zero_{};
  Mask solution_one_{};
};

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 4 && argc != 5)
      throw std::runtime_error(
          "usage: p123_independent_verifier SHARD SHARDS "
          "RESIDUAL_OUTPUT [CAP_DIRECTORY]");
    const std::size_t shard = std::stoull(argv[1]);
    const std::size_t shards = std::stoull(argv[2]);
    const std::filesystem::path residual_path = argv[3];
    const std::filesystem::path cap_directory =
        argc == 5 ? argv[4] : "work/math_agent";
    std::vector<Cap> caps = LoadCaps(cap_directory);
    std::vector<Line> lines = BuildLines();
    IndependentP123Verifier verifier(
        std::move(caps), std::move(lines), residual_path);
    return verifier.Run(shard, shards) ? 10 : 20;
  } catch (const std::exception& error) {
    std::cerr << "INDEPENDENT_P123_ERROR " << error.what() << '\n';
    return 2;
  }
}
