#include <gtest/gtest-param-test.h>
#include <gtest/gtest.h>

#include <clients/routing/exceptions.hpp>
#include <cstdint>
#include <optional>
#include <string>
#include <tuple>
#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>

#include "clients/routing/router_types.hpp"
#include "vendors/vendor.hpp"
#include "vendors/yamaps/matrix_tester.hpp"
#include "vendors/yamaps/yamaps_bicycle_family_router.hpp"
#include "vendors/yamaps/yamaps_car_family_router.hpp"
#include "vendors/yamaps/yamaps_masstransit_router.hpp"
#include "vendors/yamaps/yamaps_pedestrian_router.hpp"
#include "vendors/yamaps/yamaps_router.hpp"
#include "vendors/yamaps/yamaps_router_test_fixture_test.hpp"
#include "vendors/yamaps/yamaps_router_vendor.hpp"

#include <routing-base/router_settings.hpp>

using ::testing::Bool;
using ::testing::Combine;
using ::testing::Range;
using ::testing::Values;

using clients::routing::Directions;
using clients::routing::InsolubleRequestError;
using clients::routing::MatrixInfo;
using clients::routing::Path;
using clients::routing::Point;
using clients::routing::Points;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterSettings;
using clients::routing::RouterTolls;
using clients::routing::RouterVehicle;
using clients::routing::RouterVehicleType;
using clients::routing::Tester;
using clients::routing::Vendor;
using clients::routing::YaMapsBicycleFamilyRouter;
using clients::routing::YaMapsCarFamilyRouter;
using clients::routing::YaMapsMasstransitRouter;
using clients::routing::YaMapsPedestrianRouter;
using clients::routing::YaMapsRouter;
using clients::routing::YaMapsRouterVendor;
using routing_base::DirectionOpt;
using routing_base::ExperimentalArgs;

namespace {

bool IsUrlVehicle(RouterVehicleType type) {
  switch (type) {
    case RouterVehicleType::kVehicleCar:
    case RouterVehicleType::kVehicleTaxi:
    case RouterVehicleType::kVehicleTruck:
    case RouterVehicleType::kVehicleScooter:
    case RouterVehicleType::kVehicleBicycle:
      return true;

    case RouterVehicleType::kVehiclePedestrian:
    case RouterVehicleType::kVehicleMasstransit:
      return false;

    default:
      return false;
  }
}

bool IsCarFamily(RouterVehicleType type) {
  switch (type) {
    case RouterVehicleType::kVehicleCar:
    case RouterVehicleType::kVehicleTaxi:
    case RouterVehicleType::kVehicleTruck:
      return true;

    case RouterVehicleType::kVehicleScooter:
    case RouterVehicleType::kVehicleBicycle:
    case RouterVehicleType::kVehiclePedestrian:
    case RouterVehicleType::kVehicleMasstransit:
      return false;

    default:
      return false;
  }
}

static const double kAbsPosError = 0.003;

}  // namespace

struct YaMapsMatrixRouterTestFixture : public YaMapsRouterTestFixture {
  clients::routing::Tester CreateRouter(RouterVehicleType vehicle_type) {
    const std::string& base_url = "http://maps.example.com";

    auto vendor = YaMapsRouterVendor(
        *http,
        YaMapsRouterVendor::AllBackendsSettings{{{base_url, base_url, "", ""}},
                                                {{base_url, base_url, "", ""}},
                                                {{base_url, base_url, "", ""}},
                                                {{base_url, base_url, "", ""}}},
        config_storage.GetSource(), {}, {});
    auto router_ptr = vendor.GetRouterByType(vehicle_type);
    return Tester{std::dynamic_pointer_cast<YaMapsRouter>(router_ptr)};
  }
};

class YaMapsMatrixRouterRequest
    : public YaMapsMatrixRouterTestFixture,
      public ::testing::WithParamInterface<
          std::tuple<RouterVehicleType, std::optional<int64_t>>> {};

class YaMapsMatrixRouterTestParseMatrix
    : public YaMapsMatrixRouterTestFixture,
      public ::testing::WithParamInterface<std::tuple<
          RouterVehicleType, std::string, narray::Array2D<MatrixInfo>>> {};

class RouterTypeParam
    : public YaMapsMatrixRouterTestFixture,
      public ::testing::WithParamInterface<RouterVehicleType> {};

UTEST_P(YaMapsMatrixRouterRequest, MakeRequestData) {
  const auto [vehicle_type, dtm] = GetParam();

  using namespace ::geometry::literals;
  Points points{{37.588687_lon, 55.733911_lat}, {37.537786_lon, 55.796942_lat}};
  Directions points_dirs{std::nullopt, geometry::Azimuth::from_value(15)};

  RouterSettings settings;
  if (dtm.has_value()) {
    settings.dtm = *dtm;
  }

  const auto& router = CreateRouter(vehicle_type);
  const auto actual_url =
      router.MakeMatrixUrl(points, points_dirs, points, points_dirs, settings);

  if (dtm.has_value()) {
    ASSERT_TRUE(actual_url.find("dtm=" + std::to_string(*dtm)) !=
                std::string::npos);
  }

  if (IsUrlVehicle(vehicle_type)) {
    ASSERT_TRUE(actual_url.find("vehicle_type=" + ToString(vehicle_type)) !=
                std::string::npos);
  } else {
    ASSERT_FALSE(actual_url.find("vehicle_type=") != std::string::npos);
  }

  ASSERT_TRUE(actual_url.find("lang=ru-RU") != std::string::npos);

  ASSERT_TRUE(actual_url.find("srcll=37.588687%2C55.733911"
                              "~37.537786%2C55.796942") != std::string::npos);
  ASSERT_TRUE(actual_url.find("dstll=37.588687%2C55.733911"
                              "~37.537786%2C55.796942") != std::string::npos);

  if (IsCarFamily(vehicle_type)) {
    ASSERT_TRUE(actual_url.find("srcdir=~15") != std::string::npos);
    ASSERT_TRUE(actual_url.find("dstdir=~15") != std::string::npos);
  }

  if (vehicle_type == RouterVehicleType::kVehiclePedestrian) {
    ASSERT_EQ(
        actual_url.rfind('/'),
        std::string("http://maps.example.com/pedestrian/v2/matrix?something")
            .rfind('/'));
  } else {
    ASSERT_EQ(
        actual_url.rfind('/'),
        std::string("http://maps.example.com/v2/matrix?something").rfind('/'));
  }
}

UTEST_P(YaMapsMatrixRouterTestParseMatrix, ParseValidDocument) {
  const auto [vehicle_type, input_file, expected_result] = GetParam();

  std::string file_contents = clients::routing::utest::ReadFile(input_file);
  const auto& router = CreateRouter(vehicle_type);
  const auto& result = router.ParseMatrixInfo(file_contents);

  ASSERT_EQ(expected_result.size(), result.size());
  for (size_t i = 0; i < result.RowCount(); ++i) {
    for (size_t j = 0; j < result.ColumnCount(); ++j) {
      EXPECT_EQ(expected_result[i][j].src_point_idx,
                result[i][j].src_point_idx);
      EXPECT_EQ(expected_result[i][j].dst_point_idx,
                result[i][j].dst_point_idx);

      if (expected_result[i][j].time) {
        EXPECT_EQ(*expected_result[i][j].time, *result[i][j].time);
      } else {
        EXPECT_EQ(expected_result[i][j].time, result[i][j].time);
      }

      if (expected_result[i][j].distance) {
        EXPECT_NEAR(expected_result[i][j].distance->value(),
                    result[i][j].distance->value(), kAbsPosError);
      } else {
        EXPECT_EQ(expected_result[i][j].distance, result[i][j].distance);
      }
    }
  }
}

INSTANTIATE_UTEST_SUITE_P(
    YaMapsMatrixRouterRequest, YaMapsMatrixRouterRequest,
    Values(std::make_tuple(RouterVehicleType::kVehicleCar,
                           1572614121  // dtm
                           ),
           std::make_tuple(RouterVehicleType::kVehicleScooter,
                           std::nullopt  // dtm
                           ),
           std::make_tuple(RouterVehicleType::kVehiclePedestrian,
                           std::nullopt  // dtm
                           )));

INSTANTIATE_UTEST_SUITE_P(
    TestRouteMatrixParsing, YaMapsMatrixRouterTestParseMatrix,
    Values(
        /// car
        std::make_tuple(
            RouterVehicleType::kVehicleCar,
            "router_yamaps_matrix/yamaps_router_matrix.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0)),
                            MatrixInfo(0, 1, MatrixInfo::Time{1823},
                                       MatrixInfo::Distance::from_value(9116)),
                            MatrixInfo(1, 0, MatrixInfo::Time{1823},
                                       MatrixInfo::Distance::from_value(9116)),
                            MatrixInfo(1, 1, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0))},
                2)),
        std::make_tuple(
            RouterVehicleType::kVehicleCar,
            "router_yamaps_matrix/yamaps_router_matrix_no_route.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, std::nullopt, std::nullopt),
                            MatrixInfo(1, 0, std::nullopt, std::nullopt)},
                1)),

        /// bicycle
        std::make_tuple(
            RouterVehicleType::kVehicleBicycle,
            "router_yamaps_bicycle_matrix/yamaps_router_matrix.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0)),
                            MatrixInfo(0, 1, MatrixInfo::Time{1555},
                                       MatrixInfo::Distance::from_value(4166)),
                            MatrixInfo(1, 0, MatrixInfo::Time{1545},
                                       MatrixInfo::Distance::from_value(4167)),
                            MatrixInfo(1, 1, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0))},
                2)),
        std::make_tuple(
            RouterVehicleType::kVehicleBicycle,
            "router_yamaps_bicycle_matrix/yamaps_router_matrix_no_route.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, std::nullopt, std::nullopt),
                            MatrixInfo(1, 0, std::nullopt, std::nullopt)},
                1)),

        /// pedestrian
        std::make_tuple(
            RouterVehicleType::kVehiclePedestrian,
            "router_yamaps_pedestrian_matrix/yamaps_router_matrix.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0)),
                            MatrixInfo(0, 1, MatrixInfo::Time{2277},
                                       MatrixInfo::Distance::from_value(3162)),
                            MatrixInfo(1, 0, MatrixInfo::Time{2277},
                                       MatrixInfo::Distance::from_value(3162)),
                            MatrixInfo(1, 1, MatrixInfo::Time{0},
                                       MatrixInfo::Distance::from_value(0))},
                2)),
        std::make_tuple(
            RouterVehicleType::kVehiclePedestrian,
            "router_yamaps_pedestrian_matrix/yamaps_router_matrix_no_route.bin",
            narray::Array2D<MatrixInfo>(
                std::vector{MatrixInfo(0, 0, std::nullopt, std::nullopt),
                            MatrixInfo(1, 0, std::nullopt, std::nullopt)},
                1))));
