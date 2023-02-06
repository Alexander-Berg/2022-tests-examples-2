#include "filter_by_vfh.hpp"

#include <gtest/gtest.h>

#include <boost/lexical_cast.hpp>
#include <testing/source_path.hpp>

#include <trip-planner/operations/filter/filter_by_vfh_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_vfh/"
    "static_test/main.json");

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByVfhRequired, testFilter) {
  const auto params_json = R"(
  {"vfh_required" : true}
  )";

  const auto params =
      ::formats::json::FromString(params_json).As<FilterByVfh::ParamsT>();

  auto [search_query, search_result, _] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  FilterByVfh filter(info::kFilterByVfh, params);
  filter.Process(search_query, search_result);

  const auto& kVfhRequired =
      ::formats::json::ValueBuilder{"vfh_id_must_be_set"}.ExtractValue();

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {},
          },
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b4"),
           {}},
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b2"),
           {}},
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b3"),
           {{"filter_by_vfh", kVfhRequired}}},
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

TEST(FilterByVfhProhibited, testFilter) {
  const auto params_json = R"(
  {"vfh_prohibited" : true}
  )";

  const auto params =
      ::formats::json::FromString(params_json).As<FilterByVfh::ParamsT>();

  auto [search_query, search_result, _] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  FilterByVfh filter(info::kFilterByVfh, params);
  filter.Process(search_query, search_result);

  const auto& kVfhProhibited =
      ::formats::json::ValueBuilder{"vfh_id_must_not_be_set"}.ExtractValue();

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {{"filter_by_vfh", kVfhProhibited}},
          },
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b4"),
           {{"filter_by_vfh", kVfhProhibited}}},
          {boost::lexical_cast<boost::uuids::uuid>(
               "427a330d-2506-464a-accf-346b31e288b2"),
           {{"filter_by_vfh", kVfhProhibited}}},
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
