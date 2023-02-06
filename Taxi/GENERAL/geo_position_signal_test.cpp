#include "geo_position_signal.hpp"

#include <geobus/test_geo_position_signal.fbs.h>

#include <chrono>
#include <userver/utest/utest.hpp>

namespace geobus::lowlevel {

using namespace geometry;
using namespace geometry::literals;
using namespace std::chrono_literals;
using namespace gpssignal;

namespace {

types::GpsSignalExtended MakeGpsSignalExtended(
    geometry::Longitude lon, geometry::Latitude lat, std::optional<Speed> spd,
    std::optional<Distance> acc, std::optional<Azimuth> dir,
    std::chrono::milliseconds timestamp,
    types::PositionSource source = types::PositionSource::Gps) {
  return types::GpsSignalExtended{
      gpssignal::GpsSignal{lon, lat, spd, acc, dir,
                           std::chrono::system_clock::time_point{timestamp}},
      source};
}
}  // namespace

template <typename T>
struct GeoPositionSignalTestCase {
  T reference_object;
  GeoPositionSignalParseStats parse_stats{};
};

std::ostream& operator<<(
    std::ostream& output,
    const GeoPositionSignalTestCase<types::GpsSignalExtended>& object) {
  output << "{ ref: " << object.reference_object
         << " stats: " << object.parse_stats << "}";
  return output;
}

using GpsSignalExtendedTestCase =
    GeoPositionSignalTestCase<types::GpsSignalExtended>;

struct GeoPositionSignalToGpsSignalSerialization
    : public ::testing::TestWithParam<GpsSignalExtendedTestCase> {
  static std::vector<GpsSignalExtendedTestCase> Data;
};

// clang-format off
std::vector<GpsSignalExtendedTestCase> GeoPositionSignalToGpsSignalSerialization::Data{{
  // correct cases
  { MakeGpsSignalExtended(10 * lon, 12 * lat, 10 * meters_per_second, 5 * meter, static_cast<short>(10) * degree,
    100ms, types::PositionSource::Other), {}},
  { MakeGpsSignalExtended(10 * lon, 12 * lat, std::nullopt, 5 * meter, static_cast<short>(10) * degree,
    100ms, types::PositionSource::Gps), {}},
  { MakeGpsSignalExtended(10 * lon, 12 * lat, 10 * meters_per_second, std::nullopt, static_cast<short>(10) * degree,
    100ms, types::PositionSource::Adjuster), {}},
  { MakeGpsSignalExtended(10 * lon, 12 * lat, 10 * meters_per_second, 5 * meter, std::nullopt,
    100ms, types::PositionSource::Navigator), {}},
  // incorrect cases
  { MakeGpsSignalExtended(10 * lon, 12 * lat, 10 * meters_per_second, -5 * meter, std::nullopt,
    100ms, types::PositionSource::Navigator), {false, true}}, // negative speed is incorrect in GpsSignalExtended
  { MakeGpsSignalExtended(12 * lon, std::numeric_limits<double>::quiet_NaN()  * lat, 10 * meters_per_second, 5 * meter, std::nullopt,
    100ms, types::PositionSource::Navigator), {true, false}}, // pos is wrong
  }};
// clang-format on

TEST_P(GeoPositionSignalToGpsSignalSerialization, SerializationCycle) {
  const auto reference_parse_stats = GetParam().parse_stats;
  // Serialize
  flatbuffers::FlatBufferBuilder fbb;
  auto offset = SerializeGeoPositionSignal(fbb, GetParam().reference_object);
  fbb.Finish(offset);

  const void* buffer = fbb.GetBufferPointer();

  // Parse
  GeoPositionSignalParseStats parse_stats;
  const fbs::GeoPositionSignal* root = fbs::GetGeoPositionSignal(buffer);
  ASSERT_NE(nullptr, root);
  auto parsed_object = ParseGeoPositionSignal(
      *root, parse_stats, formats::parse::To<types::GpsSignalExtended>{});

  // If parsing was successfull, then pased_object must matched
  // otherwise, it doesn't matter
  EXPECT_EQ(reference_parse_stats, parse_stats) << parsed_object;

  if (reference_parse_stats.IsSuccess()) {
    EXPECT_EQ(GetParam().reference_object, parsed_object);
  }
}

INSTANTIATE_TEST_SUITE_P(
    GeoPositionSignalToGpsSignalSerialization,
    GeoPositionSignalToGpsSignalSerialization,
    ::testing::ValuesIn(GeoPositionSignalToGpsSignalSerialization::Data));
}  // namespace geobus::lowlevel
