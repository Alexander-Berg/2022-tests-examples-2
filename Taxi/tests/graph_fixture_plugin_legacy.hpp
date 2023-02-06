#pragma once

#include <exception>

#include <boost/filesystem.hpp>
#include <boost/filesystem/path.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/mapmatcher/matcher_cache.h>
#include <yandex/taxi/graph2/shortest_path/shortest_path_data.h>
#include <yandex/taxi/graph2/threading.h>

#include <graph/components/mutex_control.hpp>
#include <graph/config/graph.hpp>
#include <graph/graph_loader.hpp>
#include <graph/persistent_index.hpp>
#include <graph/tests/graph_fixture_config.hpp>

namespace graph::test {

/// Common base for Google Test and Google Benchmark fixtures
class GraphFixturePluginLegacy : public graph::test::GraphTestFixtureConfig {
 protected:
  /// Access to graph
  static std::shared_ptr<const ::graph::Graph> Graph() { return graph_; }

  /// Access to persistent index
  static std::shared_ptr<const graph::PersistentIndex> PersistentIndex() {
    return persistent_index_;
  }

 public:
  static void PluginSetUpTestSuite();
  static void PluginTearDownTestSuite() {}

 private:
  inline static std::shared_ptr<const ::graph::Graph> graph_;

  /// Access to persistent index
  inline static std::shared_ptr<const graph::PersistentIndex> persistent_index_;

  static bool initialized_;
};

}  // namespace graph::test
