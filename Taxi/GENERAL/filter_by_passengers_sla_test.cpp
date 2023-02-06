#include "filter_by_passengers_sla.hpp"

#include <gtest/gtest.h>
#include <boost/lexical_cast.hpp>

#include <testing/source_path.hpp>

#include <internal/tests/experiments3_adapter_mock.hpp>
#include <tests/helpers/trip_planner_operations_test_helper.hpp>
#include <trip-planner/operations/filter/filter_by_passengers_sla_info.hpp>

#include <iostream>

namespace {

using namespace std::chrono_literals;

using ::testing::_;
using ::testing::Return;

const auto kMainFilePath = utils::CurrentSourcePath(
    "src/trip-planner/operations/filter/filter_by_passengers_sla/static_test/"
    "main.json");
const auto kPassengersSlaAlreadyViolated =
    ::formats::json::ValueBuilder{"sla_already_violated"}.ExtractValue();
const auto kRideSlaAlreadyViolated =
    ::formats::json::ValueBuilder{"ride_sla_already_violated"}.ExtractValue();
const auto kPassengersSlaViolated =
    ::formats::json::ValueBuilder{"sla_violated"}.ExtractValue();
const auto kRideSlaViolated =
    ::formats::json::ValueBuilder{"ride_sla_violated"}.ExtractValue();

const auto kFilterName = "filter_by_passengers_sla";

using ToStopsMap = std::unordered_map<shuttle_control::models::StopIdT,
                                      shuttle_control::models::ShortRouteInfo>;

const auto kSlaParamsJson = R"(
  {
    "pickup_deviation": {
      "min_acceptable_deviation_s": 30,
      "deviation_percent": 100,
      "max_acceptable_deviation_s": 300
    },
    "dropoff_deviation": {
      "min_acceptable_deviation_s": 60,
      "deviation_percent": 50,
      "max_acceptable_deviation_s": 600
    }
  }
)";

const auto kTripId1 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b1");
const auto kTripId2 = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288b2");
const auto kWorkshiftId = boost::lexical_cast<boost::uuids::uuid>(
    "427a330d-2506-464a-accf-346b31e288c1");

}  // namespace

namespace shuttle_control::trip_planner::operations::filter {

TEST(FilterByPassengersSla, SlaSatisfied) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId1,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{1},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 60s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId2,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{3},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 120s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
      }
    }
  }

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{60s, 600}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{60s, 600}},
                 {models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{2},
      ToStopsMap{{models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{3},
      ToStopsMap{{models::StopIdT{4}, models::ShortRouteInfo{60s, 600}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(kWorkshiftId, models::Workshift{
                                              .workshift_id = kWorkshiftId,
                                              .template_id = kWorkshiftId,
                                              .route_name = "route_1",
                                              .work_time =
                                                  {
                                                      .start = now - 600s,
                                                      .end = now + 600s,
                                                  },
                                          });

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto sla_params = ::formats::json::FromString(kSlaParamsJson)
                              .As<experiments3::shuttle_sla_params::Value>();
  EXPECT_CALL(*experiments3, GetSLAParams("route_1", _, _))
      .Times(2)
      .WillRepeatedly(Return(sla_params));

  FilterByPassengersSla filter(info::kFilterByPassengersSla, route_cache_ptr,
                               shuttle_eta_to_stops_cache, stops_mutual_cache,
                               workshifts_cache, experiments3);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {kTripId1, {}},
          {kTripId2, {}},
      };

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        for (auto& [trip_id, trip_level] : shuttle_level.trips) {
          const auto& it = expected_skip_reasons.find(trip_id);
          EXPECT_FALSE(it == expected_skip_reasons.end());
          EXPECT_EQ(it->second, trip_level.skip_reasons) << trip_id;
          expected_skip_reasons.erase(it);
        }
      }
    }
  }

  EXPECT_TRUE(expected_skip_reasons.empty());
}

TEST(FilterByPassengersSla, RideSLAAlreadyViolated) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId1,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{1},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 60s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId2,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{3},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 120s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
      }
    }
  }

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{60s, 600}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{60s, 600}},
                 {models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{2},
      ToStopsMap{{models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{3},
      ToStopsMap{{models::StopIdT{4}, models::ShortRouteInfo{60s, 600}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(kWorkshiftId, models::Workshift{
                                              .workshift_id = kWorkshiftId,
                                              .template_id = kWorkshiftId,
                                              .route_name = "route_1",
                                              .work_time =
                                                  {
                                                      .start = now - 600s,
                                                      .end = now + 120s,
                                                  },
                                          });

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto sla_params = ::formats::json::FromString(kSlaParamsJson)
                              .As<experiments3::shuttle_sla_params::Value>();
  EXPECT_CALL(*experiments3, GetSLAParams("route_1", _, _))
      .Times(2)
      .WillRepeatedly(Return(sla_params));

  FilterByPassengersSla filter(info::kFilterByPassengersSla, route_cache_ptr,
                               shuttle_eta_to_stops_cache, stops_mutual_cache,
                               workshifts_cache, experiments3);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {kTripId1, {{kFilterName, kRideSlaAlreadyViolated}}},
          {kTripId2, {{kFilterName, kRideSlaAlreadyViolated}}},
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

TEST(FilterByPassengersSla, RideSLAViolated) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId1,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{1},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 60s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId2,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{3},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 120s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
      }
    }
  }

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{60s, 600}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{60s, 600}},
                 {models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{2},
      ToStopsMap{{models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{3},
      ToStopsMap{{models::StopIdT{4}, models::ShortRouteInfo{60s, 600}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(kWorkshiftId, models::Workshift{
                                              .workshift_id = kWorkshiftId,
                                              .template_id = kWorkshiftId,
                                              .route_name = "route_1",
                                              .work_time =
                                                  {
                                                      .start = now - 600s,
                                                      .end = now + 200s,
                                                  },
                                          });

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto sla_params = ::formats::json::FromString(kSlaParamsJson)
                              .As<experiments3::shuttle_sla_params::Value>();
  EXPECT_CALL(*experiments3, GetSLAParams("route_1", _, _))
      .Times(2)
      .WillRepeatedly(Return(sla_params));

  FilterByPassengersSla filter(info::kFilterByPassengersSla, route_cache_ptr,
                               shuttle_eta_to_stops_cache, stops_mutual_cache,
                               workshifts_cache, experiments3);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {kTripId1, {{kFilterName, kRideSlaViolated}}},
          {kTripId2, {}},
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

TEST(FilterByPassengersSla, PassengerSLAAlreadyViolated) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId1,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{1},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 60s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId2,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{3},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 30s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
      }
    }
  }

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{60s, 600}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{60s, 600}},
                 {models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{2},
      ToStopsMap{{models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{3},
      ToStopsMap{{models::StopIdT{4}, models::ShortRouteInfo{60s, 600}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(kWorkshiftId, models::Workshift{
                                              .workshift_id = kWorkshiftId,
                                              .template_id = kWorkshiftId,
                                              .route_name = "route_1",
                                              .work_time =
                                                  {
                                                      .start = now - 600s,
                                                      .end = now + 600s,
                                                  },
                                          });

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto sla_params = ::formats::json::FromString(kSlaParamsJson)
                              .As<experiments3::shuttle_sla_params::Value>();
  EXPECT_CALL(*experiments3, GetSLAParams("route_1", _, _))
      .Times(2)
      .WillRepeatedly(Return(sla_params));

  FilterByPassengersSla filter(info::kFilterByPassengersSla, route_cache_ptr,
                               shuttle_eta_to_stops_cache, stops_mutual_cache,
                               workshifts_cache, experiments3);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {kTripId1, {{kFilterName, kPassengersSlaAlreadyViolated}}},
          {kTripId2, {{kFilterName, kPassengersSlaAlreadyViolated}}},
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

TEST(FilterByPassengersSla, PassengerSLAViolated) {
  auto [search_query, search_result, route_cache] =
      tests::helpers::TripPlannerOpearationTestHelper::Build(
          ::formats::json::blocking::FromFile(kMainFilePath));

  const auto route_cache_ptr =
      std::make_shared<models::RoutesCacheIndex>(std::move(route_cache));

  const auto now = ::utils::datetime::Now();

  for (auto& [route_id, route_level] : search_result.routes) {
    for (auto& [segment_id, segment_level] : route_level.segments) {
      for (auto& [shuttle_id, shuttle_level] : segment_level.shuttles) {
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId1,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{1},
                    .dropoff_stop_id = models::StopIdT{3},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 60s,
            .dropoff_timestamp = now + 120s,
            .created_at = now,
        });
        shuttle_level.bookings.push_back(models::ShortBookingInfo{
            .booking_id = kTripId2,
            .status = models::BookingStatus::kCreated,
            .booked_segment =
                {
                    .pickup_stop_id = models::StopIdT{3},
                    .dropoff_stop_id = models::StopIdT{4},
                    .pickup_lap = models::StopLapT{1},
                    .dropoff_lap = models::StopLapT{1},
                },
            .pickup_timestamp = now + 120s,
            .dropoff_timestamp = now + 180s,
            .created_at = now,
        });
      }
    }
  }

  const auto shuttle_eta_to_stops_cache =
      std::make_shared<models::ShuttleETAToStopCacheResult>();
  shuttle_eta_to_stops_cache->emplace(
      models::ShuttleIdT{1},
      ToStopsMap{{models::StopIdT{1}, models::ShortRouteInfo{60s, 600}}});

  const auto stops_mutual_cache =
      std::make_shared<models::StopsRouteInfoCacheResult>();
  stops_mutual_cache->emplace(
      models::StopIdT{1},
      ToStopsMap{{models::StopIdT{2}, models::ShortRouteInfo{70s, 600}},
                 {models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{2},
      ToStopsMap{{models::StopIdT{3}, models::ShortRouteInfo{60s, 600}}});
  stops_mutual_cache->emplace(
      models::StopIdT{3},
      ToStopsMap{{models::StopIdT{4}, models::ShortRouteInfo{60s, 600}}});

  const auto workshifts_cache = std::make_shared<caches::WorkshiftsCacheData>();
  workshifts_cache->emplace(kWorkshiftId, models::Workshift{
                                              .workshift_id = kWorkshiftId,
                                              .template_id = kWorkshiftId,
                                              .route_name = "route_1",
                                              .work_time =
                                                  {
                                                      .start = now - 600s,
                                                      .end = now + 600s,
                                                  },
                                          });

  const auto experiments3 =
      std::make_shared<internal::Experiments3AdapterMock>();
  const auto sla_params = ::formats::json::FromString(kSlaParamsJson)
                              .As<experiments3::shuttle_sla_params::Value>();
  EXPECT_CALL(*experiments3, GetSLAParams("route_1", _, _))
      .Times(2)
      .WillRepeatedly(Return(sla_params));

  FilterByPassengersSla filter(info::kFilterByPassengersSla, route_cache_ptr,
                               shuttle_eta_to_stops_cache, stops_mutual_cache,
                               workshifts_cache, experiments3);
  filter.Process(search_query, search_result);

  std::unordered_map<boost::uuids::uuid,
                     std::unordered_map<std::string, ::formats::json::Value>,
                     boost::hash<boost::uuids::uuid>>
      expected_skip_reasons{
          {kTripId1, {{kFilterName, kPassengersSlaViolated}}},
          {kTripId2, {}},
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
