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
#include <graph/matcher_cache.hpp>
#include <graph/persistent_index.hpp>
#include <graph/tests/graph_fixture_config.hpp>

// Arcadia-includes, for services that are in Tier0
#ifdef ARCADIA_ROOT
#include <taxi/graph/libs/graph/graph.h>
#include <taxi/graph/libs/graph/persistent_index.h>
#endif

namespace graph::test {

/// Common base for Google Test and Google Benchmark fixtures
class GraphFixturePlugin : public graph::test::GraphTestFixtureConfig {
 protected:
  /// Access to graph
  static std::shared_ptr<const ::graph::Graph> Graph() {
#ifdef ARCADIA_ROOT
    UINVARIANT(
        graph_ != nullptr,
        "Graph is nullptr. This service is in Tier0, use different graph");
#endif
    return graph_;
  }

  /// Access to persistent index
  static std::shared_ptr<const graph::PersistentIndex> PersistentIndex() {
#ifdef ARCADIA_ROOT
    UINVARIANT(persistent_index_ != nullptr,
               "Persistent index is nullptr. This service is in Tier0, use "
               "different methods");
#endif
    return persistent_index_;
  }

#ifdef ARCADIA_ROOT
  /// @brief Access to the graph.
  /// \see ::graph::Graph
  static std::shared_ptr<const NTaxi::NGraph2::TGraph>& GetGraph() {
    UINVARIANT(graph2_ != nullptr, "Graph test plugin is not initialized");
    return graph2_;
  }
  /// @brief Access to the persistent graph index
  static std::shared_ptr<const NTaxi::NGraph2::TPersistentIndex>&
  GetPersistentIndex() {
    UINVARIANT(persistent_index2_ != nullptr,
               "Graph test plugin is not initialized");
    return persistent_index2_;
  }

  static std::shared_ptr<::graph::MatcherCache>& GetMatcherCache() {
    UINVARIANT(matcher_cache2_ != nullptr,
               "Graph test plugin is not initialized");
    return matcher_cache2_;
  }
#endif

 public:
  static void PluginSetUpTestSuite();
  static void PluginTearDownTestSuite() {}

 private:
  inline static std::shared_ptr<const ::graph::Graph> graph_;

  /// Access to persistent index
  inline static std::shared_ptr<const graph::PersistentIndex> persistent_index_;

  /// Tier0 support
#ifdef ARCADIA_ROOT
  inline static std::shared_ptr<const NTaxi::NGraph2::TGraph> graph2_;

  /// Access to persistent index
  inline static std::shared_ptr<const NTaxi::NGraph2::TPersistentIndex>
      persistent_index2_;

  /// Access to matcher cache
  inline static std::shared_ptr<::graph::MatcherCache> matcher_cache2_;
#endif

  static bool initialized_;
};

}  // namespace graph::test
