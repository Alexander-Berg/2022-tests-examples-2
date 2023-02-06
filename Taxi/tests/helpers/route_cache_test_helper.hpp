#pragma once

#include <models/route.hpp>
#include <models/routes_cache.hpp>

#include <tests/helpers/interlayers/route_info.hpp>

namespace shuttle_control::tests::helpers {

struct RouteCacheTestHelper {
  models::RoutesCacheIndex routes_cache;

  // todo @nefedov-dima support schedules
  static RouteCacheTestHelper Build(
      const std::unordered_map<models::RouteIdT, interlayers::RouteInfo>&
          routes_info);
};

}  // namespace shuttle_control::tests::helpers
