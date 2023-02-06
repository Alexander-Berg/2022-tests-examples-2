#include "search_stops_linear.hpp"

#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <trip-planner/operations/search/search_stops_linear_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/search/search_stops_linear/static_test/"
    "main.json");

}  // namespace

namespace shuttle_control::trip_planner::operations::search {

TEST(SearchStopsLinear, MainScenario) {
  const auto params_json = R"(
    {
      "max_line_dist_to_pickup" : 1000,
      "max_line_dist_from_dropoff" : 1000
    }
  )";

  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  SearchStopsLinearOperationParams>();

  const auto& routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  SearchStopsLinear search(info::kSearchStopsLinear, params, routes_cache_ptr);

  search.Process(search_query, search_result);

  std::unordered_map<models::RouteIdT, std::unordered_set<models::SegmentIdT>>
      expected_route_segments = {
          {models::RouteIdT(1), {{models::StopIdT(1), models::StopIdT(2)}}},
          {models::RouteIdT(2), {}},
          {models::RouteIdT(3), {}},
          {models::RouteIdT(4), {}},
          {models::RouteIdT(5), {{models::StopIdT(12), models::StopIdT(11)}}},
      };

  for (const auto& [route_id, route_level] : search_result.routes) {
    const auto route_it = expected_route_segments.find(route_id);
    ASSERT_FALSE(route_it == expected_route_segments.end());
    auto& expected_segments = route_it->second;
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      const auto segment_it = expected_segments.find(segment_id);
      ASSERT_FALSE(segment_it == expected_segments.end());
      EXPECT_EQ(segment_id, segment_level.segment_id);
      expected_segments.erase(segment_it);
    }
    EXPECT_TRUE(expected_segments.empty());
    expected_route_segments.erase(route_it);
  }
  EXPECT_TRUE(expected_route_segments.empty());
}

TEST(SearchStopsLinear, NoFullCircles) {
  const auto params_json = R"(
    {
      "max_line_dist_to_pickup" : 1000,
      "max_line_dist_from_dropoff" : 50000
    }
  )";

  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  SearchStopsLinearOperationParams>();

  const auto& routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  SearchStopsLinear search(info::kSearchStopsLinear, params, routes_cache_ptr);

  search.Process(search_query, search_result);

  std::unordered_map<models::RouteIdT, std::unordered_set<models::SegmentIdT>>
      expected_route_segments = {
          {models::RouteIdT(1), {{models::StopIdT(1), models::StopIdT(2)}}},
          {models::RouteIdT(2), {{models::StopIdT(3), models::StopIdT(4)}}},
          {models::RouteIdT(3), {}},
          {models::RouteIdT(4), {}},
          {models::RouteIdT(5), {{models::StopIdT(12), models::StopIdT(11)}}},
      };

  for (const auto& [route_id, route_level] : search_result.routes) {
    const auto route_it = expected_route_segments.find(route_id);
    ASSERT_FALSE(route_it == expected_route_segments.end());
    auto& expected_segments = route_it->second;
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      const auto segment_it = expected_segments.find(segment_id);
      ASSERT_FALSE(segment_it == expected_segments.end());
      EXPECT_EQ(segment_id, segment_level.segment_id);
      expected_segments.erase(segment_it);
    }
    EXPECT_TRUE(expected_segments.empty());
    expected_route_segments.erase(route_it);
  }
  EXPECT_TRUE(expected_route_segments.empty());
}

}  // namespace shuttle_control::trip_planner::operations::search
