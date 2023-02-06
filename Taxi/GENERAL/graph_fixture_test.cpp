#include <gtest/gtest.h>
#include <graph/tests/graph_fixture.hpp>

namespace graph::examples {

//! [GRAPH_FIXTURE]

using GraphFixtureExample = ::graph::test::GraphTestFixtureLegacy;

// Use TEST_F instead of TEST to get access to GraphFixtureExample methods
TEST_F(GraphFixtureExample, Basic) {
  using ::geometry::lat;
  using ::geometry::lon;
  using ::geometry::meter;

  // Check that Graph() is not nullptr - just in case
  ASSERT_NE(nullptr, Graph());

  ::geometry::Position source_pos{37.642418 * lon, 55.734999 * lat};
  // Now you can get access to test graph via Graph() static method.
  PositionOnEdge nearest_edge = Graph()->NearestEdge(source_pos);

  std::ignore = nearest_edge;
}
//! [GRAPH_FIXTURE]
}  // namespace graph::examples
