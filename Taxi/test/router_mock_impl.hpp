#include "router_mock.hpp"

#pragma once

#include <userver/utils/assert.hpp>

namespace clients::routing {

inline RoutePath RouterMock::MakeOnePointRoute(
    const std::vector<::geometry::Position>& path, const DirectionOpt&,
    const RouterSettings&, const QuerySettings&) {
  RoutePath ret;

  constexpr auto kRouteTime = std::chrono::seconds{40};
  static const auto kRouteDistance = geometry::Distance{1000 * geometry::meter};

  RoutePoint dst_point(path.back());
  dst_point.distance_since_ride_start = kRouteDistance;
  dst_point.time_since_ride_start = kRouteTime;

  ret.path.push_back(dst_point);
  ret.info = RouteInfo(kRouteTime, kRouteDistance);
  ret.legs = {routing_base::Leg{0}};

  return ret;
}

inline RoutePath RouterMock::MakeTwoPointsRoute(
    const std::vector<::geometry::Position>& path, const DirectionOpt&,
    const RouterSettings&, const QuerySettings&) {
  UASSERT(path.size() == 2);
  const auto& src = path.front();
  const auto& dst = path.back();

  constexpr auto kRouteTime = std::chrono::seconds{40};
  static const auto kRouteDistance = geometry::Distance{1000 * geometry::meter};

  RoutePath ret;
  ret.path.push_back(RoutePoint(src));

  RoutePoint dst_point(dst);
  dst_point.distance_since_ride_start = kRouteDistance;
  dst_point.time_since_ride_start = kRouteTime;

  ret.path.push_back(dst_point);
  ret.info = clients::routing::RouteInfo(kRouteTime, kRouteDistance);

  ret.legs = {routing_base::Leg{0}};

  return ret;
}

inline RoutePath RouterMock::MakeNPointsRoute(
    const std::vector<::geometry::Position>& path, const DirectionOpt&,
    const RouterSettings&, const QuerySettings&) {
  UASSERT(path.size() >= 2);

  RoutePath ret;
  const auto& src = path.front();
  ret.path.push_back(RoutePoint(src));

  constexpr auto kRouteTime = std::chrono::seconds{40};
  static const auto kRouteDistance = geometry::Distance{1000 * geometry::meter};
  std::chrono::seconds final_route_time{0};
  geometry::Distance final_route_distance{0};

  for (size_t i = 1; i < path.size(); ++i) {
    RoutePoint dst_point(path[i]);
    dst_point.time_since_ride_start = kRouteTime * i;
    dst_point.distance_since_ride_start =
        kRouteDistance.value() * geometry::Distance{i * geometry::meter};
    ret.path.push_back(dst_point);
    // legs - all points except last
    ret.legs.push_back({routing_base::Leg{i - 1}});
    final_route_time += dst_point.time_since_ride_start;
    final_route_distance += dst_point.distance_since_ride_start;
  }
  ret.info =
      clients::routing::RouteInfo(final_route_time, final_route_distance);

  return ret;
}

template <typename Callable,
          typename T = decltype(std::declval<Callable>()(
              Path{}, DirectionOpt{}, RouterSettings{}, QuerySettings{}))>
inline std::vector<T> MultiplyResults(Callable callable, const Path& p,
                                      const DirectionOpt& d,
                                      const RouterSettings& st,
                                      const QuerySettings& qst) {
  return {callable(p, d, st, qst)};
}

template <typename Callable>
inline void RouterMock::SetDefaultFetchRoutePathAndInfo(Callable callable) {
  const auto& path_callable = callable;
  const auto& info_callable = [&callable](const Path& p, const DirectionOpt& d,
                                          const RouterSettings& st,
                                          const QuerySettings& qst) {
    return callable(p, d, st, qst).info;
  };
  ON_CALL(*this, FetchRoutePath).WillByDefault(path_callable);
  ON_CALL(*this, FetchRouteInfo).WillByDefault(info_callable);

  const auto& paths_callable =
      std::bind(&MultiplyResults<decltype(path_callable)>, path_callable,
                std::placeholders::_1, std::placeholders::_2,
                std::placeholders::_3, std::placeholders::_4);
  const auto& infos_callable =
      std::bind(&MultiplyResults<decltype(info_callable)>, info_callable,
                std::placeholders::_1, std::placeholders::_2,
                std::placeholders::_3, std::placeholders::_4);
  ON_CALL(*this, FetchRoutePaths).WillByDefault(paths_callable);
  ON_CALL(*this, FetchRouteInfos).WillByDefault(infos_callable);
}

inline void RouterMock::SetDefaultMakeNPointsRoute() {
  SetDefaultFetchRoutePathAndInfo(&MakeNPointsRoute);
}

inline void RouterMock::SetDefaultMakeTwoPointsRoute() {
  SetDefaultFetchRoutePathAndInfo(&MakeTwoPointsRoute);
}

inline void RouterMock::SetDefaultMakeOnePointRoute() {
  SetDefaultFetchRoutePathAndInfo(&MakeOnePointRoute);
}

}  // namespace clients::routing
