#include <gtest/gtest.h>

#include <fts-universal-signal/conversions.hpp>

namespace {
fts_universal_signal::Position GetPosition(int seed) {
  fts_universal_signal::Position result(
      geometry::Position(geometry::units::Longitude{25 + 0.1 * (seed % 10)},
                         geometry::units::Latitude{25 + 0.1 * (seed % 10)}),
      gpssignal::Speed::from_value(2 + 0.1 * (seed % 10)),
      gpssignal::Distance::from_value(2 + 0.1 * (seed % 10)),
      gpssignal::Azimuth::from_value(2 + 0.1 * (seed % 10)),
      gpssignal::Distance::from_value(2 + 0.1 * (seed % 10)));
  return result;
}

::handlers::libraries::fts_universal_signal::PositionV2 GetPositionV2(
    int seed) {
  ::handlers::libraries::fts_universal_signal::PositionV2 result;
  result.lat = geometry::units::Latitude{25 + 0.1 * (seed % 10)};
  result.lon = geometry::units::Longitude{25 + 0.1 * (seed % 10)};
  result.speed = gpssignal::Speed::from_value(2 + 0.1 * (seed % 10));
  result.accuracy = gpssignal::Distance::from_value(2 + 0.1 * (seed % 10));
  result.direction = gpssignal::Azimuth::from_value(2 + 0.1 * (seed % 10));
  result.altitude = gpssignal::Distance::from_value(2 + 0.1 * (seed % 10));
  return result;
}

fts_universal_signal::UniversalSignal GetUniversalSignal() {
  fts_universal_signal::UniversalSignal result;
  result.timestamp =
      std::chrono::system_clock::time_point{std::chrono::milliseconds{1005000}};
  result.sensors = {
      fts_universal_signal::Sensor(
          "key1", std::vector<unsigned char>{'v', 'a', 'l', 'u', 'e', '1'}),
      fts_universal_signal::Sensor(
          "key2", std::vector<unsigned char>{'v', 'a', 'l', 'u', 'e', '2'})};
  // geodata1
  result.geodata.emplace_back();
  result.geodata.back().time_shift = std::chrono::seconds{0};
  result.geodata.back().positions.push_back(GetPosition(1));
  result.geodata.back().positions.push_back(GetPosition(2));
  // geodata2
  result.geodata.emplace_back();
  result.geodata.back().time_shift = std::chrono::seconds{0};
  result.geodata.back().positions.push_back(GetPosition(3));
  result.geodata.back().positions.push_back(GetPosition(4));

  return result;
}

fts_universal_signal::UniversalSignalV2 GetUniversalSignalV2() {
  fts_universal_signal::UniversalSignalV2 result;
  result.timestamp = std::chrono::milliseconds{1005000};
  result.sensors.extra = {{"key1", "dmFsdWUx"}, {"key2", "dmFsdWUy"}};
  // geodata1
  result.geodata.emplace_back();
  result.geodata.back().time_shift = std::chrono::seconds{0};
  result.geodata.back().positions.push_back({GetPositionV2(1)});
  result.geodata.back().positions.push_back({GetPositionV2(2)});
  // geodata2
  result.geodata.emplace_back();
  result.geodata.back().time_shift = std::chrono::seconds{0};
  result.geodata.back().positions.push_back({GetPositionV2(3)});
  result.geodata.back().positions.push_back({GetPositionV2(4)});

  return result;
}
}  // namespace

TEST(ConversionV1ToV2, Conversions) {
  auto signal_v1 = GetUniversalSignal();
  auto signal_v2_expected = GetUniversalSignalV2();
  auto signal_v2_actual = fts_universal_signal::ToUniversalSignalV2(signal_v1);
  ASSERT_EQ(signal_v2_expected, signal_v2_actual);
}

TEST(ConversionV2ToV1, Conversions) {
  auto signal_v1_expected = GetUniversalSignal();
  auto signal_v2 = GetUniversalSignalV2();
  auto signal_v1_actual = fts_universal_signal::ToUniversalSignal(signal_v2);

  std::sort(signal_v1_expected.sensors.begin(),
            signal_v1_expected.sensors.end());
  std::sort(signal_v1_actual.sensors.begin(), signal_v1_actual.sensors.end());
  ASSERT_EQ(signal_v1_expected, signal_v1_actual);
}
