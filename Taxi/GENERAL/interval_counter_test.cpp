#include "interval_counter.hpp"

#include <gtest/gtest.h>

TEST(IntervalCounterTest, SuccessRate) {
  time_t t = 10000001;
  utils::SuccessIntervalCounterThreadSafe sic(t);

  sic.SetPeriod(std::chrono::seconds(5));
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000002;
  float rate = sic.SuccessRate(t);
  EXPECT_EQ(rate, 0.5);

  rate = sic.SuccessRate(t);
  EXPECT_EQ(rate, 0.5);

  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000003;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000004;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000005;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000006;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000007;
  rate = sic.SuccessRate(t);
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000008;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000009;
  sic.IncrementSuccess(1, t);
  sic.IncrementFailed(1, t);

  t = 10000009;
  rate = sic.SuccessRate(t);

  t = 10000010;
  rate = sic.SuccessRate(t);

  t = 10000010;
  rate = sic.SuccessRate(t);
  EXPECT_EQ(rate, 0.5);

  t = 10000011;
  rate = sic.SuccessRate(t);
  EXPECT_EQ(rate, 0.5);
}
