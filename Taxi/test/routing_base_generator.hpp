#pragma once

#include <geometry/test/geometry_generator.hpp>
#include <routing-base/route_info.hpp>

namespace routing_base::test {

/// This plugins provides functions for generating
/// routing_base structures and objects

class RoutingBaseGenerator : public geometry::test::GeometryGenerator {
 public:
  using Time = std::chrono::seconds;
  using Distance = ::geometry::Distance;
  /// Create route path with specified time and distance
  static RoutePath CreateRoutePath(Time duration, Distance distance,
                                   size_t legs_count = 1,
                                   size_t positions_per_leg = 7);
};

}  // namespace routing_base::test

#include "routing_base_generator_impl.hpp"
