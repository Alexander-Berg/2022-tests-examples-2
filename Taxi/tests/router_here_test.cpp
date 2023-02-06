#include <gtest/gtest.h>

#include <fstream>

#include <clients/router_exceptions.hpp>
#include <clients/router_here.hpp>
#include <clients/router_here_base.hpp>
#include <clients/router_pedestrian_here.hpp>
#include <common/mock_handlers_context.hpp>
#include <handlers/context.hpp>
#include <threads/async.hpp>
#include <utils/file_system.cpp>

namespace {

const std::string kBaseUrl = "http://route.cit.api.here.com";
const std::string kBaseMatrixUrl = "http://matrix.route.cit.api.here.com";
const std::string kAppId = "unit";
const std::string kAppCode = "test";

using clients::routing::RouterHere;
namespace here = clients::routing::here;

const clients::Graphite& graphite() {
  static const clients::Graphite client;
  return client;
}

const utils::http::Client& http_client() {
  static utils::Async async(2, "xx", false);
  static const utils::http::Client client(async, 1, "test_http_client", false);
  return client;
}

std::string ReadFile(const std::string& name) {
  return utils::ReadFile(utils::PathJoin(SOURCE_DIR "/tests/static/", name));
}

}  // namespace

class HereRouterWithAmountOfPointsAndJams
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<int, bool>>,
      public MockHeadersContext {};

TEST_P(HereRouterWithAmountOfPointsAndJams, FailsOnShortPath) {
  using utils::geometry::kNoDirection;

  int path_length;
  bool with_jams;
  std::tie(path_length, with_jams) = GetParam();

  RouterHere router(http_client(), graphite(), kBaseUrl, kBaseMatrixUrl, kAppId,
                    kAppCode, with_jams);
  RouterHere::path_t path(path_length);

  EXPECT_THROW(router.RouteEx(path, kNoDirection, GetContext(), {}),
               clients::routing::BadRequestError);
  EXPECT_THROW(router.Route(path, kNoDirection, GetContext(), {}),
               clients::routing::BadRequestError);
  EXPECT_THROW(router.GetWaypointInfo(path, GetContext(), {}),
               clients::routing::BadRequestError);
}

INSTANTIATE_TEST_CASE_P(HereRouter, HereRouterWithAmountOfPointsAndJams,
                        testing::Combine(testing::Range(0, 2),
                                         testing::Bool()), );

class HereRouterWithJamsAndExpectedUrl
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<bool, std::string, here::Mode>>,
      public MockHeadersContext {};

TEST_P(HereRouterWithJamsAndExpectedUrl, GenerateUrl) {
  const bool with_jams = std::get<0>(GetParam());
  const std::string& expected_url = std::get<1>(GetParam());
  here::Mode mode = std::get<2>(GetParam());  // mode do not matter

  RouterHere::path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  path.emplace_back(4.4, -6.4);

  RouterHere router(http_client(), graphite(), kBaseUrl, kBaseMatrixUrl, kAppId,
                    kAppCode, with_jams);

  const std::string& actual_url = router.MakeQueryUrl(
      path, utils::geometry::kNoDirection, mode, GetContext().config);
  // begin with
  EXPECT_EQ(expected_url, actual_url.substr(0, expected_url.size()))
      << actual_url;
}

INSTANTIATE_TEST_CASE_P(
    HereRouter, HereRouterWithJamsAndExpectedUrl,
    testing::Values(
        std::make_tuple(false,
                        "http://route.cit.api.here.com/routing/7.2/"
                        "calculateroute.json?mode=balanced;car;traffic:"
                        "disabled;tollroad:-2,boatFerry:-3,railFerry:-3"
                        "&app_id=unit&app_code=test"
                        "&waypoint0=geo!2.4,-1.4"
                        "&waypoint1=geo!-7.4,3.4"
                        "&waypoint2=geo!-6.4,4.4&"
                        "generalizationTolerances=0.005",
                        here::Mode::kFull),
        std::make_tuple(true,
                        "http://route.cit.api.here.com/routing/7.2/"
                        "calculateroute.json?mode=balanced;car;traffic:enabled;"
                        "tollroad:-2,boatFerry:-3,railFerry:-3"
                        "&app_id=unit&app_code=test"
                        "&waypoint0=geo!2.4,-1.4"
                        "&waypoint1=geo!-7.4,3.4"
                        "&waypoint2=geo!-6.4,4.4"
                        "&generalizationTolerances=0.005",
                        here::Mode::kFull)), );

class HereRouterParseSummary : public testing::Test,
                               public testing::WithParamInterface<const char*> {
};

TEST_P(HereRouterParseSummary, ValidDocument) {
  const std::string& body = ReadFile(GetParam());

  const auto& route_info = here::ParseSummary(body, {});
  EXPECT_LT(0.0, route_info.total_distance);
  EXPECT_LT(0.0, route_info.total_time);
}

INSTANTIATE_TEST_CASE_P(HereRouter, HereRouterParseSummary,
                        testing::Values("router_here/summary_no_jams.bin",
                                        "router_here/summary_jams.bin"), );

class HereRouterParseWaypoint : public testing::Test,
                                public testing::WithParamInterface<const char*>,
                                public MockHeadersContext {};

TEST_P(HereRouterParseWaypoint, ValidDocument) {
  const std::string& body = ReadFile(GetParam());

  const auto& route_info = here::ParseFull(body, false, GetContext());
  EXPECT_LT(0.0, route_info->total_distance);
  EXPECT_LT(0.0, route_info->total_time);

  // waypoints
  const auto& waypoints = route_info->GetWaypoints();
  EXPECT_EQ(3u, waypoints.size());
  for (size_t i = 1; i < waypoints.size(); ++i) {
    EXPECT_LE(waypoints[i - 1].time_since_ride_start,
              waypoints[i].time_since_ride_start);
    EXPECT_LE(waypoints[i - 1].distance_since_ride_start,
              waypoints[i].distance_since_ride_start);
  }
  EXPECT_EQ(0.0, waypoints.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, waypoints.front().distance_since_ride_start);
  EXPECT_EQ(route_info->GetTotalTime(),
            waypoints.back().time_since_ride_start.count());
  EXPECT_EQ(route_info->GetTotalDistance(),
            waypoints.back().distance_since_ride_start);

  // movement
  const auto& movement = route_info->GetMovement();
  EXPECT_EQ(0u, movement.size());

  // path
  const auto& path = route_info->GetRawPath();
  EXPECT_EQ(movement.size(), path.size());
}

INSTANTIATE_TEST_CASE_P(HereRouter, HereRouterParseWaypoint,
                        testing::Values("router_here/waypoint_no_jams.bin",
                                        "router_here/waypoint_jams.bin"), );

class HereRouterParseFull : public testing::Test,
                            public testing::WithParamInterface<const char*>,
                            public MockHeadersContext {};

TEST_P(HereRouterParseFull, ValidDocument) {
  const std::string& body = ReadFile(GetParam());

  const auto& route_info = here::ParseFull(body, true, GetContext());
  EXPECT_LT(0.0, route_info->total_distance);
  EXPECT_LT(0.0, route_info->total_time);

  // waypoints
  const auto& waypoints = route_info->GetWaypoints();
  EXPECT_EQ(3u, waypoints.size());
  for (size_t i = 1; i < waypoints.size(); ++i) {
    EXPECT_LE(waypoints[i - 1].time_since_ride_start,
              waypoints[i].time_since_ride_start);
    EXPECT_LE(waypoints[i - 1].distance_since_ride_start,
              waypoints[i].distance_since_ride_start);
  }
  EXPECT_EQ(0.0, waypoints.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, waypoints.front().distance_since_ride_start);
  EXPECT_EQ(route_info->GetTotalTime(),
            waypoints.back().time_since_ride_start.count());
  EXPECT_EQ(route_info->GetTotalDistance(),
            waypoints.back().distance_since_ride_start);

  // movement
  const auto& movement = route_info->GetMovement();
  EXPECT_LE(3u, movement.size());
  for (size_t i = 1; i < waypoints.size(); ++i) {
    EXPECT_LE(movement[i - 1].time_since_ride_start,
              movement[i].time_since_ride_start);
    EXPECT_LE(movement[i - 1].distance_since_ride_start,
              movement[i].distance_since_ride_start);
  }
  EXPECT_EQ(0.0, movement.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, movement.front().distance_since_ride_start);
  EXPECT_EQ(route_info->GetTotalTime(),
            movement.back().time_since_ride_start.count());
  EXPECT_EQ(route_info->GetTotalDistance(),
            movement.back().distance_since_ride_start);

  // path
  const auto& path = route_info->GetRawPath();
  EXPECT_EQ(movement.size(), path.size());
}

INSTANTIATE_TEST_CASE_P(HereRouter, HereRouterParseFull,
                        testing::Values("router_here/full_no_jams.bin",
                                        "router_here/full_jams.bin"), );

TEST(HereRouterParseBadRequest, One) {
  const std::string& no_route = ReadFile("router_here/error_no_route.bin");
  const std::string& invalid = ReadFile("router_here/error_invalid.bin");

  EXPECT_THROW(here::ParseBadRequest(no_route, {}),
               clients::routing::InsolubleRequestError);
  EXPECT_THROW(here::ParseBadRequest(invalid, {}),
               clients::routing::BadResponseError);
}

class HereRouterTestMatrix
    : public testing::Test,
      public testing::WithParamInterface<std::pair<const char*, const char*>>,
      public MockHeadersContext {};

TEST_P(HereRouterTestMatrix, GenerateMatrixUrl) {
  std::string expected_url_file;
  std::string response_file;
  std::tie(expected_url_file, response_file) = GetParam();
  RouterHere router(http_client(), graphite(), kBaseUrl, kBaseMatrixUrl, kAppId,
                    kAppCode, true);

  std::vector<clients::routing::TrackPoint> from_bulk;
  clients::routing::Point to = {-0.101881, 51.507854};
  from_bulk.emplace_back(-0.0999, 51.5141, 30, 0, 0);
  from_bulk.emplace_back(-0.1023, 51.5079, 60, 0, 0);
  from_bulk.emplace_back(-0.100261, 51.513638, 45, 0, 0);
  const std::string& actual_url =
      router.MakeMatrixQueryUrl(from_bulk, to, GetContext().config) + "\n";
  const std::string& expected_url = ReadFile(expected_url_file);
  ASSERT_EQ(expected_url, actual_url);
  const auto& response = ReadFile(response_file);
  const auto& route_infos = here::ParseMatrixRow(response, LogExtra(), 3);

  clients::routing::RouteInfos true_route_infos = {
      {522, 1555}, {143, 120}, {454, 1609}};
  ASSERT_EQ(route_infos.size(), true_route_infos.size());
  for (unsigned i = 0; i < route_infos.size(); ++i) {
    ASSERT_FLOAT_EQ(route_infos[i].total_time, true_route_infos[i].total_time);
    ASSERT_FLOAT_EQ(route_infos[i].total_distance,
                    true_route_infos[i].total_distance);
  }
}

INSTANTIATE_TEST_CASE_P(
    HereRouter, HereRouterTestMatrix,
    testing::Values(std::make_pair("router_here/matrix.bin.meta",
                                   "router_here/matrix.bin")), );

class HereRouterTestBadMatrix : public testing::Test,
                                public testing::WithParamInterface<const char*>,
                                public MockHeadersContext {};

TEST_P(HereRouterTestBadMatrix, GenerateMatrixUrl) {
  std::string response_file = GetParam();
  RouterHere router(http_client(), graphite(), kBaseUrl, kBaseMatrixUrl, kAppId,
                    kAppCode, true);

  const auto& response = ReadFile(response_file);
  const auto& route_infos = here::ParseMatrixRow(response, LogExtra(), 3);

  clients::routing::RouteInfos true_route_infos = {
      {522, 1555}, {-1, -1}, {454, 1609}};
  ASSERT_EQ(route_infos.size(), true_route_infos.size());
  for (unsigned i = 0; i < route_infos.size(); ++i) {
    ASSERT_FLOAT_EQ(route_infos[i].total_time, true_route_infos[i].total_time);
    ASSERT_FLOAT_EQ(route_infos[i].total_distance,
                    true_route_infos[i].total_distance);
  }
}

INSTANTIATE_TEST_CASE_P(HereRouter, HereRouterTestBadMatrix,
                        testing::Values("router_here/bad_matrix.bin"), );

class RouterPedestrianHereTest : public clients::routing::RouterPedestrianHere {
 public:
  using Point = clients::routing::Point;
  using path_t = clients::routing::path_t;

  RouterPedestrianHereTest(const utils::http::Client& http_client,
                           const clients::Graphite& graphite,
                           const std::string& base_url,
                           const std::string& base_matrix_url)
      : RouterPedestrianHere(http_client, graphite, base_url, base_matrix_url,
                             "test_id", "test_code") {}

  std::string MakeQueryUrlTest(const path_t& path) const {
    return MakeQueryUrl(path);
  }

  std::string MakeBulkQueryUrlTest(const std::vector<Point>& from_bulk,
                                   const std::vector<Point>& to_bulk) const {
    return MakeBulkQueryUrl(from_bulk, to_bulk);
  }
};

class HerePedestrianRouterTestUrlResponse
    : public ::testing::Test,
      public ::testing::WithParamInterface<std::pair<const char*, const char*>>,
      public MockHeadersContext {};

TEST_P(HerePedestrianRouterTestUrlResponse, GenerateUrl) {
  std::string expected_url_file;
  std::string response_file;
  std::tie(expected_url_file, response_file) = GetParam();
  RouterPedestrianHereTest router(http_client(), graphite(), kBaseUrl,
                                  kBaseMatrixUrl);
  clients::routing::path_t path;
  path.emplace_back(-0.0999, 51.5141);
  path.emplace_back(-0.1023, 51.5079);
  const std::string& actual_url = router.MakeQueryUrlTest(path) + "\n";
  const std::string& expected_url = ReadFile(expected_url_file);
  ASSERT_EQ(expected_url, actual_url);
  const auto& response = ReadFile(response_file);
  const auto& route_info = here::ParseFull(response, true, GetContext());
  const auto& raw_path = route_info->GetRawPath();
  path.clear();
  for (const auto& point : raw_path) {
    path.emplace_back(point);
  }
  std::vector<clients::routing::Point> true_path = {
      {-0.0999, 51.5141},     {-0.0998158, 51.514},    {-0.100261, 51.513638},
      {-0.0991023, 51.5133},  {-0.0982654, 51.512939}, {-0.0986409, 51.508282},
      {-0.101881, 51.507854}, {-0.1023746, 51.5078},   {-0.1024042, 51.50788},
      {-0.1023, 51.5079}};
  ASSERT_EQ(path.size(), true_path.size());
  for (unsigned i = 0; i < true_path.size(); ++i) {
    ASSERT_FLOAT_EQ(path[i].lon, true_path[i].lon);
    ASSERT_FLOAT_EQ(path[i].lat, true_path[i].lat);
  }
  ASSERT_EQ(static_cast<int>(route_info->GetTotalTime()), 1055);
  ASSERT_EQ(static_cast<int>(route_info->GetTotalDistance()), 1026);
}

INSTANTIATE_TEST_CASE_P(
    TestPedestrianUrlGenerationAndResponse, HerePedestrianRouterTestUrlResponse,
    testing::Values(std::make_pair("router_here/pedestrian_route.bin.meta",
                                   "router_here/pedestrian_route.bin")), );

class HerePedestrianMatrixRouterTestUrlResponse
    : public ::testing::Test,
      public ::testing::WithParamInterface<
          std::pair<const char*, const char*>> {};

TEST_P(HerePedestrianMatrixRouterTestUrlResponse, GenerateMatrixUrl) {
  std::string expected_url_file;
  std::string response_file;
  std::tie(expected_url_file, response_file) = GetParam();
  RouterPedestrianHereTest router(http_client(), graphite(), kBaseUrl,
                                  kBaseMatrixUrl);
  clients::routing::path_t from_bulk;
  clients::routing::path_t to_bulk;
  from_bulk.emplace_back(-0.0999, 51.5141);
  from_bulk.emplace_back(-0.1023, 51.5079);
  to_bulk.emplace_back(-0.100261, 51.513638);
  to_bulk.emplace_back(-0.101881, 51.507854);
  const std::string& actual_url =
      router.MakeBulkQueryUrlTest(from_bulk, to_bulk) + "\n";
  const std::string& expected_url = ReadFile(expected_url_file);
  ASSERT_EQ(expected_url, actual_url);
  const auto& response = ReadFile(response_file);
  const auto& result_infos =
      here::ParseMatrix(response, LogExtra(), from_bulk.size(), to_bulk.size());

  using InfoType = std::pair<double, double>;
  std::map<std::pair<unsigned, unsigned>, InfoType> true_infos = {
      {{0, 0}, {53, 53}},
      {{0, 1}, {992, 980}},
      {{1, 0}, {994, 973}},
      {{1, 1}, {55, 45}}};
  ASSERT_EQ(result_infos.size(), true_infos.size());
  for (const auto& info : result_infos) {
    InfoType true_info = true_infos[{info.from_idx, info.to_idx}];
    InfoType parsed_info = {info.total_time, info.total_distance};
    ASSERT_FLOAT_EQ(parsed_info.first, true_info.first);
    ASSERT_FLOAT_EQ(parsed_info.second, true_info.second);
  }
}

INSTANTIATE_TEST_CASE_P(
    TestPedestrianUrlGenerationAndResponse,
    HerePedestrianMatrixRouterTestUrlResponse,
    testing::Values(std::make_pair("router_here/pedestrian_matrix.bin.meta",
                                   "router_here/pedestrian_matrix.bin")), );
