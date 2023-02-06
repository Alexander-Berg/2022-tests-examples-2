#include <gtest/gtest.h>

#include <gmock/gmock-matchers.h>
#include <gmock/gmock-more-matchers.h>
#include <clients/routing/exceptions.hpp>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>

#include "vendors/yamaps/yamaps_masstransit_router.hpp"
#include "vendors/yamaps/yamaps_router.hpp"
#include "vendors/yamaps/yamaps_router_test_fixture_test.hpp"

using ::testing::Bool;
using ::testing::Combine;
using ::testing::Range;
using ::testing::Values;

using clients::routing::InsolubleRequestError;
using clients::routing::Path;
using clients::routing::Points;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterFeatures;
using clients::routing::RouterJams;
using clients::routing::RouterSettings;
using clients::routing::RouterTransportType;
using clients::routing::RouterTransportTypes;
using clients::routing::RouterVehicleType;
using clients::routing::YaMapsMasstransitRouter;

class YaMapsMasstransitRouterTest : public YaMapsMasstransitRouter {
 public:
  using YaMapsMasstransitRouter::ParseRouteInfos;
  using YaMapsMasstransitRouter::ParseRoutePaths;
  using YaMapsMasstransitRouter::YaMapsMasstransitRouter;

  std::string MakeMasstransitUrl(const Path& path, const RequestType& type,
                                 const RouterSettings& settings) const {
    return YaMapsMasstransitRouter::MakeUrl(path, type, settings, {}, {});
  }
};

namespace {

static const double kAbsError = 0.1;
static const double kAbsPosError = 0.003;

}  // namespace

struct YaMapsMasstransitRouterTestFixture : YaMapsRouterTestFixture {
  YaMapsMasstransitRouterTest CreateRouter() {
    const std::string& base_url = "http://maps.example.com";
    const std::string& matrix_url = "";

    return YaMapsMasstransitRouterTest(
        *http, {base_url, matrix_url, "", ""}, config_storage.GetSource(),
        std::nullopt, RouterVehicleType::kVehicleMasstransit, nullptr);
  }
};

UTEST_F(YaMapsMasstransitRouterTestFixture, MakeQueryUrlLinear) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakeMasstransitUrl(
      path, YaMapsMasstransitRouter::RequestType::kSummary, {});

  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(
      actual_url.find("http://maps.example.com/masstransit/v2/summary") !=
      std::string::npos);
}

UTEST_F(YaMapsMasstransitRouterTestFixture, MakeQueryUrlLinearRoute) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakeMasstransitUrl(
      path, YaMapsMasstransitRouter::RequestType::kFull, {});

  ASSERT_TRUE(actual_url.find("rll=-1.400000%2C2.400000"
                              "~3.400000%2C-7.400000") != std::string::npos);
  ASSERT_TRUE(actual_url.find("http://maps.example.com/masstransit/v2/route") !=
              std::string::npos);
}

UTEST_F(YaMapsMasstransitRouterTestFixture, MakeQueryAvoidUrl) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  RouterSettings settings;
  settings.avoid_transport = RouterTransportTypes::kTransportSuburban |
                             RouterTransportTypes::kTransportUnderground;

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakeMasstransitUrl(
      path, YaMapsMasstransitRouter::RequestType::kFull, settings);

  ASSERT_TRUE(actual_url.find("avoid=suburban%2Cunderground") !=
              std::string::npos);
}

UTEST_F(YaMapsMasstransitRouterTestFixture, MakeQueryAvoidUrl2) {
  using namespace ::geometry::literals;
  Path path{{-1.4_lon, 2.4_lat}, {3.4_lon, -7.4_lat}};

  RouterSettings settings;
  settings.avoid_transport = RouterTransportTypes::kTransportMinibus;

  const auto& router = CreateRouter();
  const std::string& actual_url = router.MakeMasstransitUrl(
      path, YaMapsMasstransitRouter::RequestType::kFull, settings);

  ASSERT_TRUE(actual_url.find("avoid=minibus") != std::string::npos);
}

UTEST_F(YaMapsMasstransitRouterTestFixture, NoPath) {
  // Request router for summary for impossible route (destionation point 0.0,
  // 0.0), router returns empty response (in this case Content-Length = 0)

  std::string file_contents = clients::routing::utest::ReadFile(
      "router_yamaps_masstransit/router_masstransit_yamaps_no_path.bin");

  const auto& router = CreateRouter();
  EXPECT_THROW(router.ParseRouteInfos(file_contents, RouterJams::kNoJams),
               InsolubleRequestError);
}

UTEST_F(YaMapsMasstransitRouterTestFixture, SupportedFeatures) {
  const auto& router = CreateRouter();
  // Every feature in this list is used by someone in production!
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRouteInfo));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kRoutePath));
  EXPECT_TRUE(router.HasFeatures(RouterFeatures::kMatrixInfo));
}

struct YaMapsMasstransitRouterDetailedTestParseWithFilenameParamStruct {
  std::string filename;
  double distance;
  double time;
  size_t number_of_legs;
  int count;
  std::string vehicle;
};

struct YaMapsMasstransitRouterDetailedTestParseWithFilenameParam
    : public YaMapsMasstransitRouterTestFixture,
      public ::testing::WithParamInterface<
          YaMapsMasstransitRouterDetailedTestParseWithFilenameParamStruct> {};

UTEST_P(YaMapsMasstransitRouterDetailedTestParseWithFilenameParam,
        ParseValidDocument) {
  auto params = GetParam();

  std::string file_contents =
      clients::routing::utest::ReadFile(params.filename);

  const auto& router = CreateRouter();
  const auto& results =
      router.ParseRoutePaths(file_contents, clients::routing::Path{},
                             RouterJams::kNoJams, std::nullopt);
  ASSERT_FALSE(results.empty());

  const auto& points_info_ptr = results.front();
  EXPECT_NEAR(params.time, points_info_ptr.info.time->count(), kAbsError);
  EXPECT_NEAR(params.distance, points_info_ptr.info.distance->value(),
              kAbsError);

  const auto& route_points = points_info_ptr.path;
  ASSERT_EQ(params.count, route_points.size());

  EXPECT_EQ(0.0, route_points[0].time_since_ride_start.count());
  EXPECT_EQ(0.0, route_points[0].distance_since_ride_start.value());
  EXPECT_NEAR(37.524284, route_points[0].longitude.value(), kAbsPosError);
  EXPECT_NEAR(55.700008, route_points[0].latitude.value(), kAbsPosError);

  // Allowed error is 2% here, it's too much and should be
  // decreased when problem with diferent distance calculation will be
  // solved
  EXPECT_NEAR(params.time, route_points.back().time_since_ride_start.count(),
              params.time * 0.02);
  EXPECT_NEAR(params.distance,
              route_points.back().distance_since_ride_start.value(),
              params.distance * 0.02);

  EXPECT_EQ(params.number_of_legs, points_info_ptr.legs.size());
  EXPECT_THAT(points_info_ptr.vehicle_type_legs,
              ::testing::Optional(::testing::ElementsAre(::testing::Field(
                  &routing_base::VehicleTypeLeg::vehicle_types,
                  ::testing::UnorderedElementsAre(params.vehicle)))));
}
INSTANTIATE_UTEST_SUITE_P(
    TestRouteParsing, YaMapsMasstransitRouterDetailedTestParseWithFilenameParam,
    Values(
        YaMapsMasstransitRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_masstransit/avoid_bus.bin", 6594, 1862, 1, 61,
            "underground"},
        YaMapsMasstransitRouterDetailedTestParseWithFilenameParamStruct{
            "router_yamaps_masstransit/avoid_underground.bin", 6204, 1505, 1,
            23, "bus"}));
