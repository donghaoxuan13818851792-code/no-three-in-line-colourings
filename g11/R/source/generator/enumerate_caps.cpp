#include <array>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

using namespace std;
using U128 = unsigned __int128;
constexpr int N = 11;

array<array<U128, N * N>, N * N> line_mask;
array<int, N> coldeg;
vector<int> selected;
uint64_t nodes = 0, solutions = 0, meets_long_diagonals = 0, extendible = 0;
int target = 22, singleton_row = -1;
bool emit_caps = false;

inline bool bit(U128 m, int p) { return (m >> p) & 1; }

void recurse(int row, U128 blocked) {
  ++nodes;
  if (row == N) {
    int sum = accumulate(coldeg.begin(), coldeg.end(), 0);
    if (sum != target) return;
    for (int c = 0; c < N; ++c)
      if (coldeg[c] == 0 || coldeg[c] > 2) return;
    ++solutions;
    bool main_diag = false, anti_diag = false;
    U128 selected_mask = 0;
    for (int p : selected) {
      int x = p / N, y = p % N;
      main_diag |= x == y;
      anti_diag |= x + y == N - 1;
      selected_mask |= U128(1) << p;
    }
    meets_long_diagonals += main_diag && anti_diag;
    if (emit_caps && main_diag && anti_diag) {
      static constexpr char hex[] = "0123456789abcdef";
      string out(31, '0');
      U128 value = selected_mask;
      for (int i = 30; i >= 0; --i) {
        out[i] = hex[value & 15];
        value >>= 4;
      }
      cout << out << '\n';
    }
    if (target == 21) {
      int singleton_col = -1;
      for (int c = 0; c < N; ++c)
        if (coldeg[c] == 1) singleton_col = c;
      int candidate = singleton_row * N + singleton_col;
      bool already_selected = false;
      for (int p : selected) already_selected |= p == candidate;
      if (!already_selected && !bit(blocked, candidate)) ++extendible;
    }
    return;
  }

  int remaining_including = N - row;
  for (int c = 0; c < N; ++c)
    if (coldeg[c] + remaining_including < (target == 22 ? 2 : 1)) return;

  int need = row == singleton_row ? 1 : 2;
  for (int a = 0; a < N; ++a) {
    int pa = row * N + a;
    if (coldeg[a] >= 2 || bit(blocked, pa)) continue;
    int b_start = need == 1 ? a : a + 1;
    int b_end = need == 1 ? a + 1 : N;
    for (int b = b_start; b < b_end; ++b) {
      int pb = row * N + b;
      if (need == 2 && (coldeg[b] >= 2 || bit(blocked, pb))) continue;

      U128 next = blocked;
      for (int q : selected) {
        next |= line_mask[pa][q];
        if (need == 2) next |= line_mask[pb][q];
      }
      selected.push_back(pa);
      ++coldeg[a];
      if (need == 2) {
        selected.push_back(pb);
        ++coldeg[b];
      }
      recurse(row + 1, next);
      if (need == 2) {
        --coldeg[b];
        selected.pop_back();
      }
      --coldeg[a];
      selected.pop_back();
    }
  }
}

int main(int argc, char** argv) {
  target = argc > 1 ? stoi(argv[1]) : 22;
  singleton_row = argc > 2 ? stoi(argv[2]) : -1;
  emit_caps = argc > 3 && string(argv[3]) == "emit";
  if (target == 21 && singleton_row < 0) {
    cerr << "For target 21, supply the unique singleton row 0..10.\n";
    return 2;
  }
  for (int p = 0; p < N * N; ++p) {
    auto [x1, y1] = pair{p / N, p % N};
    for (int q = p + 1; q < N * N; ++q) {
      auto [x2, y2] = pair{q / N, q % N};
      U128 m = 0;
      for (int r = 0; r < N * N; ++r) {
        auto [x3, y3] = pair{r / N, r % N};
        if ((x2 - x1) * (y3 - y1) == (y2 - y1) * (x3 - x1)) m |= U128(1) << r;
      }
      line_mask[p][q] = line_mask[q][p] = m;
    }
  }
  coldeg.fill(0);
  recurse(0, 0);
  ostream& summary = emit_caps ? cerr : cout;
  summary << "target " << target << " singleton_row " << singleton_row << " nodes " << nodes
          << " oriented_solutions " << solutions
          << " meets_long_diagonals " << meets_long_diagonals
          << " extendible " << extendible << '\n';
}
