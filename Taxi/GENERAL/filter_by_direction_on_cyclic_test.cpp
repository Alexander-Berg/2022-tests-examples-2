#include "filter_by_direction_on_cyclic.hpp"

#include <gtest/gtest.h>

#include <boost/lexical_cast.hpp>
#include <testing/source_path.hpp>

#include <trip-planner/operations/filter/filter_by_direction_on_cyclic_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_direction_on_cyclic/"
    "static_test/main.json");

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByDirectionOnCyclic, TestFilter) {
  const auto params_json = R"(
  {"max_route_percent" : 55}
  )";

  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto params = ::formats::json::FromString(params_json)
                          .As<FilterByDirectionOnCyclic::ParamsT>();
  const auto& routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  FilterByDirectionOnCyclic filter(info::kFilterByDirectionOnCyclic, params,
                                   routes_cache_ptr);
  filter.Process(search_query, search_result);

  const auto& kTripLengthExceedsMaxPercent =
      ::formats::json::ValueBuilder{"trip_length_exceeds_max_percent"}
          .ExtractValue();
  const auto kNoTripLengthProvided =
      ::formats::json::ValueBuilder{"no_trip_length_provided"}.ExtractValue();

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {{"filter_by_direction_on_cyclic", kTripLengthExceedsMaxPercent}},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {{"filter_by_direction_on_cyclic", kNoTripLengthProvided}},
          },
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b2"),
           {}},
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b3"),
           {}},
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          ASSERT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons);
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

}  // namespace shuttle_control::trip_planner::operations::filter
