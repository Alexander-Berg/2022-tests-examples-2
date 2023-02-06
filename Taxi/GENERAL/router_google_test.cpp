#include <gtest/gtest.h>
#include <userver/formats/json/serialize.hpp>

#include <clients/routing/exceptions.hpp>
#include <vendors/google/router_google.hpp>

#include <geometry/distance.hpp>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>
#include <utest/routing/router_test_fixture_test.hpp>

#include <userver/http/parser/http_request_parse_args.hpp>
#include <userver/http/url.hpp>

using clients::routing::BadRequestError;
using clients::routing::DirectionOpt;
using clients::routing::Path;
using clients::routing::QuerySettings;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterGoogle;
using clients::routing::RouterJams;
using clients::routing::RouterMode;
using clients::routing::RouterSettings;
using clients::routing::RouterTolls;
using clients::routing::RouterVehicleType;

class RouterGoogleTest : public RouterGoogle {
 public:
  using RouterGoogle::RouterGoogle;
  using RouterGoogle::Step;

  std::string MakeUrl(const std::string& base_url, const Path& path,
                      const DirectionOpt& source_direction,
                      const RouterSettings& settings,
                      const QuerySettings& query_settings) const {
    return RouterGoogle::MakeUrl(base_url, path, source_direction, settings,
                                 query_settings);
  }

  RouteInfo ParseRouteInfo(const std::string& response) const {
    return RouterGoogle::ParseRouteInfo(response);
  }

  RoutePath ParseRoutePath(const std::string& response) const {
    return RouterGoogle::ParseRoutePath(response);
  }

  RoutePath::Path ToRoutePath(const std::vector<Step>& steps) const {
    return RouterGoogle::ToRoutePath(steps);
  }
};

namespace {
const std::string kBaseUrl = "https://maps.googleapis.com";

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

struct RouterGoogleTestFixture : public RouterTestFixture {
  RouterGoogleTest CreateRouter(RouterVehicleType router_type) {
    return RouterGoogleTest(*http, kBaseUrl, config_storage.GetSource(),
                            router_type);
  }
};

class GoogleRouterWithAmountOfPointsAndJams
    : public RouterGoogleTestFixture,
      public testing::WithParamInterface<std::tuple<int, bool>> {};

UTEST_P(GoogleRouterWithAmountOfPointsAndJams, FailsOnShortPath) {
  int path_length = 0;
  bool with_jams = false;
  std::tie(path_length, with_jams) = GetParam();

  Path path(path_length);
  RouterJams jams = with_jams ? RouterJams::kJams : RouterJams::kNoJams;

  auto router = CreateRouter(RouterVehicleType::kVehicleCar);

  EXPECT_THROW(router.MakeUrl(kBaseUrl, path, std::nullopt, {jams}, {}),
               BadRequestError);
}

INSTANTIATE_UTEST_SUITE_P(GoogleRouter, GoogleRouterWithAmountOfPointsAndJams,
                          testing::Combine(testing::Range(0, 2),
                                           testing::Bool()));

class GoogleRouterParseSummary
    : public RouterGoogleTestFixture,
      public testing::WithParamInterface<const char*> {};

UTEST_F(GoogleRouterParseSummary, ValidDocument) {
  const std::string& json =
      clients::routing::utest::ReadFile("router_google/response.json");

  auto router = CreateRouter(RouterVehicleType::kVehicleTruck);
  const auto& route_info = router.ParseRouteInfo(json);

  EXPECT_NEAR(2137146.0 + 1000000, route_info.distance->value(), 0.001);
  EXPECT_EQ(74384 + 50000, route_info.time->count());

  EXPECT_EQ(std::nullopt, route_info.blocked);
  EXPECT_EQ(std::nullopt, route_info.has_dead_jam);
  EXPECT_EQ(std::nullopt, route_info.has_toll_roads);
}

UTEST_F(GoogleRouterParseSummary, ValidDocumentJams) {
  const std::string& json =
      clients::routing::utest::ReadFile("router_google/response_jams.json");

  auto router = CreateRouter(RouterVehicleType::kVehicleTaxi);
  const auto& route_info = router.ParseRouteInfo(json);

  EXPECT_NEAR(2137146.0 + 1000000, route_info.distance->value(), 0.001);
  EXPECT_EQ(2 * (74384 + 50000), route_info.time->count());

  EXPECT_EQ(std::nullopt, route_info.blocked);
  EXPECT_EQ(std::nullopt, route_info.has_dead_jam);
  EXPECT_EQ(std::nullopt, route_info.has_toll_roads);
}
class GoogleRouterParse : public RouterGoogleTestFixture {};

UTEST_F(GoogleRouterParse, ValidDocumentLegs) {
  // This test checks for correctnes of leg indices with responses that contain
  // steps with lenght 1, as those were previously ignored due to being useless
  // for actual eta and distance calculations
  // It also contains steps which have distance = 0
  const std::string& json =
      clients::routing::utest::ReadFile("router_google/response_special.json");

  auto router = CreateRouter(RouterVehicleType::kVehicleCar);
  const auto& route_path = router.ParseRoutePath(json);

  EXPECT_LT(route_path.legs.back().point_index, route_path.path.size());
}

class GoogleRouterParseFull : public RouterGoogleTestFixture,
                              public testing::WithParamInterface<const char*> {
};

UTEST_P(GoogleRouterParseFull, ValidDocument) {
  const std::string& json = clients::routing::utest::ReadFile(GetParam());

  auto router = CreateRouter(RouterVehicleType::kVehicleTruck);
  const auto& route_path = router.ParseRoutePath(json);
  const auto& route_info = route_path.info;

  EXPECT_NEAR(2137146.0 + 1000000, route_info.distance->value(), 0.001);
  EXPECT_EQ(74384 + 50000, route_info.time->count());

  EXPECT_EQ(std::nullopt, route_path.info.blocked);
  EXPECT_EQ(std::nullopt, route_path.info.has_dead_jam);
  EXPECT_EQ(std::nullopt, route_path.info.has_toll_roads);

  const auto& path = route_path.path;
  //  "a~l~Fjk~uOwHJy@P" decodes to
  //  [
  //   [41.85073, -87.65126],
  //   [41.85229, -87.65132],
  //   [41.85258, -87.65141],
  //   [41.85258, -87.65141],
  //   [41.85383, -87.65145],
  //   [41.85388, -87.64843],
  //  ]
  EXPECT_EQ(6, path.size());
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(0), ::geometry::Position(41.85073 * geometry::lat,
                                       -87.65126 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(1), ::geometry::Position(41.85229 * geometry::lat,
                                       -87.65132 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(2), ::geometry::Position(41.85258 * geometry::lat,
                                       -87.65141 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(3), ::geometry::Position(41.85258 * geometry::lat,
                                       -87.65141 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(4), ::geometry::Position(41.85383 * geometry::lat,
                                       -87.65145 * geometry::lon)));
  ASSERT_TRUE(geometry::AreClosePositions(
      path.at(5), ::geometry::Position(41.85388 * geometry::lat,
                                       -87.64843 * geometry::lon)));

  for (size_t i = 1; i < path.size(); ++i) {
    EXPECT_LE(path[i - 1].time_since_ride_start, path[i].time_since_ride_start);
    EXPECT_LE(path[i - 1].distance_since_ride_start,
              path[i].distance_since_ride_start);
  }
  EXPECT_EQ(0.0, path.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, path.front().distance_since_ride_start.value());
  /// Full route info is a sum of legs infos
  EXPECT_EQ(route_path.info.time->count(), 74384 + 50000);
  EXPECT_EQ(route_path.info.distance->value(), 2137146 + 1000000);

  /// Check step info
  EXPECT_NEAR(path.back().time_since_ride_start.count(), 19 + 96, 1.0);
  EXPECT_NEAR(path.back().distance_since_ride_start.value(), 207 + 389, 1.0);

  // Check legs
  ASSERT_EQ(route_path.legs.size(), 2ull);
  ASSERT_EQ(route_path.legs.at(0).point_index, 0ull);
  ASSERT_EQ(route_path.legs.at(1).point_index, 3ull);
}

// {"route": [[37.531405,55.696361], [37.531661,55.709434]], "request_path":
// true, "use_jams": ...}
INSTANTIATE_UTEST_SUITE_P(GoogleRouter, GoogleRouterParseFull,
                          testing::Values("router_google/response.json"));

class GoogleRouterParseBadRequest
    : public RouterGoogleTestFixture,
      public testing::WithParamInterface<const char*> {};

UTEST_P(GoogleRouterParseBadRequest, OneBad) {
  const std::string& json = clients::routing::utest::ReadFile(GetParam());
  auto router = CreateRouter(RouterVehicleType::kVehicleTaxi);
  EXPECT_ANY_THROW(router.ParseRouteInfo(json));
}
INSTANTIATE_UTEST_SUITE_P(GoogleRouter, GoogleRouterParseBadRequest,
                          testing::Values("router_google/error_invalid.json"));

class GoogleRouterTestWithExpectedUrlParams : public RouterGoogleTestFixture {};

UTEST_F(GoogleRouterTestWithExpectedUrlParams, MakeBody) {
  const std::string& expected_data =
      "https://maps.googleapis.com/google/maps/api/directions/"
      "json?origin=heading%3D42%3A1.1%2C1.1&destination=2."
      "2%2C2.2&mode=driving&units=metric&avoid=tolls"
      "&departure_time=now";

  using namespace ::geometry::literals;
  Path path = {{1.1_lon, 1.1_lat}, {2.2_lon, 2.2_lat}};

  auto router = CreateRouter(RouterVehicleType::kVehicleCar);

  const std::string& actual_data = router.MakeUrl(
      kBaseUrl, path, geometry::Azimuth::from_value(42),
      {RouterJams::kJams, RouterMode::kApprox, RouterTolls::kNoTolls}, {});
  const auto& expected_args = GetArgsFromUrl(expected_data);
  const auto& actual_args = GetArgsFromUrl(actual_data);

  ASSERT_EQ(expected_args, actual_args);
}

UTEST_F(GoogleRouterTestWithExpectedUrlParams, MakeBodyNoHeading) {
  const std::string& expected_data =
      "https://maps.googleapis.com/google/maps/api/directions/"
      "json?origin=1.1%2C1.1&destination=2."
      "2%2C2.2&mode=walking&units=metric&avoid=tolls"
      "&departure_time=now";

  using namespace ::geometry::literals;
  Path path = {{1.1_lon, 1.1_lat}, {2.2_lon, 2.2_lat}};

  auto router = CreateRouter(RouterVehicleType::kVehiclePedestrian);

  const std::string& actual_data = router.MakeUrl(
      kBaseUrl, path, geometry::Azimuth::from_value(42),
      {RouterJams::kJams, RouterMode::kApprox, RouterTolls::kNoTolls}, {});
  const auto& expected_args = GetArgsFromUrl(expected_data);
  const auto& actual_args = GetArgsFromUrl(actual_data);

  ASSERT_EQ(expected_args, actual_args);
}

UTEST_F(GoogleRouterTestWithExpectedUrlParams, MakeBodyWithApiKey) {
  const std::string& expected_data =
      "https://maps.googleapis.com/google/maps/api/directions/"
      "json?origin=heading%3D42%3A1.1%2C1.1&destination=2."
      "2%2C2.2&mode=driving&units=metric&avoid=tolls"
      "&departure_time=now&google_api_key=taxi";

  using namespace ::geometry::literals;
  Path path = {{1.1_lon, 1.1_lat}, {2.2_lon, 2.2_lat}};

  auto router = CreateRouter(RouterVehicleType::kVehicleCar);

  QuerySettings query_settings;
  query_settings.external_api_keys.google_api_key = "taxi";

  const std::string& actual_data = router.MakeUrl(
      kBaseUrl, path, geometry::Azimuth::from_value(42),
      {RouterJams::kJams, RouterMode::kApprox, RouterTolls::kNoTolls},
      query_settings);
  const auto& expected_args = GetArgsFromUrl(expected_data);
  const auto& actual_args = GetArgsFromUrl(actual_data);

  ASSERT_EQ(expected_args, actual_args);
}

class GoogleRouterParsePath : public RouterGoogleTestFixture {};

UTEST_F(GoogleRouterParsePath, ToRoutePath) {
  using geometry::lat;
  using geometry::lon;
  auto router = CreateRouter(RouterVehicleType::kVehicleCar);

  const auto pos0 = geometry::Position(37 * lon, 55 * lat);
  const auto pos1 = geometry::Position(37.1 * lon, 55 * lat);
  const auto pos2 = geometry::Position(37.2 * lon, 55 * lat);
  const auto pos3 = geometry::Position(37.3 * lon, 55 * lat);
  const auto pos4 = geometry::Position(37.4 * lon, 55 * lat);
  const auto step_distance0 = geometry::SphericalProjectionDistance(pos0, pos2);
  const auto step_distance1 = geometry::SphericalProjectionDistance(pos2, pos4);
  const auto steps =
      std::vector<RouterGoogleTest::Step>{{
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
