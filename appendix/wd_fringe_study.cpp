#include "src/fringe.hpp"
#include "src/taquin.hpp"
#include "src/wd.hpp"

void wd_vs_fringe() {
  load_fringe_table<4>(table4);
  auto wd_table = load_wd_table<4>();
  auto wd_estimate = wd_table.get_estimator();

  auto t = Taquin<4>();
  double wd_mean_value = 0.0, fringe_mean_value = 0.0;
  double wd_win_rate = 0.0, fringe_win_rate = 0.0;
  unsigned n_throws = 2000000;
  for (unsigned n = 0; n < n_throws; ++n) {
    t.scramble();
    unsigned wd = wd_estimate(t);
    unsigned f = fringe_estimate<4>(t);
    wd_mean_value += wd;
    fringe_mean_value += f;
    if (wd > f)
      wd_win_rate += 1.0;
    if (f > wd)
      fringe_win_rate += 1.0;
  }
  print("             WD  Fringe");
  print("mean value", wd_mean_value / n_throws, fringe_mean_value / n_throws);
  print("win rates", wd_win_rate / n_throws, fringe_win_rate / n_throws);
}

int main() {
  wd_vs_fringe();
  return 0;
}
