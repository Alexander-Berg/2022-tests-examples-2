#include <gtest/gtest.h>

#include <clients/routing/exceptions.hpp>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>

#include "clients/routing/router_types.hpp"
#include "vendors/yamaps/yamaps_bicycle_family_router.hpp"
#include "vendors/yamaps/yamaps_router.hpp"
#include "vendors/yamaps/yamaps_router_test_fixture_test.hpp"

using ::testing::Bool;
using ::testing::Combine;
using ::testing::Range;
using ::testing::Values;

using clients::routing::Directions;
using clients::routing::InsolubleRequestError;
using clients::routing::MatrixInfo;
using clients::routing::Path;
using clients::routing::Points;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterFeatures;
using clients::routing::RouterJams;
using clients::routing::RouterSettings;
using clients::routing::RouterVehicleType;
using clients::routing::YaMapsBicycleFamilyRouter;

class YaMapsBicycleRouterTest : public YaMapsBicycleFamilyRouter {
 public:
  using YaMapsBicycleFamilyRouter::MakeMatrixUrl;
  using YaMapsBicycleFamilyRouter::ParseRoutePaths;
  using YaMapsBicycleFamilyRouter::YaMapsBicycleFamilyRouter;

  std::vector<RouteInfo> ParseBicycleRouteInfos(
      const std::string& response) const {
    return YaMapsBicycleFamilyRouter::ParseRouteInfos(response, {});
  }

  std::string MakeBicycleUrl(const Path& path, const RequestType& type,
                             const RouterSettings& settings) const {
    return YaMapsBicycleFamilyRouter::MakeUrl(path, type, settings, {}, {});
  }

  narray::Array2D<MatrixInfo> ParseBicycleMatrixInfo(
      const std::string& serialized) const {
    return YaMapsBicycleFamilyRouter::ParseMatrixInfo(serialized);
  }
};

namespace {

static const double kAbsError = 1.0;  // the constant must match the library
static const double kAbsPosError = 0.003;

}  // namespace

struct YaMapsBicycleRouterTestFixture : public YaMapsRouterTestFixture {
  YaMapsBicycleRouterTest CreateRouter() {
    const std::string& base_url = "http://maps.example.com";
    const std::string& matrix_url = "http://maps-matrix.example.com";
    return YaMapsBicycleRouterTest(*http, {base_url, matrix_url, "", ""},
                                   config_storage.GetSource(), std::nullopt,
                                   RouterVehicleType::kVehicleBicycle, nullptr);
  }

  YaMapsBicycleRouterTest CreateScooterRouter() {
    const std::string& base_url = "http://maps.example.com";
    const std::string& matrix_url = "";

    return YaMapsBicycleRouterTest(*http, {base_url, matrix_url, "", ""},
                                   config_storage.GetSource(), std::nullopt,
                                   RouterVehicleType::kVehicleScooter, nullptr);
  }
};

struct YaMapsBicycleRouterMultiLegs : public YaMapsBicycleRouterTestFixture {};

UTEST_F(YaMapsBicycleRouterMultiLegs, Base) {
  std::string file_contents = clients::routing::utest::ReadFile(
      "router_yamaps_bicycle/route_multi_destination.bin");

  const auto& router = CreateRouter();
  const auto& results =
      router.ParseRoutePaths(file_contents, clients::routing::Path{},
                             RouterJams::kNoJams, std::nullopt);
  EXPECT_TRUE(!results.empty());
  if (!results.empty()) {
    const auto& route_path = results.front();
    const auto& legs = route_path.legs;
    ASSERT_EQ(legs.size(), 2);
    ASSERT_EQ(legs[0].point_index, 0);
    /// Legs are different
    ASSERT_EQ(legs[1].point_index, 40);
  }
}

UTEST_F(YaMapsBicycleRouterTestFixture, MakeQueryUrlLinear) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakeBicycleUrl(
      path, YaMapsBicycleRouterTest::RequestType::kSummary, {});

  ASSERT_TRUE(actual_url.find("http://maps.example.com/v2/summary") !=
              std::string::npos);
  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("lang=ru-RU") != std::string::npos);
  ASSERT_TRUE(actual_url.find("origin=yataxi") != std::string::npos);
}

UTEST_F(YaMapsBicycleRouterTestFixture, MakeQueryUrlScooter) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateRouter();
  const auto& scooter_router = CreateScooterRouter();

  RouterSettings settings;
  settings.vehicle = routing_base::RouterVehicle();

  const std::string& actual_url = router.MakeBicycleUrl(
      path, YaMapsBicycleRouterTest::RequestType::kSummary, settings);
  const std::string& scooter_actual_url = scooter_router.MakeBicycleUrl(
      path, YaMapsBicycleRouterTest::RequestType::kSummary, settings);

  ASSERT_TRUE(actual_url.find("http://maps.example.com/v2/summary") !=
              std::string::npos);
  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("lang=ru-RU") != std::string::npos);
  ASSERT_TRUE(actual_url.find("origin=yataxi") != std::string::npos);
  ASSERT_TRUE(actual_url.find("vehicle_type=bicycle") != std::string::npos);

  ASSERT_TRUE(scooter_actual_url.find("http://maps.example.com/v2/summary") !=
              std::string::npos);
  ASSERT_TRUE(scooter_actual_url.find("rll=-1.400000%2C2.400000"
                                      "~3.400000%2C-7.400000") !=
              std::string::npos);
  ASSERT_TRUE(scooter_actual_url.find("lang=ru-RU") != std::string::npos);
  ASSERT_TRUE(scooter_actual_url.find("origin=yataxi") != std::string::npos);
  ASSERT_TRUE(scooter_actual_url.find("vehicle_type=scooter") !=
              std::string::npos);
}

UTEST_F(YaMapsBicycleRouterTestFixture, MakeMatrixUrl) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};
  Directions dirs{std::nullopt, geometry::Azimuth::from_value(15)};

  const auto& router = CreateRouter();
  const std::string& actual_url =
      router.MakeMatrixUrl(path, dirs, path, dirs, {});

  EXPECT_TRUE(actual_url.find("http://maps-matrix.example.com/v2/matrix") !=
              std::string::npos);
  EXPECT_TRUE(actual_url.find("srcll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  EXPECT_TRUE(actual_url.find("dstll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
}

UTEST_F(YaMapsBicycleRouterTestFixture, SummaryNoPath) {
  // Request router for summary for impossible route (from 0.0,0.0 to 1.0,1.0
  // points), router returns empty response (in this case Content-Length = 0)

  std::string file_contents = clients::routing::utest::ReadFile(
      "router_yamaps_bicycle/router_yamaps_bicycle_summary_no_path.bin");

  const auto& router = CreateRouter();
  EXPECT_THROW(router.ParseBicycleRouteInfos(file_contents),
               InsolubleRequestError);
}

UTEST_F(YaMapsBicycleRouterTestFixture, SupportedFeatures) {
  const auto& router = CreateRouter();
  // Every feature in this list is used by someone in production!
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRouteInfo));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRoutePath));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kMatrixInfo));
}

struct YaMapsBicycleRouterTestParseWithFilenameParamStruct {
  std::string filename;
  double distance;
  double time;
};

class YaMapsBicycleRouterTestParseWithFilenameParam
    : public YaMapsBicycleRouterTestFixture,
      public ::testing::WithParamInterface<
          YaMapsBicycleRouterTestParseWithFilenameParamStruct> {};

UTEST_P(YaMapsBicycleRouterTestParseWithFilenameParam, ParseValidDocument) {
  auto params = GetParam();

  std::string file_contents =
      clients::routing::utest::ReadFile(params.filename);

  const auto& router = CreateRouter();
  auto results = router.ParseBicycleRouteInfos(file_contents);
  EXPECT_TRUE(!results.empty());
  if (!results.empty()) {
    const auto& route_info = results.front();
    EXPECT_NEAR(params.time, route_info.time->count(), kAbsError);
    EXPECT_NEAR(params.distance, route_info.distance->value(), kAbsError);
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsBicycleRouterTestParseWithFilenameParam,
    Values(
        YaMapsBicycleRouterTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_summary_zero_path.bin",
            0, 0},
        YaMapsBicycleRouterTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_summary_0.bin", 1031,
            386},
        YaMapsBicycleRouterTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_summary_1.bin", 18942,
            5722}));

UTEST_F(YaMapsBicycleRouterTestFixture, RouteNoPath) {
  // Request router for route for impossible route (from 0.0,0.0 to 1.0,1.0
  // points), router returns empty response (in this case Content-Length = 0)

  std::string file_contents = clients::routing::utest::ReadFile(
      "router_yamaps_bicycle/router_yamaps_bicycle_route_no_path.bin");

  const auto& router = CreateRouter();
  EXPECT_THROW(router.ParseRoutePaths(file_contents, clients::routing::Path{},
                                      RouterJams::kNoJams, std::nullopt),
               InsolubleRequestError);
}

struct YaMapsBicycleRouterDetailedTestParseWithFilenameParamStruct {
  std::string filename;
  double distance;
  double time;
  size_t number_of_legs;
  int count;
};

class YaMapsBicycleRouterDetailedTestParseWithFilenameParam
    : public YaMapsBicycleRouterTestFixture,
      public ::testing::WithParamInterface<
          YaMapsBicycleRouterDetailedTestParseWithFilenameParamStruct> {};

UTEST_P(YaMapsBicycleRouterDetailedTestParseWithFilenameParam,
        ParseValidDocument) {
  auto params = GetParam();

  std::string file_contents =
      clients::routing::utest::ReadFile(params.filename);

  const auto& router = CreateRouter();
  const auto& results =
      router.ParseRoutePaths(file_contents, clients::routing::Path{},
                             RouterJams::kNoJams, std::nullopt);
  EXPECT_TRUE(!results.empty());
  if (!results.empty()) {
    const auto& route_path = results.front();
    EXPECT_NEAR(params.time, route_path.info.time->count(), kAbsError);
    EXPECT_NEAR(params.distance, route_path.info.distance->value(), kAbsError);

    const auto& route_points = route_path.path;
    ASSERT_EQ(params.count, route_points.size());

    EXPECT_EQ(0.0, route_points.front().time_since_ride_start.count());
    EXPECT_EQ(0.0, route_points.front().distance_since_ride_start.value());

    EXPECT_NEAR(route_path.info.time->count(),
                route_points.back().time_since_ride_start.count(), kAbsError);
    EXPECT_NEAR(route_path.info.distance->value(),
                route_points.back().distance_since_ride_start.value(),
                kAbsError);

    EXPECT_NEAR(37.565971, route_points.back().longitude.value(), kAbsPosError);
    EXPECT_NEAR(55.682605, route_points.back().latitude.value(), kAbsPosError);

    EXPECT_EQ(params.number_of_legs, route_path.legs.size());
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsBicycleRouterDetailedTestParseWithFilenameParam,
    Values(
        YaMapsBicycleRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_route_zero_path.bin",
            0, 0, 1, 2},
        YaMapsBicycleRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_route_0.bin", 1031,
            386, 1, 60},
        YaMapsBicycleRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_bicycle/router_yamaps_bicycle_route_1.bin", 18942,
            5722, 1, 959}));

class YaMapsBicycleRouterMNTestParseWithFilenameParam
    : public YaMapsBicycleRouterTestFixture,
      public ::testing::WithParamInterface<
          std::tuple<std::string, narray::Array2D<MatrixInfo>>> {};

UTEST_P(YaMapsBicycleRouterMNTestParseWithFilenameParam, ParseValidDocument) {
  auto params = GetParam();

  std::string input_file = std::get<0>(params);
  std::string file_contents = clients::routing::utest::ReadFile(input_file);

  const auto& router = CreateRouter();
  const auto& result = router.ParseBicycleMatrixInfo(file_contents);

  narray::Array2D<MatrixInfo> expected_result = std::get<1>(params);

  ASSERT_EQ(expected_result.size(), result.size());
  for (size_t i = 0; i < result.RowCount(); ++i) {
    for (size_t j = 0; j < result.ColumnCount(); ++j) {
      EXPECT_EQ(expected_result[i][j].src_point_idx,
                result[i][j].src_point_idx);
      EXPECT_EQ(expected_result[i][j].dst_point_idx,
                result[i][j].dst_point_idx);
      EXPECT_EQ(expected_result[i][j].time, result[i][j].time);
      EXPECT_EQ(expected_result[i][j].distance, result[i][j].distance);
    }
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteBicycleParsing, YaMapsBicycleRouterMNTestParseWithFilenameParam,
    Values(
        std::make_tuple(
            "router_yamaps_bicycle/router_yamaps_bicycle_matrix_0.bin",
            narray::Array2D<MatrixInfo>(
                {MatrixInfo(0, 0, MatrixInfo::Time{1},
                            MatrixInfo::Distance::from_value(3)),
                 MatrixInfo(0, 1, MatrixInfo::Time{3},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 0, MatrixInfo::Time{3},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 1, MatrixInfo::Time{1},
                            MatrixInfo::Distance::from_value(3))},
                2)),
        std::make_tuple(
            "router_yamaps_bicycle/router_yamaps_bicycle_matrix_no_route.bin",
            narray::Array2D<MatrixInfo>(
                {MatrixInfo(0, 0, std::nullopt, std::nullopt),
                 MatrixInfo(0, 1, std::nullopt, std::nullopt),
                 MatrixInfo(1, 0, MatrixInfo::Time{3},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 1, MatrixInfo::Time{1},
                            MatrixInfo::Distance::from_value(3))},
                2))));
