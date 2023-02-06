#include <gtest/gtest.h>

#include "aggregation/bytes_counter_aggregator.hpp"

namespace dorblu {

TEST(TestBytesCounterAggregation, Test1) {
  int seconds = 60;
  dorblu::aggregation::BytesCounterAggregator agg;

  DorBluPB::Stats stats;
  auto* it1 = stats.add_bytes_counters();
  it1->set_prefix("test_prefix1");
  it1->set_counter(10 * seconds);
  auto* it2 = stats.add_bytes_counters();
  it2->set_prefix("test_prefix1");
  it2->set_counter(20 * seconds);
  auto* it3 = stats.add_bytes_counters();
  it3->set_prefix("test_prefix2");
  it3->set_counter(40 * seconds);

  agg.ProcessMessage(stats);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 2);
  ASSERT_TRUE(res.find("test_prefix1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1"], 30);
  ASSERT_FLOAT_EQ(res["test_prefix2"], 40);
}

TEST(TestBytesCounterAggregation, Test2) {
  int seconds = 60;
  dorblu::aggregation::BytesCounterAggregator agg;

  DorBluPB::Stats stats;
  auto* it1 = stats.add_bytes_counters();
  it1->set_prefix("test_prefix1");
  it1->set_counter(10 * seconds);
  DorBluPB::Stats stats2;
  auto* it2 = stats2.add_bytes_counters();
  it2->set_prefix("test_prefix1");
  it2->set_counter(20 * seconds);
  auto* it3 = stats2.add_bytes_counters();
  it3->set_prefix("test_prefix2");
  it3->set_counter(40 * seconds);

  agg.ProcessMessage(stats);
  agg.ProcessMessage(stats2);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 2);
  ASSERT_TRUE(res.find("test_prefix1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1"], 30);
  ASSERT_FLOAT_EQ(res["test_prefix2"], 40);
}

}  // namespace dorblu
