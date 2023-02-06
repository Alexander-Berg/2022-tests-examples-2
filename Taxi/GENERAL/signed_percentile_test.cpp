#include "signed_percentile.hpp"
#include <utils/mock_now.hpp>

#include <gtest/gtest.h>

TEST(SignedPercentile, Zero) {
  utils::statistics::SignedPercentile<100> p;

  EXPECT_EQ(0, p.GetPercentile(0));
  EXPECT_EQ(0, p.GetPercentile(50));
  EXPECT_EQ(0, p.GetPercentile(100));
}

TEST(SignedPercentile, One) {
  utils::statistics::SignedPercentile<100> p;

  p.Account(3);

  EXPECT_EQ(3, p.GetPercentile(0));
  EXPECT_EQ(3, p.GetPercentile(50));
  EXPECT_EQ(3, p.GetPercentile(100));
}

TEST(SignedPercentile, Hundred) {
  utils::statistics::SignedPercentile<100> p;

  for (int i = 0; i < 100; ++i) p.Account(i);

  EXPECT_EQ(0, p.GetPercentile(0));
  EXPECT_EQ(49, p.GetPercentile(50));
  EXPECT_EQ(99, p.GetPercentile(100));
  EXPECT_EQ(0, p.GetPercentile(101));
  EXPECT_EQ(0, p.GetPercentile(200));
}

TEST(SignedPercentile, Many) {
  utils::statistics::SignedPercentile<3> p;

  p.Account(0);
  p.Account(0);
  p.Account(0);
  p.Account(1);
  p.Account(1);

  EXPECT_EQ(0, p.GetPercentile(0));
  EXPECT_EQ(0, p.GetPercentile(50));
  EXPECT_EQ(1, p.GetPercentile(100));
  EXPECT_EQ(0, p.GetPercentile(101));
  EXPECT_EQ(0, p.GetPercentile(200));
}

TEST(SignedPercentile, Bounds) {
  utils::statistics::SignedPercentile<10> p;
  p.Account(0);
  EXPECT_EQ(0, p.GetPercentile(100));

  p.Account(-100);
  EXPECT_EQ(-10, p.GetPercentile(0));

  p.Account(100);
  EXPECT_EQ(10, p.GetPercentile(100));
}

TEST(SignedPercentile, Sign) {
  utils::statistics::SignedPercentile<10> p;

  for (int i = -5; i <= 5; ++i) p.Account(i);
  for (int i = 0; i <= 10; ++i) {
    EXPECT_EQ(-5 + i, p.GetPercentile(i * 10));
  }
}
