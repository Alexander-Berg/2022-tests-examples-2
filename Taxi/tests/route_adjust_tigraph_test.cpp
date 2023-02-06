#include <gtest/gtest.h>

#include <clients/adjusting/tigraph/route_adjust_tigraph.hpp>
#include <utils/file_system.hpp>

namespace {

using clients::route_adjust::ClientTigraph;
using clients::route_adjust::Result;

std::string ReadBody(const std::string& file_name) {
  return utils::ReadFile(SOURCE_DIR "/tests/static/" + file_name);
}

}  // namespace

TEST(RouteAdjustTigraph, IncorrectResponse) {
  LogExtra log_extra;

  EXPECT_ANY_THROW(ClientTigraph::ParseResponseBody({}, "", false, log_extra));
  EXPECT_ANY_THROW(
      ClientTigraph::ParseResponseBody({}, "HelloWorld!", false, log_extra));
  EXPECT_ANY_THROW(ClientTigraph::ParseResponseBody({}, "1", false, log_extra));
  EXPECT_ANY_THROW(
      ClientTigraph::ParseResponseBody({}, "{}", false, log_extra));
}

TEST(RouteAdjustTigraph, Simple) {
  LogExtra log_extra;
  const auto& body = ReadBody("ra_tigraph_body.blob");

  Result result;
  ASSERT_NO_THROW(
      result = ClientTigraph::ParseResponseBody({}, body, false, log_extra));

  // track
  ASSERT_FALSE(result.track.empty());
  EXPECT_GE(4u, result.track.size());  // DropSameTimePoints dropped a point
  EXPECT_GE(result.track.front().timestamp, result.track.back().timestamp);

  // probable_positions
  ASSERT_FALSE(result.edge_position.empty());
  EXPECT_EQ(result.track.front().timestamp, result.edge_position.timestamp);
  ASSERT_FALSE(result.edge_position.options.front().empty());
}

struct TwoSamePointsTestParam {
  bool do_not_calc_directions_experiment = false;
  double point0direction = 0.0;
  double point1direction = 0.0;
};

class TigraphTest : public ::testing::TestWithParam<TwoSamePointsTestParam> {};

TEST_P(TigraphTest, TwoSamePointsTrack) {
  const auto& param = GetParam();
  const auto track = [] {
    utils::geometry::Track track;
    const utils::geometry::TrackPoint point{39.752557, 43.563217, 155.4, 58.5,
                                            1000};
    track.push_back(point);
    track.push_back(point);
    return track;
  }();

  const auto& body = ReadBody("two_same_points.json");
  LogExtra log_extra;

  const auto& result_track = ClientTigraph::ParseResponseBody(
      track, body, param.do_not_calc_directions_experiment, log_extra);

  ASSERT_NEAR(param.point0direction, result_track.track[0].direction, 0.01);
  ASSERT_NEAR(param.point1direction, result_track.track[1].direction, 0.01);
}

INSTANTIATE_TEST_CASE_P(
    TwoSamePoints, TigraphTest,
    ::testing::Values(TwoSamePointsTestParam{false, -1.0, -1.0},
                      TwoSamePointsTestParam{true, 127.768, 127.768}), );
