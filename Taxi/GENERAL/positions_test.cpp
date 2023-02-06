#include "positions.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

static bool PositionsEquals(const geobus::Positions& pos1,
                            const geobus::Positions& pos2) {
  if (pos1.size() != pos2.size()) return false;
  for (size_t i = 0; i < pos1.size(); ++i) {
    const auto& p1 = pos1[i];
    const auto& p2 = pos2[i];
    const models::DriverId& d1 = p1.first;
    const models::DriverId& d2 = p2.first;

    if (!d1.dbid.empty() && !d2.dbid.empty()) {
      if (d1.dbid != d2.dbid) return false;
    } else if (!d1.clid.empty() && !d2.clid.empty()) {
      if (d1.clid != d2.clid) return false;
    }

    if (!(p1.second == p2.second)) return false;
  }

  return true;
}

TEST(GeobusPositions, One) {
  const config::Config config(config::DocsMapForTest());

  geobus::Positions orig_pos;
  orig_pos.push_back(
      {models::DriverId("1", "1", "01234"),
       utils::geometry::TrackPoint{0, 1, 2, 3, 4,
                                   utils::geometry::PointSource::Adjuster}});
  orig_pos.push_back(
      {models::DriverId("1", "1", "56789"),
       utils::geometry::TrackPoint{5, 6, 7, 8, 9,
                                   utils::geometry::PointSource::Navigator}});

  std::vector<TrackerDriverInfo> orig_drivers;
  for (const auto& item : orig_pos) {
    const auto& p = item.second;
    TrackerDriverInfo driver_info(item.first, p.lon, p.lat, p.timestamp,
                                  p.timestamp, p.direction, p.speed,
                                  p.accuracy);
    orig_drivers.push_back(driver_info);
  }

  const std::string& data =
      geobus::SerializePositionEvent(orig_drivers, config);
  const auto& event = geobus::DeserializePositionEvent(data);

  EXPECT_TRUE(PositionsEquals(orig_pos, event.positions));
}
