#pragma once

namespace routing_base::test {

RoutePath RoutingBaseGenerator::CreateRoutePath(Time duration,
                                                Distance distance,
                                                size_t legs_count,
                                                size_t positions_per_leg) {
  legs_count = std::max<size_t>(1, legs_count);
  positions_per_leg = std::max<size_t>(1, positions_per_leg);

  const size_t total_points = legs_count * positions_per_leg;
  const Time time_per_point =
      std::max<Time>(duration / total_points, std::chrono::seconds{1});
  const Distance distance_per_point =
      distance / static_cast<double>(total_points);  // Distance is double-based

  RoutePath result{duration, distance};
  result.path.reserve(total_points);
  for (size_t i = 0; i < total_points; ++i) {
    result.path.push_back(RoutePoint{
        CreatePosition(/*seed*/ i + legs_count + positions_per_leg),
        time_per_point * i, distance_per_point * static_cast<double>(i)});
  }

  // fix last point
  result.path.back().time_since_ride_start = duration;
  result.path.back().distance_since_ride_start = distance;

  // fill legs
  result.legs.reserve(legs_count);
  for (size_t i = 0; i < legs_count; ++i) {
    result.legs.push_back(Leg{i * positions_per_leg});
  }

  return result;
}

}  // namespace routing_base::test
