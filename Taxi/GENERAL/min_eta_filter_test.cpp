#include "min_eta_filter.hpp"

#include "userver/utest/utest.hpp"

namespace {
using MinEtaFilter = driver_route_responder::filters::MinEtaFilter;

using Timelefts = driver_route_responder::models::Timelefts;
using Position = driver_route_responder::internal::Position;
using InternalTimelefts = driver_route_responder::models::InternalTimelefts;
}  // namespace

TEST(MinEtaFilter, BaseTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(0),
                                                   0 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(70),
                                                   1500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  auto copy = timelefts;
  MinEtaFilter filter{};
  filter.ApplyFilter(copy);

  double expected_time = 60;
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(),
            expected_time);
  double expected_distance = 0;
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->distance.value(),
            expected_distance);
  expected_time = 70;
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->time.count(),
            expected_time);
  expected_distance = 1500;
  EXPECT_EQ(copy.timeleft_data[1].time_distance_left->distance.value(),
            expected_distance);

  EXPECT_EQ(copy.timeleft_data[0].raw_time_distance_left->time,
            timelefts.timeleft_data[0].raw_time_distance_left->time);
  EXPECT_EQ(
      copy.timeleft_data[0].raw_time_distance_left->distance.value(),
      timelefts.timeleft_data[0].raw_time_distance_left->distance.value());
  EXPECT_EQ(copy.timeleft_data[1].raw_time_distance_left->time,
            timelefts.timeleft_data[1].raw_time_distance_left->time);
  EXPECT_EQ(
      copy.timeleft_data[1].raw_time_distance_left->distance.value(),
      timelefts.timeleft_data[1].raw_time_distance_left->distance.value());
}
