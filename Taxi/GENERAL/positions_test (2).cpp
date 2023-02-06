#include <channels/positions/lowlevel.hpp>
#include <channels/positions/traits.hpp>
#include <lowlevel/fb_serialization_test.hpp>
#include <test/lowlevel_comparisons.hpp>
#include "test_traits.hpp"

#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

namespace geobus::lowlevel {

bool operator!=(const TrackPoint& point1, const TrackPoint& point2) {
  return !operator==(point1, point2);
}

bool operator==(const Positions& pos1, const Positions& pos2) {
  if (pos1.size() != pos2.size()) return false;
  for (size_t i = 0; i < pos1.size(); ++i) {
    const auto& p1 = pos1[i];
    const auto& p2 = pos2[i];
    if (p1.driver_id != p2.driver_id) return false;
    if (p1.point != p2.point) return false;
  }

  return true;
}

TEST(GeobusPositions, One) {
  Positions orig_pos;
  const auto timepoint = std::chrono::time_point_cast<std::chrono::seconds>(
      ::utils::datetime::Now());
  orig_pos.push_back({::geobus::types::DriverId{"1_01234"},
                      TrackPoint{0, 1, 2, 3, timepoint,
                                 geobus::types::PositionSource::Adjuster}});
  orig_pos.push_back({::geobus::types::DriverId{"1_56789"},
                      TrackPoint{5, 6, 7, 8, timepoint,
                                 geobus::types::PositionSource::Navigator}});

  const std::string& data = SerializePositionEvent({orig_pos, timepoint});
  const auto& event = DeserializePositionEvent(data);

  EXPECT_EQ(orig_pos, event.positions);
  EXPECT_EQ(timepoint, event.time_orig);
}

TEST(GeobusPositions, InvalidMessage) {
  std::string data(42, '\0');
  EXPECT_THROW({ DeserializePositionEvent(data); }, std::runtime_error);
}

TEST(GeobusPositions, MinusOne) {
  Positions orig_pos;
  const auto timepoint = std::chrono::time_point_cast<std::chrono::seconds>(
      ::utils::datetime::Now());
  orig_pos.push_back({::geobus::types::DriverId{"1_01234"},
                      TrackPoint{0, 1, -1, 3, timepoint,
                                 geobus::types::PositionSource::Adjuster}});
  orig_pos.push_back({::geobus::types::DriverId{"1_56789"},
                      TrackPoint{5, 6, 7, -1, timepoint,
                                 geobus::types::PositionSource::Navigator}});

  const std::string& data = SerializePositionEvent({orig_pos, timepoint});
  const auto& event = DeserializePositionEvent(data);

  EXPECT_EQ(orig_pos, event.positions);
  EXPECT_EQ(timepoint, event.time_orig);
}

TEST(GeobusPositions, EmptyPositions) {
  Positions orig_pos;
  const auto timepoint = std::chrono::time_point_cast<std::chrono::seconds>(
      ::utils::datetime::Now());

  const std::string& data = SerializePositionEvent({orig_pos, timepoint});
  const auto& event = DeserializePositionEvent(data);

  EXPECT_EQ(orig_pos, event.positions);
  EXPECT_EQ(timepoint, event.time_orig);
}

// =================== New V2 channel ========================
namespace positions {

INSTANTIATE_TYPED_TEST_SUITE_P(DriverPositionTest, FlatbuffersSerializationTest,
                               types::DriverPosition);

}

}  // namespace geobus::lowlevel
