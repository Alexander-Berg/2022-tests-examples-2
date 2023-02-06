#include "route_info.hpp"

#include <tests/parsers/common.hpp>
#include <tests/parsers/models.hpp>

namespace shuttle_control::tests::helpers::interlayers {

RouteInfo Parse(const formats::json::Value& value,
                ::formats::parse::To<RouteInfo>) {
  models::Route route{parsers::ParseToRouteMeta(value["meta"])};
  std::unordered_map<models::StopIdT, std::string> stops_ya_transport_ids;

  const auto& json_points =
      value["points"].As<std::vector<formats::json::Value>>();

  for (const auto& json_point : json_points) {
    models::Route::ViaPoint via_point{
        json_point["point_id"].As<models::PointIdT>(),
        tests::parsers::ParseToPosition(json_point["position"]),
        json_point["is_anchor"].As<bool>(false),
    };

    if (json_point.HasMember("stop_id")) {
      models::Route::StopPoint stop_point{
          std::move(via_point),
          json_point["stop_id"].As<models::StopIdT>(),
          json_point["name"].As<std::string>(),
          json_point["is_terminal"].As<bool>(false),
          {}};
      auto&& ya_transport_id =
          json_point["ya_transport_id"].As<std::optional<std::string>>();
      if (ya_transport_id) {
        stops_ya_transport_ids.emplace(stop_point.stop_id,
                                       std::move(ya_transport_id.value()));
      }
      route.AddStopPoint(std::move(stop_point));
    } else {
      route.AddViaPoint(std::move(via_point));
    }
  }

  return RouteInfo{
      std::move(route),
      ::geometry::Distance::from_value(value["length"].As<double>(0.0)),
      value["geo_data"].As<std::optional<models::GeoData>>().value_or(
          models::GeoData{}),
      std::move(stops_ya_transport_ids),
  };
}

bool RouteInfo::operator==(const RouteInfo& other) const {
  return route == other.route && length == other.length &&
         geo_data == other.geo_data;
}

}  // namespace shuttle_control::tests::helpers::interlayers
