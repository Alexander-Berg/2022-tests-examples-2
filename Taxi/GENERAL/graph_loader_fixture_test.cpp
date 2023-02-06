#include "graph_loader_fixture.hpp"

namespace graph::test {

void GraphLoaderFixture::TestGraph(
    const std::shared_ptr<const NTaxiExternal::NGraph2::TGraph>& graph) {
  ASSERT_NE(nullptr, graph);

  NTaxiExternal::NGraph2::TPoint source_pos{37.642418, 55.734999};
  NTaxiExternal::NGraph2::TPositionOnEdge adjusted_pos;
  EXPECT_TRUE(graph->NearestEdge(
      adjusted_pos, source_pos, NTaxiExternal::NGraph2::TEdgeAccess::EA_UNKNOWN,
      NTaxiExternal::NGraph2::TEdgeCategory::EC_ROADS, 100));
  EXPECT_NE(NTaxiExternal::NGraph2::UNDEFINED, adjusted_pos.EdgeId);
}

}  // namespace graph::test
