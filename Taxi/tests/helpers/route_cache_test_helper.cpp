#include "route_cache_test_helper.hpp"

#include <utils/algo.hpp>

namespace shuttle_control::tests::helpers {

RouteCacheTestHelper RouteCacheTestHelper::Build(
    const std::unordered_map<models::RouteIdT, interlayers::RouteInfo>&
        routes_info) {
  models::RoutesCacheIndex routes_cache{};

  for (const auto& [route_id, route_info] : routes_info) {
    const auto& [route, length, geo_data, stops_ya_transport_ids] = route_info;

    routes_cache.route_name_to_id.emplace(route.GetMeta().name, route_id);

    auto& route_data = routes_cache.routes
                           .try_emplace(route_id,
                                        models::RouteData{
                                            route.GetMeta().name,
                                            {},
                                            {},
                                            {},
                                            route.GetMeta().is_cyclic,
                                            route.GetMeta().is_dynamic,
                                            route.GetMeta().is_deleted,
                                            length,
                                            geo_data,
                                            route.GetMeta().version,
                                        })
                           .first->second;

    for (models::RouteIndexT i = 0; i < route.Size(); ++i) {
      const auto& point = route[i];
      const auto* stop = route.GetStop(i);

      route_data.points.emplace_back(point.point_id);
      auto& point_data =
          routes_cache.points
              .try_emplace(point.point_id,
                           models::PointData{point.position, {}, {}})
              .first->second;
      point_data.route_dependent_data.emplace(
          route_id, models::RoutePointData{i, point.is_anchor});

      if (!stop) continue;

      route_data.stops.emplace_back(stop->stop_id);
      point_data.stop_id = stop->stop_id;

      auto& stop_data =
          routes_cache.stops
              .try_emplace(
                  stop->stop_id,
                  models::StopData{stop->point_id,
                                   stop->name,
                                   ::utils::FindOptional(stops_ya_transport_ids,
                                                         stop->stop_id),
                                   {},
                                   false,
                                   stop->is_terminal})
              .first->second;

      stop_data.has_active_route =
          stop_data.has_active_route || !route.GetMeta().is_deleted;

      if (!stop->is_terminal) continue;

      route_data.terminals.emplace_back(stop->stop_id);
    }
  }

  return RouteCacheTestHelper{std::move(routes_cache)};
}

}  // namespace shuttle_control::tests::helpers
