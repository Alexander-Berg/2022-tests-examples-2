#include "calc_pickup_eta.hpp"

#include <gmock/gmock.h>

#include <boost/lexical_cast.hpp>

#include <userver/utest/utest.hpp>

#include <clients/routing/test/router_mock.hpp>
#include <clients/routing/test/test_router_selector.hpp>
#include <internal/tests/experiments3_adapter_mock.hpp>
#include <testing/source_path.hpp>
#include <testing/taxi_config_arcadia.hpp>
#include <tests/helpers/trip_planner_operations_test_helper.hpp>
#include <trip-planner/operations/routing/calc_pickup_eta_info.hpp>

namespace {

using ::testing::_;
using ::testing::ElementsAre;
using ::testing::Return;
using namespace std::chrono_literals;

using ToStopsMap = std::unordered_map<shuttle_control::models::StopIdT,
                                      shuttle_control::models::ShortRouteInfo>;

const auto kFixedRouteFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/routing/calc_pickup_eta/static_test/"
    "main.json");

const auto kDynamicRouteFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/routing/calc_pickup_eta/static_test/"
    "dynamic.json");

}  // namespace

namespace shuttle_control::trip_planner::operations::routing {

UTEST(CalcPickupEta, GenericScenario) {
  const auto params_json = R"(
    {
      "max_bulk_size": 1,
      "max_parallel_requests": 1
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kFixedRouteFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto stop_1 = route_cache_ptr->points.at(models::PointIdT(2)).position;
  const auto stop_2 = route_cache_ptr->points.at(models::PointIdT(4)).position;
  const auto stop_3 = route_cache_ptr->points.at(models::PointIdT(6)).position;

  auto mock_router = std::make_shared<::clients::routing::RouterMock>(
      ::clients::routing::RouterVehicleType::kVehicleCar, "linear-fallback");
  mock_router->EnableDefaults();
  EXPECT_CALL(*mock_router, FetchRouteInfo).Times(0);
  EXPECT_CALL(*mock_router, FetchRouteInfo(ElementsAre(_, stop_1), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(300, 5000))));
  EXPECT_CALL(*mock_router,
              FetchRouteInfo(ElementsAre(_, stop_1, stop_2), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(500, 7000))));
  EXPECT_CALL(*mock_router, FetchRouteInfo(ElementsAre(_, stop_2), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(200, 5000))));
  EXPECT_CALL(*mock_router,
              FetchRouteInfo(ElementsAre(_, stop_2, stop_3, stop_1), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(600, 10000))));

  const auto default_storage = ::dynamic_config::MakeDefaultStorage({});
  ::clients::routing::TestRouterSelector router_selector(
      default_storage.GetSource(), nullptr);
  router_selector.AddRouter(mock_router);

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto false_match = experiments3::ShuttleMatchInWorkshift::Value{false};
  EXPECT_CALL(*experiments3, GetMatchInWorkshift)
      .Times(2)
      .WillRepeatedly(Return(false_match));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  CalcPickupEtaOperationParams>();

  CalcPickupEta calc(info::kCalcPickupEta, params, route_cache_ptr,
                     shuttle_eta_to_stops_cache, stops_mutual_cache,
                     experiments3, workshifts_cache, router_selector);

  const auto before_calc = utils::datetime::Now();

  auto result = calc.Process(search_query, search_result);

  auto it = result.find(info::outputs::kTripPickupEta);
  ASSERT_FALSE(it == result.end());
  ASSERT_TRUE(it->second);

  auto result_satus = it->second->get();
  ASSERT_EQ(result_satus, OutputExportStatus::kSuccess);

  std::unordered_map<boost::uuids::uuid, models::RouteInfo,
                     boost::hash<boost::uuids::uuid>>
      expected_etas = {{boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b1"),
                        {std::chrono::seconds(300), 5000,
                         before_calc + std::chrono::seconds(300)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b2"),
                        {std::chrono::seconds(500), 7000,
                         before_calc + std::chrono::seconds(500)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b3"),
                        {std::chrono::seconds(600), 10000,
                         before_calc + std::chrono::seconds(600)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b4"),
                        {std::chrono::seconds(200), 5000,
                         before_calc + std::chrono::seconds(200)}}};

  const auto after_calc = utils::datetime::Now();
  const auto delta_calc =
      std::chrono::ceil<std::chrono::seconds>(after_calc - before_calc);

  for (const auto& [route_id, route_level] : search_result.routes) {
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      for (const auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (const auto& [trip_id, trip_level] : shuttle_level.trips) {
          auto it = expected_etas.find(trip_id);
          ASSERT_FALSE(it == expected_etas.end());
          ASSERT_TRUE(trip_level.eta_at_pickup.has_value());
          const auto& trip_eta = *trip_level.eta_at_pickup;
          EXPECT_GE(trip_eta.timestamp, it->second.timestamp)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.timestamp, it->second.timestamp + delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          it->second.timestamp = trip_eta.timestamp;
          EXPECT_EQ(trip_eta, it->second);
          expected_etas.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_etas.empty());
}

UTEST(CalcPickupEta, BeforeWorkshiftStart) {
  const auto params_json = R"(
    {
      "max_bulk_size": 1,
      "max_parallel_requests": 1
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kFixedRouteFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto stop_1 = route_cache_ptr->points.at(models::PointIdT(2)).position;
  const auto stop_2 = route_cache_ptr->points.at(models::PointIdT(4)).position;
  const auto stop_3 = route_cache_ptr->points.at(models::PointIdT(6)).position;

  auto mock_router = std::make_shared<::clients::routing::RouterMock>(
      ::clients::routing::RouterVehicleType::kVehicleCar, "linear-fallback");
  mock_router->EnableDefaults();
  EXPECT_CALL(*mock_router, FetchRouteInfo).Times(0);
  EXPECT_CALL(*mock_router, FetchRouteInfo(ElementsAre(_, stop_2), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(200, 5000))));
  EXPECT_CALL(*mock_router,
              FetchRouteInfo(ElementsAre(_, stop_2, stop_3, stop_1), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(600, 10000))));
  EXPECT_CALL(*mock_router,
              FetchRouteInfo(ElementsAre(stop_1, stop_2), _, _, _))
      .WillOnce(Return(::clients::routing::RouterResponse(
          ::clients::routing::RouteInfo(200, 2000))));

  const auto default_storage = ::dynamic_config::MakeDefaultStorage({});
  ::clients::routing::TestRouterSelector router_selector(
      default_storage.GetSource(), nullptr);
  router_selector.AddRouter(mock_router);

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  const auto before_calc = utils::datetime::Now();
  workshifts_cache->emplace(
      boost::lexical_cast<boost::uuids::uuid>(
          "427a330d-2506-464a-accf-346b31e288c1"),
      models::Workshift{
          .workshift_id = boost::lexical_cast<boost::uuids::uuid>(
              "427a330d-2506-464a-accf-346b31e288c1"),
          .template_id = boost::lexical_cast<boost::uuids::uuid>(
              "427a330d-2506-464a-accf-346b31e288c1"),
          .route_name = "route_1",
          .work_time = {.start = before_calc + std::chrono::seconds(500)}});

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto false_match = experiments3::ShuttleMatchInWorkshift::Value{false};
  const auto true_match = experiments3::ShuttleMatchInWorkshift::Value{true};
  EXPECT_CALL(*experiments3, GetMatchInWorkshift("route_1", _, _))
      .WillOnce(Return(true_match));
  EXPECT_CALL(*experiments3, GetMatchInWorkshift("route_2", _, _))
      .WillOnce(Return(false_match));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  CalcPickupEtaOperationParams>();

  CalcPickupEta calc(info::kCalcPickupEta, params, route_cache_ptr,
                     shuttle_eta_to_stops_cache, stops_mutual_cache,
                     experiments3, workshifts_cache, router_selector);

  auto result = calc.Process(search_query, search_result);

  auto it = result.find(info::outputs::kTripPickupEta);
  ASSERT_FALSE(it == result.end());
  ASSERT_TRUE(it->second);

  auto result_satus = it->second->get();
  ASSERT_EQ(result_satus, OutputExportStatus::kSuccess);

  std::unordered_map<boost::uuids::uuid, models::RouteInfo,
                     boost::hash<boost::uuids::uuid>>
      expected_etas = {{boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b3"),
                        {std::chrono::seconds(600), 10000,
                         before_calc + std::chrono::seconds(600)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b4"),
                        {std::chrono::seconds(200), 5000,
                         before_calc + std::chrono::seconds(200)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b1"),
                        {std::chrono::seconds(500), 0,
                         before_calc + std::chrono::seconds(500)}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b2"),
                        {std::chrono::seconds(700), 2000,
                         before_calc + std::chrono::seconds(700)}}};

  const auto after_calc = utils::datetime::Now();
  const auto delta_calc =
      std::chrono::ceil<std::chrono::seconds>(after_calc - before_calc);

  for (const auto& [route_id, route_level] : search_result.routes) {
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      for (const auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (const auto& [trip_id, trip_level] : shuttle_level.trips) {
          ASSERT_TRUE(trip_level.eta_at_pickup.has_value());
          const auto& trip_eta = *trip_level.eta_at_pickup;
          const auto it = expected_etas.find(trip_id);
          ASSERT_FALSE(it == expected_etas.end());
          EXPECT_EQ(trip_eta.distance, it->second.distance);
          EXPECT_GE(trip_eta.time, it->second.time - delta_calc)
              << "Result time out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.time, it->second.time)
              << "Result time out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_GE(trip_eta.timestamp, it->second.timestamp - delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.timestamp, it->second.timestamp + delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          expected_etas.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_etas.empty());
}

UTEST(CalcPickupEta, DynamicGenericScenario) {
  const auto params_json = R"(
    {
      "max_bulk_size": 1,
      "max_parallel_requests": 1
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kDynamicRouteFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  auto mock_router = std::make_shared<::clients::routing::RouterMock>(
      ::clients::routing::RouterVehicleType::kVehicleCar, "linear-fallback");
  mock_router->EnableDefaults();
  EXPECT_CALL(*mock_router, FetchRouteInfo).Times(0);

  const auto default_storage = ::dynamic_config::MakeDefaultStorage({});
  ::clients::routing::TestRouterSelector router_selector(
      default_storage.GetSource(), nullptr);
  router_selector.AddRouter(mock_router);

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{100s, 1000}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{100s, 1000}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  const auto workshift_config =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto false_match = experiments3::ShuttleMatchInWorkshift::Value{false};
  EXPECT_CALL(*workshift_config, GetMatchInWorkshift)
      .Times(1)
      .WillRepeatedly(Return(false_match));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  CalcPickupEtaOperationParams>();

  CalcPickupEta calc(info::kCalcPickupEta, params, route_cache_ptr,
                     shuttle_eta_to_stops_cache, stops_mutual_cache,
                     workshift_config, workshifts_cache, router_selector);

  const auto before_calc = utils::datetime::Now();

  auto result = calc.Process(search_query, search_result);

  auto it = result.find(info::outputs::kTripPickupEta);
  ASSERT_FALSE(it == result.end());
  ASSERT_TRUE(it->second);

  auto result_satus = it->second->get();
  ASSERT_EQ(result_satus, OutputExportStatus::kSuccess);

  std::unordered_map<boost::uuids::uuid, models::RouteInfo,
                     boost::hash<boost::uuids::uuid>>
      expected_etas = {{boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b1"),
                        {100s, 1000, before_calc + 100s}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b2"),
                        {200s, 2000, before_calc + 200s}}};

  const auto after_calc = utils::datetime::Now();
  const auto delta_calc =
      std::chrono::ceil<std::chrono::seconds>(after_calc - before_calc);

  for (const auto& [route_id, route_level] : search_result.routes) {
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      for (const auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (const auto& [trip_id, trip_level] : shuttle_level.trips) {
          auto it = expected_etas.find(trip_id);
          ASSERT_FALSE(it == expected_etas.end());
          ASSERT_TRUE(trip_level.eta_at_pickup.has_value());
          const auto& trip_eta = *trip_level.eta_at_pickup;
          EXPECT_GE(trip_eta.timestamp, it->second.timestamp)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.timestamp, it->second.timestamp + delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          it->second.timestamp = trip_eta.timestamp;
          EXPECT_EQ(trip_eta, it->second);
          expected_etas.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_etas.empty());
}

UTEST(CalcPickupEta, DynamicBeforeWorkhiftStart) {
  const auto params_json = R"(
    {
      "max_bulk_size": 1,
      "max_parallel_requests": 1
    }
  )";

  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kDynamicRouteFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  auto mock_router = std::make_shared<::clients::routing::RouterMock>(
      ::clients::routing::RouterVehicleType::kVehicleCar, "linear-fallback");
  mock_router->EnableDefaults();
  EXPECT_CALL(*mock_router, FetchRouteInfo).Times(0);

  const auto default_storage = ::dynamic_config::MakeDefaultStorage({});
  ::clients::routing::TestRouterSelector router_selector(
      default_storage.GetSource(), nullptr);
  router_selector.AddRouter(mock_router);

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{100s, 1000}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{100s, 1000}}});

  const auto before_calc = utils::datetime::Now();

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(
      boost::lexical_cast<boost::uuids::uuid>(
          "427a330d-2506-464a-accf-346b31e288c1"),
      models::Workshift{.workshift_id = boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288c1"),
                        .template_id = boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288c1"),
                        .route_name = "route_1",
                        .work_time = {.start = before_calc + 500s}});

  const auto workshift_config =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto true_match = experiments3::ShuttleMatchInWorkshift::Value{true};
  EXPECT_CALL(*workshift_config, GetMatchInWorkshift)
      .Times(1)
      .WillRepeatedly(Return(true_match));

  const auto params =
      ::formats::json::FromString(params_json)
          .As<::experiments3::shuttle_v1_trip_planner_search_settings::
                  CalcPickupEtaOperationParams>();

  CalcPickupEta calc(info::kCalcPickupEta, params, route_cache_ptr,
                     shuttle_eta_to_stops_cache, stops_mutual_cache,
                     workshift_config, workshifts_cache, router_selector);

  auto result = calc.Process(search_query, search_result);

  auto it = result.find(info::outputs::kTripPickupEta);
  ASSERT_FALSE(it == result.end());
  ASSERT_TRUE(it->second);

  auto result_satus = it->second->get();
  ASSERT_EQ(result_satus, OutputExportStatus::kSuccess);

  std::unordered_map<boost::uuids::uuid, models::RouteInfo,
                     boost::hash<boost::uuids::uuid>>
      expected_etas = {{boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b1"),
                        {500s, 1000, before_calc + 500s}},
                       {boost::lexical_cast<boost::uuids::uuid>(
                            "427a330d-2506-464a-accf-346b31e288b2"),
                        {600s, 2000, before_calc + 600s}}};

  const auto after_calc = utils::datetime::Now();
  const auto delta_calc =
      std::chrono::ceil<std::chrono::seconds>(after_calc - before_calc);

  for (const auto& [route_id, route_level] : search_result.routes) {
    for (const auto& [segment_id, segment_level] : route_level.segments) {
      for (const auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (const auto& [trip_id, trip_level] : shuttle_level.trips) {
          ASSERT_TRUE(trip_level.eta_at_pickup.has_value());
          const auto& trip_eta = *trip_level.eta_at_pickup;
          const auto it = expected_etas.find(trip_id);
          ASSERT_FALSE(it == expected_etas.end());
          EXPECT_EQ(trip_eta.distance, it->second.distance);
          EXPECT_GE(trip_eta.time, it->second.time - delta_calc)
              << "Result time out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.time, it->second.time)
              << "Result time out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_GE(trip_eta.timestamp, it->second.timestamp - delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          EXPECT_LE(trip_eta.timestamp, it->second.timestamp + delta_calc)
              << "Result timestemp out of expected range for trip "
              << boost::uuids::to_string(trip_id);
          expected_etas.erase(it);
        }
      }
    }
  }
  EXPECT_TRUE(expected_etas.empty());
}

}  // namespace shuttle_control::trip_planner::operations::routing
