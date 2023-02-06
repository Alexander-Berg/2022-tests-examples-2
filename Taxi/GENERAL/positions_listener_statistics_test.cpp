#include <geobus/channels/positions/listener_statistics.hpp>
#include <yaga/statistics/percentile_json.hpp>

#include <userver/formats/json/value_builder.hpp>

#include "positions_listener_statistics_tester.hpp"

#include <gtest/gtest.h>

namespace geobus::statistics {

class PositionsListenerStatisticsFixture : public ::testing::Test {};

TEST_F(PositionsListenerStatisticsFixture, TestReset) {
  // This test case was written to catch encountered error, when we forgot
  // to reset base class ocasionally.

  PositionsListenerStatistics stats;
  stats.IncReceivedMessages(1);

  PositionsListenerStatisticsTester tester(stats);

  EXPECT_EQ(1, tester.GetReceivedMessages());
  EXPECT_EQ(1, tester.GetReceivedPositions());

  stats.Reset();
  EXPECT_EQ(0, tester.GetReceivedMessages());
  EXPECT_EQ(0, tester.GetReceivedPositions());
}

TEST_F(PositionsListenerStatisticsFixture, TestAdd) {
  // This test case was written to catch encountered error, when we forgot
  // to reset base class ocasionally.

  PositionsListenerStatistics stats1;
  stats1.IncReceivedMessages(1);

  PositionsListenerStatisticsTester tester(stats1);

  EXPECT_EQ(1, tester.GetReceivedMessages());
  EXPECT_EQ(1, tester.GetReceivedPositions());

  PositionsListenerStatistics stats2;
  stats2.IncReceivedMessages(1);

  stats1.Add(stats2);
  EXPECT_EQ(2, tester.GetReceivedMessages());
  EXPECT_EQ(2, tester.GetReceivedPositions());
}

}  // namespace geobus::statistics
