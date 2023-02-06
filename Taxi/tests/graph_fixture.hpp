#pragma once

#include <gtest/gtest.h>

#include <boost/filesystem/path.hpp>

#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <yandex/taxi/graph2/graph.h>
#include <yandex/taxi/graph2/shortest_path/shortest_path_data.h>

#include <graph/config/graph.hpp>
#include <graph/graph_loader.hpp>
#include <graph/persistent_index.hpp>
#include <graph/tests/graph_fixture_plugin.hpp>
#include <graph/tests/graph_fixture_plugin_legacy.hpp>

namespace graph::test {

/// Inheriting this class in your google test fixtures will provide access to
/// graph
/// \snippet examples/graph_fixture_test.cpp GRAPH_FIXTURE
class GraphTestFixture : public testing::Test, public GraphFixturePlugin {
 public:
  static void SetUpTestSuite() {
    compatibilitySetUpTestSuiteMarker = true;
    GraphFixturePlugin::PluginSetUpTestSuite();
  }
  static void TearDownTestSuite() {
    GraphFixturePlugin::PluginTearDownTestSuite();
  }

  void SetUp() override {
    if (!compatibilitySetUpTestSuiteMarker) {
      compatibilitySetUpTestSuiteMarker = true;
      SetUpTestSuite();
    }
  }

  // Because userver managed to break Google Test TAXICOMMON-5127
  // we have to use dirty hack to work around
  static inline bool compatibilitySetUpTestSuiteMarker{false};
};

/// Inheriting this class in your google test fixtures will provide access to
/// graph
/// \snippet examples/graph_fixture_test.cpp GRAPH_FIXTURE
class GraphTestFixtureLegacy : public testing::Test,
                               public GraphFixturePluginLegacy {
 public:
  static void SetUpTestSuite() {
    GraphFixturePluginLegacy::PluginSetUpTestSuite();
  }
  static void TearDownTestSuite() {
    GraphFixturePluginLegacy::PluginTearDownTestSuite();
  }
};

/// \example        examples/graph_fixture_test.cpp
/// Simple example for graph test fixture

}  // namespace graph::test
