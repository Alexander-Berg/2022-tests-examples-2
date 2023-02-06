#pragma once

#include <userver/formats/json.hpp>
#include <userver/formats/parse/common_containers.hpp>

#include <models/route.hpp>

namespace geometry {

struct Position;

}  // namespace geometry

namespace shuttle_control::tests::parsers {

template <typename MapT, typename F>
MapT ParseToMap(const ::formats::json::Value& json_values,
                const F& key_extractor) {
  using ValueT = typename MapT::mapped_type;

  MapT map;
  const auto& values = json_values.As<std::vector<ValueT>>({});
  for (const auto& value : values) {
    map.emplace(std::invoke(key_extractor, value), value);
  }
  return map;
}

::geometry::Position ParseToPosition(const ::formats::json::Value& value);

models::Route::Meta ParseToRouteMeta(const formats::json::Value& value);

template <class IdT>
models::RouteIndexSegment<IdT> ParseToRouteIndexSegment(
    const formats::json::Value& value) {
  using Segment = typename models::RouteIndexSegment<IdT>::SegmentPoint;

  const auto& parse_segment = [](const formats::json::Value& value) {
    return Segment{
        value["idx"].As<models::RouteIndexT>(),
        value["id"].As<IdT>(),
    };
  };

  return models::RouteIndexSegment<IdT>{
      value.HasMember("start")
          ? std::make_optional(parse_segment(value["start"]))
          : std::nullopt,
      parse_segment(value["end"]),
      value["is_start_on_point"].As<bool>(),
  };
}

}  // namespace shuttle_control::tests::parsers
