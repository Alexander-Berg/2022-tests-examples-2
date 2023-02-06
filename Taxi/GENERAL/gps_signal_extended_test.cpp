#include <gtest/gtest.h>

#include <geobus/serialization/gps_signal_extended.hpp>
#include <geobus/test/gps_signal_plugin_test.hpp>
#include <geobus/types/gps_signal_extended.hpp>

namespace geobus::types {

class GpsSignalExtendedFixture : public ::geobus::test::GpsSignalTestPlugin,
                                 public ::testing::Test {};

TEST_F(GpsSignalExtendedFixture, Serialization) {
  const auto reference = CreateGpsSignalExtended(20);
  const auto as_json = formats::json::ValueBuilder(reference).ExtractValue();
  const auto test_value = as_json.As<GpsSignalExtended>();

  TestGpsSignalsAreClose(reference, test_value);
}

}  // namespace geobus::types
