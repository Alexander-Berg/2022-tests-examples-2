#include "filter_by_formulas.hpp"

#include <boost/lexical_cast.hpp>

#include <gtest/gtest.h>

#include <testing/source_path.hpp>

#include <trip-planner/operations/filter/filter_by_formulas_info.hpp>

#include <tests/helpers/trip_planner_operations_test_helper.hpp>

namespace {

namespace op = shuttle_control::trip_planner::operations;

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_formulas/static_test/"
    "main.json");

op::filter::FilterByFormulas CreateFilter(const std::string& params_json) {
  return op::filter::FilterByFormulas{
      op::filter::info::kFilterByFormulas,
      ::formats::json::FromString(params_json)
          .As<op::filter::FilterByFormulas::ParamsT>()};
}

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByFormulas, EmptyFormulas) {
  const auto params_json = R"(
    { "formulas": {} }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  CreateFilter(params_json).Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b2"),
              {},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b3"),
              {},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {},
          },
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          EXPECT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons);
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

TEST(FilterByFormulas, FormulaLimitMax) {
  const auto params_json = R"(
    {
      "formulas": {
        "filter_out_all_matches": {
          "formula": {
            "coeff_walk_pickup_time": 0,
            "coeff_walk_dropoff_time": 0,
            "coeff_shuttle_eta": 10,
            "coeff_user_wait_time": 0,
            "coeff_shuttle_ride_time": 0,
            "coeff_walk_ab_time": 10000,
            "coeff_car_ab_time": 0
          },
          "max_score": 1
        }
      }
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  CreateFilter(params_json).Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {{
                  "filter_by_formulas",
                  ::formats::json::FromString(R"(
                    {
                      "formula_name": "filter_out_all_matches",
                      "limit": {
                        "type": "max",
                        "value": 1
                      },
                      "score": 1190000
                    }
                  )"),
              }},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b2"),
              {{
                  "filter_by_formulas",
                  ::formats::json::FromString(R"(
                    {
                      "formula_name": "filter_out_all_matches",
                      "limit": {
                        "type": "max",
                        "value": 1
                      },
                      "score": 1190150
                    }
                  )"),
              }},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b3"),
              {{
                  "filter_by_formulas",
                  ::formats::json::FromString(R"(
                    {
                      "formula_name": "filter_out_all_matches",
                      "limit": {
                        "type": "max",
                        "value": 1
                      },
                      "score": 1190180
                    }
                  )"),
              }},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {{
                  "filter_by_formulas",
                  ::formats::json::FromString(R"(
                    {
                      "formula_name": "filter_out_all_matches",
                      "limit": {
                        "type": "max",
                        "value": 1
                      },
                      "score": 1190180
                    }
                  )"),
              }},
          },
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          EXPECT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons);
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

TEST(FilterByFormulas, FormulaLimitMin) {
  const auto& block_reason = ::formats::json::FromString(R"(
    {
      "formula_name": "filter_out_all_matches",
      "limit": {
        "type": "min",
        "value": 100
      },
      "score": 0
    }
  )");

  const auto params_json = R"(
    {
      "formulas": {
        "filter_out_all_matches": {
          "formula": {
            "coeff_walk_pickup_time": 0,
            "coeff_walk_dropoff_time": 0,
            "coeff_shuttle_eta": 0,
            "coeff_user_wait_time": 0,
            "coeff_shuttle_ride_time": 0,
            "coeff_walk_ab_time": 0,
            "coeff_car_ab_time": 0
          },
          "min_score": 100
        }
      }
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  CreateFilter(params_json).Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {{"filter_by_formulas", block_reason}},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b2"),
              {{"filter_by_formulas", block_reason}},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b3"),
              {{"filter_by_formulas", block_reason}},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {{"filter_by_formulas", block_reason}},
          },
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          EXPECT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons);
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

TEST(FilterByFormulas, NoDataProvider) {
  const auto& kNoDataProvider =
      ::formats::json::ValueBuilder{"no_data_provided"}.ExtractValue();

  const auto params_json = R"(
    { "formulas": {} }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  auto& target_segments = search_result.routes.at(models::RouteIdT{2}).segments;
  for (auto& [segment_id, segment_level] : target_segments) {
    segment_level.from_dropoff = std::nullopt;
    segment_level.to_pickup = std::nullopt;
  }

  CreateFilter(params_json).Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b1"),
              {},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b2"),
              {},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b3"),
              {{"filter_by_formulas", kNoDataProvider}},
          },
          {
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b4"),
              {{"filter_by_formulas", kNoDataProvider}},
          },
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          EXPECT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons);
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

}  // namespace shuttle_control::trip_planner::operations::filter
