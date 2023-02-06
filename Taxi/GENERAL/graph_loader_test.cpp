#include <gtest/gtest.h>

#include "graph_loader_fixture.hpp"

namespace graph::test {

TEST_F(GraphLoaderFixture, TestRoadGraph) {
  graph::GraphLoader loader;

  auto graph = loader.LoadGraph(kTestGraphDataDir,
                                graph::configs::kPopulateMemoryMapName);
  ASSERT_NE(nullptr, graph);

  auto graph_raw = graph->GetRawGraph();
  ASSERT_NE(nullptr, graph_raw);

  TestGraph(graph_raw);
}

TEST_F(GraphLoaderFixture, TestPersistentIndex) {
  graph::GraphLoader loader;

  auto graph = loader.LoadGraph(kTestGraphDataDir,
                                graph::configs::kPopulateMemoryMapName);
  ASSERT_NE(nullptr, graph);

  auto graph_raw = graph->GetRawGraph();
  ASSERT_NE(nullptr, graph_raw);

  NTaxiExternal::NGraph2::TPoint source_pos{37.642418, 55.734999};
  NTaxiExternal::NGraph2::TPositionOnEdge adjusted_pos;
  ASSERT_TRUE(graph_raw->NearestEdge(
      adjusted_pos, source_pos, NTaxiExternal::NGraph2::TEdgeAccess::EA_UNKNOWN,
      NTaxiExternal::NGraph2::TEdgeCategory::EC_ROADS, 100));
  ASSERT_NE(NTaxiExternal::NGraph2::UNDEFINED, adjusted_pos.EdgeId);

  const auto& persistent_index = loader.LoadPersistentIndex(
      kTestGraphDataDir, graph::configs::kPopulateMemoryMapName);
  const auto& input_short_id = graph::EdgeId{adjusted_pos.EdgeId};
  const auto& result_long_id =
      persistent_index->FindEdgePersistentId(input_short_id);
  ASSERT_TRUE(result_long_id);

  const auto& result_short_id = persistent_index->FindEdgeId(*result_long_id);
  ASSERT_TRUE(result_short_id);
  ASSERT_EQ(input_short_id, *result_short_id);
}

TEST_F(GraphLoaderFixture, TestPathValidation) {
  static const std::string kInvalidPath = "/missing/directory/on/any/host";
  graph::GraphLoader loader;

  ASSERT_THROW(
      loader.LoadGraph(kInvalidPath, graph::configs::kPopulateMemoryMapName),
      std::runtime_error);
  ASSERT_THROW(
      loader.LoadGraph(kInvalidPath, graph::configs::kSimpleMemoryMapName),
      std::runtime_error);
  ASSERT_THROW(
      loader.LoadGraph(kInvalidPath, graph::configs::kPopulateMemoryMapName),
      std::runtime_error);
  ASSERT_THROW(
      loader.LoadGraph(kInvalidPath, graph::configs::kSimpleMemoryMapName),
      std::runtime_error);
  ASSERT_THROW(loader.LoadPersistentIndex(
                   kInvalidPath, graph::configs::kPopulateMemoryMapName),
               std::runtime_error);
}

}  // namespace graph::test
