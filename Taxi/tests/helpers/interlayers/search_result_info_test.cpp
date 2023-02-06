#include "search_result_info.hpp"

#include <gtest/gtest.h>

#include <boost/lexical_cast.hpp>

namespace shuttle_control::tests::helpers::interlayers {

TEST(SearchResultInfo, ParseFull) {
  const auto& result_info_json = R"(
    {
      "car_ab_info": {
        "distance": 60.0,
        "time": 10,
        "timestamp": "2020-01-19T20:50:38+0000"
      },
      "walk_ab_info": {
        "distance": 60.0,
        "time": 10,
        "timestamp": "2020-01-19T20:50:38+0000"
      },
      "routes": [
        {
          "route_id": 16,
          "segments": [
            {
              "from_dropoff": {
                "distance": 60.0,
                "time": 10,
                "timestamp": "2020-01-19T20:50:38+0000"
              },
              "to_pickup": {
                "distance": 60.0,
                "time": 10,
                "timestamp": "2020-01-19T20:50:38+0000"
              },
              "segment_id": {
                "begin": 1,
                "end": 3
              },
              "shuttles": [
                {
                  "shuttle_id": 16,
                  "trips": [
                    {
                      "trip_id": "427a330d-2506-464a-accf-346b31e288b2",
                      "pickup_stop_info": {
                        "stop_id": 100,
                        "lap": 1
                      },
                      "dropoff_stop_info": {
                        "stop_id": 1,
                        "lap": 2
                      },
                      "trip_route_id": 100,
                      "next_trip_stop_info": {
                        "stop_id": 50,
                        "lap": 1
                      },
                      "shuttle_load": {
                        "seats_available": 16,
                        "seats_taken": 8
                      },
                      "eta_at_pickup": {
                        "distance": 300.0,
                        "time": 30,
                        "timestamp": "2022-01-01T20:00:00+0000"
                      },
                      "route_info": {
                        "distance": 1500.0,
                        "time": 120,
                        "timestamp": "2022-01-01T20:02:30+0000"
                      },
                      "per_seat_price" : {
                        "amount": "1000",
                        "currency": "TGR"
                      },
                      "total_price" : {
                        "amount": "2000",
                        "currency": "TGR"
                      },
                      "score": 100500,
                      "skip_reasons": {
                        "reason": "personally_dont_like_it",
                        "elaborate": {
                          "why": "because"
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  )";
  const auto& actual_result_info =
      ::formats::json::FromString(result_info_json).As<SearchResultInfo>();

  const auto& elaborate_reason_json = R"(
    {
      "why": "because"
    }
  )";

  trip_planner::operations::TripLevelResult expected_trip{
      boost::lexical_cast<boost::uuids::uuid>(
          "427a330d-2506-464a-accf-346b31e288b2"),
      {models::StopIdT{100}, models::StopLapT{1}},
      {models::StopIdT{1}, models::StopLapT{2}},
      std::nullopt,
      {{models::StopIdT{50}, models::StopLapT{1}}},
      {16, 8},
      {{std::chrono::seconds(30), 300.0,
        ::formats::json::FromString("\"2022-01-01T20:00:00+0000\"")
            .As<std::chrono::system_clock::time_point>()}},
      {{std::chrono::seconds(120), 1500.0,
        ::formats::json::FromString("\"2022-01-01T20:02:30+0000\"")
            .As<std::chrono::system_clock::time_point>()}},
      {{models::MoneyType{1000}, "TGR"}},
      {{models::MoneyType{2000}, "TGR"}},
      {100500},
      {{"reason", ::formats::json::ValueBuilder{"personally_dont_like_it"}
                      .ExtractValue()},
       {"elaborate", ::formats::json::FromString(elaborate_reason_json)}},
  };

  TripLevelResultInfo expected_trip_result{
      expected_trip.trip_id,
      expected_trip,
      models::RouteIdT{100},
  };

  ShuttleLevelResultInfo expected_shuttle_info{
      shuttle_control::models::ShuttleIdT{16},
      {{expected_trip.trip_id, expected_trip_result}},
  };
  SegmentLevelResultInfo expected_segment_info{
      shuttle_control::models::SegmentIdT{shuttle_control::models::StopIdT{1},
                                          shuttle_control::models::StopIdT{3}},
      models::RouteInfo{
          std::chrono::seconds{10},
          60.0,
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
      },
      models::RouteInfo{
          std::chrono::seconds{10},
          60.0,
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
      },
      {{expected_shuttle_info.shuttle_id, expected_shuttle_info}},
  };
  RouteLevelResultInfo expected_route_info{
      shuttle_control::models::RouteIdT{16},
      {{expected_segment_info.segment_id, expected_segment_info}},
  };
  const SearchResultInfo expected_result_info{
      models::RouteInfo{
          std::chrono::seconds{10},
          60.0,
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
      },
      models::RouteInfo{
          std::chrono::seconds{10},
          60.0,
          ::formats::json::FromString("\"2020-01-19T20:50:38+0000\"")
              .As<std::chrono::system_clock::time_point>(),
      },
      std::nullopt,
      {{expected_route_info.route_id, expected_route_info}},
  };

  EXPECT_EQ(expected_result_info, actual_result_info);
}

}  // namespace shuttle_control::tests::helpers::interlayers
