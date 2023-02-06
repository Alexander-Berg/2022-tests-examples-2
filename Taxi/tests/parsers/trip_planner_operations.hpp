#pragma once

#include <userver/formats/json_fwd.hpp>

namespace shuttle_control::trip_planner::operations {

struct SearchQuery;
struct TripLevelResult;

SearchQuery Parse(const ::formats::json::Value& value,
                  formats::parse::To<SearchQuery>);

TripLevelResult Parse(const ::formats::json::Value& value,
                      formats::parse::To<TripLevelResult>);

}  // namespace shuttle_control::trip_planner::operations
