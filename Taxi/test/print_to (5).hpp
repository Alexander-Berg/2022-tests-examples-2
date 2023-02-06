#pragma once

#include <iostream>

#include <geometry/io.hpp>

namespace routing_base {

void PrintTo(const RoutePoint& point, std::ostream* o) {
  if (o == nullptr) {
    return;
  }

  *o << point << ", " << point.distance_since_ride_start << ", "
     << point.time_since_ride_start.count();
}

}  // namespace routing_base
