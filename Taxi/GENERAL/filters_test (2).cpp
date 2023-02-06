#include "filters.hpp"

#include <userver/utest/utest.hpp>

namespace {
using MinEtaFilter = driver_route_responder::filters::MinEtaFilter;
using LinearDecreaseFilter =
    driver_route_responder::filters::LinearDecreaseFilter;
using Filters = driver_route_responder::filters::Filters;
using driver_route_responder::filters::ApplyFilters;
using driver_route_responder::filters::VisitFallback;
using driver_route_responder::filters::VisitOrderCoreInfo;
using driver_route_responder::filters::VisitTimelefts;
using driver_route_responder::filters::VisitTrackstoryCache;

using Timelefts = driver_route_responder::models::Timelefts;
using Position = driver_route_responder::internal::Position;
using InternalTimelefts = driver_route_responder::models::InternalTimelefts;
}  // namespace

TEST(Filters, FiltersTest) {
  int server_delta = 60;
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  int client_delta = 3;
  Position position;
  position.signal.timestamp = now + std::chrono::seconds{client_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(1);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(30),
                                                   300 * ::geometry::meter};

  Filters filters = {LinearDecreaseFilter{}, MinEtaFilter{}};
  VisitTimelefts(filters, timelefts_ptr);
  VisitTrackstoryCache(filters, position);
  ApplyFilters(filters, timelefts);

  auto expected_time = 60;
  EXPECT_EQ(timelefts.timeleft_data[0].time_distance_left->time.count(),
            expected_time);
  auto expected_distance = 0;
  EXPECT_EQ(timelefts.timeleft_data[0].time_distance_left->distance.value(),
            expected_distance);
}
