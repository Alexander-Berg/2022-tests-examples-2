#include <gtest/gtest.h>
#include <userver/formats/json/serialize.hpp>

#include <clients/routing/exceptions.hpp>
#include <vendors/tigraph/router_tigraph.hpp>

#include <utest/routing/file_utils.hpp>
#include <utest/routing/mock_config_test.hpp>
#include <utest/routing/mock_http_client.hpp>
#include <utest/routing/router_test_fixture_test.hpp>

using clients::routing::BadRequestError;
using clients::routing::DirectionOpt;
using clients::routing::Path;
using clients::routing::RouteInfo;
using clients::routing::RoutePath;
using clients::routing::RouterJams;
using clients::routing::RouterMode;
using clients::routing::RouterSettings;
using clients::routing::RouterTiGraph;
using clients::routing::RouterTolls;

class RouterTiGraphTest : public RouterTiGraph {
 public:
  using RouterTiGraph::RouterTiGraph;

  std::string MakeBody(const Path& path, const DirectionOpt& source_direction,
                       const RequestType& type,
                       const RouterSettings& settings) const {
    return RouterTiGraph::MakeBody(path, source_direction, type, settings);
  }

  RouteInfo ParseRouteInfo(const std::string& response) const {
    return RouterTiGraph::ParseRouteInfo(response);
  }

  RoutePath ParseRoutePath(const std::string& response) const {
    return RouterTiGraph::ParseRoutePath(response);
  }
};

struct TiGraphRouterTestFixture : RouterTestFixture {
  RouterTiGraphTest CreateRouter() {
    const std::string base_url = "http://tigraph-router.taxi.yandex.net";
    return RouterTiGraphTest(*http, base_url, config_storage.GetSource());
  }
};

class TiGraphRouterWithAmountOfPointsAndJams
    : public TiGraphRouterTestFixture,
      public testing::WithParamInterface<std::tuple<int, bool>> {};

UTEST_P(TiGraphRouterWithAmountOfPointsAndJams, FailsOnShortPath) {
  int path_length = 0;
  bool with_jams = false;
  std::tie(path_length, with_jams) = GetParam();

  Path path(path_length);
  RouterJams jams = with_jams ? RouterJams::kJams : RouterJams::kNoJams;

  auto router = CreateRouter();

  EXPECT_THROW(router.MakeBody(path, std::nullopt,
                               RouterTiGraph::RequestType::kSummary, {jams}),
               BadRequestError);
}
INSTANTIATE_UTEST_SUITE_P(TiGraphRouter, TiGraphRouterWithAmountOfPointsAndJams,
                          testing::Combine(testing::Range(0, 2),
                                           testing::Bool()));

class TiGraphRouterParseSummary
    : public TiGraphRouterTestFixture,
      public testing::WithParamInterface<const char*> {};

UTEST_P(TiGraphRouterParseSummary, ValidDocument) {
  const std::string& json = clients::routing::utest::ReadFile(GetParam());

  auto router = CreateRouter();
  const auto& route_info = router.ParseRouteInfo(json);

  EXPECT_NEAR(9681.0, route_info.distance->value(), 0.001);
  EXPECT_LT(1000.0, route_info.time->count());

  EXPECT_EQ(false, *route_info.blocked);
  EXPECT_EQ(false, *route_info.has_dead_jam);
  EXPECT_EQ(false, *route_info.has_toll_roads);
}

// {"route": [[37.643409,55.734588], [37.582377,55.784164]], "use_jams": ...}
INSTANTIATE_UTEST_SUITE_P(TiGraphRouter, TiGraphRouterParseSummary,
                          testing::Values("router_tigraph/summary_no_jams.json",
                                          "router_tigraph/summary_jams.json"));

class TiGraphRouterParseFull : public TiGraphRouterTestFixture,
                               public testing::WithParamInterface<const char*> {
};

UTEST_P(TiGraphRouterParseFull, ValidDocument) {
  const std::string& json = clients::routing::utest::ReadFile(GetParam());

  auto router = CreateRouter();
  const auto& route_path = router.ParseRoutePath(json);

  EXPECT_NEAR(2060.0, route_path.info.distance->value(), 0.001);
  EXPECT_LT(249.0, route_path.info.time->count());

  EXPECT_EQ(false, *route_path.info.blocked);
  EXPECT_EQ(false, *route_path.info.has_dead_jam);
  EXPECT_EQ(false, *route_path.info.has_toll_roads);

  const auto& path = route_path.path;
  EXPECT_EQ(64u, path.size());
  for (size_t i = 1; i < path.size(); ++i) {
    EXPECT_LE(path[i - 1].time_since_ride_start, path[i].time_since_ride_start);
    EXPECT_LE(path[i - 1].distance_since_ride_start,
              path[i].distance_since_ride_start);
  }
  EXPECT_EQ(0.0, path.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, path.front().distance_since_ride_start.value());
  EXPECT_EQ(route_path.info.time->count(),
            path.back().time_since_ride_start.count());
  EXPECT_EQ(route_path.info.distance->value(),
            path.back().distance_since_ride_start.value());

  EXPECT_EQ(2, route_path.legs.size());
  EXPECT_EQ(0, route_path.legs[0].point_index);
  EXPECT_EQ(10, route_path.legs[1].point_index);
}

// {"route": [[37.531405,55.696361], [37.531661,55.709434]], "request_path":
// true, "use_jams": ...}
INSTANTIATE_UTEST_SUITE_P(TiGraphRouter, TiGraphRouterParseFull,
                          testing::Values("router_tigraph/full_no_jams.json",
                                          "router_tigraph/full_jams.json"));

class TiGraphRouterParseBadRequest
    : public TiGraphRouterTestFixture,
      public testing::WithParamInterface<const char*> {};

UTEST_P(TiGraphRouterParseBadRequest, OneBad) {
  const std::string& json = clients::routing::utest::ReadFile(GetParam());
  auto router = CreateRouter();
  EXPECT_ANY_THROW(router.ParseRouteInfo(json));
}
INSTANTIATE_UTEST_SUITE_P(TiGraphRouter, TiGraphRouterParseBadRequest,
                          testing::Values("router_tigraph/error_invalid.json"));

class TiGraphRouterTestWithExpectedUrlParams
    : public TiGraphRouterTestFixture,
      public testing::WithParamInterface<std::tuple<bool, bool, std::string>> {
};

UTEST_P(TiGraphRouterTestWithExpectedUrlParams, MakeBody) {
  bool with_jams = std::get<0>(GetParam());
  RouterJams jams = with_jams ? RouterJams::kJams : RouterJams::kNoJams;

  const std::string& expected_data = std::get<2>(GetParam());
  RouterTiGraph::RequestType type = std::get<1>(GetParam())
                                        ? RouterTiGraph::RequestType::kFull
                                        : RouterTiGraph::RequestType::kSummary;

  using namespace ::geometry::literals;
  Path path = {{1.0_lon, 1.0_lat}, {2.0_lon, 2.0_lat}};

  auto router = CreateRouter();

  const std::string& actual_data =
      router.MakeBody(path, std::nullopt, type,
                      {jams, RouterMode::kApprox, RouterTolls::kNoTolls});
  ASSERT_EQ(formats::json::FromString(expected_data),
            formats::json::FromString(actual_data));
}

// clang-format off
INSTANTIATE_UTEST_SUITE_P(MakeData, TiGraphRouterTestWithExpectedUrlParams,
                         testing::Values(
                            std::make_tuple(true, false,
                              R"json(
                                {
                                  "request_path": false,
                                  "point_discretization": 300,
                                  "route": [[1.0,1.0],[2.0,2.0]],
                                  "use_jams": true,
                                  "use_tolls": false,
                                  "mode": "approx"
                                }
                              )json"),
                             std::make_tuple(false, false,
                              R"json(
                                {
                                  "request_path": false,
                                  "point_discretization": 300,
                                  "route": [[1.0,1.0],[2.0,2.0]],
                                  "use_jams": false,
                                  "use_tolls": false,
                                  "mode": "approx"
                                }
                              )json"),
                             std::make_tuple(false, true,
                              R"json(
                                {
                                  "request_path": true,
                                  "point_discretization": 300,
                                  "route": [[1.0,1.0],[2.0,2.0]],
                                  "use_jams": false,
                                  "use_tolls": false,
                                  "mode": "approx"
                                }
                              )json")
                         ));
// clang-format on
