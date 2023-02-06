#include "shuttle_info.hpp"

#include <gtest/gtest.h>

#include <boost/lexical_cast.hpp>

namespace shuttle_control::tests::helpers::interlayers {

TEST(ShuttleInfo, ParseFull) {
  const auto& shuttle_info_json = R"(
    {
      "bookings": [
        {
          "booked_segment": {
            "booking_id": "427a330d-2506-464a-accf-346b31e288b8",
            "dropoff_lap": 1,
            "dropoff_stop_id": 3,
            "pickup_lap": 1,
            "pickup_stop_id": 1
          },
          "booking_id": "427a330d-2506-464a-accf-346b31e288b8",
          "dropoff_timestamp": "2020-01-19T20:50:38+0000",
          "pickup_timestamp": "2020-01-19T20:50:38+0000",
          "status": "created",
          "created_at": "2020-01-19T20:50:38+0000",
          "picked_up_at": "2020-01-19T20:50:38+0000"
        }
      ],
      "direction": 12,
      "next_stop_info": {
        "lap": 1,
        "stop_id": 1
      },
      "shift_route_to": 10,
      "shuttle_desc": {
        "capacity": 16,
        "driver_id": {
          "driver_profile_id": "driver_profile_id",
          "park_id": "park_id"
        },
        "drw_state": "active",
        "ended_at": "2020-01-19T20:50:38+0000",
        "revision": 16,
        "route_id": 16,
        "shift_subscription_id": 16,
        "shuttle_id": 16,
        "started_at": "2020-01-19T20:50:38+0000",
        "ticket_check_enabled": false,
        "use_external_confirmation_code": false,
        "ticket_length": 4,
        "vfh_id": "vfh_id",
        "view_id": 16,
        "work_mode": "shuttle",
        "workshift_id": "427a330d-2506-464a-accf-346b31e288b8",
        "remaining_pauses": 0,
        "pause_state": "inactive"
      },
      "stateful_position": {
        "route_position": {
          "cur_point_segment": {
            "end": {
              "id": 11,
              "idx": 11
            },
            "is_start_on_point": true,
            "start": {
              "id": 10,
              "idx": 10
            }
          },
          "cur_stop_segment": {
            "end": {
              "id": 1,
              "idx": 11
            },
            "is_start_on_point": false
          },
          "position": [
            33.3333,
            55.5555
          ]
        },
        "state": {
          "advanced_at": "2020-01-19T20:50:38+0000",
          "average_speed": 35,
          "begin_stop_id": 1,
          "block_reason": "None",
          "current_lap": 1,
          "next_stop_id": 1,
          "processed_at": "2020-01-19T20:50:38+0000",
          "updated_at": "2020-01-19T20:50:38+0000"
        }
      }
    }
  )";

  const auto& actual_shuttle_info =
      ::formats::json::FromString(shuttle_info_json).As<ShuttleInfo>();

  const ShuttleInfo expected_shuttle_info{
      shuttle_control::models::ShuttleDescriptor{
          ::models::DbidUuid{"park_id", "driver_profile_id"},
          shuttle_control::models::ShuttleIdT{16},
          shuttle_control::models::RouteIdT{16},
          16,
          16,
          shuttle_control::models::DRWState::Active,
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
          4,
          false,
          false,
          shuttle_control::models::WorkModeType::kShuttle,
          boost::lexical_cast<boost::uuids::uuid>(
              "427a330d-2506-464a-accf-346b31e288b8"),
          16,
          shuttle_control::models::RouteViewIdT{16},
          "vfh_id",
          0,
          shuttle_control::models::PauseState::kInactive,
          std::nullopt,
      },
      models::StopIdT{10},
      shuttle_control::models::ShuttleStatefulPosition{
          shuttle_control::models::ShuttleEnRoutePosition{
              shuttle_control::models::RouteIndexSegment<
                  shuttle_control::models::PointIdT>{
                  {{10, shuttle_control::models::PointIdT{10}}},
                  {11, shuttle_control::models::PointIdT{11}},
                  true,
              },
              shuttle_control::models::RouteIndexSegment<
                  shuttle_control::models::StopIdT>{
                  std::nullopt,
                  {11, shuttle_control::models::StopIdT{1}},
                  false,
              },
              ::geometry::Position{::geometry::Latitude{33.3333},
                                   ::geometry::Longitude{55.5555}},
          },
          shuttle_control::models::ShuttleTripState{
              shuttle_control::models::ShuttleLapT{1},
              shuttle_control::models::StopIdT{1},
              shuttle_control::models::StopIdT{1},
              std::nullopt,  // end_lap
              std::nullopt,  // end_stop_id
              ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
                  .As<std::chrono::system_clock::time_point>(),
              shuttle_control::models::KmHSpeed::from_value(35),
              ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
                  .As<std::chrono::system_clock::time_point>(),
              shuttle_control::models::DriverBlockReason::kNone,
              ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
                  .As<std::chrono::system_clock::time_point>(),
          },
      },
      ::geometry::Azimuth::from_value(12),
      shuttle_control::models::ShuttleStopInfo{
          shuttle_control::models::StopIdT{1},
          shuttle_control::models::StopLapT{1},
      },
      {shuttle_control::models::ShortBookingInfo{
          boost::lexical_cast<boost::uuids::uuid>(
              "427a330d-2506-464a-accf-346b31e288b8"),
          shuttle_control::models::BookingStatus::kCreated,
          shuttle_control::models::BookedSeatSegment{
              boost::lexical_cast<boost::uuids::uuid>(
                  "427a330d-2506-464a-accf-346b31e288b8"),
              shuttle_control::models::StopIdT{1},
              shuttle_control::models::StopIdT{3},
              shuttle_control::models::StopLapT{1},
              shuttle_control::models::StopLapT{1},
          },
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
      }},
  };

  EXPECT_EQ(expected_shuttle_info, actual_shuttle_info);
}

TEST(ShuttleInfo, ParseDefaults) {
  const auto& shuttle_info_json = R"(
    {
      "shuttle_desc": {
        "capacity": 16,
        "driver_id": {
          "driver_profile_id": "driver_profile_id",
          "park_id": "park_id"
        },
        "route_id": 16,
        "shuttle_id": 16,
        "remaining_pauses": 0,
        "pause_state": "inactive"
      }
    }
  )";

  const auto& actual_shuttle_info =
      ::formats::json::FromString(shuttle_info_json).As<ShuttleInfo>();

  const ShuttleInfo expected_shuttle_info{
      shuttle_control::models::ShuttleDescriptor{
          ::models::DbidUuid{"park_id", "driver_profile_id"},
          shuttle_control::models::ShuttleIdT{16},
          shuttle_control::models::RouteIdT{16},
          16,
          1,
          shuttle_control::models::DRWState::Disabled,
          std::nullopt,
          std::nullopt,
          4,
          false,
          false,
          shuttle_control::models::WorkModeType::kShuttle,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          0,
          shuttle_control::models::PauseState::kInactive,
          std::nullopt,
      },
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      {},
  };

  EXPECT_EQ(expected_shuttle_info, actual_shuttle_info);
}

}  // namespace shuttle_control::tests::helpers::interlayers
