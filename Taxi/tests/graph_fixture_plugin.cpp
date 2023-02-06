#if defined(ARCADIA_ROOT)
#include <library/cpp/testing/common/env.h>
#endif

#include <graph/tests/graph_fixture_plugin.hpp>

#include <iostream>

namespace graph::test {

/// Tier0 services
#if defined(ARCADIA_ROOT)
const TString graphDataDir = BinaryPath("taxi/graph/data/graph3/");
const TString precalcPath =
    BinaryPath("taxi/graph/data/graph3/graph_precalc.mms.2");
const char* GraphTestFixtureConfig::kTestGraphDataDir = graphDataDir.c_str();
const char* GraphTestFixtureConfig::kTestPrecalcPath = precalcPath.c_str();

void GraphFixturePlugin::PluginSetUpTestSuite() {
  const graph::GraphLoader loader;
  if (boost::filesystem::exists(kGraphDataDir)) {
    auto graph_holder = loader.LoadArcGraph(
        kGraphDataDir, graph::configs::kPopulateMemoryMapName);

    loader.BuildEdgeStorage(graph_holder, 4);
    graph2_ = std::move(graph_holder);
    persistent_index2_ = loader.LoadArcPersistentIndex(
        kGraphDataDir, graph::configs::kPopulateMemoryMapName);
    matcher_cache2_ = std::make_shared<::graph::MatcherCache>(
        *(graph2_->GetRoadGraph().RoadGraph));
  } else if (boost::filesystem::exists(kTestGraphDataDir)) {
    std::cout << "Using test graph because production graph is not present at "
                 "location "
              << kGraphDataDir << std::endl;
    auto graph_holder = loader.LoadArcGraph(
        kTestGraphDataDir, graph::configs::kPopulateMemoryMapName);

    loader.BuildEdgeStorage(graph_holder, 4);
    graph2_ = std::move(graph_holder);
    persistent_index2_ = loader.LoadArcPersistentIndex(
        kTestGraphDataDir, graph::configs::kPopulateMemoryMapName);
    matcher_cache2_ = std::make_shared<::graph::MatcherCache>(
        *(graph2_->GetRoadGraph().RoadGraph));
  } else {
    throw std::logic_error("Missing graph files");
  }
}
#else
/// Other (pin-storage)
void GraphFixturePlugin::PluginSetUpTestSuite() {
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
#endif

}  // namespace graph::test
