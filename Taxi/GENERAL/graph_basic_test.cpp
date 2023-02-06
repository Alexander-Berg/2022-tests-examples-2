#include <geometry/position.hpp>
#include <graph/config/graph.hpp>
#include <graph/graph_loader.hpp>
#include <graph/tests/graph_fixture_config.hpp>

#include <gtest/gtest.h>

#include <boost/filesystem/path.hpp>

namespace graph::examples {

TEST(Examples, BasicGraphLoad) {
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::meter;

  //! [GRAPH_LOAD]
  graph::GraphLoader loader;
  std::shared_ptr<const ::graph::Graph> graph_ptr =
      loader.LoadGraph(graph::test::GraphTestFixtureConfig::kTestGraphDataDir,
                       graph::configs::kPopulateMemoryMapName);
  //! [GRAPH_LOAD]

  const ::graph::Graph& graph = *graph_ptr;

  //! [NEAREST_EDGE]
  ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
  graph::PositionOnEdge nearest_edge = graph.NearestEdge(source_pos);
  //! [NEAREST_EDGE]

  //! [NEAREST_EDGES]
  // Simple way to get up to 10000 nearest edges
  ::geometry::Position source_pos2{37.642418 * lon, 55.734999 * lat};
  auto nearest_edges = graph.NearestEdges(
      source_pos2, graph::EdgeAccess::kUnknown,
      graph::EdgeCategory::kFieldRoads, 100.0 * meter, 10000, 10000);
  //! [NEAREST_EDGES]

  auto pos_on_edge = nearest_edge;
  //! [GET_COORDS]
  // Be careful not to pass undefined pos_on_edge
  ASSERT_FALSE(pos_on_edge.IsUndefined());
  // It won't throw an error, but return either ::geometry::Position{0,0} or
  // ::geometry::Position{nan, nan} - or some other irrelevant position.
  ::geometry::Position pos = graph.GetCoords(pos_on_edge);
  //! [GET_COORDS]

  std::ignore = pos;
}

}  // namespace graph::examples
