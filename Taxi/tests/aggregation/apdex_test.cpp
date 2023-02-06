
#include <gtest/gtest.h>

#include "aggregation/apdex_aggregator.hpp"

namespace dorblu {

TEST(TestApdexAggregation, Test1) {
  dorblu::aggregation::ApdexAggregator agg;
  DorBluPB::Stats stats;
  auto a1 = stats.add_apdexes();
  a1->set_prefix("test_prefix1");
  a1->set_ok(1);
  a1->set_tolerated(1);
  a1->set_total(2);
  agg.ProcessMessage(stats);
  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 1);
  ASSERT_TRUE(res.find("test_prefix1") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1"], 0.75);
}

TEST(TestApdexAggregation, Test2) {
  dorblu::aggregation::ApdexAggregator agg;

  DorBluPB::Stats stats;
  auto a1 = stats.add_apdexes();
  a1->set_prefix("test_prefix1");
  a1->set_ok(2);
  a1->set_tolerated(0);
  a1->set_total(2);
  agg.ProcessMessage(stats);

  DorBluPB::Stats stats2;
  auto a2 = stats2.add_apdexes();
  a2->set_prefix("test_prefix1");
  a2->set_ok(0);
  a2->set_tolerated(2);
  a2->set_total(2);
  auto a3 = stats2.add_apdexes();
  a3->set_prefix("test_prefix2");
  a3->set_ok(2);
  a3->set_tolerated(1);
  a3->set_total(3);
  agg.ProcessMessage(stats2);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 2);
  ASSERT_TRUE(res.find("test_prefix1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1"], 0.75);
  ASSERT_FLOAT_EQ(res["test_prefix2"], 0.8333333);
}

}  // namespace dorblu
