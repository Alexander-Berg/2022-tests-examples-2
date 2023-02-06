#include "search_routes_linear.hpp"

#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <trip-planner/operations/search/search_routes_linear_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/search/search_routes_linear/static_test/"
    "main.json");

}  // namespace

namespace shuttle_control::trip_planner::operations::search {

TEST(SearchRoutesLinear, WithoutPermitedRoutes) {
  const auto params_json = R"(
  {}
  )";
  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  SearchRoutesLinearOperationParams>();
  const auto& routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  SearchRoutesLinear search(info::kSearchRoutesLinear, params,
                            routes_cache_ptr);
  search.Process(search_query, search_result);

  std::unordered_set<models::RouteIdT> expected_routes = {
      models::RouteIdT(1),
      models::RouteIdT(4),
  };

  for (const auto& [route_id, route_level] : search_result.routes) {
    const auto it = expected_routes.find(route_id);
    ASSERT_FALSE(it == expected_routes.end());
    EXPECT_EQ(route_id, route_level.route_id);
    EXPECT_TRUE(route_level.segments.empty());
    expected_routes.erase(it);
  }
  EXPECT_TRUE(expected_routes.empty());
}

TEST(SearchRoutesLinear, WithPermitedRoutes) {
  const auto params_json = R"(
  {
    "routes_permitted" : ["route_1", "route_2", "route_3"]
  }
  )";
  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  SearchRoutesLinearOperationParams>();
  const auto& routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  SearchRoutesLinear search(info::kSearchRoutesLinear, params,
                            routes_cache_ptr);
  search.Process(search_query, search_result);

  std::unordered_set<models::RouteIdT> expected_routes = {
      models::RouteIdT(1),
  };

  for (const auto& [route_id, route_level] : search_result.routes) {
    const auto it = expected_routes.find(route_id);
    ASSERT_FALSE(it == expected_routes.end());
    EXPECT_EQ(route_id, route_level.route_id);
    EXPECT_TRUE(route_level.segments.empty());
    expected_routes.erase(it);
  }
  EXPECT_TRUE(expected_routes.empty());
}

}  // namespace shuttle_control::trip_planner::operations::search
