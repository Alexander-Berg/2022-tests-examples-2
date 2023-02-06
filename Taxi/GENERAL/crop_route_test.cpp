#include "crop_route.hpp"

#include <userver/utest/utest.hpp>

namespace {
using RouteId = driver_route_responder::models::RouteId;
using Route = driver_route_responder::models::Route;

using Position = ::geometry::Position;
using Distance = ::geometry::Distance;
using Latitude = ::geometry::Latitude;
using Longitude = ::geometry::Longitude;
}  // namespace

TEST(CropRouteTest, TwoPointsRoute) {
  using driver_route_responder::internal::CropRoute;

  RouteId route_id("route_id");
  std::vector<routing_base::RoutePoint> route_path;
  route_path = {{Position{Longitude(11), Latitude(21)}, std::chrono::seconds(0),
                 Distance(0 * ::geometry::meter)},
                {Position{Longitude(13), Latitude(23)},
                 std::chrono::seconds(20), Distance(400 * ::geometry::meter)}};
  routing_base::RouteInfo route_info;
  route_info.distance = Distance(400 * ::geometry::meter);
  route_info.time = std::chrono::seconds(20);
  route_info.blocked = false;
  route_info.has_toll_roads = false;
  route_info.has_dead_jam = false;
  Route route;
  route.route_id = route_id.GetUnderlying();
  route.request_id = "route_request";
  route.path = std::move(route_path);
  route.info = std::move(route_info);
  route.legs = {{0}};

  geobus::types::TimeleftData timeleft_data;
  timeleft_data.destination_position = {Longitude(13), Latitude(23)};
  geobus::types::Timelefts timelefts;
  timelefts.adjusted_pos = {Longitude(12), Latitude(22)};
  timelefts.adjusted_segment_index = 0;
  timelefts.timeleft_data = {std::move(timeleft_data)};
  auto timelefts_ptr = std::make_shared<geobus::types::Timelefts>(timelefts);
  auto last = timelefts_ptr->timeleft_data.begin();

  auto cropped_route = CropRoute(route, timelefts_ptr, last);

  ASSERT_EQ(2, cropped_route.size());
  EXPECT_EQ(cropped_route[0], Position(Longitude(12), Latitude(22)));
  EXPECT_EQ(cropped_route[1], Position(Longitude(13), Latitude(23)));
}

TEST(CropRouteTest, Base) {
  using driver_route_responder::internal::CropRoute;

  RouteId route_id("route_id");
  std::vector<routing_base::RoutePoint> route_path;
  route_path = {{Position{Longitude(10), Latitude(20)}, std::chrono::seconds(0),
                 Distance(0 * ::geometry::meter)},
                {Position{Longitude(11), Latitude(21)},
                 std::chrono::seconds(10), Distance(100 * ::geometry::meter)},
                {Position{Longitude(13), Latitude(23)},
                 std::chrono::seconds(20), Distance(200 * ::geometry::meter)},
                {Position{Longitude(14), Latitude(24)},
                 std::chrono::seconds(30), Distance(300 * ::geometry::meter)},
                {Position{Longitude(15), Latitude(25)},
                 std::chrono::seconds(40), Distance(400 * ::geometry::meter)},
                {Position{Longitude(16), Latitude(26)},
                 std::chrono::seconds(50), Distance(500 * ::geometry::meter)}};
  routing_base::RouteInfo route_info;
  route_info.distance = Distance(500 * ::geometry::meter);
  route_info.time = std::chrono::seconds(50);
  route_info.blocked = false;
  route_info.has_toll_roads = false;
  route_info.has_dead_jam = false;
  Route route;
  route.route_id = route_id.GetUnderlying();
  route.request_id = "route_request";
  route.path = std::move(route_path);
  route.info = std::move(route_info);
  route.legs = {{0}, {2}, {4}};

  std::vector<geobus::types::TimeleftData> timeleft_data(3);
  timeleft_data[0].destination_position = {Longitude(13), Latitude(23)};
  timeleft_data[1].destination_position = {Longitude(15), Latitude(25)};
  timeleft_data[2].destination_position = {Longitude(16), Latitude(26)};
  geobus::types::Timelefts timelefts;
  timelefts.adjusted_pos = {Longitude(12), Latitude(22)};
  timelefts.adjusted_segment_index = 1;
  timelefts.timeleft_data = std::move(timeleft_data);
  auto timelefts_ptr = std::make_shared<geobus::types::Timelefts>(timelefts);
  auto last = timelefts_ptr->timeleft_data.begin() + 1;

  auto cropped_route = CropRoute(route, timelefts_ptr, last);

  ASSERT_EQ(4, cropped_route.size());
  EXPECT_EQ(cropped_route[0], Position(Longitude(12), Latitude(22)));
  EXPECT_EQ(cropped_route[1], Position(Longitude(13), Latitude(23)));
  EXPECT_EQ(cropped_route[2], Position(Longitude(14), Latitude(24)));
  EXPECT_EQ(cropped_route[3], Position(Longitude(15), Latitude(25)));
}

TEST(CropRouteTest, FirstPoint) {
  using driver_route_responder::internal::CropRoute;

  RouteId route_id("route_id");
  std::vector<routing_base::RoutePoint> route_path;
  route_path = {{Position{Longitude(10), Latitude(20)}, std::chrono::seconds(0),
                 Distance(0 * ::geometry::meter)},
                {Position{Longitude(11), Latitude(21)},
                 std::chrono::seconds(10), Distance(100 * ::geometry::meter)},
                {Position{Longitude(13), Latitude(23)},
                 std::chrono::seconds(20), Distance(200 * ::geometry::meter)},
                {Position{Longitude(14), Latitude(24)},
                 std::chrono::seconds(30), Distance(300 * ::geometry::meter)},
                {Position{Longitude(15), Latitude(25)},
                 std::chrono::seconds(40), Distance(400 * ::geometry::meter)},
                {Position{Longitude(16), Latitude(26)},
                 std::chrono::seconds(50), Distance(500 * ::geometry::meter)}};
  routing_base::RouteInfo route_info;
  route_info.distance = Distance(500 * ::geometry::meter);
  route_info.time = std::chrono::seconds(50);
  route_info.blocked = false;
  route_info.has_toll_roads = false;
  route_info.has_dead_jam = false;
  Route route;
  route.route_id = route_id.GetUnderlying();
  route.request_id = "route_request";
  route.path = std::move(route_path);
  route.info = std::move(route_info);
  route.legs = {{0}, {2}, {4}};

  std::vector<geobus::types::TimeleftData> timeleft_data(3);
  timeleft_data[0].destination_position = {Longitude(13), Latitude(23)};
  timeleft_data[1].destination_position = {Longitude(15), Latitude(25)};
  timeleft_data[2].destination_position = {Longitude(16), Latitude(26)};
  geobus::types::Timelefts timelefts;
  timelefts.adjusted_pos = {Longitude(10.5), Latitude(20.5)};
  timelefts.adjusted_segment_index = 0;
  timelefts.timeleft_data = std::move(timeleft_data);
  auto timelefts_ptr = std::make_shared<geobus::types::Timelefts>(timelefts);
  auto last = timelefts_ptr->timeleft_data.begin();

  auto cropped_route = CropRoute(route, timelefts_ptr, last);

  ASSERT_EQ(3, cropped_route.size());
  EXPECT_EQ(cropped_route[0], Position(Longitude(10.5), Latitude(20.5)));
  EXPECT_EQ(cropped_route[1], Position(Longitude(11), Latitude(21)));
  EXPECT_EQ(cropped_route[2], Position(Longitude(13), Latitude(23)));
}

TEST(CropRouteTest, LastPoint) {
  using driver_route_responder::internal::CropRoute;

  RouteId route_id("route_id");
  std::vector<routing_base::RoutePoint> route_path;
  route_path = {{Position{Longitude(10), Latitude(20)}, std::chrono::seconds(0),
                 Distance(0 * ::geometry::meter)},
                {Position{Longitude(11), Latitude(21)},
                 std::chrono::seconds(10), Distance(100 * ::geometry::meter)},
                {Position{Longitude(13), Latitude(23)},
                 std::chrono::seconds(20), Distance(200 * ::geometry::meter)},
                {Position{Longitude(14), Latitude(24)},
                 std::chrono::seconds(30), Distance(300 * ::geometry::meter)},
                {Position{Longitude(15), Latitude(25)},
                 std::chrono::seconds(40), Distance(400 * ::geometry::meter)},
                {Position{Longitude(16), Latitude(26)},
                 std::chrono::seconds(50), Distance(500 * ::geometry::meter)}};
  routing_base::RouteInfo route_info;
  route_info.distance = Distance(500 * ::geometry::meter);
  route_info.time = std::chrono::seconds(50);
  route_info.blocked = false;
  route_info.has_toll_roads = false;
  route_info.has_dead_jam = false;
  Route route;
  route.route_id = route_id.GetUnderlying();
  route.request_id = "route_request";
  route.path = std::move(route_path);
  route.info = std::move(route_info);
  route.legs = {{0}, {2}, {4}};

  std::vector<geobus::types::TimeleftData> timeleft_data(3);
  timeleft_data[0].destination_position = {Longitude(13), Latitude(23)};
  timeleft_data[1].destination_position = {Longitude(15), Latitude(25)};
  timeleft_data[2].destination_position = {Longitude(16), Latitude(26)};
  geobus::types::Timelefts timelefts;
  timelefts.adjusted_pos = {Longitude(10.5), Latitude(20.5)};
  timelefts.adjusted_segment_index = 0;
  timelefts.timeleft_data = std::move(timeleft_data);
  auto timelefts_ptr = std::make_shared<geobus::types::Timelefts>(timelefts);
  auto last = std::prev(timelefts_ptr->timeleft_data.end());

  auto cropped_route = CropRoute(route, timelefts_ptr, last);

  ASSERT_EQ(6, cropped_route.size());
  EXPECT_EQ(cropped_route[0], Position(Longitude(10.5), Latitude(20.5)));
  EXPECT_EQ(cropped_route[1], Position(Longitude(11), Latitude(21)));
  EXPECT_EQ(cropped_route[2], Position(Longitude(13), Latitude(23)));
  EXPECT_EQ(cropped_route[3], Position(Longitude(14), Latitude(24)));
  EXPECT_EQ(cropped_route[4], Position(Longitude(15), Latitude(25)));
  EXPECT_EQ(cropped_route[5], Position(Longitude(16), Latitude(26)));
}
