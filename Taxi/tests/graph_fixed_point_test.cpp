#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <caches/surge_points.hpp>
#include <graph/tests/graph_fixture.hpp>

#include <models/graph_surge_points.hpp>
#include <utils/arrange_surge_points.hpp>
#include <utils/polygon_calculator.hpp>
#include <views/common.hpp>

#include "easyview_visualizer_test.hpp"

namespace tests {
using graph::test::GraphTestFixture;

UTEST_F(GraphTestFixture, NearestFixedPoint) {
  using ::geometry::lat;
  using ::geometry::lon;
  using surge_points_cache::caches::AllPoints;

  GraphTestFixture::SetUp();

  // Prepare test data
  AllPoints::SurgePoints sample_points;
  std::unordered_map<std::string, ::geometry::Position> id_to_point = {
      {"id1", {55.736958 * lat, 37.642077 * lon}},
      {"id2", {55.737277 * lat, 37.642090 * lon}},
      {"id3", {55.733864 * lat, 37.642289 * lon}},
      {"id4", {55.736499 * lat, 37.643782 * lon}},
  };
  for (const auto& [id, location] : id_to_point) {
    auto& next_pt = sample_points.emplace_back();
    next_pt.id = id;
    next_pt.position_id = fmt::format("stable_{}", id);
    next_pt.location = location;
    next_pt.mode = clients::taxi_admin_surger::SurgePointMode::kApply;
  }

  // Add point that should be ignored
  {
    auto& ignored_point = sample_points.emplace_back();
    ignored_point.id = "id0";
    ignored_point.position_id = "stable_id0";
    ignored_point.location = {55.736499 * lat, 37.643782 * lon};
    ignored_point.mode = clients::taxi_admin_surger::SurgePointMode::kIgnore;
  }

  models::GraphSurgePoints surge_points_graph{GetGraph()};
  surge_points_graph.Update(AllPoints{std::move(sample_points), true},
                            {100.0, 100.0});

  const geometry::Position sample_point{55.735422 * lat, 37.642736 * lon};

  {
    auto points = surge_points_graph.NearestFixedPoints(sample_point);
    ASSERT_EQ(points.size(), 4);
  }

  {
    models::GraphSearchOptions opts;
    opts.max_points = 2;
    auto points = surge_points_graph.NearestFixedPoints(sample_point, opts);
    ASSERT_EQ(points.size(), 2);
  }

  {
    models::GraphSearchOptions opts;
    opts.max_distance = 200;
    auto points = surge_points_graph.NearestFixedPoints(sample_point, opts);
    ASSERT_EQ(points.size(), 2);
  }
}

class PolygonCalculatorTest : public GraphTestFixture {
 protected:
  PolygonCalculatorTest() {}
  void SetUp() override {
    GraphTestFixture::SetUp();
    radius = 3000.0;

    using ::models::Point;
    auto add_fixed_point = [this](double x, double y, std::string position_id) {
      fixed_points.push_back(models::FixedPoint{Point(x, y), position_id});
    };

    add_fixed_point(37.624319, 55.736674, "a");
    add_fixed_point(37.628036, 55.736851, "b");
    add_fixed_point(37.626207, 55.732999, "c");
    add_fixed_point(37.582755, 55.804231, "d");
    add_fixed_point(37.622319, 55.715794, "e");
  }

  std::vector<models::FixedPoint> fixed_points;
  double radius;
};

// TODO: think about how to automatize these tests

UTEST_F(PolygonCalculatorTest, PolygonCalculatorGetPolygons) {
  utils::PolygonCalculator polygon_calculator(*GetGraph());
  models::EdgesInfo edges_info =
      polygon_calculator.GatherEdgesInfo(fixed_points, {radius, false, false});
  auto polygons = polygon_calculator.GetPolygons(edges_info, {1.0, 0.01, true});

  ASSERT_EQ(polygons.size(), fixed_points.size());
  // Put your own path and take a look with easyview
  /*EasyviewVisualizer
  visualizer("/home/diplomate/Desktop/useful/polygons.yson"); for (const auto&
  polygon : polygons) {
    visualizer.WritePolygon(polygon);
  }*/
}

UTEST_F(PolygonCalculatorTest, PolygonCalculatorGetNearestEdges) {
  models::GraphSurgePoints surge_points_graph{GetGraph()};

  double segmentation_factor = 0;

  auto edges = handlers::pin_storage::GetNearestEdges(
      fixed_points, radius, true, segmentation_factor, surge_points_graph);
  for (const auto& edge : edges) {
    ASSERT_GE(edge.nearest_fixed_points.size(), 1);
    if (edge.nearest_fixed_points.size() > 4) {
      std::string points_msg;
      for (const auto& point : edge.nearest_fixed_points) {
        points_msg += "\n" + fmt::format("id={}, distance={}",
                                         point.position_id, point.distance);
      }
      throw std::runtime_error(fmt::format(
          "Error! Edge belongs to {} points, start=({};{}),"
          "end=({};{}), fixed points:{}",
          edge.nearest_fixed_points.size(), edge.start.GetLongitudeAsDouble(),
          edge.start.GetLatitudeAsDouble(), edge.end.GetLongitudeAsDouble(),
          edge.end.GetLatitudeAsDouble(), points_msg));
    }
  }
  EXPECT_TRUE(std::any_of(edges.begin(), edges.end(), [](const auto& edge) {
    return edge.nearest_fixed_points.size() > 1;
  }));

  edges = handlers::pin_storage::GetNearestEdges(
      fixed_points, radius, false, segmentation_factor, surge_points_graph);
  for (const auto& edge : edges) {
    EXPECT_EQ(edge.nearest_fixed_points.size(), 1);
  }

  // Put your own path and take a look with easyview
  /*EasyviewVisualizer visualizer("/home/diplomate/Desktop/useful/edges.yson");
  for (const auto& edge : edges) {
    visualizer.WriteEdge(edge);
  }*/
}

UTEST_F(GraphTestFixture, ArrangePoints) {
  using ::models::Point;

  GraphTestFixture::SetUp();

  double kRadius = 2500.0;
  std::vector<utils::PinPosition> pins{
      {Point(37.600887, 55.737124), 1}, {Point(37.598738, 55.735871), 2},
      {Point(37.593080, 55.730698), 1}, {Point(37.587779, 55.731345), 2},
      {Point(37.584340, 55.721319), 1}, {Point(37.575458, 55.721319), 2}};
  utils::ArrangePointsSettings settings;
  settings.precalc_edges_distance_m = kRadius;
  settings.coverage = {utils::Coverage{1500, 10}, utils::Coverage{2000, 20},
                       utils::Coverage{3000, 95}};
  auto arrange_result = utils::ArrangePoints(*GetGraph(), pins, settings);

  const std::vector<Point> expected_fixed_points{Point(37.5898, 55.7261),
                                                 Point(37.5749, 55.7215),
                                                 Point(37.6005, 55.7369)};
  const double kEps = 0.0001;
  ASSERT_EQ(arrange_result.fixed_points.size(), expected_fixed_points.size());
  for (size_t i = 0; i < expected_fixed_points.size(); i++) {
    ASSERT_NEAR(expected_fixed_points[i].Lat,
                arrange_result.fixed_points[i].pos.Lat, kEps);
    ASSERT_NEAR(expected_fixed_points[i].Lon,
                arrange_result.fixed_points[i].pos.Lon, kEps);
  }
}

}  // namespace tests
