#include "linear_decrease_filter.hpp"

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {
using LinearDecreaseFilter =
    driver_route_responder::filters::LinearDecreaseFilter;

using Timelefts = driver_route_responder::models::Timelefts;
using Position = driver_route_responder::internal::Position;
using InternalTimelefts = driver_route_responder::models::InternalTimelefts;
}  // namespace

TEST(LinearDecreaseFilter, FilterByServerTimeTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(100),
                                                   1000 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(200),
                                                   2500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  auto copy = timelefts;

  int client_delta = 3;

  Position position;
  position.signal.timestamp = now + std::chrono::seconds{client_delta};

  LinearDecreaseFilter filter{};
  filter.VisitTimelefts(timelefts_ptr);
  filter.VisitTrackstoryCache(position);
  filter.ApplyFilter(copy);

  double expected_time = 40;
  EXPECT_NEAR(copy.timeleft_data[0].time_distance_left->time.count(),
              expected_time, 1);
  double expected_distance = 400;
  EXPECT_NEAR(copy.timeleft_data[0].time_distance_left->distance.value(),
              expected_distance, 20);
  expected_time = 140;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->time.count(),
              expected_time, 1);
  expected_distance = 1900;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->distance.value(),
              expected_distance, 20);

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

TEST(LinearDecreaseFilter, FilterByClientTimeTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(100),
                                                   1000 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(200),
                                                   2500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  auto copy = timelefts;
  int client_delta = 120;

  Position position;
  position.signal.timestamp = now + std::chrono::seconds{client_delta};

  LinearDecreaseFilter filter{};
  filter.VisitTimelefts(timelefts_ptr);
  filter.VisitTrackstoryCache(position);
  filter.ApplyFilter(copy);

  double expected_time = 0;
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->time.count(),
            expected_time);
  double expected_distance = 0;
  EXPECT_EQ(copy.timeleft_data[0].time_distance_left->distance.value(),
            expected_distance);
  expected_time = 100;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->time.count(),
              expected_time, 1);
  expected_distance = 1500;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->distance.value(),
              expected_distance, 20);

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

TEST(LinearDecreaseFilter, VisitFallbackTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  ::utils::datetime::MockNowSet(
      std::chrono::system_clock::time_point{std::chrono::seconds{10000}});
  auto now = ::utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(100),
                                                   1000 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(200),
                                                   2500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  InternalTimelefts expected;
  expected.timeleft_data.resize(2);
  expected.timeleft_data[0].time_distance_left = {std::chrono::seconds(60),
                                                  600 * ::geometry::meter};
  expected.timeleft_data[0].raw_time_distance_left = {std::chrono::seconds(100),
                                                      1000 * ::geometry::meter};
  expected.timeleft_data[1].time_distance_left = {std::chrono::seconds(160),
                                                  2100 * ::geometry::meter};
  expected.timeleft_data[1].raw_time_distance_left = {std::chrono::seconds(200),
                                                      2500 * ::geometry::meter};
  int client_delta = 40;

  Position position;
  position.signal.timestamp = now - std::chrono::seconds{client_delta};

  LinearDecreaseFilter filter{std::chrono::seconds{20}};
  filter.VisitTimelefts(timelefts_ptr);
  filter.VisitTrackstoryCache(position);
  filter.VisitFallback();
  filter.ApplyFilter(timelefts);

  ::utils::datetime::MockNowUnset();

  EXPECT_EQ(expected.timeleft_data, timelefts.timeleft_data);
}

TEST(LinearDecreaseFilter, OnlyTimeleftsVisitTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(100),
                                                   1000 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(200),
                                                   2500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  auto copy = timelefts;

  LinearDecreaseFilter filter{};
  filter.VisitTimelefts(timelefts_ptr);
  filter.ApplyFilter(copy);

  double expected_time = 40;
  EXPECT_NEAR(copy.timeleft_data[0].time_distance_left->time.count(),
              expected_time, 1);
  double expected_distance = 400;
  EXPECT_NEAR(copy.timeleft_data[0].time_distance_left->distance.value(),
              expected_distance, 20);
  expected_time = 140;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->time.count(),
              expected_time, 1);
  expected_distance = 1900;
  EXPECT_NEAR(copy.timeleft_data[1].time_distance_left->distance.value(),
              expected_distance, 20);

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

TEST(LinearDecreaseFilter, OnlyTrackstoryCacheVisitTest) {
  auto timelefts_ptr = std::make_shared<Timelefts>();
  auto now = utils::datetime::Now();
  timelefts_ptr->timestamp = now;
  int server_delta = 60;
  timelefts_ptr->update_timestamp = now - std::chrono::seconds{server_delta};

  InternalTimelefts timelefts;
  timelefts.timeleft_data.resize(2);
  timelefts.timeleft_data[0].time_distance_left = {std::chrono::seconds(100),
                                                   1000 * ::geometry::meter};
  timelefts.timeleft_data[0].raw_time_distance_left =
      timelefts.timeleft_data[0].time_distance_left;
  timelefts.timeleft_data[1].time_distance_left = {std::chrono::seconds(200),
                                                   2500 * ::geometry::meter};
  timelefts.timeleft_data[1].raw_time_distance_left =
      timelefts.timeleft_data[1].time_distance_left;

  auto copy = timelefts;

  int client_delta = 120;

  Position position;
  position.signal.timestamp = now + std::chrono::seconds{client_delta};

  LinearDecreaseFilter filter{};
  filter.VisitTrackstoryCache(position);
  filter.ApplyFilter(copy);

  EXPECT_EQ(copy.timeleft_data, timelefts.timeleft_data);
}
