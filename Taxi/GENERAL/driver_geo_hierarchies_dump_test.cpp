#include "driver_geo_hierarchies.hpp"

#include <vector>

#include <userver/dump/test_helpers.hpp>
#include <userver/utest/utest.hpp>

TEST(DriverGeoHierarchies, DriverGeoHierarchyCache) {
  using namespace std::chrono;

  const auto now = utils::datetime::Now();
  std::vector<caches::drivers::DriverGeoHierarchyDbEntry> entries = {
      {now, 1, std::nullopt},
      {now + seconds{3}, 1, {{"z"}}},
      {now + seconds{1}, 2, {{"a2", "sss", "s"}}},
      {now + seconds{2}, 4, {{"ddd", "a3", "s"}}},
      {now, 3, {{"a1", "a2", "a3"}}},
      {now + minutes{1}, 55, {{"ddd", "a1", "s"}}},
  };

  caches::drivers::DriverGeoHierarchyCache cache;
  for (auto&& entry : entries) {
    cache.insert_or_assign(entry.driver_id_id, std::move(entry));
    dump::TestWriteReadCycle(cache);
  }
}
