#include <gtest/gtest.h>

#include <algorithm>
#include <chrono>

#include <boost/units/systems/si/length.hpp>

#include <clients/routing/router_types.hpp>

#include <models/order_route_info.hpp>
#include <models/route_point.hpp>

namespace {

namespace cm = combo_contractors::models;
namespace cr = clients::routing;

using namespace std::chrono_literals;

using TimePoint = std::chrono::system_clock::time_point;

const std::vector<cm::RoutePoint> kRoute{
    {"order_id0", cm::RoutePointType::kStart, {}, TimePoint{0s}},
    {"order_id0", cm::RoutePointType::kFinish, {}, TimePoint{1s}},
    {"order_id1", cm::RoutePointType::kStart, {}, TimePoint{2s}},
    {"order_id2", cm::RoutePointType::kStart, {}, TimePoint{3s}},
    {"", cm::RoutePointType::kContractor, {}, {}},
    {"order_id3", cm::RoutePointType::kStart, {}, {}},
    {"order_id3", cm::RoutePointType::kFinish, {}, {}},
    {"order_id2", cm::RoutePointType::kFinish, {}, {}},
    {"order_id1", cm::RoutePointType::kFinish, {}, {}}};

using boost::units::si::meters;

const auto kRoutePathFromContractor{[] {
  cr::RoutePath route_path;
  route_path.path = {{{}, 4s, 4 * meters},
                     {{}, 5s, 5 * meters},
                     {{}, 6s, 6 * meters},
                     {{}, 7s, 7 * meters},
                     {{}, 8s, 8 * meters}};
  route_path.legs = {{0}, {1}, {2}, {3}};
  return route_path;
}()};

}  // namespace

TEST(OrderRouteInfo, GetRouteInfosFromContractor) {
  auto infos = GetRouteInfos(kRoute, kRoutePathFromContractor, TimePoint{4s});

  ASSERT_EQ(infos.size(), 4);
  ASSERT_TRUE(infos.count("order_id0"));
  ASSERT_TRUE(infos.count("order_id1"));
  ASSERT_TRUE(infos.count("order_id2"));
  ASSERT_TRUE(infos.count("order_id3"));

  ASSERT_FALSE(infos["order_id0"].driving_time);
  ASSERT_FALSE(infos["order_id0"].left_time);
  ASSERT_EQ(infos["order_id0"].past_time, 4s);

  ASSERT_FALSE(infos["order_id1"].driving_time);
  ASSERT_EQ(infos["order_id1"].left_time, 4s);
  ASSERT_EQ(infos["order_id1"].past_time, 2s);
  ASSERT_EQ(infos["order_id1"].transporting_time, 6s);

  ASSERT_FALSE(infos["order_id2"].driving_time);
  ASSERT_EQ(infos["order_id2"].left_time, 3s);
  ASSERT_EQ(infos["order_id2"].past_time, 1s);
  ASSERT_EQ(infos["order_id2"].transporting_time, 4s);

  ASSERT_EQ(infos["order_id3"].driving_time, 1s);
  ASSERT_EQ(infos["order_id3"].left_time, 2s);
  ASSERT_FALSE(infos["order_id3"].past_time);
  ASSERT_EQ(infos["order_id3"].transporting_time, 1s);
}

TEST(OrderRouteInfo, GetParameters) {
  auto infos = GetRouteInfos(kRoute, kRoutePathFromContractor, TimePoint{4s});
  auto parameters = GetParameters(GetOrders(kRoute), infos);

  ASSERT_EQ(parameters.size(), 28);
  ASSERT_TRUE(parameters.count("driving_time_0"));
  ASSERT_DOUBLE_EQ(parameters["driving_time_0"], 0);
  ASSERT_TRUE(parameters.count("left_time_0"));
  ASSERT_DOUBLE_EQ(parameters["left_time_0"], 0);
  ASSERT_DOUBLE_EQ(parameters["past_time_0"], 4);
  ASSERT_DOUBLE_EQ(parameters["driving_dist_0"], 0);
  ASSERT_DOUBLE_EQ(parameters["left_dist_0"], 0);

  ASSERT_TRUE(parameters.count("driving_time_1"));
  ASSERT_DOUBLE_EQ(parameters["driving_time_1"], 0);
  ASSERT_DOUBLE_EQ(parameters["left_time_1"], 4);
  ASSERT_DOUBLE_EQ(parameters["past_time_1"], 2);
  ASSERT_DOUBLE_EQ(parameters["transporting_time_1"], 6);
  ASSERT_DOUBLE_EQ(parameters["driving_dist_1"], 0);
  ASSERT_DOUBLE_EQ(parameters["left_dist_1"], 4);

  ASSERT_TRUE(parameters.count("driving_time_2"));
  ASSERT_DOUBLE_EQ(parameters["driving_time_2"], 0);
  ASSERT_DOUBLE_EQ(parameters["left_time_2"], 3);
  ASSERT_DOUBLE_EQ(parameters["past_time_2"], 1);
  ASSERT_DOUBLE_EQ(parameters["transporting_time_2"], 4);
  ASSERT_DOUBLE_EQ(parameters["driving_dist_2"], 0);
  ASSERT_DOUBLE_EQ(parameters["left_dist_2"], 3);

  ASSERT_DOUBLE_EQ(parameters["driving_time_3"], 1);
  ASSERT_DOUBLE_EQ(parameters["left_time_3"], 2);
  ASSERT_TRUE(parameters.count("past_time_3"));
  ASSERT_DOUBLE_EQ(parameters["past_time_3"], 0);
  ASSERT_DOUBLE_EQ(parameters["transporting_time_3"], 1);
  ASSERT_DOUBLE_EQ(parameters["driving_dist_3"], 1);
  ASSERT_DOUBLE_EQ(parameters["left_dist_3"], 2);
  ASSERT_DOUBLE_EQ(parameters["transporting_dist_3"], 1);
}
