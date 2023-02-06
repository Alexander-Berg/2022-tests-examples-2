#pragma once

#include <gtest/gtest.h>

#include <channels/positions/lowlevel.hpp>
#include <geobus/channels/positions/track_point.hpp>
#include <gpssignal/test/print_to.hpp>

#include <geobus/types/driver_id.hpp>
#include <geobus/types/driver_position.hpp>
#include <geobus/types/gps_signal_extended.hpp>

namespace geobus::lowlevel {

inline void PrintTo(const TrackPoint& track_point, std::ostream* os) {
  *os << "[lat, lon]: " << track_point.latitude << "," << track_point.longitude
      << " [dir, spd, acc]: " << track_point.direction << ", "
      << track_point.speed_kmph << ", " << track_point.accuracy
      << " timestamp: "
      << std::chrono::system_clock::to_time_t(track_point.timestamp)
      << " src: ";
  PrintTo(track_point.source, os);
}

inline void PrintTo(const DriverPositionInfo& driver_position,
                    std::ostream* os) {
  *os << "driver_id: " << driver_position.driver_id << " ";
  PrintTo(driver_position.point, os);
}
}  // namespace geobus::lowlevel
