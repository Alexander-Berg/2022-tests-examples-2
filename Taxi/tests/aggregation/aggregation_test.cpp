#include <gtest/gtest.h>

#include "aggregation/aggregation.hpp"

namespace dorblu {

TEST(TestAggregation, TestEmpty) {
  dorblu::aggregation::AggregationManager agg({});
  // TODO
}

TEST(TestAggregation, TestEmptyStats) {
  dorblu::aggregation::AggregationManager agg({});
  DorBluPB::MainMessage message;
  auto r1 = message.add_rules();
  r1->set_name("rule_name1");
  agg.ProcessMessage(message);
}

TEST(TestAggregation, TestOneMessage) {
  dorblu::aggregation::AggregationManager agg({});
  DorBluPB::MainMessage message;
  auto r1 = message.add_rules();
  r1->set_name("rule_name1");
  auto t1 = r1->mutable_stats()->add_timings();
  t1->set_prefix("test_timings_prefix1");
  t1->add_timings(100);
  agg.ProcessMessage(message);
  // TODO
}

}  // namespace dorblu
