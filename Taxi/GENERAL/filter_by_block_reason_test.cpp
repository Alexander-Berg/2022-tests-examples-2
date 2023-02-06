#include "filter_by_block_reason.hpp"

#include <gtest/gtest.h>
#include <boost/lexical_cast.hpp>

#include <testing/source_path.hpp>

#include <internal/tests/experiments3_adapter_mock.hpp>
#include <tests/helpers/trip_planner_operations_test_helper.hpp>

#include <trip-planner/operations/filter/filter_by_block_reason_info.hpp>

namespace {

using ::testing::_;
using ::testing::Return;

const auto kMainFilePath = ::utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_block_reason/static_test/"
    "main.json");

const auto kOutOfWorkshift =
    ::formats::json::ValueBuilder{"out_of_workshift"}.ExtractValue();
const auto kImmobility =
    ::formats::json::ValueBuilder{"immobility"}.ExtractValue();

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByBlockReason, OutOfWorkshiftConfigDisabled) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  const auto workshift_id = boost::lexical_cast<boost::uuids::uuid>(
      "427a330d-2506-464a-accf-346b31e288c1");
  auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(
      workshift_id,
      models::Workshift{
          .workshift_id = workshift_id,
          .template_id = workshift_id,
          .route_name = "route_1",
          .work_time = {.start = now + std::chrono::seconds(500),
                        .end = now + std::chrono::seconds(1000)}});

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto false_match = experiments3::ShuttleMatchInWorkshift::Value{false};
  EXPECT_CALL(*experiments3, GetMatchInWorkshift("route_1", _, _))
      .WillOnce(Return(false_match));

  FilterByBlockReason filter(info::kFilterByBlockReason, route_cache_ptr,
                             experiments3, workshifts_cache);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {{boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b1"),
                                {}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b2"),
                                {{"filter_by_block_reason", kOutOfWorkshift}}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b3"),
                                {{"filter_by_block_reason", kImmobility}}}};

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

TEST(FilterByBlockReason, TestBeforeWorkshift) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  const auto workshift_id = boost::lexical_cast<boost::uuids::uuid>(
      "427a330d-2506-464a-accf-346b31e288c1");
  auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(
      workshift_id,
      models::Workshift{
          .workshift_id = workshift_id,
          .template_id = workshift_id,
          .route_name = "route_1",
          .work_time = {.start = now + std::chrono::seconds(500),
                        .end = now + std::chrono::seconds(1000)}});

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto true_match = experiments3::ShuttleMatchInWorkshift::Value{true};
  EXPECT_CALL(*experiments3, GetMatchInWorkshift("route_1", _, _))
      .WillOnce(Return(true_match));

  FilterByBlockReason filter(info::kFilterByBlockReason, route_cache_ptr,
                             experiments3, workshifts_cache);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {{boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b1"),
                                {}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b2"),
                                {}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b3"),
                                {{"filter_by_block_reason", kImmobility}}}};

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

TEST(FilterByBlockReason, TestAfterWorkshift) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  const auto workshift_id = boost::lexical_cast<boost::uuids::uuid>(
      "427a330d-2506-464a-accf-346b31e288c1");
  auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(
      workshift_id,
      models::Workshift{.workshift_id = workshift_id,
                        .template_id = workshift_id,
                        .route_name = "route_1",
                        .work_time = {.start = now - std::chrono::seconds(1000),
                                      .end = now - std::chrono::seconds(500)}});

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto true_match = experiments3::ShuttleMatchInWorkshift::Value{true};
  EXPECT_CALL(*experiments3, GetMatchInWorkshift("route_1", _, _))
      .WillOnce(Return(true_match));

  FilterByBlockReason filter(info::kFilterByBlockReason, route_cache_ptr,
                             experiments3, workshifts_cache);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons = {{boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b1"),
                                {}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b2"),
                                {{"filter_by_block_reason", kOutOfWorkshift}}},
                               {boost::lexical_cast<boost::uuids::uuid>(
                                    "427a330d-2506-464a-accf-346b31e288b3"),
                                {{"filter_by_block_reason", kImmobility}}}};

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
