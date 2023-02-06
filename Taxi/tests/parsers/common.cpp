#include "common.hpp"

#include <geometry/position.hpp>

namespace shuttle_control::tests::parsers {

::geometry::Position ParseToPosition(const ::formats::json::Value& value) {
  if (value.IsArray()) {
    return ::geometry::Position{::geometry::Latitude{value[0].As<double>()},
                                ::geometry::Longitude{value[1].As<double>()}};
  }
  return ::geometry::Position{::geometry::Latitude{value["lat"].As<double>()},
                              ::geometry::Longitude{value["lon"].As<double>()}};
}

models::Route::Meta ParseToRouteMeta(const formats::json::Value& value) {
  return models::Route::Meta{
      value["id"].As<models::RouteIdT>(),  value["name"].As<std::string>(),
      value["is_cyclic"].As<bool>(false),  value["is_dynamic"].As<bool>(false),
      value["is_deleted"].As<bool>(false), value["version"].As<int64_t>(1),
  };
}

}  // namespace shuttle_control::tests::parsers
