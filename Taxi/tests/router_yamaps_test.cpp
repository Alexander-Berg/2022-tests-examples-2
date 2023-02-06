#include <clients/router_yamaps.hpp>

#include <fstream>
#include <sstream>
#include <tuple>

#include <google/protobuf/message.h>
#include <gtest/gtest.h>

#include <yandex/maps/proto/common2/geo_object.pb.h>
#include <yandex/maps/proto/common2/response.pb.h>

#include <clients/router_exceptions.hpp>
#include <common/mock_handlers_context.hpp>
#include <handler_util/errors.hpp>
#include <threads/async.hpp>

namespace {

const clients::Graphite& graphite() {
  static const clients::Graphite client;
  return client;
}

const utils::http::Client& http_client() {
  static utils::Async async(2, "xx", false);
  static const utils::http::Client client(async, 1, "test_http_client", false);
  return client;
}

}  // namespace

using ::testing::Bool;
using ::testing::Combine;
using ::testing::Range;
using ::testing::Values;
using namespace yandex::maps::proto;
using namespace clients::routing;

class YaMapsRouterTestWithAmountOfPointsAndJamsParams
    : public ::testing::Test,
      public ::testing::WithParamInterface<std::tuple<int, bool>>,
      public MockHeadersContext {};

TEST_P(YaMapsRouterTestWithAmountOfPointsAndJamsParams, FailsOnShortPath) {
  const std::string& base_url = "http://maps.example.com";
  int path_length;
  bool with_jams;
  std::tie(path_length, with_jams) = GetParam();
  RouterYaMaps router(http_client(), graphite(), base_url, with_jams);
  clients::routing::Router::path_t path(path_length);

  EXPECT_THROW(
      router.RouteEx(path, utils::geometry::kNoDirection, GetContext(), {}),
      clients::routing::BadRequestError);
}

INSTANTIATE_TEST_CASE_P(TestCheckPathLength,
                        YaMapsRouterTestWithAmountOfPointsAndJamsParams,
                        Combine(Range(0, 2), Bool()), );

class YaMapsRoutePointsTestWithAmountOfPointsAndJamsParams
    : public ::testing::Test,
      public ::testing::WithParamInterface<std::tuple<int, bool>>,
      public MockHeadersContext {};

TEST_P(YaMapsRoutePointsTestWithAmountOfPointsAndJamsParams, FailsOnShort) {
  const std::string& base_url = "http://maps.example.com";
  int path_length;
  bool with_jams;
  std::tie(path_length, with_jams) = GetParam();
  RouterYaMaps router(http_client(), graphite(), base_url, with_jams);
  clients::routing::Router::path_t path(path_length);

  EXPECT_THROW(router.GetWaypointInfo(path, GetContext(), {})->Get(),
               clients::routing::BadRequestError);
}

INSTANTIATE_TEST_CASE_P(TestCheckPathLength,
                        YaMapsRoutePointsTestWithAmountOfPointsAndJamsParams,
                        Combine(Range(0, 2), Bool()), );

class YaMapsRouterTestWithJamsAndExpectedUrlParams
    : public ::testing::Test,
      public ::testing::WithParamInterface<
          std::tuple<bool, std::string, RouterYaMaps::Mode>>,
      public MockHeadersContext {};

TEST_P(YaMapsRouterTestWithJamsAndExpectedUrlParams, GenerateUrl) {
  const std::string& base_url = "http://maps.example.com";
  const std::string& expected_url = std::get<1>(GetParam());
  bool with_jams = std::get<0>(GetParam());
  RouterYaMaps::Mode mode = std::get<2>(GetParam());
  RouterYaMaps router(http_client(), graphite(), base_url, with_jams);
  clients::routing::Router::path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url =
      router.MakeQueryUrl(path, utils::geometry::kNoDirection, mode,
                          {/*empty infos*/}, GetContext());
  ASSERT_EQ(expected_url, actual_url);
}

INSTANTIATE_TEST_CASE_P(
    TestUrlGeneration, YaMapsRouterTestWithJamsAndExpectedUrlParams,
    Values(std::make_tuple(
               false,
               "http://maps.example.com/route/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&output=all",
               RouterYaMaps::Mode::kFull),
           std::make_tuple(
               true,
               "http://maps.example.com/route_jams/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&output=all",
               RouterYaMaps::Mode::kFull),
           std::make_tuple(
               false,
               "http://maps.example.com/route/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&output=time",
               RouterYaMaps::Mode::kSummary),
           std::make_tuple(
               true,
               "http://maps.example.com/route_jams/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&output=time",
               RouterYaMaps::Mode::kSummary),
           std::make_tuple(
               false,
               "http://maps.example.com/route/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&multi=stsp",
               RouterYaMaps::Mode::kMatrixSummary),
           std::make_tuple(
               true,
               "http://maps.example.com/route_jams/?lang=ru-RU&origin=yataxi"
               "&rll=-1.4,2.4~3.4,-7.4&multi=stsp",
               RouterYaMaps::Mode::kMatrixSummary)), );

class YaMapsTaxi : public ::testing::Test, public MockHeadersContext {};

TEST_F(YaMapsTaxi, GenerateUrl) {
  const std::string& base_url = "http://maps.example.com";
  const std::string& expected_url =
      "http://maps.example.com/route/"
      "?lang=ru-RU&origin=yataxi&rll=-1.4,2.4~3.4,-7.4&output=all&vehicle_type="
      "taxi";
  RouterYaMapsTaxi router(http_client(), graphite(), base_url, false);
  clients::routing::Router::path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url = router.MakeQueryUrl(
      path, utils::geometry::kNoDirection, RouterYaMaps::Mode::kFull,
      {/*empty infos*/}, GetContext());
  ASSERT_EQ(expected_url, actual_url);
}

class YaMapsRouterTestParseWithFilenameParam
    : public ::testing::Test,
      public ::testing::WithParamInterface<const char*>,
      public MockHeadersContext {};

TEST_P(YaMapsRouterTestParseWithFilenameParam, ParseValidDocument) {
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route_jams/?lang=ru-RU&rll=30.325%2C59.879~30.321123%2C59.875005&origin=yataxi"
  // -H "Accept: application/x-protobuf" -o /tmp/routerresp
  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += '/';
  input_file += GetParam();
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());
  std::unique_ptr<clients::routing::RouteInfoEx> ri{RouterYaMaps::ParseEx(
      file_contents,
      clients::routing::Router::path_t{{30.325, 59.879},
                                       {30.321123, 59.875005}},
      input_file.find("jams") != std::string::npos, GetContext())};
  ri->GetTotalTime();
  ri->GetTotalDistance();
  ri->GetRawPath();
  EXPECT_FALSE(ri->IsBlocked());
  auto movement = ri->GetMovement();

  std::ostringstream oss;
  for (const auto& mp : movement) {
    oss << mp.lon() << mp.lat() << mp.time_since_ride_start.count();
  }
}

INSTANTIATE_TEST_CASE_P(TestRouteParsing,
                        YaMapsRouterTestParseWithFilenameParam,
                        Values("yamaps_router_route.bin",
                               "yamaps_router_routejams.bin"), );

class YaMapsParseResponse : public ::testing::Test,
                            public MockHeadersContext {};

TEST_F(YaMapsParseResponse, BadData) {
  EXPECT_THROW(
      RouterYaMaps::ParseEx("<html>Bad Request</html>", {}, true, GetContext()),
      BadResponseError);
}

TEST_F(YaMapsParseResponse, ParseBlockedRoute) {
  const std::string input_file(SOURCE_DIR
                               "/tests/static/yamaps_router_blocked.bin");
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());
  const bool kNoJams = false;
  std::unique_ptr<clients::routing::RouteInfoEx> ri{RouterYaMaps::ParseEx(
      file_contents, clients::routing::Router::path_t{{1., 2.}, {3., 4.}},
      kNoJams, GetContext())};
  EXPECT_TRUE(ri->IsBlocked());
}

class YaMapsRoutePointsShortTestParseWithFilenameParam
    : public ::testing::Test,
      public ::testing::WithParamInterface<
          std::tuple<const char*, double, double>>,
      public MockHeadersContext {};

TEST_P(YaMapsRoutePointsShortTestParseWithFilenameParam, ParseValidDocument) {
  static const double kAbsError = 0.000000001;

  // Short Jams
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route_jams/?lang=ru-RU&rll=30.325%2C59.879~30.321123%2C59.875005&origin=yataxi&&output=time"
  // -H "Accept: application/x-protobuf" -o yamaps_router_summary_jams.bin

  // Short without jams
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route/?lang=ru-RU&rll=30.325%2C59.879~30.321123%2C59.875005&origin=yataxi&&output=time"
  // -H "Accept: application/x-protobuf" -o yamaps_router_summary.bin

  auto params = GetParam();

  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += '/';
  input_file += std::get<0>(params);
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());

  clients::routing::Router::path_t path;
  path.reserve(2);
  path.emplace_back(30.325, 59.879);
  path.emplace_back(30.321123, 59.875005);

  auto points_info_ptr = RouterYaMaps::ParseSections(
      file_contents, path, input_file.find("jams") != std::string::npos,
      GetContext().log_extra);

  ASSERT_NE(points_info_ptr, nullptr);

  EXPECT_NEAR(std::get<1>(params), points_info_ptr->total_time, kAbsError);
  EXPECT_NEAR(std::get<2>(params), points_info_ptr->total_distance, kAbsError);

  auto route_points = points_info_ptr->GetWaypoints();
  ASSERT_EQ(2u, route_points.size());

  EXPECT_NEAR(0.0, route_points[0].time_since_ride_start.count(), kAbsError);
  EXPECT_NEAR(0.0, route_points[0].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(30.325, route_points[0].lon(), kAbsError);
  EXPECT_NEAR(59.879, route_points[0].lat(), kAbsError);

  EXPECT_NEAR(std::get<1>(params),
              route_points[1].time_since_ride_start.count(), kAbsError);
  EXPECT_NEAR(std::get<2>(params), route_points[1].distance_since_ride_start,
              kAbsError);
  EXPECT_NEAR(30.321123, route_points[1].lon(), kAbsError);
  EXPECT_NEAR(59.875005, route_points[1].lat(), kAbsError);
}

INSTANTIATE_TEST_CASE_P(
    TestRouteParsing, YaMapsRoutePointsShortTestParseWithFilenameParam,
    Values(std::make_tuple("yamaps_router_summary.bin", 267.77520680427551,
                           2013.9430685043),
           std::make_tuple("yamaps_router_summary_jams.bin", 339.4662210941,
                           1788.1053810119)), );

class YaMapsRoutePointsDetailedTestParseWithFilenameParam
    : public ::testing::Test,
      public ::testing::WithParamInterface<
          std::tuple<const char*, double, double, double, double>>,
      public MockHeadersContext {};

TEST_P(YaMapsRoutePointsDetailedTestParseWithFilenameParam,
       ParseValidDocument) {
  static const double kAbsError = 0.000000001;

  // Detailed with jams
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route_jams/?lang=ru-RU&rll=30.325%2C59.879~30.321123%2C59.875005~30.313950%2C59.868775&origin=yataxi"
  // -H "Accept: application/x-protobuf" -o yamaps_router_detailed_jams.bin

  // Detailed without jams
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route/?lang=ru-RU&rll=30.325%2C59.879~30.321123%2C59.875005~30.313950%2C59.868775&origin=yataxi"
  // -H "Accept: application/x-protobuf" -o yamaps_router_detailed.bin

  auto params = GetParam();

  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += '/';
  input_file += std::get<0>(params);
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());

  clients::routing::Router::path_t path;
  path.reserve(2);
  path.emplace_back(30.325, 59.879);
  path.emplace_back(30.321123, 59.875005);
  path.emplace_back(30.313950, 59.868775);

  auto points_info_ptr = RouterYaMaps::ParseSections(
      file_contents, path, input_file.find("jams") != std::string::npos,
      GetContext().log_extra);

  ASSERT_NE(points_info_ptr, nullptr);

  EXPECT_NEAR(std::get<3>(params), points_info_ptr->total_time, kAbsError);
  EXPECT_NEAR(std::get<4>(params), points_info_ptr->total_distance, kAbsError);

  auto route_points = points_info_ptr->GetWaypoints();
  ASSERT_EQ(3u, route_points.size());

  EXPECT_NEAR(0.0, route_points[0].time_since_ride_start.count(), kAbsError);
  EXPECT_NEAR(0.0, route_points[0].distance_since_ride_start, kAbsError);
  EXPECT_NEAR(30.325, route_points[0].lon(), kAbsError);
  EXPECT_NEAR(59.879, route_points[0].lat(), kAbsError);

  EXPECT_NEAR(std::get<1>(params),
              route_points[1].time_since_ride_start.count(), kAbsError);
  EXPECT_NEAR(std::get<2>(params), route_points[1].distance_since_ride_start,
              kAbsError);
  EXPECT_NEAR(30.321123, route_points[1].lon(), kAbsError);
  EXPECT_NEAR(59.875005, route_points[1].lat(), kAbsError);

  EXPECT_NEAR(std::get<3>(params),
              route_points[2].time_since_ride_start.count(), kAbsError);
  EXPECT_NEAR(std::get<4>(params), route_points[2].distance_since_ride_start,
              kAbsError);
  EXPECT_NEAR(30.313950, route_points[2].lon(), kAbsError);
  EXPECT_NEAR(59.868775, route_points[2].lat(), kAbsError);
}

INSTANTIATE_TEST_CASE_P(
    TestRouteParsing, YaMapsRoutePointsDetailedTestParseWithFilenameParam,
    Values(std::make_tuple("yamaps_router_detailed.bin", 267.7752068043,
                           2013.9430685043, 595.1059472561, 3547.6877450943),
           std::make_tuple("yamaps_router_detailed_jams.bin", 346.0511928797,
                           1788.1053810120, 791.0431302190,
                           3455.1855773926)), );

class YaMapsRouterTest : public ::testing::Test, public MockHeadersContext {};

TEST_F(YaMapsRouterTest, EmptyFullResponseAsNoRoute) {
  // Request router for impossible route (destionation point 0.0, 0.0), router
  // returns empty response
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route_jams/?lang=ru-RU&rll=30.325%2C59.879~0.0%2C0.0&output=all&origin=yataxi"
  // -H "Accept: application/x-protobuf"
  // -o yamaps_router_no_route.bin

  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += "/yamaps_router_no_route.bin";
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());

  clients::routing::Router::path_t path;
  path.reserve(2);
  path.emplace_back(30.325, 59.879);
  path.emplace_back(0.0, 0.0);

  EXPECT_THROW(RouterYaMaps::ParseEx(file_contents, path, true, GetContext()),
               InsolubleRequestError);
}

TEST_F(YaMapsRouterTest, EmptySummaryResponseAsNoRoute) {
  // Request router for summary for impossible route (destionation point 0.0,
  // 0.0), router returns empty response (in this case Content-Length = 0 , in
  // contrast to &output=time when answer length is 2)
  // curl -v
  // "http://core-router-taxi.maps.yandex.net/route_jams/?lang=ru-RU&rll=30.325%2C59.879~0.0%2C0.0&output=time&origin=yataxi"
  // -H "Accept: application/x-protobuf"
  // -o yamaps_router_no_route_summary.bin

  // empty string corresponding empty response from router
  std::string router_answer;

  EXPECT_THROW(
      RouterYaMaps::ParseSummary(router_answer, true, GetContext().log_extra),
      InsolubleRequestError);
}

class YaMapsRouterTestMatrix : public ::testing::Test,
                               public MockHeadersContext {};

TEST_F(YaMapsRouterTestMatrix, ParseValidDocument) {
  static const double kAbsError = 0.000000001;

  // curl -v
  // "http://router.tst.maps.yandex.net/route/?lang=ru-RU&rll=37.011802,55.505807~37.044689,-55.485849~37.081904,55.468481~37.134800,55.445726~37.172477,55.427008&origin=yataxi&multi=stsp"
  // -H "Accept: text/xml" -o yamaps_router_matrix.bin
  std::string input_file(SOURCE_DIR "/tests/static/");
  input_file += '/';
  input_file += "yamaps_router_matrix.xml";
  std::ifstream input_stream(input_file);
  std::string file_contents;
  file_contents.assign((std::istreambuf_iterator<char>(input_stream)),
                       std::istreambuf_iterator<char>());

  std::vector<clients::routing::RouteInfo> ri{
      RouterYaMaps::ParseMatrixSummary(file_contents, {})};

  ASSERT_EQ(4u, ri.size());

  EXPECT_FALSE(ri[0].Empty());
  EXPECT_NEAR(13455.59, ri[0].total_distance, kAbsError);
  EXPECT_NEAR(856.19, ri[0].total_time, kAbsError);

  EXPECT_TRUE(ri[1].Empty());

  EXPECT_FALSE(ri[0].Empty());
  EXPECT_NEAR(7365.82, ri[2].total_distance, kAbsError);
  EXPECT_NEAR(445.98, ri[2].total_time, kAbsError);

  EXPECT_FALSE(ri[0].Empty());
  EXPECT_NEAR(3168.92, ri[3].total_distance, kAbsError);
  EXPECT_NEAR(164.36, ri[3].total_time, kAbsError);
}

class YaMapsV2 : public ::testing::Test, public MockHeadersContext {};

TEST_F(YaMapsV2, GenerateUrl) {
  const std::string& base_url = "http://maps.example.com";
  const std::string& expected_url =
      "http://maps.example.com/v2/route"
      "?lang=ru-RU&origin=yataxi&rll=-1.4,2.4~3.4,-7.4"
      "&mode=approx";
  RouterYaMapsV2 router(http_client(), graphite(), base_url, true);
  clients::routing::Router::path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url = router.MakeQueryUrl(
      path, utils::geometry::kNoDirection, RouterYaMaps::Mode::kFull,
      {/*empty infos*/}, GetContext());
  ASSERT_EQ(expected_url, actual_url);
}

TEST_F(YaMapsV2, GenerateUrlWithTime) {
  const std::string& base_url = "http://maps.example.com";
  const std::string& expected_url =
      "http://maps.example.com/v2/route"
      "?lang=ru-RU&origin=yataxi&rll=-1.4,2.4~3.4,-7.4&dtm=12345"
      "&mode=nojams";
  RouterYaMapsV2 router(http_client(), graphite(), base_url, true);
  clients::routing::Router::path_t path;
  path.emplace_back(-1.4, 2.4);
  path.emplace_back(3.4, -7.4);
  const std::string& actual_url = router.MakeQueryUrl(
      path, utils::geometry::kNoDirection, RouterYaMaps::Mode::kFull,
      {{"dtm", "12345"}}, GetContext());
  ASSERT_EQ(expected_url, actual_url);
}
