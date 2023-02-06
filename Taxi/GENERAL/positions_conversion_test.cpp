#include <channels/positions/positions_conversion.hpp>
#include <channels/positions/track_point_conversion.hpp>

#include <geobus/channels/positions/plugin_test.hpp>

#include "lowlevel_positions_plugin_test.hpp"

#include <gtest/gtest.h>

#include <userver/utils/mock_now.hpp>

namespace geobus::lowlevel {

class DriverPositionTestFixture
    : public ::testing::Test,
      public ::geobus::test::PositionsTestPlugin,
      public ::geobus::test::LowlevelPositionsTestPlugin {
 protected:
  using TrackPoint = ::geobus::lowlevel::TrackPoint;
  using GpsSignalExtended = types::GpsSignalExtended;
  using DriverPosition = types::DriverPosition;
  using PositionEvent = lowlevel::PositionEvent;
  using DriverPositionInfo = lowlevel::DriverPositionInfo;

  using ::geobus::test::DriverIdTestPlugin::CreateDbid_Uuid;
  using ::geobus::test::LowlevelPositionsTestPlugin::
      TestDriverPositionsAreClose;
  using ::geobus::test::PositionsTestPlugin::TestDriverPositionsAreClose;

  void TestConversionCycle(const DriverPositionInfo& position_info) const;
  void TestConversionCycle(const DriverPosition& position) const;
};

void DriverPositionTestFixture::TestConversionCycle(
    const DriverPositionInfo& position_info) const {
  const auto& reference_value = position_info;

  DriverPosition converted_value =
      ::geobus::ToDriverPosition(DriverPositionInfo{reference_value});

  DriverPositionInfo test_value =
      ::geobus::ToDriverPositionInfo(converted_value);

  TestDriverPositionsAreClose(reference_value, test_value);
}

void DriverPositionTestFixture::TestConversionCycle(
    const DriverPosition& position) const {
  const auto& reference_value = position;
  DriverPositionInfo converted_value =
      ::geobus::ToDriverPositionInfo(reference_value);

  DriverPosition test_value =
      ::geobus::ToDriverPosition(std::move(converted_value));

  TestDriverPositionsAreClose(reference_value, test_value);
}

TEST_F(DriverPositionTestFixture, ConversionFromDriverPosition) {
  TrackPoint point = CreateValidTrackPoint(75);
  auto dbid_uuid = CreateDbid_Uuid(90);

  DriverPositionInfo position_info{dbid_uuid, point};
  TestConversionCycle(position_info);
}

TEST_F(DriverPositionTestFixture, ConversionToDriverPosition) {
  DriverPosition position = CreateDriverPosition(12);
  TestConversionCycle(position);
}

TEST_F(DriverPositionTestFixture, ConvertInvalidTrackPoint) {
  auto dbid_uuid = CreateDbid_Uuid(90);

  TrackPoint invalid_point = CreateInvalidTrackPoint(25);
  EXPECT_FALSE(invalid_point.IsValid());
  EXPECT_THROW(::geobus::ToDriverPosition(std::move(dbid_uuid), invalid_point),
               std::exception);
}

TEST_F(DriverPositionTestFixture, ConvertInvalidDriverId) {
  auto invalid_dbid_uuid = CreateInvalidDbid_Uuid(87);

  EXPECT_FALSE(invalid_dbid_uuid.IsValid());

  TrackPoint valid_point = CreateValidTrackPoint(25);
  EXPECT_TRUE(valid_point.IsValid());
  EXPECT_THROW(
      ::geobus::ToDriverPosition(std::move(invalid_dbid_uuid), valid_point),
      std::exception);
}

// Test that when converting vector of positions, invalid are skipped
TEST_F(DriverPositionTestFixture, SkipInvalid) {
  PositionEvent raw_positions;

  // Add one valid and two invalid points
  raw_positions.positions.push_back(
      DriverPositionInfo{CreateDbid_Uuid(75), CreateValidTrackPoint(29)});
  // now, invalid position and invalid driver id
  raw_positions.positions.push_back(
      DriverPositionInfo{CreateDbid_Uuid(75), CreateInvalidTrackPoint(29)});
  raw_positions.positions.push_back(DriverPositionInfo{
      CreateInvalidDbid_Uuid(71), CreateValidTrackPoint(29)});

  ::geobus::types::Message<DriverPosition> result;
  EXPECT_NO_THROW(result = ToDriverPositions(std::move(raw_positions)));
  EXPECT_EQ(1u, result.size());
}

// Test that when converting vector of positions, invalid are skipped
TEST_F(DriverPositionTestFixture, Timestamp) {
  using namespace std::chrono_literals;
  PositionEvent raw_positions;

  // Add one valid and two invalid points
  raw_positions.positions.push_back(
      DriverPositionInfo{CreateDbid_Uuid(75), CreateValidTrackPoint(29)});
  // now, invalid position and invalid driver id
  raw_positions.positions.push_back(DriverPositionInfo{
      CreateInvalidDbid_Uuid(71), CreateValidTrackPoint(29)});

  std::chrono::system_clock::time_point timestamp{};
  timestamp += 100s;
  raw_positions.time_orig = timestamp;

  ::geobus::types::Message<DriverPosition> result;
  EXPECT_NO_THROW(result = ToDriverPositions(std::move(raw_positions)));
  EXPECT_EQ(1u, result.size());
  EXPECT_EQ(timestamp, result.timestamp);
}

TEST_F(DriverPositionTestFixture, PositionEvent) {
  std::vector<DriverPosition> drivers_positions;

  drivers_positions.push_back(CreateDriverPosition(5));
  drivers_positions.push_back(CreateDriverPosition(7));
  drivers_positions.push_back(CreateDriverPosition(0));

  auto result = ::geobus::ToPositionEvent(drivers_positions);
  EXPECT_EQ(drivers_positions.size(), result.positions.size());
}

}  // namespace geobus::lowlevel
