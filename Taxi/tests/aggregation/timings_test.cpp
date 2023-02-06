#include <gtest/gtest.h>

#include <aggregation/timings_aggregator.hpp>

namespace dorblu {

TEST(TestTimingsAggregation, TestEmptyResult) {
  dorblu::aggregation::TimingsAggregator agg;
  auto res = agg.Collect();
  ASSERT_TRUE(res.empty());
  res = agg.Collect();
  ASSERT_TRUE(res.empty());
}

TEST(TestTimingsAggregation, TestSimple) {
  dorblu::aggregation::TimingsAggregator agg;
  DorBluPB::Stats stats;
  agg.ProcessMessage(stats);
  auto res = agg.Collect();
  ASSERT_TRUE(res.empty());
}

TEST(TestTimingsAggregation, TestPercentiles) {
  dorblu::aggregation::PrefixTimingAggregator agg;

  DorBluPB::Timings t;
  t.set_prefix("test_prefix");
  for (int i = 100; i > 0; --i) {
    t.add_timings(i);
  }
  agg.ProcessTiming(t);
  auto percentiles = agg.Collect();
  ASSERT_EQ(percentiles.size(), 8);
  ASSERT_FLOAT_EQ(percentiles.at(1.00f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.99f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.98f), 99);
  ASSERT_FLOAT_EQ(percentiles.at(0.97f), 98);
  ASSERT_FLOAT_EQ(percentiles.at(0.95f), 96);
  ASSERT_FLOAT_EQ(percentiles.at(0.90f), 91);
  ASSERT_FLOAT_EQ(percentiles.at(0.85f), 86);
  ASSERT_FLOAT_EQ(percentiles.at(0.75f), 76);
}

TEST(TestTimingsAggregation, TestPercentiles2) {
  dorblu::aggregation::PrefixTimingAggregator agg;

  DorBluPB::Timings t;
  t.set_prefix("test_prefix");
  for (int i = 100; i > 0; --i) {
    t.add_timings(i);
  }
  agg.ProcessTiming(t);
  agg.ProcessTiming(t);

  auto percentiles = agg.Collect();
  ASSERT_EQ(percentiles.size(), 8);
  ASSERT_FLOAT_EQ(percentiles.at(1.00f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.99f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.98f), 99);
  ASSERT_FLOAT_EQ(percentiles.at(0.97f), 98);
  ASSERT_FLOAT_EQ(percentiles.at(0.95f), 96);
  ASSERT_FLOAT_EQ(percentiles.at(0.90f), 91);
  ASSERT_FLOAT_EQ(percentiles.at(0.85f), 86);
  ASSERT_FLOAT_EQ(percentiles.at(0.75f), 76);
}

TEST(TestTimingsAggregation, TestPercentiles10) {
  dorblu::aggregation::PrefixTimingAggregator agg;

  DorBluPB::Timings t;
  t.set_prefix("test_prefix");
  for (int i = 100; i > 0; --i) {
    t.add_timings(i);
  }
  for (int i = 0; i < 10; ++i) {
    agg.ProcessTiming(t);
  }

  auto percentiles = agg.Collect();
  ASSERT_EQ(percentiles.size(), 8);
  ASSERT_FLOAT_EQ(percentiles.at(1.00f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.99f), 100);
  ASSERT_FLOAT_EQ(percentiles.at(0.98f), 99);
  ASSERT_FLOAT_EQ(percentiles.at(0.97f), 98);
  ASSERT_FLOAT_EQ(percentiles.at(0.95f), 96);
  ASSERT_FLOAT_EQ(percentiles.at(0.90f), 91);
  ASSERT_FLOAT_EQ(percentiles.at(0.85f), 86);
  ASSERT_FLOAT_EQ(percentiles.at(0.75f), 76);
}

TEST(TestTimingsAggregation, TestPercentilesPrefixes) {
  dorblu::aggregation::TimingsAggregator agg;

  DorBluPB::Stats s;
  auto t1 = s.add_timings();
  t1->set_prefix("test_prefix1");
  for (int i = 100; i > 0; --i) {
    t1->add_timings(i);
  }
  auto t2 = s.add_timings();
  t2->set_prefix("test_prefix2");
  for (int i = 100; i > 0; --i) {
    t2->add_timings(2 * i);
  }
  auto t3 = s.add_timings();
  t3->set_prefix("test_prefix3");
  for (int i = 100; i > 0; --i) {
    t3->add_timings(3 * i);
  }

  agg.ProcessMessage(s);
  agg.ProcessMessage(s);

  auto res = agg.Collect();
  ASSERT_EQ(res.size(), 3);
  ASSERT_TRUE(res.find("test_prefix1") != res.end());
  ASSERT_TRUE(res.find("test_prefix2") != res.end());
  ASSERT_TRUE(res.find("test_prefix3") != res.end());
  for (const auto& it : res) {
    int mult = 1;
    if (it.first == "test_prefix2") mult = 2;
    if (it.first == "test_prefix3") mult = 3;

    const auto& percentiles = it.second;
    ASSERT_EQ(percentiles.size(), 8);
    ASSERT_FLOAT_EQ(percentiles.at(1.00f), mult * 100);
    ASSERT_FLOAT_EQ(percentiles.at(0.99f), mult * 100);
    ASSERT_FLOAT_EQ(percentiles.at(0.98f), mult * 99);
    ASSERT_FLOAT_EQ(percentiles.at(0.97f), mult * 98);
    ASSERT_FLOAT_EQ(percentiles.at(0.95f), mult * 96);
    ASSERT_FLOAT_EQ(percentiles.at(0.90f), mult * 91);
    ASSERT_FLOAT_EQ(percentiles.at(0.85f), mult * 86);
    ASSERT_FLOAT_EQ(percentiles.at(0.75f), mult * 76);
  }
}

}  // namespace dorblu
