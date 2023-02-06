#include <gtest/gtest.h>

#include <clients/routing/exceptions.hpp>
#include <clients/routing/router_types.hpp>
#include <vendors/yamaps/yamaps_car_family_router.hpp>

#include <optional>
#include <tuple>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>

#include "vendors/yamaps/yamaps_router.hpp"
#include "vendors/yamaps/yamaps_router_test_fixture_test.hpp"

namespace {

using ::testing::Bool;
using ::testing::Combine;
using ::testing::Range;
using ::testing::Values;

using clients::routing::DirectionOpt;
using clients::routing::EcoClass;
using clients::routing::ExperimentalArgs;
using clients::routing::InsolubleRequestError;
using clients::routing::MatrixInfo;
using clients::routing::Path;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterFeatures;
using clients::routing::RouterJams;
using clients::routing::RouterMode;
using clients::routing::RouterSettings;
using clients::routing::RouterType;
using clients::routing::RouterVehicle;
using clients::routing::RouterVehicleType;
using clients::routing::VehicleLength;
using clients::routing::VehicleWeight;
using clients::routing::YaMapsCarFamilyRouter;

}  // namespace

class YaMapsCarRouterTest : public YaMapsCarFamilyRouter {
 public:
  using YaMapsCarFamilyRouter::YaMapsCarFamilyRouter;

  std::string MakeCarFamilyUrl(
      const Path& path, const DirectionOpt& source_direction,
      const RequestType& type, const RouterSettings& settings,
      const ExperimentalArgs& experimental_args = {}) const {
    return YaMapsCarFamilyRouter::MakeUrl(path, type, settings,
                                          source_direction, experimental_args);
  }

  using YaMapsCarFamilyRouter::ParseRouteInfos;
  using YaMapsCarFamilyRouter::ParseRoutePaths;
};

namespace {

static const double kAbsError = 0.1;
static const double kAbsPosError = 0.003;
}  // namespace

struct YaMapsCarRouterTestFixture : public YaMapsRouterTestFixture {
  YaMapsCarRouterTest CreateCarRouter() {
    const std::string& base_url = "http://maps.example.com";
    const std::string& matrix_url = "";

    return YaMapsCarRouterTest(*http, {base_url, matrix_url, "", ""},
                               config_storage.GetSource(), std::nullopt,
                               RouterVehicleType::kVehicleCar, nullptr);
  }

  YaMapsCarRouterTest CreateTruckRouter() {
    const std::string& base_url = "http://maps.example.com";
    const std::string& matrix_url = "";

    return YaMapsCarRouterTest(*http, {base_url, matrix_url, "", ""},
                               config_storage.GetSource(), std::nullopt,
                               RouterVehicleType::kVehicleTruck, nullptr);
  }
};

class YaMapsCarRouterTestFixtureWithJamsAndExpectedUrlParams
    : public YaMapsCarRouterTestFixture,
      public ::testing::WithParamInterface<
          std::tuple<bool, bool, std::string>> {};

UTEST_P(YaMapsCarRouterTestFixtureWithJamsAndExpectedUrlParams, GenerateUrl) {
  const bool use_jams = std::get<0>(GetParam());
  RouterJams jams = (use_jams ? RouterJams::kJams : RouterJams::kNoJams);

  const bool get_full = std::get<1>(GetParam());
  YaMapsCarRouterTest::RequestType type =
      (get_full ? YaMapsCarRouterTest::RequestType::kFull
                : YaMapsCarRouterTest::RequestType::kSummary);

  const std::string& expected_url = std::get<2>(GetParam());

  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateCarRouter();
  auto settings = RouterSettings{jams};
  settings.results_count = 2;
  const std::string& actual_url =
      router.MakeCarFamilyUrl(path, std::nullopt, type, settings);

  // can not compare just string (arg order in undefined)
  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("lang=ru-RU") != std::string::npos);
  ASSERT_TRUE(actual_url.find(use_jams ? "mode=approx" : "mode=nojams") !=
              std::string::npos);
  ASSERT_TRUE(actual_url.find("results=2") != std::string::npos);
  ASSERT_TRUE(actual_url.find("features=geometry") != std::string::npos);
  auto last = actual_url.rfind('/');
  ASSERT_EQ(last, expected_url.rfind('/'));
  ASSERT_EQ(actual_url.substr(0, last), expected_url.substr(0, last));
}

INSTANTIATE_UTEST_SUITE_P(
    TestUrlGeneration, YaMapsCarRouterTestFixtureWithJamsAndExpectedUrlParams,
    Values(
        std::make_tuple(false, false,
                        "http://maps.example.com/v2/route"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=time&origin=yataxi"
                        "&lang=ru-RU&mode=nojams&results=2"),
        std::make_tuple(true, false,
                        "http://maps.example.com/v2/route"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=time&origin=yataxi"
                        "&lang=ru-RU&mode=approx&results=2"),
        std::make_tuple(true, true,
                        "http://maps.example.com/v2/summary"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=all&origin=yataxi"
                        "&lang=ru-RU&mode=approx&results=2")));

UTEST_P(YaMapsCarRouterTestFixtureWithJamsAndExpectedUrlParams,
        GenerateUrlDtm) {
  const bool use_jams = std::get<0>(GetParam());
  RouterJams jams = (use_jams ? RouterJams::kJams : RouterJams::kNoJams);

  const bool get_full = std::get<1>(GetParam());
  YaMapsCarRouterTest::RequestType type =
      (get_full ? YaMapsCarRouterTest::RequestType::kFull
                : YaMapsCarRouterTest::RequestType::kSummary);

  const std::string& expected_url = std::get<2>(GetParam());

  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateCarRouter();
  auto settings = RouterSettings{jams};
  settings.dtm = 12345;
  const std::string& actual_url =
      router.MakeCarFamilyUrl(path, std::nullopt, type, settings);

  // can not compare just string (arg order in undefined)
  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("lang=ru-RU") != std::string::npos);
  ASSERT_TRUE(actual_url.find(use_jams ? "mode=best" : "mode=nojams") !=
              std::string::npos);
  ASSERT_TRUE(actual_url.find("dtm=12345") != std::string::npos);
  auto last = actual_url.rfind('/');
  ASSERT_EQ(last, expected_url.rfind('/'));
  ASSERT_EQ(actual_url.substr(0, last), expected_url.substr(0, last));
}
INSTANTIATE_UTEST_SUITE_P(
    TestUrlGenerationDtm,
    YaMapsCarRouterTestFixtureWithJamsAndExpectedUrlParams,
    Values(
        std::make_tuple(false, false,
                        "http://maps.example.com/v2/route"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=time&origin=yataxi"
                        "&lang=ru-RU&dtm=12345&mode=nojams"),
        std::make_tuple(true, false,
                        "http://maps.example.com/v2/route"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=time&origin=yataxi"
                        "&lang=ru-RU&dtm=12345&mode=nojams"),
        std::make_tuple(true, true,
                        "http://maps.example.com/v2/summary"
                        "?rll=-1.4%2C2.4~3.4%2C-7.4&output=all&origin=yataxi"
                        "&lang=ru-RU&dtm=12345&mode=nojams")));

UTEST_F(YaMapsCarRouterTestFixture, MakeQueryVehicleUrl) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& car_router = CreateCarRouter();
  const auto& truck_router = CreateTruckRouter();

  auto vehicle = RouterVehicle{};
  vehicle.vehicle_pass_ids = {"id1", "id2"};
  vehicle.vehicle_length = 50 * routing_base::units::meters;  // 50 m
  vehicle.vehicle_weight = 5 * routing_base::units::tons;     // 5 ton
  vehicle.vehicle_eco_class = static_cast<EcoClass>(3);
  vehicle.vehicle_has_trailer = true;

  auto settings = RouterSettings{};
  settings.vehicle = vehicle;

  const std::string& actual_url = car_router.MakeCarFamilyUrl(
      path, std::nullopt, YaMapsCarRouterTest::RequestType::kSummary, settings);
  const std::string& truck_actual_url = truck_router.MakeCarFamilyUrl(
      path, std::nullopt, YaMapsCarRouterTest::RequestType::kSummary, settings);

  ASSERT_TRUE(actual_url.find("vehicle_type=car") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_pass_ids=id1%2Cid2") !=
              std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_length=50") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_weight=5") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_eco_class=3") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_has_trailer=1") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_payload") == std::string::npos);

  ASSERT_TRUE(truck_actual_url.find("vehicle_type=truck") != std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_pass_ids=id1%2Cid2") !=
              std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_length=50") != std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_weight=5") != std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_eco_class=3") !=
              std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_has_trailer=1") !=
              std::string::npos);
  ASSERT_TRUE(truck_actual_url.find("vehicle_payload") == std::string::npos);
}

class YaMapsCarRouterTestFixtureWithSnippetsAndExpectedUrlParams
    : public YaMapsCarRouterTestFixture,
      public ::testing::WithParamInterface<std::tuple<bool>> {};

UTEST_P(YaMapsCarRouterTestFixtureWithSnippetsAndExpectedUrlParams,
        GenerateUrlWithSnippets) {
  const bool use_accidents_snippet = std::get<0>(GetParam());

  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateCarRouter();
  auto settings = RouterSettings{};
  if (use_accidents_snippet) {
    settings.snippets.insert(routing_base::SnippetId::kAccidentsRank);
  }
  const std::string& actual_url = router.MakeCarFamilyUrl(
      path, std::nullopt, YaMapsCarRouterTest::RequestType::kFull, settings);

  // can not compare just string (arg order is undefined)
  if (use_accidents_snippet) {
    ASSERT_TRUE(actual_url.find("snippet_ids=taxi_accident_rank") !=
                std::string::npos);
  } else {
    ASSERT_TRUE(actual_url.find("snippets=") == std::string::npos);
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestUrlGenerationWithSnippets,
    YaMapsCarRouterTestFixtureWithSnippetsAndExpectedUrlParams,
    Values(std::make_tuple(false), std::make_tuple(true)));

class YaMapsRouterPointsShortTestParseWithFilenameParam
    : public YaMapsCarRouterTestFixture,
      public ::testing::WithParamInterface<
          std::tuple<const char*, double, double>> {};

UTEST_P(YaMapsRouterPointsShortTestParseWithFilenameParam, ParseValidDocument) {
  // Short Jams
  // curl -v
  // "http://core-driving-router.maps.yandex.net/v2/summary?lang=ru-RU& \
  //   rll=30.325%2C59.879~30.321123%2C59.875005&origin=yataxi&output=time&mode=approx"
  // -H "Accept: application/x-protobuf" -o yamaps_router_summary_jams.bin

  // Short without jams
  // curl -v
  // "http://core-driving-router.maps.yandex.net/v2/summary?lang=ru-RU& \
  //   rll=30.325%2C59.879~30.321123%2C59.875005&origin=yataxi&output=time&mode=nojams"
  // -H "Accept: application/x-protobuf" -o yamaps_router_summary.bin

  auto params = GetParam();

  std::string input_file = std::get<0>(params);
  std::string file_contents = clients::routing::utest::ReadFile(input_file);

  using namespace ::geometry::literals;
  Path path = {{30.325_lon, 59.879_lat}, {30.321123_lon, 59.875005_lat}};

  const auto& router = CreateCarRouter();
  const auto& jams =
      (input_file.find("jams") != std::string::npos ? RouterJams::kJams
                                                    : RouterJams::kNoJams);
  const auto& results = router.ParseRouteInfos(file_contents, jams);
  EXPECT_TRUE(!results.empty());

  if (!results.empty()) {
    const auto& info = results.front();
    EXPECT_NEAR(std::get<1>(params), info.time->count(), kAbsError);
    EXPECT_NEAR(std::get<2>(params), info.distance->value(), kAbsError);
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsRouterPointsShortTestParseWithFilenameParam,
    Values(std::make_tuple("router_yamaps/summary.bin", 306, 2006),
           std::make_tuple("router_yamaps/summary_jams.bin", 412, 1744.7)));

UTEST_F(YaMapsCarRouterTestFixture, EmptySummaryResponseAsNoRoute) {
  // Request router for summary for impossible route (destionation point 0.0,
  // 0.0), router returns empty response (in this case Content-Length = 0 , in
  // contrast to &output=time when answer length is 2)
  // curl -v
  // "http://core-driving-router.maps.yandex.net/v2/route?lang=ru-RU& \
  //   rll=30.325%2C59.879~0.0%2C0.0&output=time&origin=yataxi&mode=approx"
  // -H "Accept: application/x-protobuf"
  // -o yamaps_router_no_route_summary.bin

  // empty string corresponding empty response from router
  std::string router_answer;

  const auto& router = CreateCarRouter();
  EXPECT_THROW(router.ParseRouteInfos(router_answer, RouterJams::kJams),
               InsolubleRequestError);
}

struct YaMapsRouterPointDetailedTestParseWithFilenameParamStruct {
  std::string filename;
  double distance;
  double time;
  size_t number_of_legs;
  int count;
};

class YaMapsRouterPointDetailedTestParseWithFilenameParam
    : public YaMapsCarRouterTestFixture,
      public ::testing::WithParamInterface<
          YaMapsRouterPointDetailedTestParseWithFilenameParamStruct> {};

UTEST_P(YaMapsRouterPointDetailedTestParseWithFilenameParam,
        ParseValidDocument) {
  // Detailed with jams
  // curl -v
  // "http://core-driving-router.maps.yandex.net/v2/route?lang=ru-RU& \
  //   rll=30.325%2C59.879~30.321123%2C59.875005~30.313950%2C59.868775&origin=yataxi&mode=approx"
  // -H "Accept: application/x-protobuf" -o yamaps_router_detailed_jams.bin

  // Detailed without jams
  // curl -v
  // "http://core-driving-router.maps.yandex.net/v2/route?lang=ru-RU& \
  //   rll=30.325%2C59.879~30.321123%2C59.875005~30.313950%2C59.868775&origin=yataxi&mode=nojams"
  // -H "Accept: application/x-protobuf" -o yamaps_router_detailed.bin

  auto params = GetParam();

  std::string file_contents =
      clients::routing::utest::ReadFile(params.filename);

  using namespace ::geometry::literals;

  clients::routing::Path path;
  path.reserve(3);
  path.emplace_back(30.325_lon, 59.879_lat);
  path.emplace_back(30.321123_lon, 59.875005_lat);
  path.emplace_back(30.313950_lon, 59.868775_lat);

  const auto& router = CreateCarRouter();
  const auto& jams =
      (params.filename.find("jams") != std::string::npos ? RouterJams::kJams
                                                         : RouterJams::kNoJams);
  const auto& results =
      router.ParseRoutePaths(file_contents, path, jams, std::nullopt);
  EXPECT_TRUE(!results.empty());

  if (!results.empty()) {
    const auto& points_info_ptr = results.front();
    EXPECT_NEAR(params.time, points_info_ptr.info.time->count(), kAbsError);
    EXPECT_NEAR(params.distance, points_info_ptr.info.distance->value(),
                kAbsError);

    const auto& route_points = points_info_ptr.path;
    ASSERT_EQ(params.count, route_points.size());

    EXPECT_EQ(0.0, route_points[0].time_since_ride_start.count());
    EXPECT_EQ(0.0, route_points[0].distance_since_ride_start.value());
    EXPECT_NEAR(30.325, route_points[0].longitude.value(), kAbsPosError);
    EXPECT_NEAR(59.879, route_points[0].latitude.value(), kAbsPosError);

    // Allowed error is 2% here, it's too much and should be
    // decreased when problem with diferent distance calculation will be
    // solved
    EXPECT_NEAR(params.time, route_points.back().time_since_ride_start.count(),
                params.time * 0.02);
    EXPECT_NEAR(params.distance,
                route_points.back().distance_since_ride_start.value(),
                params.distance * 0.02);
    EXPECT_NEAR(30.313950, route_points.back().longitude.value(), kAbsPosError);
    EXPECT_NEAR(59.868775, route_points.back().latitude.value(), kAbsPosError);
    EXPECT_EQ(params.number_of_legs, points_info_ptr.legs.size());
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsRouterPointDetailedTestParseWithFilenameParam,
    Values(
        YaMapsRouterPointDetailedTestParseWithFilenameParamStruct{
            "router_yamaps/detailed.bin", 3541, 747, 2, 97},
        YaMapsRouterPointDetailedTestParseWithFilenameParamStruct{
            "router_yamaps/detailed_jams.bin", 3541, 990, 2, 97}));

UTEST_F(YaMapsCarRouterTestFixture, ResponseForTwoSamePoints) {
  // Request router for path between two identical points

  std::string file_contents =
      clients::routing::utest::ReadFile("router_yamaps/same_points.bin");

  using namespace ::geometry::literals;

  clients::routing::Path path;
  path.reserve(2);
  path.emplace_back(28.314943_lon, 57.819959_lat);
  path.emplace_back(28.314943_lon, 57.819959_lat);

  const auto& router = CreateCarRouter();
  const auto& results = router.ParseRoutePaths(file_contents, path,
                                               RouterJams::kJams, std::nullopt);
  EXPECT_TRUE(!results.empty());

  if (!results.empty()) {
    const auto& info = results.front();
    const auto& route_points = info.path;

    ASSERT_EQ(route_points.size(), 2);
    EXPECT_NEAR(57.819959, route_points.front().latitude.value(), kAbsPosError);
    EXPECT_NEAR(28.314943, route_points.front().longitude.value(),
                kAbsPosError);
    EXPECT_NEAR(0, route_points.front().time_since_ride_start.count(),
                kAbsPosError);
    EXPECT_NEAR(0, route_points.front().distance_since_ride_start.value(),
                kAbsPosError);
    EXPECT_NEAR(57.819959, route_points.back().latitude.value(), kAbsPosError);
    EXPECT_NEAR(28.314943, route_points.back().longitude.value(), kAbsPosError);
    EXPECT_NEAR(0, route_points.back().time_since_ride_start.count(),
                kAbsPosError);
    EXPECT_NEAR(0, route_points.back().distance_since_ride_start.value(),
                kAbsPosError);
    EXPECT_EQ(1, info.legs.size());
  }
}

UTEST_F(YaMapsCarRouterTestFixture, ParseSnippets) {
  std::string file_contents =
      clients::routing::utest::ReadFile("router_yamaps/snippets.bin");

  using namespace ::geometry::literals;

  clients::routing::Path path;
  path.reserve(2);
  path.emplace_back(37.784882_lon, 55.850107_lat);
  path.emplace_back(37.486583_lon, 55.868320_lat);

  const auto& router = CreateCarRouter();
  const auto& results = router.ParseRoutePaths(file_contents, path,
                                               RouterJams::kJams, std::nullopt);
  EXPECT_TRUE(!results.empty());

  if (!results.empty()) {
    const auto& info = results.front();

    const auto it = info.snippets.find(routing_base::SnippetId::kAccidentsRank);
    EXPECT_TRUE(it != info.snippets.end());

    if (it != info.snippets.end()) {
      const auto& snippet_data = it->second;
      EXPECT_EQ(231, snippet_data.size());
      EXPECT_EQ("\xB7\x9C\x8C\x42", snippet_data[0]);
      EXPECT_EQ("\x1E\xA8\x37\x3F", snippet_data[230]);
    }
  }
}

UTEST_F(YaMapsCarRouterTestFixture, MakeUrlWithExperimentalArgs) {
  const auto& router = CreateCarRouter();
  auto settings = RouterSettings{RouterJams::kJams};
  settings.results_count = 2;

  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  ExperimentalArgs experimental_args;
  experimental_args["exp_arg1"] = "exp_value1";
  experimental_args["exp_arg2"] = "exp_value2";

  const std::string& actual_url = router.MakeCarFamilyUrl(
      path, std::nullopt, YaMapsCarRouterTest::RequestType::kFull, settings,
      experimental_args);
  EXPECT_TRUE(actual_url.find("exp_arg1=exp_value1") != std::string::npos);
  EXPECT_TRUE(actual_url.find("exp_arg2=exp_value2") != std::string::npos);
}

UTEST_F(YaMapsCarRouterTestFixture, SupportedFeatures) {
  const auto& router = CreateCarRouter();
  // Every feature in this list is used by someone in production!
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRouteInfo));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRoutePath));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kMatrixInfo));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kAlternatives));
}
