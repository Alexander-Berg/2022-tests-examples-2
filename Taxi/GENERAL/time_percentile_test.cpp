#include "time_percentile.hpp"

#include <chrono>

#include <gtest/gtest.h>

TEST(time_percentile, base) {
  using namespace std::chrono_literals;
  yaga::statistics::TimePercentile<100> p;
  p.AccountTime(10ms);
  p.AccountTime(10ms);
  p.AccountTime(10ms);
  p.AccountTime(10ms);
  p.AccountTime(10ms);

  p.AccountTime(10ms);
  p.AccountTime(20ms);

  p.AccountTime(30ms);

  p.AccountTime(40ms);

  p.AccountTime(70ms);

  EXPECT_EQ(10, p.GetPercentile(50).count());
  EXPECT_EQ(20, p.GetPercentile(69).count());
  EXPECT_EQ(30, p.GetPercentile(79).count());
  EXPECT_EQ(40, p.GetPercentile(89).count());
  EXPECT_EQ(70, p.GetPercentile(100).count());
}
