#pragma once

#include <models/routes_cache.hpp>
#include <trip-planner/operations/search_query.hpp>
#include <trip-planner/operations/search_result.hpp>

namespace shuttle_control::tests::helpers {

struct TripPlannerOpearationTestHelper {
  trip_planner::operations::SearchQuery query;
  trip_planner::operations::SearchResult result;

  models::RoutesCacheIndex route_cache;

  bool operator==(const TripPlannerOpearationTestHelper& other) const;

  static TripPlannerOpearationTestHelper Build(const ::formats::json::Value&);
};

}  // namespace shuttle_control::tests::helpers
