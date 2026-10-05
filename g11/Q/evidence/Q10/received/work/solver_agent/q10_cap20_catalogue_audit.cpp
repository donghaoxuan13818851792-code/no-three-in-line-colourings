// Independent terminal audit for a sorted q10_cap20_enum catalogue.
// This program does not use the generator's DFS, secant-blocking state,
// row-pattern tables, or pruning logic.  It rederives the 628 maximal lines
// and checks every emitted mask directly.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Bits = unsigned __int128;
constexpr int SIDE = 11;
constexpr int POINTS = SIDE * SIDE;
constexpr Bits GRID = (Bits(1) << POINTS) - 1;

int pop(Bits x) {
  return std::popcount(static_cast<uint64_t>(x)) +
         std::popcount(static_cast<uint64_t>(x >> 64));
}

Bits read_hex(const std::string &s) {
  if (s.size() != 31) throw std::runtime_error("mask is not 31 hex digits");
  Bits x = 0;
  for (char ch : s) {
    int d = -1;
    if ('0' <= ch && ch <= '9') d = ch - '0';
    if ('a' <= ch && ch <= 'f') d = ch - 'a' + 10;
    if ('A' <= ch && ch <= 'F') d = ch - 'A' + 10;
    if (d < 0) throw std::runtime_error("invalid hex digit");
    x = (x << 4) | d;
  }
  if (x & ~GRID) throw std::runtime_error("mask has point outside grid");
  return x;
}

int highest(Bits x) {
  const uint64_t hi = static_cast<uint64_t>(x >> 64);
  if (hi) return 127 - std::countl_zero(hi);
  const uint64_t lo = static_cast<uint64_t>(x);
  return lo ? 63 - std::countl_zero(lo) : -1;
}

std::vector<Bits> derive_lines() {
  std::set<Bits> unique;
  for (int a = 0; a < POINTS; ++a) {
    const int ar = a / SIDE, ac = a % SIDE;
    for (int b = a + 1; b < POINTS; ++b) {
      const int br = b / SIDE, bc = b % SIDE;
      Bits line = 0;
      for (int q = 0; q < POINTS; ++q) {
        const int qr = q / SIDE, qc = q % SIDE;
        if ((br - ar) * (qc - ac) == (bc - ac) * (qr - ar))
          line |= Bits(1) << q;
      }
      if (pop(line) >= 3) unique.insert(line);
    }
  }
  if (unique.size() != 628) throw std::runtime_error("geometry is not 628 lines");
  return {unique.begin(), unique.end()};
}

std::vector<Bits> read_caps(const std::string &path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot open cap catalogue");
  std::vector<Bits> caps;
  std::string word;
  while (in >> word) caps.push_back(read_hex(word));
  if (caps.size() != 676) throw std::runtime_error("cap catalogue is not 676 masks");
  return caps;
}

int main(int argc, char **argv) try {
  std::string anchor_text, catalogue_path, caps_path;
  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    auto value = [&]() -> std::string {
      if (++i == argc) throw std::runtime_error("missing argument value");
      return argv[i];
    };
    if (arg == "--anchor") anchor_text = value();
    else if (arg == "--catalogue") catalogue_path = value();
    else if (arg == "--caps") caps_path = value();
    else throw std::runtime_error("unknown argument: " + arg);
  }
  if (anchor_text.empty() || catalogue_path.empty() || caps_path.empty())
    throw std::runtime_error("need --anchor, --catalogue, and --caps");

  const Bits anchor = read_hex(anchor_text);
  if (pop(anchor) != 22) throw std::runtime_error("anchor size is not 22");
  const auto lines = derive_lines();
  for (Bits line : lines)
    if (pop(anchor & line) > 2) throw std::runtime_error("anchor has a triple");
  const auto caps = read_caps(caps_path);

  std::ifstream input(catalogue_path);
  if (!input) throw std::runtime_error("cannot open mask catalogue");
  std::string word, previous;
  uint64_t count = 0, extendible = 0, least_eligible = 0;
  std::array<std::array<uint64_t, 55>, 55> shard_counts{};
  while (input >> word) {
    ++count;
    if (!previous.empty() && !(previous < word))
      throw std::runtime_error("catalogue is not strictly sorted and unique at mask " +
                               std::to_string(count));
    previous = word;
    const Bits mask = read_hex(word);
    if (pop(mask) != 20) throw std::runtime_error("mask size is not 20");
    if (mask & anchor) throw std::runtime_error("mask intersects anchor");

    std::array<int, SIDE> row_degree{}, col_degree{};
    for (int p = 0; p < POINTS; ++p) if ((mask >> p) & 1) {
      ++row_degree[p / SIDE];
      ++col_degree[p % SIDE];
    }
    std::array<int, 2> singleton_rows{}, singleton_cols{};
    int nr = 0, nc = 0;
    for (int i = 0; i < SIDE; ++i) {
      if (row_degree[i] == 1) {
        if (nr == 2) throw std::runtime_error("more than two singleton rows");
        singleton_rows[nr++] = i;
      } else if (row_degree[i] != 2) throw std::runtime_error("bad row degree");
      if (col_degree[i] == 1) {
        if (nc == 2) throw std::runtime_error("more than two singleton columns");
        singleton_cols[nc++] = i;
      } else if (col_degree[i] != 2) throw std::runtime_error("bad column degree");
    }
    if (nr != 2 || nc != 2) throw std::runtime_error("wrong singleton degree count");
    const auto pair_id = [](std::array<int, 2> pair) {
      int id = 0;
      for (int a = 0; a < SIDE; ++a)
        for (int b = a + 1; b < SIDE; ++b, ++id)
          if (pair[0] == a && pair[1] == b) return id;
      throw std::runtime_error("singleton pair not found");
    };
    ++shard_counts[pair_id(singleton_rows)][pair_id(singleton_cols)];

    for (Bits line : lines) {
      if (pop(mask & line) > 2) throw std::runtime_error("collinear triple in mask");
      if (pop(line & ~(anchor | mask) & GRID) > 8)
        throw std::runtime_error("residual four-colour line capacity violated");
    }

    bool is_extendible = false;
    for (Bits cap : caps) if ((mask & ~cap) == 0) {
      is_extendible = true;
      break;
    }
    extendible += is_extendible;
    int available_above = 0;
    for (int p = highest(mask) + 1; p < POINTS; ++p)
      available_above += ((anchor >> p) & 1) == 0;
    least_eligible += available_above >= 3;
  }
  if (!input.eof()) throw std::runtime_error("catalogue read failure");

  uint64_t partition_total = 0;
  for (const auto &row : shard_counts)
    partition_total += std::accumulate(row.begin(), row.end(), uint64_t{0});
  if (partition_total != count) throw std::runtime_error("shard partition total mismatch");
  std::cout << "AUDIT_OK count " << count
            << " least_eligible " << least_eligible
            << " extendible " << extendible
            << " nonextendible " << count - extendible
            << " maximal_lines " << lines.size()
            << "\n";
  return 0;
} catch (const std::exception &error) {
  std::cerr << "AUDIT_FAILED " << error.what() << "\n";
  return 1;
}
