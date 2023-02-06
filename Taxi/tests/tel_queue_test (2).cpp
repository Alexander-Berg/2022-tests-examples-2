#include <gtest/gtest.h>

#include "models/call_routing.hpp"

namespace callcenter_stats::unit_tests {

using namespace callcenter_stats::models::call_routing;

class TelQueueTests : public ::testing::Test {};

TEST_F(TelQueueTests, TestParse) {
  const auto& tel_queue = TelQueue::Parse("krasnodar_disp_cc_on_s1", "_on_");
  EXPECT_EQ(tel_queue.metaqueue, "krasnodar_disp_cc");
  EXPECT_EQ(tel_queue.subcluster, "s1");
}

TEST_F(TelQueueTests, TestParseNoSubcluster) {
  const auto& tel_queue = TelQueue::Parse("krasnodar_disp_cc_on_", "_on_");
  EXPECT_EQ(tel_queue.metaqueue, "krasnodar_disp_cc");
  EXPECT_EQ(tel_queue.subcluster, "");
}

TEST_F(TelQueueTests, TestParseNoQueue) {
  const auto& tel_queue = TelQueue::Parse("_on_s1", "_on_");
  EXPECT_EQ(tel_queue.metaqueue, "");
  EXPECT_EQ(tel_queue.subcluster, "s1");
}

TEST_F(TelQueueTests, TestParseNoDelimiter) {
  const auto& tel_queue = TelQueue::Parse("krasnodar_disp_cc", "_on_");
  EXPECT_EQ(tel_queue.metaqueue, "krasnodar_disp_cc");
  EXPECT_EQ(tel_queue.subcluster, "");
}

TEST_F(TelQueueTests, TestParse2Delimiters) {
  const auto& tel_queue = TelQueue::Parse("disp_on_river_on_s1", "_on_");
  EXPECT_EQ(tel_queue.metaqueue, "disp");
  EXPECT_EQ(tel_queue.subcluster, "river_on_s1");
}

TEST_F(TelQueueTests, TestToString) {
  const auto& queue_name = TelQueue{"queue", "subcluster", "_"}.ToString();
  EXPECT_EQ(queue_name, "queue_subcluster");
}

TEST_F(TelQueueTests, TestToStringNoQueue) {
  const auto& queue_name = TelQueue{"", "subcluster", "_"}.ToString();
  EXPECT_EQ(queue_name, "_subcluster");
}
TEST_F(TelQueueTests, TestToStringNoSubcluster) {
  const auto& queue_name = TelQueue{"queue", "", "_"}.ToString();
  EXPECT_EQ(queue_name, "queue");
}

}  // namespace callcenter_stats::unit_tests
