#include <gtest/gtest.h>
#include <array>
#include <geometry/is_on_the_right.hpp>
#include <geometry/test/geometry_plugin_test.hpp>
#include <graph/graph_object_index.hpp>
#include <graph/tests/graph_fixture.hpp>
#include <graph/tests/print_to.hpp>
#include <graph/types.hpp>
#include <iostream>
#include <random>

namespace graph::test {

using GraphObjectFixture = graph::test::GraphTestFixtureLegacy;

TEST_F(GraphObjectFixture, TestEdgeAccessApi) {
  auto graph = Graph();

  graph->NearestEdge({55.734680 * ::geometry::lat, 37.642423 * ::geometry::lon},
                     EdgeAccess::kAutomobile | EdgeAccess::kTaxi);
};

TEST_F(GraphObjectFixture, TestSegmentGeometry) {
  auto graph = Graph();

  // Get any edge. It doesn't matter which one
  const auto poe = graph->NearestEdge(
      {55.734680 * ::geometry::lat, 37.642423 * ::geometry::lon},
      EdgeAccess::kAutomobile | EdgeAccess::kTaxi);

  const auto pog = graph->GetPositionOnGraph(poe);

  auto pog_start{pog};
  pog_start.segment_position = 0.0;

  auto pog_end{pog};
  pog_end.segment_position = 1.0;

  const auto coords_start = graph->GetCoords(pog_start);
  const auto coords_end = graph->GetCoords(pog_end);

  const auto segment_line = graph->GetSegmentGeometry(pog);
  ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(
      segment_line.start, coords_start);
  ::geometry::test::GeometryTestPlugin::TestPositionsAreClose(segment_line.end,
                                                              coords_end);
};

TEST_F(GraphObjectFixture, TestIsOnTheRight) {
  using namespace geometry;

  auto graph = Graph();

  // Get any edge. It doesn't matter which one
  const auto poe = graph->NearestEdge(
      {55.734680 * ::geometry::lat, 37.642423 * ::geometry::lon},
      EdgeAccess::kAutomobile | EdgeAccess::kTaxi);

  const auto pog = graph->GetPositionOnGraph(poe);
  const auto segment_line = graph->GetSegmentGeometry(pog);

  // Take any four points. It doesn't matter which, all that matters is that
  // result of geometry IsOnTheRight method should match the method
  // from graph

  std::array test_positions{
      Position{-175 * lon, 80 * lat}, Position{175 * lon, 80 * lat},
      Position{-175 * lon, -80 * lat}, Position{175 * lon, -80 * lat}};

  for (const auto& pos : test_positions) {
    const bool test_value = graph->IsOnTheRightSideOfRoad(pog, pos);
    const bool ref_value = ::geometry::IsOnTheRight(segment_line, pos);
    EXPECT_EQ(ref_value, test_value) << pos;
  }
};

TEST_F(GraphObjectFixture, TestRoadSideFilter) {
  auto graph = Graph();

  const ::geometry::Position target{55.734680 * ::geometry::lat,
                                    37.642423 * ::geometry::lon};
  const auto positions =
      graph->NearestEdges(target, EdgeAccess::kAutomobile | EdgeAccess::kTaxi,
                          EdgeCategory::kLocalRoads, 200 * ::geometry::meter,
                          10, 10, Graph::RoadSideFilter::ProperSide);

  for (const auto poe : positions) {
    const auto pog = graph->GetPositionOnGraph(poe);
    const auto segment_line = graph->GetSegmentGeometry(pog);
    EXPECT_TRUE(::geometry::IsOnTheRight(segment_line, target));
  }
}

TEST_F(GraphObjectFixture, TestBridgeOnly) {
  auto graph = Graph();

  const ::geometry::Position target{55.734611 * ::geometry::lat,
                                    37.597922 * ::geometry::lon};

  // take all roads
  const auto all_positions =
      graph->NearestEdges(target, EdgeAccess::kAutomobile | EdgeAccess::kTaxi,
                          EdgeCategory::kLocalRoads, 500 * ::geometry::meter,
                          100, 100, Graph::RoadSideFilter::NoFilter,
                          EdgeStructType::kBridge | EdgeStructType::kRoad |
                              EdgeStructType::kTunnel);

  EXPECT_GE(all_positions.size(), 30);

  // take bride-only positions
  const auto positions = graph->NearestEdges(
      target, EdgeAccess::kAutomobile | EdgeAccess::kTaxi,
      EdgeCategory::kLocalRoads, 500 * ::geometry::meter, 100, 100,
      Graph::RoadSideFilter::NoFilter, EdgeStructType::kBridge);

  // There are only like 30+ edges in this bridge
  EXPECT_LE(positions.size(), 30);
}

}  // namespace graph::test
