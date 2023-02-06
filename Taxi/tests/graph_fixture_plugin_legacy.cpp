#include <graph/tests/graph_fixture_plugin_legacy.hpp>

#include <iostream>

namespace graph::test {

void GraphFixturePluginLegacy::PluginSetUpTestSuite() {
  const graph::GraphLoader loader;
  if (boost::filesystem::exists(kGraphDataDir)) {
    graph_ =
        loader.LoadGraph(kGraphDataDir, graph::configs::kPopulateMemoryMapName);
    loader.BuildEdgeStorage(graph_, 4);
    persistent_index_ = loader.LoadPersistentIndex(
        kGraphDataDir, graph::configs::kPopulateMemoryMapName);

  } else if (boost::filesystem::exists(kTestGraphDataDir)) {
    std::cout << "Using test graph because production graph is not present at "
                 "location "
              << kGraphDataDir << std::endl;
    graph_ = loader.LoadGraph(kTestGraphDataDir,
                              graph::configs::kPopulateMemoryMapName);
    loader.BuildEdgeStorage(graph_, 4);
    persistent_index_ = loader.LoadPersistentIndex(
        kTestGraphDataDir, graph::configs::kPopulateMemoryMapName);
  } else {
    throw std::logic_error("Missing graph files");
  }
}

}  // namespace graph::test
