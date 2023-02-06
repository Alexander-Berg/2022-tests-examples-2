#include <channels/positions/track_point_conversion.hpp>
#include <generators/lowlevel_gps_signal_generator.hpp>
#include <geobus/test/gps_signal_plugin_test.hpp>
#include <test/lowlevel_track_point_plugin_test.hpp>

#include <gtest/gtest.h>

class TrackPointTestFixture
    : public ::testing::Test,
      public ::geobus::test::GpsSignalTestPlugin,
      public ::geobus::test::LowlevelTrackPointTestPlugin {
 protected:
  using TrackPoint = ::geobus::lowlevel::TrackPoint;
  using GpsSignalExtended = ::geobus::types::GpsSignalExtended;

  using ::geobus::test::GpsSignalTestPlugin::TestGpsSignalsAreClose;

  void TestConversionCycle(const TrackPoint& point) const;
  void TestConversionCycle(const GpsSignalExtended& point) const;
};

void TrackPointTestFixture::TestConversionCycle(const TrackPoint& point) const {
  const auto& reference_value = point;
  SCOPED_TRACE(__FUNCTION__);
  GpsSignalExtended converted_value =
      ::geobus::ToGpsSignalExtended(reference_value);

  TrackPoint test_value = ::geobus::ToTrackPoint(converted_value);

  TestTrackPointsAreClose(reference_value, test_value);
}

//! [TestGpsSignalsAreCloseSnippet]
void TrackPointTestFixture::TestConversionCycle(
    const GpsSignalExtended& point) const {
  SCOPED_TRACE(__FUNCTION__);
  const auto& reference_value = point;
  TrackPoint converted_value = ::geobus::ToTrackPoint(reference_value);

  GpsSignalExtended test_value = ::geobus::ToGpsSignalExtended(converted_value);

  TestGpsSignalsAreClose(reference_value, test_value);
}
//! [TestGpsSignalsAreCloseSnippet]

TEST_F(TrackPointTestFixture, ConversionFromGpsSignal) {
  TrackPoint point = CreateValidTrackPoint(75);
  TestConversionCycle(point);

  const_cast<double&>(point.speed_kmph) = TrackPoint::kNoSpeed;
  TestConversionCycle(point);

  const_cast<double&>(point.direction) = TrackPoint::kNoDirection;
  TestConversionCycle(point);
}

TEST_F(TrackPointTestFixture, ConversionToGpsSignal) {
  GpsSignalExtended signal = CreateGpsSignalExtended(17);
  TestConversionCycle(signal);
}

TEST_F(TrackPointTestFixture, ConversionToGpsSignalNoSpeed) {
  GpsSignalExtended signal = CreateGpsSignalExtended(17);
  signal.speed = std::nullopt;
  TestConversionCycle(signal);
}

TEST_F(TrackPointTestFixture, ConversionToGpsSignalNoDirection) {
  GpsSignalExtended signal = CreateGpsSignalExtended(17);
  signal.direction = std::nullopt;
  TestConversionCycle(signal);
}

/* TrackPoint can not represent absence of accuracy */
/*
TEST_F(TrackPointTestFixture, ConversionToGpsSignalNoAccuracy) {
  GpsSignalExtended signal = CreateGpsSignalExtended(17);
  signal.accuracy = std::nullopt;
  TestConversionCycle(signal);
}
*/
