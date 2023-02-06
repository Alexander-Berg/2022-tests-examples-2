#include <chrono>
#include <vector>

#include <gtest/gtest.h>

#include <geometry/position.hpp>
#include <geometry/units.hpp>

#include <fts-universal-signal/fbs.hpp>
#include <fts-universal-signal/universal_signal.hpp>

using namespace fts_universal_signal;

namespace {

std::vector<unsigned char> Convert(const std::string& data) {
  return std::vector<unsigned char>(data.begin(), data.end());
}

}  // namespace

TEST(FlatBuffersTests, SerializeDeserialize) {
  Sensor sensor{"key", Convert("data")};

  Position signal{};
  signal.position =
      geometry::Position(geometry::Longitude{11}, geometry::Latitude{22});
  signal.accuracy = Position::Distance::from_value(2.0);
  signal.direction = Position::Azimuth::from_value(180);

  UniversalSignal universal_signal{};
  universal_signal.timestamp =
      std::chrono::system_clock::time_point{std::chrono::seconds{1000}};
  universal_signal.geodata.push_back(GeoDatum());
  auto& geodatum = universal_signal.geodata[0];
  geodatum.positions.push_back(signal);
  geodatum.positions.push_back(signal);
  universal_signal.sensors.push_back(sensor);

  auto data = UniversalSignalToFbs(universal_signal);
  auto other = UniversalSignalFromFbs(data);

  ASSERT_EQ(universal_signal, other);
}
