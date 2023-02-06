#pragma once

#include <models/route.hpp>
#include <models/routes_cache.hpp>

namespace shuttle_control::tests::helpers::interlayers {

struct RouteInfo {
  models::Route route;
  geometry::units::Distance length;
  models::GeoData geo_data;

  std::unordered_map<models::StopIdT, std::string> stops_ya_transport_ids;

  bool operator==(const RouteInfo& other) const;

  friend RouteInfo Parse(const ::formats::json::Value& value,
                         ::formats::parse::To<RouteInfo>);
};

}  // namespace shuttle_control::tests::helpers::interlayers
