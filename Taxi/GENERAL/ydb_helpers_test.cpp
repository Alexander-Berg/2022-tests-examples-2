#include <gtest/gtest.h>
#include <chrono>
#include <optional>
#include <vector>

#include "geometry/units.hpp"
#include "gpssignal/gps_signal.hpp"
#include "gpssignal/units.hpp"
#include "trackstory-shared/types.hpp"
#include "trackstory/helpers.hpp"
#include "trackstory/ydb_helpers.hpp"

using gpssignal::GpsSignal;
using trackstory::GpsPositionMap;
using trackstory::TimePoint;
using trackstory::ydb_helpers::ArePositionsEqual;
using trackstory::ydb_helpers::CompareYdbData;

namespace {

GpsSignal MakePoint(double lon, double lat, long timestamp,
                    std::optional<double> speed = {},
                    std::optional<double> accuracy = {},
                    std::optional<int> direction = {},
                    std::optional<double> altitude = {}) {
  GpsSignal point{};

  TimePoint timepoint = trackstory::helpers::UnixTimeToTimePoint(timestamp);

  point.timestamp = timepoint;
  point.SetLatitudeFromDouble(lat);
  point.SetLongitudeFromDouble(lon);

  if (speed)
    point.speed = gpssignal::Speed{*speed * geometry::meters_per_second};

  if (accuracy)
    point.accuracy = gpssignal::Distance{*accuracy * geometry::meters};

  if (direction) point.direction = gpssignal::Azimuth::from_value(*direction);

  if (altitude)
    point.altitude = gpssignal::Distance{*altitude * geometry::meters};

  return point;
}

GpsPositionMap MakeMap(std::vector<GpsSignal> points) {
  GpsPositionMap out{};
  for (const auto& point : points) {
    auto map_timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
        point.timestamp.time_since_epoch());
    out[map_timestamp.count()] = point;
  }
  return out;
}

const TimePoint epoch = TimePoint(std::chrono::seconds{0});
const TimePoint epoch_plus_100 = TimePoint(std::chrono::seconds{100});

}  // namespace

TEST(YdbHelpers, EqualPointsOne) {
  gpssignal::GpsSignal signal{};
  ASSERT_TRUE(ArePositionsEqual(signal, signal));
}

TEST(YdbHelpers, DifferentPoints) {
  auto signal1 = MakePoint(0, 0, 1);
  auto signal2 = MakePoint(0, 0, 2);
  ASSERT_FALSE(ArePositionsEqual(signal1, signal2));
}

TEST(YdbHelpers, PointsWithOptionals) {
  auto signal1 = MakePoint(0, 0, 1);
  auto signal2 = MakePoint(0, 0, 1, 1.0, 1, 10, 0);
  ASSERT_TRUE(ArePositionsEqual(signal1, signal2));
}

TEST(YdbHelpers, PointsWithDifferentOptionals) {
  // For now don't care if optionals differ
  auto signal1 = MakePoint(0, 0, 1, {}, {}, 15, {});
  auto signal2 = MakePoint(0, 0, 1, 1.0, 1, 10, 0);
  ASSERT_TRUE(ArePositionsEqual(signal1, signal2));
}

TEST(YdbHelpers, PointsWithEqualsOptionals) {
  auto signal1 = MakePoint(0, 0, 1, {}, {}, 10, {});
  auto signal2 = MakePoint(0, 0, 1, 1.0, 1, 10, 0);
  ASSERT_TRUE(ArePositionsEqual(signal1, signal2));
}

TEST(YdbHelpers, Statistics) {
  auto map = MakeMap({MakePoint(0, 0, 1), MakePoint(0, 1, 2)});

  auto stats = CompareYdbData(map, map, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 0);
  ASSERT_EQ(stats.points_not_in_ydb, 0);
}

// Something changed in Tier0 and this test became flaky
TEST(YdbHelpers, DISABLED_StatisticsDifferentAmount) {
  auto map1 = MakeMap({MakePoint(0, 0, 10), MakePoint(0, 1, 20)});

  auto map2 =
      MakeMap({MakePoint(0, 0, 10), MakePoint(0, 1, 20), MakePoint(1, 1, 30)});

  auto map3 =
      MakeMap({MakePoint(0, 0, 10), MakePoint(0, 1, 20), MakePoint(1, 1, 5)});

  auto map4 =
      MakeMap({MakePoint(0, 0, 10), MakePoint(0, 1, 20), MakePoint(1, 1, 15)});

  // more in ydb

  auto stats = CompareYdbData(map1, map2, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 1);
  ASSERT_EQ(stats.points_not_in_ydb, 0);

  stats = CompareYdbData(map1, map3, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 1);
  ASSERT_EQ(stats.points_not_in_ydb, 0);

  stats = CompareYdbData(map1, map4, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 1);
  ASSERT_EQ(stats.points_not_in_ydb, 0);

  // less in ydb

  stats = CompareYdbData(map2, map1, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 0);
  // This one is flaky
  ASSERT_EQ(stats.points_not_in_ydb, 1);

  stats = CompareYdbData(map3, map1, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 0);
  ASSERT_EQ(stats.points_not_in_ydb, 1);

  stats = CompareYdbData(map4, map1, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 2);
  ASSERT_EQ(stats.points_in_ydb, 0);
  ASSERT_EQ(stats.points_not_in_ydb, 1);
}

TEST(YdbHelpers, StatisticsEmpty) {
  GpsPositionMap empty{};

  auto stats = CompareYdbData(empty, empty, epoch, epoch_plus_100);

  ASSERT_EQ(stats.different_points, 0);
  ASSERT_EQ(stats.equal_points, 0);
  ASSERT_EQ(stats.points_in_ydb, 0);
  ASSERT_EQ(stats.points_not_in_ydb, 0);
}
