#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <caches/surge_points.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture.hpp>

#include <models/graph_surge_points.hpp>
#include <models/nearest_edges.hpp>
#include <utils/arrange_surge_points.hpp>

namespace tests {
using graph::test::GraphTestFixture;

namespace {

class NearestEdgesTest : public GraphTestFixture {
 protected:
  void SetUp() override {
    using ::geometry::lat;
    using ::geometry::lon;
    using ::models::Point;
    using surge_points_cache::caches::AllPoints;

    GraphTestFixture::SetUp();

    max_distance = 150.0;
    is_multiple_points_assigned = false;
    segmentation_factor = 1;

    using ::models::Point;
    auto add_fixed_point = [this](double x, double y, std::string position_id) {
      fixed_points.push_back(models::FixedPoint{Point(x, y), position_id});
    };

    add_fixed_point(37.617646, 55.774543, "a");
  }

  std::vector<models::FixedPoint> fixed_points;
  double max_distance;
  bool is_multiple_points_assigned;
  double segmentation_factor;
};

UTEST_F(NearestEdgesTest, MaxRoadRankValueTen) {
  models::GraphSurgePoints graph_fixed_points{GetGraph()};

  int max_road_rank = 10;

  std::vector<models::NearestEdge> nearest_edges = models::GetNearestEdges(
      fixed_points, max_distance, is_multiple_points_assigned,
      segmentation_factor, max_road_rank, graph_fixed_points);

  ASSERT_EQ(nearest_edges.size(), 5);
}

UTEST_F(NearestEdgesTest, MaxRoadRankValueSix) {
  models::GraphSurgePoints graph_fixed_points{GetGraph()};

  int max_road_rank = 6;

  std::vector<models::NearestEdge> nearest_edges = models::GetNearestEdges(
      fixed_points, max_distance, is_multiple_points_assigned,
      segmentation_factor, max_road_rank, graph_fixed_points);

  ASSERT_EQ(nearest_edges.size(), 0);
}

}  // namespace

}  // namespace tests
