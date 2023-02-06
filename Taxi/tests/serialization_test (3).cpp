#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>

#include <caches/surge_points.hpp>

using clients::taxi_admin_surger::SurgePoint;
using clients::taxi_admin_surger::SurgePointMode;
using dump::TestWriteReadCycle;
using surge_points_cache::caches::AllPoints;

TEST(SurgePoints, Serialization) {
  AllPoints::SurgePoints points;
  points.emplace_back(SurgePoint{
      /*id*/ "id1",
      /*version*/ 2,
      /*created*/ std::chrono::system_clock::now(),
      /*updated*/ std::chrono::system_clock::now(),
      /*location*/
      geometry::PositionAsArray{10 * geometry::lat, 20 * geometry::lon},
      /*mode*/ SurgePointMode::kApply,
      /*name*/ "name",
      /*surge_zone_name*/ "surge_zone_name",
      /*tags*/ {"foo", "bar"},
      /*snapshot*/ "snapshot",
      /*employed*/ true});

  points.emplace_back(SurgePoint{
      /*id*/ "id2",
      /*version*/ 1,
      /*created*/ std::chrono::system_clock::now(),
      /*updated*/ std::chrono::system_clock::now(),
      /*location*/
      geometry::PositionAsArray{10 * geometry::lat, 20 * geometry::lon},
      /*mode*/ SurgePointMode::kCalculate,
      /*name*/ "",
      /*surge_zone_name*/ "surge_zone_name",
      /*tags*/ {},
      /*snapshot*/ "not a snapshot",
      /*employed*/ false});

  AllPoints all_points{std::move(points), true};
  TestWriteReadCycle(all_points);
}
