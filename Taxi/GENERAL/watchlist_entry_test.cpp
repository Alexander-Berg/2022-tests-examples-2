#include "watchlist_entry.hpp"
#include <internal/position_helper.hpp>

#include <gtest/gtest.h>

TEST(watchlist_entry_fbs, base) {
  ::geometry::Position original(37.37 * ::geometry::lon,
                                55.55 * ::geometry::lat);
  auto fbs =
      ::driver_route_watcher::internal::SerializeWatchlistEntry(original);
  auto converted =
      ::driver_route_watcher::internal::DeserializeWatchlistEntry(fbs);

  ASSERT_TRUE(::geometry::AreClosePositions(original, converted, 0.000001));
}

TEST(watchlist_entry_fbs, deserialize_empty) {
  auto converted =
      ::driver_route_watcher::internal::DeserializeWatchlistEntry("");
  ASSERT_TRUE(driver_route_watcher::internal::IsEmpty(converted));
}
