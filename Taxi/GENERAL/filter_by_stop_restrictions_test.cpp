#include "filter_by_stop_restrictions.hpp"

#include <gtest/gtest.h>
#include <boost/lexical_cast.hpp>

#include <testing/source_path.hpp>

#include <internal/tests/experiments3_adapter_mock.hpp>
#include <tests/helpers/trip_planner_operations_test_helper.hpp>
#include <trip-planner/operations/filter/filter_by_stop_restrictions_info.hpp>

namespace {

using testing::_;
using testing::AnyOf;
using testing::Return;

const auto kMainFilePath = ::utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_stop_restrictions/"
    "static_test/main.json");

const auto kOpName = "filter_by_stop_restrictions";

const auto kDropoffStopNotAllowed =
    ::formats::json::ValueBuilder{"dropoff_stop_not_allowed"}.ExtractValue();
const auto kDropoffStopProhibited =
    ::formats::json::ValueBuilder{"dropoff_stop_prohibited"}.ExtractValue();
const auto kPickupStopNotAllowed =
    ::formats::json::ValueBuilder{"pickup_stop_not_allowed"}.ExtractValue();
const auto kPickupStopProhibited =
    ::formats::json::ValueBuilder{"pickup_stop_prohibited"}.ExtractValue();

const auto kTripId1 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b1");
const auto kTripId2 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b2");
const auto kTripId3 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b3");
const auto kTripId4 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b4");
const auto kTripId5 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b5");
const auto kTripId6 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b6");

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByStopRestrictions, NoRestrictions) {
  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  const auto& experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto driver1 = std::optional<::models::DbidUuid>{{
      .park_id = "park_1",
      .driver_profile_id = "driver_1",
  }};
  const auto driver2 = std::optional<::models::DbidUuid>{{
      .park_id = "park_2",
      .driver_profile_id = "driver_2",
  }};
  const auto empty_restrictions =
      experiments3::shuttle_control_stop_restrictions::Value{};
  EXPECT_CALL(*experiments3, GetStopRestrictions).Times(0);
  EXPECT_CALL(*experiments3,
              GetStopRestrictions("route_1", _, _, _, _, driver1))
      .Times(3)
      .WillRepeatedly(Return(empty_restrictions));
  EXPECT_CALL(*experiments3,
              GetStopRestrictions("route_2", _, _, _, _, driver2))
      .Times(3)
      .WillRepeatedly(Return(empty_restrictions));

  FilterByStopRestrictions filter(info::kFilterByStopRestrictions,
                                  routes_cache_ptr, experiments3);

  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {
          {kTripId1, {}}, {kTripId2, {}}, {kTripId3, {}},
          {kTripId4, {}}, {kTripId5, {}}, {kTripId6, {}},
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

TEST(FilterByStopRestrictions, WithRestrictions) {
  auto [search_query, search_result, routes_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto routes_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(routes_cache));

  const auto& experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();

  const auto& restrictions_json = R"(
    {
      "route_1": {
        "pickup_allowed_stops" : ["stop_1"],
        "dropoff_allowed_stops" : ["stop_3"]
      },
      "route_2": {
        "pickup_prohibited_stops" : ["stop_2"],
        "dropoff_prohibited_stops" : ["stop_2"]
      }
    }
  )";

  const auto restrictions =
      ::formats::json::FromString(restrictions_json)
          .As<experiments3::shuttle_control_stop_restrictions::Value>();
  EXPECT_CALL(*experiments3, GetStopRestrictions)
      .Times(6)
      .WillRepeatedly(Return(restrictions));

  FilterByStopRestrictions filter(info::kFilterByStopRestrictions,
                                  routes_cache_ptr, experiments3);

  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {
          {kTripId1, {{kOpName, kDropoffStopNotAllowed}}},
          {kTripId2, {}},
          {kTripId3, {{kOpName, kPickupStopNotAllowed}}},
          {kTripId4, {{kOpName, kDropoffStopProhibited}}},
          {kTripId5, {}},
          {kTripId6, {{kOpName, kPickupStopProhibited}}},
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          ASSERT_FALSE(it == expected_skip_reasons.end());
          expected_skip_reasons.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_skip_reasons.empty());
}

}  // namespace shuttle_control::trip_planner::operations::filter
