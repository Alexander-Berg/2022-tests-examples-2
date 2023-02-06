#include "trip_planner_operations_test_helper.hpp"

#include <gtest/gtest.h>

#include <boost/lexical_cast.hpp>

namespace shuttle_control::tests::helpers {

TEST(TripPlannerOperationsTestHelper, Parse) {
  const auto& helper_json = R"(
    {
      "definitions": {
        "routes": [
          {
            "meta": {
              "id": 1,
              "name": "route_1"
            },
            "points": [
              {
                "point_id": 1,
                "position": [33.33, 55.55],
                "stop_id": 1,
                "name": "stop_1"
              },
              {
                "point_id": 2,
                "position": [33.33, 55.55],
                "stop_id": 2,
                "name": "stop_2"
              }
            ]
          },
          {
            "meta": {
              "id": 2,
              "name": "dynamic_route",
              "is_dynamic": true
            },
            "points": [
              {
                "point_id": 3,
                "position": [33.33, 55.55],
                "stop_id": 3,
                "name": "dynamic_stop_3"
              },
              {
                "point_id": 4,
                "position": [33.33, 55.55],
                "stop_id": 4,
                "name": "dynamic_stop_4"
              }
            ]
          }
        ],
        "shuttles": [
          {
            "shift_route_to": 2,
            "shuttle_desc": {
              "driver_id": {
                "driver_profile_id": "driver_profile_id",
                "park_id": "park_id"
              },
              "drw_state": "active",
              "route_id": 1,
              "shuttle_id": 16,
              "remaining_pauses": 0,
              "pause_state": "inactive",
              "use_external_confirmation_code": true
            }
          },
          {
            "shuttle_desc": {
              "driver_id": {
                "driver_profile_id": "driver_profile_id",
                "park_id": "park_id"
              },
              "drw_state": "active",
              "route_id": 2,
              "shuttle_id": 20,
              "remaining_pauses": 0,
              "pause_state": "inactive"
            }
          }
        ]
      },
      "query": {
        "from": [
          33.3333,
          55.5555
        ],
        "origin_service_id": "origin_service_id",
        "external_confirmation_code": "111111",
        "external_passenger_id": "12345678",
        "passengers_count": 2,
        "payment_method_id": "payment_method_id",
        "payment_type": "cash",
        "tariff_zone": "UTC",
        "to": [
          33.5555,
          55.3333
        ],
        "yandex_uid": "yandex_uid",
        "phone_id": "88005553535"
      },
      "result": {
        "routes": [
          {
            "route_id": 1,
            "segments": [
              {
                "segment_id": {
                  "begin": 1,
                  "end": 3
                },
                "shuttles": [
                  {
                    "shuttle_id": 16
                  }
                ]
              }
            ]
          },
          {
            "route_id": 2,
            "segments": [
              {
                "segment_id": {
                  "begin": 1,
                  "end": 2
                },
                "shuttles": [
                  {
                    "shuttle_id": 20,
                    "trips": [
                      {
                        "dropoff_stop_info": {
                          "lap": 1,
                          "stop_id": 2
                        },
                        "pickup_stop_info": {
                          "lap": 1,
                          "stop_id": 1
                        },
                        "shuttle_load": {
                          "seats_available": 16,
                          "seats_taken": 0
                        },
                        "trip_route_id": 2,
                        "trip_id": "427a330d-2506-464a-accf-346b31e288b1"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    }
  )";
  const auto& [actual_query, actual_result, actual_cache] =
      TripPlannerOpearationTestHelper::Build(
          ::formats::json::FromString(helper_json));

  const auto expected_query = trip_planner::operations::SearchQuery{
      "unittests",
      "1.1.1",
      ::geometry::Position{::geometry::Latitude{33.3333},
                           ::geometry::Longitude{55.5555}},
      ::geometry::Position{::geometry::Latitude{33.5555},
                           ::geometry::Longitude{55.3333}},
      "UTC",
      2,
      ::handlers::PaymentType::kCash,
      "payment_method_id",
      "yandex_uid",
      "origin_service_id",
      "111111",
      "12345678",
      "88005553535",
  };

  models::Route expected_route{
      models::Route::Meta{
          models::RouteIdT{1},
          "route_1",
          false,
          false,
          false,
          1,
      },
  };
  expected_route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{1},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{1},
      "stop_1",
      false,
      {}});
  expected_route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{2},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{2},
      "stop_2",
      false,
      {}});
  expected_route.ShiftToStop(models::StopIdT{2});
  const trip_planner::operations::ShuttleLevelResult expected_shuttle_result{
      models::ShuttleIdT{16},
      models::ShuttleDescriptor{
          ::models::DbidUuid{"park_id", "driver_profile_id"},
          models::ShuttleIdT{16},
          models::RouteIdT{1},
          16,
          1,
          models::DRWState::Active,
          std::nullopt,
          std::nullopt,
          4,
          false,
          true,
          models::WorkModeType::kShuttle,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          0,
          shuttle_control::models::PauseState::kInactive,
          std::nullopt,
      },
      std::move(expected_route),
      std::nullopt,
      std::nullopt,
      std::nullopt,
      {},
      {},
  };
  const trip_planner::operations::SegmentLevelResult expected_segment_result{
      models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}},
      std::nullopt,
      std::nullopt,
      {{expected_shuttle_result.shuttle_id, expected_shuttle_result}},
  };
  const trip_planner::operations::RouteLevelResult expected_route_result{
      models::RouteIdT{1},
      {{expected_segment_result.segment_id, expected_segment_result}},
  };

  models::Route expected_dynamic_route{
      models::Route::Meta{
          models::RouteIdT{2},
          "dynamic_route",
          false,
          true,
          false,
          1,
      },
  };
  expected_dynamic_route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{3},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{3},
      "dynamic_stop_3",
      false,
      {}});
  expected_dynamic_route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{4},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{4},
      "dynamic_stop_4",
      false,
      {}});
  const trip_planner::operations::TripLevelResult expected_dynamic_trip_result{
      boost::lexical_cast<boost::uuids::uuid>(
          "427a330d-2506-464a-accf-346b31e288b1"),
      {models::StopIdT{1}, models::StopLapT{1}},
      {models::StopIdT{2}, models::StopLapT{1}},
      expected_dynamic_route,
      std::nullopt,
      {16, 0},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      {},
  };
  const trip_planner::operations::ShuttleLevelResult
      expected_dynamic_shuttle_result{
          models::ShuttleIdT{20},
          models::ShuttleDescriptor{
              ::models::DbidUuid{"park_id", "driver_profile_id"},
              models::ShuttleIdT{20},
              models::RouteIdT{2},
              16,
              1,
              models::DRWState::Active,
              std::nullopt,
              std::nullopt,
              4,
              false,
              false,
              models::WorkModeType::kShuttle,
              std::nullopt,
              std::nullopt,
              std::nullopt,
              std::nullopt,
              0,
              shuttle_control::models::PauseState::kInactive,
              std::nullopt,
          },
          std::move(expected_dynamic_route),
          std::nullopt,
          std::nullopt,
          std::nullopt,
          {},
          {{expected_dynamic_trip_result.trip_id,
            expected_dynamic_trip_result}},
      };
  const trip_planner::operations::SegmentLevelResult
      expected_dynamic_segment_result{
          models::SegmentIdT{models::StopIdT{1}, models::StopIdT{2}},
          std::nullopt,
          std::nullopt,
          {{expected_dynamic_shuttle_result.shuttle_id,
            expected_dynamic_shuttle_result}},
      };
  const trip_planner::operations::RouteLevelResult
      expected_dynamic_route_result{
          models::RouteIdT{2},
          {{expected_dynamic_segment_result.segment_id,
            expected_dynamic_segment_result}},
      };

  const trip_planner::operations::SearchResult expected_result{
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      {
          {expected_route_result.route_id, expected_route_result},
          {expected_dynamic_route_result.route_id,
           expected_dynamic_route_result},
      },
  };

  EXPECT_EQ(expected_query, actual_query);
  EXPECT_EQ(expected_result, actual_result);
  EXPECT_EQ(expected_result.routes.at(models::RouteIdT{1}),
            actual_result.routes.at(models::RouteIdT{1}))
      << "route_level";
  EXPECT_EQ(expected_result.routes.at(models::RouteIdT{1})
                .segments.at(
                    models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}}),
            actual_result.routes.at(models::RouteIdT{1})
                .segments.at(
                    models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}}))
      << "segment_level";
  EXPECT_EQ(expected_result.routes.at(models::RouteIdT{1})
                .segments
                .at(models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}})
                .shuttles.at(models::ShuttleIdT{16}),
            actual_result.routes.at(models::RouteIdT{1})
                .segments
                .at(models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}})
                .shuttles.at(models::ShuttleIdT{16}))
      << "shuttle_level";
  EXPECT_EQ(expected_result.routes.at(models::RouteIdT{1})
                .segments
                .at(models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}})
                .shuttles.at(models::ShuttleIdT{16})
                .shifted_route,
            actual_result.routes.at(models::RouteIdT{1})
                .segments
                .at(models::SegmentIdT{models::StopIdT{1}, models::StopIdT{3}})
                .shuttles.at(models::ShuttleIdT{16})
                .shifted_route)
      << "shuttle_level.route";
}

}  // namespace shuttle_control::tests::helpers
