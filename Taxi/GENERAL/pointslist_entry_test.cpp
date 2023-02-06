#include "pointslist_entry.hpp"
#include <internal/position_helper.hpp>

#include <gtest/gtest.h>

TEST(pointslist_entry_fbs, base) {
  const auto original =
      std::vector<driver_route_watcher::models::DestinationPoint>{
          {37.37 * ::geometry::lon, 55.55 * ::geometry::lat,
           std::chrono::seconds(42), std::chrono::seconds(43),
           driver_route_watcher::models::PointId("point_id_1"),
           driver_route_watcher::models::OrderId("order_id_1")},
          {37.47 * ::geometry::lon, 55.65 * ::geometry::lat,
           std::chrono::seconds(42), std::chrono::seconds(43),
           driver_route_watcher::models::PointId("point_id_1"),
           driver_route_watcher::models::OrderId("order_id_1")},
      };
  auto fbs =
      ::driver_route_watcher::internal::SerializePointslistEntry(original);
  auto converted =
      ::driver_route_watcher::internal::DeserializePointslistEntry(fbs);

  ASSERT_EQ(original.size(), converted.size());
  for (size_t i = 0; i < original.size(); ++i)
    ASSERT_TRUE(::geometry::AreClosePositions(original[i].position,
                                              converted[i].position, 0.000001));
}

TEST(pointslist_entry_fbs, deserialize_empty) {
  auto converted =
      ::driver_route_watcher::internal::DeserializePointslistEntry("");
  ASSERT_TRUE(converted.empty());
}
