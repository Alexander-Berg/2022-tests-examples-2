#include <userver/utest/utest.hpp>

#include <geobus/channels/edge_positions/plugin_test.hpp>
#include "edge_positions_conversion.hpp"

#include <userver/utils/mock_now.hpp>

namespace geobus::clients {

////////////////////////////////////////////////////////////////////////////
// Tests
////////////////////////////////////////////////////////////////////////////

class EdgePositionsTestFixture
    : public testing::Test,
      public ::geobus::test::EdgePositionsTestPlugin {};

TEST_F(EdgePositionsTestFixture, TestConversion) {
  using namespace std::chrono_literals;
  std::vector<types::DriverEdgePosition> payload;
  payload.push_back(CreateValidEdgePosition(2));
  payload.push_back(CreateValidEdgePosition(3));

  std::chrono::system_clock::time_point timestamp{};
  timestamp += 100s;

  ::utils::datetime::MockNowSet(timestamp);

  auto lowlevel_payload = ToEdgePositions(payload);
  ::utils::datetime::MockNowUnset();

  EXPECT_EQ(payload.size(), lowlevel_payload.positions.size());
  EXPECT_EQ(timestamp, lowlevel_payload.timestamp);

  auto highlevel_payload = ToEdgePositions(lowlevel_payload);

  EXPECT_EQ(payload.size(), highlevel_payload.size());
  EXPECT_EQ(payload, highlevel_payload.data);
  EXPECT_EQ(timestamp, highlevel_payload.timestamp);
}

}  // namespace geobus::clients
