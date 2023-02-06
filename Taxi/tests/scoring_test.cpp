#include <gtest/gtest.h>

#include "controllers/scoring.hpp"

namespace cs = controllers::scoring;

TEST(OrderPoint, Simple) {
  for (auto p : {cs::OrderPoint::Point::kSrc, cs::OrderPoint::Point::kDst}) {
    for (auto o :
         {cs::OrderPoint::Order::kFirst, cs::OrderPoint::Order::kSecond}) {
      cs::OrderPoint op1{p, o};
      cs::OrderPoint op2{o, p};

      EXPECT_EQ(op1, op2);
      EXPECT_EQ(op1.GetOrder(), o);
      EXPECT_EQ(op1.GetPoint(), p);
      EXPECT_EQ(op2.GetOrder(), o);
      EXPECT_EQ(op2.GetPoint(), p);
    }
  }
}

TEST(OrderPointToPoint, Simple) {
  for (auto p1 : {cs::kA1, cs::kA2, cs::kB1, cs::kB2}) {
    for (auto p2 : {cs::kA1, cs::kA2, cs::kB1, cs::kB2}) {
      cs::OrderPointToPoint p2p1(p1, p2);
      cs::OrderPointToPoint p2p2(p2, p1);

      EXPECT_EQ(p2p1.From(), p1);
      EXPECT_EQ(p2p1.To(), p2);
      EXPECT_EQ(p2p1.From(), p2p2.To());
      EXPECT_EQ(p2p1.To(), p2p2.From());
    }
  }
}

TEST(TimeAndDist, Simple) {
  cs::TimeAndDist invalid;
  EXPECT_FALSE(!!invalid);

  auto zero = cs::TimeAndDist::Zero();
  EXPECT_TRUE(!!zero);
  EXPECT_EQ(zero.time.count(), 0);
  EXPECT_EQ(zero.dist, 0);

  cs::TimeAndDist td1{std::chrono::seconds{10}, 15};
  cs::TimeAndDist td2{std::chrono::seconds{7}, 13};

  auto sum = td1 + td2;
  EXPECT_TRUE(!!sum);
  EXPECT_EQ(sum.time.count(), 17);
  EXPECT_EQ(sum.dist, 28);

  auto diff1 = td1 - td2;
  EXPECT_TRUE(!!diff1);
  EXPECT_EQ(diff1.time.count(), 3);
  EXPECT_EQ(diff1.dist, 2);

  auto diff2 = td2 - td1;
  EXPECT_TRUE(!!diff2);
  EXPECT_EQ(diff2.time.count(), -3);
  EXPECT_EQ(diff2.dist, -2);
}

TEST(PointToPointTimeAndDists, Simple) {
  cs::PointToPointTimeAndDists p2ptd;

  const cs::TimeAndDist diff{std::chrono::seconds{2}, 1};

  auto td = cs::TimeAndDist::Zero();
  for (auto& sub : cs::PointToPointTimeAndDists::kNecessarySubs) {
    EXPECT_FALSE(p2ptd.IsFilled());

    td += diff;
    p2ptd.Set(sub, td);
  }
  EXPECT_TRUE(p2ptd.IsFilled());

  td = cs::TimeAndDist::Zero();
  for (auto& sub : cs::PointToPointTimeAndDists::kNecessarySubs) {
    td += diff;
    EXPECT_EQ(p2ptd.Get(sub), td);
  }

  //  EXPECT_ANY_THROW(p2ptd.Set({cs::kA1, cs::kA1}, td));
}

TEST(Calculate, Simple) {
  taxi_config::combo_matching::AgglomerationSettings cfg;
  cfg.dist_weight = 1.0;
  cfg.dist_weight = 1.0;
  cfg.max_single_extra = 100.0;
  cfg.max_single_extra_rel = 100.0;
  cfg.min_combo_saved = 0.0;
  cfg.min_combo_saved_rel = 0.0;

  cs::PointToPointTimeAndDists p2ptd;
  using sec = std::chrono::seconds;
  p2ptd.Set({cs::kA1, cs::kB1}, {sec{10}, 20});
  p2ptd.Set({cs::kA2, cs::kB2}, {sec{10}, 40});
  p2ptd.Set({cs::kA1, cs::kA2}, {sec{10}, 5});
  p2ptd.Set({cs::kA2, cs::kA1}, {sec{10}, 8});
  p2ptd.Set({cs::kA1, cs::kB2}, {sec{10}, 42});
  p2ptd.Set({cs::kA2, cs::kB1}, {sec{10}, 18});
  p2ptd.Set({cs::kB1, cs::kB2}, {sec{10}, 10});
  p2ptd.Set({cs::kB2, cs::kB1}, {sec{10}, 12});

  auto ret = cs::Calculate(p2ptd, cfg);
  EXPECT_TRUE(!!ret);

  cfg.max_single_extra = -10.0;
  ret = cs::Calculate(p2ptd, cfg);
  EXPECT_TRUE(!ret);
}
