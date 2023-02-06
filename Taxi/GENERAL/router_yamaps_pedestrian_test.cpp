#include <gtest/gtest.h>

#include <clients/routing/exceptions.hpp>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>

#include "vendors/yamaps/yamaps_pedestrian_router.hpp"
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
using clients::routing::YaMapsPedestrianRouter;

class YaMapsPedestrianRouterTest : public YaMapsPedestrianRouter {
 public:
  using YaMapsPedestrianRouter::MakeMatrixUrl;
  using YaMapsPedestrianRouter::ParseRouteInfos;
  using YaMapsPedestrianRouter::ParseRoutePaths;
  using YaMapsPedestrianRouter::YaMapsPedestrianRouter;

  std::string MakePedestrianUrl(const Path& path, const RequestType& type,
                                const RouterSettings& settings) const {
    return YaMapsPedestrianRouter::MakeUrl(path, type, settings, {}, {});
  }

  narray::Array2D<MatrixInfo> ParsePedestrianMatrixInfo(
      const std::string& serialized) const {
    return YaMapsPedestrianRouter::ParseMatrixInfo(serialized);
  }
};

struct YaMapsPedestrianRouterTestFixture : YaMapsRouterTestFixture {
  YaMapsPedestrianRouterTest CreateRouter() {
    return YaMapsPedestrianRouterTest(
        *http, {base_url, matrix_url, "", ""}, config_storage.GetSource(),
        std::nullopt, RouterVehicleType::kVehiclePedestrian, nullptr);
  }
};

namespace {

static const double kAbsError = 0.1;
static const double kAbsPosError = 0.003;

}  // namespace

UTEST_F(YaMapsPedestrianRouterTestFixture, MakeQueryUrlLinear) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakePedestrianUrl(
      path, YaMapsPedestrianRouter::RequestType::kSummary, {});

  ASSERT_TRUE(
      actual_url.find("http://maps.example.com/pedestrian/v2/summary") !=
      std::string::npos);
}

UTEST_F(YaMapsPedestrianRouterTestFixture, MakeQueryUrl) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};
  Directions dirs{std::nullopt, geometry::Azimuth::from_value(15)};

  const auto& router = CreateRouter();
  const std::string& actual_url =
      router.MakeMatrixUrl(path, dirs, path, dirs, {});

  ASSERT_TRUE(actual_url.find("srcll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("dstll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
}

UTEST_F(YaMapsPedestrianRouterTestFixture, NoPath) {
  // Request router for summary for impossible route (destionation point 0.0,
  // 0.0), router returns empty response (in this case Content-Length = 0)

  std::string file_contents = clients::routing::utest::ReadFile(
      "router_yamaps_pedestrian/router_pedestrian_yamaps_no_path.bin");

  const auto& router = CreateRouter();
  EXPECT_THROW(router.ParseRouteInfos(file_contents, RouterJams::kNoJams),
               InsolubleRequestError);
}

UTEST_F(YaMapsPedestrianRouterTestFixture, SupportedFeatures) {
  const auto& router = CreateRouter();
  // Every feature in this list is used by someone in production!
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRouteInfo));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRoutePath));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kMatrixInfo));
}

class YaMapsPedestrianRouterMNTestParseWithFilenameParam
    : public YaMapsPedestrianRouterTestFixture,
      public ::testing::WithParamInterface<
          std::tuple<std::string, narray::Array2D<MatrixInfo>>> {};

UTEST_P(YaMapsPedestrianRouterMNTestParseWithFilenameParam,
        ParseValidDocument) {
  auto params = GetParam();

  std::string input_file = std::get<0>(params);
  std::string file_contents = clients::routing::utest::ReadFile(input_file);

  const auto& router = CreateRouter();
  const auto& result = router.ParsePedestrianMatrixInfo(file_contents);

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
    TestRoutePedestrianParsing,
    YaMapsPedestrianRouterMNTestParseWithFilenameParam,
    Values(
        std::make_tuple(
            "router_yamaps_pedestrian/yamaps_router_pedestrian_mn.bin",
            narray::Array2D<MatrixInfo>(
                {MatrixInfo(0, 0, MatrixInfo::Time{2},
                            MatrixInfo::Distance::from_value(3)),
                 MatrixInfo(0, 1, MatrixInfo::Time{8},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 0, MatrixInfo::Time{8},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 1, MatrixInfo::Time{2},
                            MatrixInfo::Distance::from_value(3))},
                2)),
        std::make_tuple(
            "router_yamaps_pedestrian/yamaps_router_pedestrian_mn_no_route.bin",
            narray::Array2D<MatrixInfo>(
                {MatrixInfo(0, 0, std::nullopt, std::nullopt),
                 MatrixInfo(0, 1, std::nullopt, std::nullopt),
                 MatrixInfo(1, 0, MatrixInfo::Time{8},
                            MatrixInfo::Distance::from_value(11)),
                 MatrixInfo(1, 1, MatrixInfo::Time{2},
                            MatrixInfo::Distance::from_value(3))},
                2))));

struct YaMapsPedestrianRouterDetailedTestParseWithFilenameParamStruct {
  std::string filename;
  double distance;
  double time;
  size_t number_of_legs;
  int count;
};

class YaMapsPedestrianRouterDetailedTestParseWithFilenameParam
    : public YaMapsPedestrianRouterTestFixture,
      public ::testing::WithParamInterface<
          YaMapsPedestrianRouterDetailedTestParseWithFilenameParamStruct> {};

UTEST_P(YaMapsPedestrianRouterDetailedTestParseWithFilenameParam,
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
    const auto& points_info_ptr = results.front();
    EXPECT_NEAR(params.time, points_info_ptr.info.time->count(), kAbsError);
    EXPECT_NEAR(params.distance, points_info_ptr.info.distance->value(),
                kAbsError);

    const auto& route_points = points_info_ptr.path;
    ASSERT_EQ(params.count, route_points.size());

    EXPECT_EQ(0.0, route_points[0].time_since_ride_start.count());
    EXPECT_EQ(0.0, route_points[0].distance_since_ride_start.value());
    EXPECT_NEAR(37.642492, route_points[0].longitude.value(), kAbsPosError);
    EXPECT_NEAR(55.734974, route_points[0].latitude.value(), kAbsPosError);

    // Allowed error is 2% here, it's too much and should be
    // decreased when problem with diferent distance calculation will be
    // solved
    EXPECT_NEAR(params.time, route_points.back().time_since_ride_start.count(),
                params.time * 0.02);
    EXPECT_NEAR(params.distance,
                route_points.back().distance_since_ride_start.value(),
                params.distance * 0.02);
    EXPECT_EQ(params.number_of_legs, points_info_ptr.legs.size());
  }
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsPedestrianRouterDetailedTestParseWithFilenameParam,
    Values(
        YaMapsPedestrianRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_pedestrian/router_pedestrian_yamaps_0.bin", 4169,
            3002, 1, 206},
        YaMapsPedestrianRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_pedestrian/router_pedestrian_yamaps_1.bin", 341, 245,
            2, 30}));
