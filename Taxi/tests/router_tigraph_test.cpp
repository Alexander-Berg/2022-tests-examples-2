#include <gtest/gtest.h>

#include <fstream>

#include <clients/router_exceptions.hpp>
#include <clients/router_tigraph.hpp>
#include <common/mock_handlers_context.hpp>
#include <handlers/context.hpp>
#include <threads/async.hpp>
#include <utils/file_system.hpp>

namespace {

const std::string kBaseUrl = "http://graph.taxi.tst.yandex.net";

using clients::routing::RouterTiGraph;

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

class TiGraphRouterWithAmountOfPointsAndJams
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<int, bool>>,
      public MockHeadersContext {};

TEST_P(TiGraphRouterWithAmountOfPointsAndJams, FailsOnShortPath) {
  using utils::geometry::kNoDirection;

  int path_length = 0;
  bool with_jams = false;
  std::tie(path_length, with_jams) = GetParam();

  RouterTiGraph router(http_client(), graphite(), kBaseUrl, with_jams);
  RouterTiGraph::path_t path(path_length);

  EXPECT_THROW(router.RouteEx(path, kNoDirection, GetContext(), {}, {}),
               clients::routing::BadRequestError);
  EXPECT_THROW(router.Route(path, kNoDirection, GetContext(), {}),
               clients::routing::BadRequestError);
  EXPECT_THROW(router.GetWaypointInfo(path, GetContext(), {}),
               clients::routing::BadRequestError);
}

INSTANTIATE_TEST_CASE_P(TiGraphRouter, TiGraphRouterWithAmountOfPointsAndJams,
                        testing::Combine(testing::Range(0, 2),
                                         testing::Bool()), );

class TiGraphRouterParseSummary
    : public testing::Test,
      public testing::WithParamInterface<const char*>,
      public MockHeadersContext {};

TEST_P(TiGraphRouterParseSummary, ValidDocument) {
  const std::string& json = ReadFile(GetParam());

  const auto& route_info =
      RouterTiGraph::ParseSummaryResponse(json, GetContext().log_extra);
  EXPECT_LT(0.0, route_info.total_distance);
  EXPECT_LT(0.0, route_info.total_time);
}

INSTANTIATE_TEST_CASE_P(TiGraphRouter, TiGraphRouterParseSummary,
                        testing::Values("router_tigraph/summary_no_jams.json",
                                        "router_tigraph/summary_jams.json"), );

class TiGraphRouterParseWaypoint
    : public testing::Test,
      public testing::WithParamInterface<const char*>,
      public MockHeadersContext {};

TEST_P(TiGraphRouterParseWaypoint, ValidDocument) {
  const std::string& json = ReadFile(GetParam());

  const auto& route_info = RouterTiGraph::ParseFullResponse(json, GetContext());
  EXPECT_LT(0.0, route_info->total_distance);
  EXPECT_LT(0.0, route_info->total_time);

  // waypoints
  const auto& waypoints = route_info->GetWaypoints();
  EXPECT_EQ(2u, waypoints.size());
  EXPECT_EQ(0.0, waypoints.front().time_since_ride_start.count());
  EXPECT_EQ(0.0, waypoints.front().distance_since_ride_start);
  EXPECT_EQ(route_info->GetTotalTime(),
            waypoints.back().time_since_ride_start.count());
  EXPECT_EQ(route_info->GetTotalDistance(),
            waypoints.back().distance_since_ride_start);

  // movement
  const auto& movement = route_info->GetMovement();
  EXPECT_EQ(338u, movement.size());
  for (size_t i = 1; i < movement.size(); ++i) {
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
  EXPECT_EQ(338u, path.size());
}

INSTANTIATE_TEST_CASE_P(TiGraphRouter, TiGraphRouterParseWaypoint,
                        testing::Values("router_tigraph/full_no_jams.json",
                                        "router_tigraph/full_jams.json"), );

class TiGraphRouterParseBadRequest
    : public testing::Test,
      public testing::WithParamInterface<const char*>,
      public MockHeadersContext {};

TEST_P(TiGraphRouterParseBadRequest, OneBad) {
  const std::string& json = ReadFile(GetParam());
  EXPECT_ANY_THROW(RouterTiGraph::ParseFullResponse(json, GetContext()));
}

INSTANTIATE_TEST_CASE_P(TiGraphRouter, TiGraphRouterParseBadRequest,
                        testing::Values("router_tigraph/error_invalid.json"), );

class TiGraphRouterTestWithExpectedUrlParams
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<bool, std::string>>,
      public MockHeadersContext {};

TEST_P(TiGraphRouterTestWithExpectedUrlParams, MakeData) {
  bool with_jams = std::get<0>(GetParam());
  const std::string& expected_data = std::get<1>(GetParam());

  RouterTiGraph router(http_client(), graphite(), kBaseUrl, with_jams);
  RouterTiGraph::path_t path;

  path.emplace_back(1, 1);
  path.emplace_back(2, 2);

  const std::string& actual_data =
      router.MakeData(path, RouterTiGraph::Mode::kFull, {});
  ASSERT_EQ(expected_data, actual_data);
}

INSTANTIATE_TEST_CASE_P(
    MakeData, TiGraphRouterTestWithExpectedUrlParams,
    testing::Values(std::make_tuple(true,
                                    "{\"detailed_info\":true,\"point_"
                                    "discretization\":300,\"route\":[[1.0,1.0],"
                                    "[2.0,"
                                    "2.0]],\"use_jams\":true}"),
                    std::make_tuple(false,
                                    "{\"detailed_info\":true,\"point_"
                                    "discretization\":300,\"route\":[[1.0,1.0],"
                                    "[2.0,"
                                    "2.0]],\"use_jams\":false}")), );
