#include <gtest/gtest.h>
#include <userver/formats/json/serialize.hpp>

#include <clients/routing/exceptions.hpp>
#include <vendors/mapbox/router_mapbox.hpp>

#include <geometry/distance.hpp>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>
#include <utest/routing/router_test_fixture_test.hpp>

#include <userver/http/parser/http_request_parse_args.hpp>
#include <userver/http/url.hpp>
#include "clients/routing/router_types.hpp"

using clients::routing::BadRequestError;
using clients::routing::Path;
using clients::routing::QuerySettings;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterMapbox;
using clients::routing::RouterVehicleType;

struct RouterMapboxTest : public RouterMapbox {
 public:
  using RouterMapbox::RouterMapbox;
  using RouterMapbox::Step;

  std::string MakeUrl(const std::string& base_url, const Path& path,
                      const QuerySettings& query_settings) const {
    return RouterMapbox::MakeUrl(base_url, path, query_settings);
  }

  RouteInfo ParseRouteInfo(const std::string& response) const {
    return RouterMapbox::ParseRouteInfo(response);
  }

  RoutePath ParseRoutePath(const std::string& response) const {
    return RouterMapbox::ParseRoutePath(response);
  }

  RoutePath::Path ToRoutePath(const std::vector<Step>& steps) const {
    return RouterMapbox::ToRoutePath(steps);
  }
};

namespace {
const std::string kBaseUrl = "https://api.mapbox.com";

::http::Args GetArgsFromUrl(const std::string& url) {
  const auto& decoded = http::parser::UrlDecode(url);
  const auto args_pos = decoded.find('?');
  if (args_pos == std::string::npos) {
    return {};
  }
  const auto args = decoded.substr(args_pos + 1);
  http::Args ret;
  http::parser::ParseAndConsumeArgs(
      args, [&ret](std::string&& key, std::string&& value) {
        ret[std::move(key)] = std::move(value);
      });
  return ret;
}
}  // namespace

struct MapboxRouterTestFixture : RouterTestFixture {
  RouterMapboxTest CreateRouter(RouterVehicleType vehicle_type) {
    return RouterMapboxTest(*http, kBaseUrl, config_storage.GetSource(),
                            vehicle_type);
  }
};

struct MapboxRouterPathLength : public MapboxRouterTestFixture,
                                public testing::WithParamInterface<int> {};

UTEST_P(MapboxRouterPathLength, SimpleTest) {
  int path_length = 0;
  path_length = GetParam();
  Path path(path_length);
  auto router = CreateRouter(RouterVehicleType::kVehicleCar);
  if (path_length >= 2) {
    EXPECT_NO_THROW(router.MakeUrl(kBaseUrl, path, {}));
  } else {
    EXPECT_THROW(router.MakeUrl(kBaseUrl, path, {}), BadRequestError);
  }
}

INSTANTIATE_UTEST_SUITE_P(MapboxRouter, MapboxRouterPathLength,
                          testing::Range(0, 3));

struct MapboxRouterRouteInfo : public MapboxRouterTestFixture {};

UTEST_F(MapboxRouterRouteInfo, ValidDocument) {
  const std::string& json =
      clients::routing::utest::ReadFile("router_mapbox/response.json");

  auto router = CreateRouter(RouterVehicleType::kVehicleTruck);
  const auto& route_info = router.ParseRouteInfo(json);

  EXPECT_NEAR(263.0, route_info.distance->value(), 0.001);
  EXPECT_EQ(83, route_info.time->count());

  EXPECT_EQ(std::nullopt, route_info.blocked);
  EXPECT_EQ(std::nullopt, route_info.has_dead_jam);
  EXPECT_EQ(std::nullopt, route_info.has_toll_roads);
  EXPECT_EQ(routing_base::RouteSource::kMapbox, route_info.route_source);
}

struct MapboxRouterRoutePath : public MapboxRouterTestFixture {};

UTEST_F(MapboxRouterRoutePath, ValidDocument) {
  const std::string& json =
      clients::routing::utest::ReadFile("router_mapbox/response.json");

  auto router = CreateRouter(RouterVehicleType::kVehicleTaxi);
  const auto& route_path = router.ParseRoutePath(json);
  const auto& route_info = route_path.info;

  EXPECT_NEAR(263.0, route_info.distance->value(), 0.001);
  EXPECT_EQ(83, route_info.time->count());

  EXPECT_EQ(std::nullopt, route_info.blocked);
  EXPECT_EQ(std::nullopt, route_info.has_dead_jam);
  EXPECT_EQ(std::nullopt, route_info.has_toll_roads);
  EXPECT_EQ(routing_base::RouteSource::kMapbox, route_info.route_source);

  const auto& path = route_path.path;
  EXPECT_EQ(8, path.size());

  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(0), ::geometry::Position(40.735221 * geometry::lat,
                                       -73.991734 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(1), ::geometry::Position(40.735124 * geometry::lat,
                                       -73.991824 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(2), ::geometry::Position(40.734944 * geometry::lat,
                                       -73.991963 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(3), ::geometry::Position(40.734751 * geometry::lat,
                                       -73.992053 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(4), ::geometry::Position(40.734577 * geometry::lat,
                                       -73.992212 * geometry::lon)));

  for (size_t i = 1; i < path.size(); ++i) {
    EXPECT_LE(path[i - 1].time_since_ride_start.count(),
              path[i].time_since_ride_start.count());
    EXPECT_LE(path[i - 1].distance_since_ride_start.value(),
              path[i].distance_since_ride_start.value() + 1);
  }
  EXPECT_EQ(0.0, path.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, path.front().distance_since_ride_start.value());
  // Full route info is a sum of legs infos
  EXPECT_EQ(route_path.info.time->count(), 83);
  EXPECT_EQ(route_path.info.distance->value(), 263);

  ///// Check step info
  EXPECT_NEAR(path.back().time_since_ride_start.count(), 83, 1.0);
  EXPECT_NEAR(path.back().distance_since_ride_start.value(), 263, 1.0);

  // Check legs
  ASSERT_EQ(route_path.legs.size(), 1ull);
  ASSERT_EQ(route_path.legs.at(0).point_index, 0ull);
}

struct MapboxTestWithExpectedUrlParams : public MapboxRouterTestFixture {};

UTEST_F(MapboxTestWithExpectedUrlParams, MakeBody) {
  const std::string& expected_data =
      "https://api.mapbox.com/directions/v5/mapbox/"
      "?mode=driving-traffic&path=1.1%2C1.2%3B2.2%2C2.3&"
      "alternatives=false&geometries=polyline&steps=true";

  using namespace ::geometry::literals;
  Path path = {{1.1_lon, 1.2_lat}, {2.2_lon, 2.3_lat}};

  auto router = CreateRouter(RouterVehicleType::kVehicleCar);

  const std::string& actual_data = router.MakeUrl(kBaseUrl, path, {});
  const auto& expected_args = GetArgsFromUrl(expected_data);
  const auto& actual_args = GetArgsFromUrl(actual_data);

  ASSERT_EQ(expected_args, actual_args);
}

struct MapboxRouterParsePath : public MapboxRouterTestFixture {};

UTEST_F(MapboxRouterParsePath, ToRoutePath) {
  using geometry::lat;
  using geometry::lon;
  auto router = CreateRouter(RouterVehicleType::kVehicleTaxi);

  const auto pos0 = geometry::Position(37 * lon, 55 * lat);
  const auto pos1 = geometry::Position(37.1 * lon, 55 * lat);
  const auto pos2 = geometry::Position(37.2 * lon, 55 * lat);
  const auto pos3 = geometry::Position(37.3 * lon, 55 * lat);
  const auto pos4 = geometry::Position(37.4 * lon, 55 * lat);
  const auto step_distance0 = geometry::SphericalProjectionDistance(pos0, pos2);
  const auto step_distance1 = geometry::SphericalProjectionDistance(pos2, pos4);
  const auto steps =
      std::vector<RouterMapboxTest::Step>{{
                                              {
                                                  pos0,
                                                  pos1,
                                                  pos2,
                                              },
                                              std::chrono::seconds(100),
                                              step_distance0,
                                          },
                                          {{
                                               pos2,
                                               pos3,
                                               pos4,
                                           },
                                           std::chrono::seconds(10),
                                           step_distance1}};

  const auto& route_info = router.ToRoutePath(steps);
  ASSERT_EQ(6ull, route_info.size());
  const auto& p0 = route_info[0];
  ASSERT_EQ(p0.distance_since_ride_start, 0 * geometry::meter);
  ASSERT_EQ(p0.time_since_ride_start, std::chrono::seconds(0));
  ASSERT_EQ(pos0, static_cast<const ::geometry::Position&>(p0));

  const auto& p1 = route_info[1];
  ASSERT_NEAR(p1.distance_since_ride_start.value(), step_distance0.value() / 2,
              0.1);
  ASSERT_EQ(p1.time_since_ride_start, std::chrono::seconds(100) / 2);
  ASSERT_EQ(pos1, static_cast<const ::geometry::Position&>(p1));

  const auto& p2 = route_info[2];
  ASSERT_NEAR(p2.distance_since_ride_start.value(), step_distance0.value(),
              0.1);
  ASSERT_EQ(p2.time_since_ride_start, std::chrono::seconds(100));
  ASSERT_EQ(pos2, static_cast<const ::geometry::Position&>(p2));

  const auto& p3 = route_info[3];
  ASSERT_NEAR(p3.distance_since_ride_start.value(), step_distance0.value(),
              0.1);
  ASSERT_EQ(p3.time_since_ride_start, std::chrono::seconds(100));
  ASSERT_EQ(pos2, static_cast<const ::geometry::Position&>(p3));

  const auto& p4 = route_info[4];
  ASSERT_NEAR(p4.distance_since_ride_start.value(),
              step_distance0.value() + step_distance1.value() / 2, 0.1);
  ASSERT_EQ(p4.time_since_ride_start, std::chrono::seconds(105));
  ASSERT_EQ(pos3, static_cast<const ::geometry::Position&>(p4));

  const auto& p5 = route_info[5];
  ASSERT_NEAR(p5.distance_since_ride_start.value(),
              step_distance0.value() + step_distance1.value(), 0.1);
  ASSERT_EQ(p5.time_since_ride_start, std::chrono::seconds(110));
  ASSERT_EQ(pos4, static_cast<const ::geometry::Position&>(p5));
}
