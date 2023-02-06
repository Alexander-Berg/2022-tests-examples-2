#include <gtest/gtest.h>

#include "aggregation/cache_rate_aggregator.hpp"

namespace dorblu {

TEST(TestCacheRateAggregation, TestCacheRate) {
  int seconds = 60;
  dorblu::aggregation::CacheRateAggregator agg;

  DorBluPB::Stats stats;
  auto* it1 = stats.add_cache_rates();
  it1->set_prefix("test_prefix1");
  auto e1 = it1->add_entries();
  e1->set_cache_status("s1");
  e1->set_count(10 * seconds);
  auto* it2 = stats.add_cache_rates();
  it2->set_prefix("test_prefix1");
  auto e2 = it2->add_entries();
  e2->set_cache_status("s1");
  e2->set_count(20 * seconds);
  auto* it3 = stats.add_cache_rates();
  it3->set_prefix("test_prefix2");
  auto e3 = it3->add_entries();
  e3->set_cache_status("s2");
  e3->set_count(40 * seconds);

  agg.ProcessMessage(stats);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 2);
  ASSERT_TRUE(res.find("test_prefix1.s1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2.s2") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1.s1"], 30);
  ASSERT_FLOAT_EQ(res["test_prefix2.s2"], 40);
}

TEST(TestCacheRateAggregation, TestCacheRate2) {
  int seconds = 60;
  dorblu::aggregation::CacheRateAggregator agg;

  DorBluPB::Stats stats;
  auto* it1 = stats.add_cache_rates();
  it1->set_prefix("test_prefix1");
  auto e1 = it1->add_entries();
  e1->set_cache_status("s1");
  e1->set_count(10 * seconds);
  DorBluPB::Stats stats2;
  auto* it2 = stats2.add_cache_rates();
  it2->set_prefix("test_prefix1");
  auto e2 = it2->add_entries();
  e2->set_cache_status("s1");
  e2->set_count(20 * seconds);
  auto* it3 = stats2.add_cache_rates();
  it3->set_prefix("test_prefix2");
  auto e3 = it3->add_entries();
  e3->set_cache_status("s2");
  e3->set_count(40 * seconds);

  agg.ProcessMessage(stats);
  agg.ProcessMessage(stats2);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 2);
  ASSERT_TRUE(res.find("test_prefix1.s1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2.s2") != res.end());
  ASSERT_FLOAT_EQ(res["test_prefix1.s1"], 30);
  ASSERT_FLOAT_EQ(res["test_prefix2.s2"], 40);
}

}  // namespace dorblu
