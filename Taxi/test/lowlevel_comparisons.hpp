#pragma once

#include <geobus/channels/positions/track_point.hpp>

namespace geobus::lowlevel {

// This is not so usefull function. It has been made only for tests
inline bool operator==(const TrackPoint& point1, const TrackPoint& point2) {
  return point1.longitude == point2.longitude &&
         point1.latitude == point2.latitude &&
         point1.direction == point2.direction &&
         point1.speed_kmph == point2.speed_kmph &&
         point1.timestamp == point2.timestamp &&
         point1.source == point2.source && point1.accuracy == point2.accuracy;
}

// This is not so usefull function. It has been made only for tests
inline bool operator==(const DriverPositionInfo& lhs,
                       const DriverPositionInfo& rhs) {
  return lhs.driver_id == rhs.driver_id && lhs.point == rhs.point;
}

// This is not so usefull function. It has been made only for tests
inline bool operator==(const PositionEvent& lhs, const PositionEvent& rhs) {
  return lhs.positions == rhs.positions && lhs.time_orig == rhs.time_orig;
}

}  // namespace geobus::lowlevel
