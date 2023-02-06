#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "graph_experiment_config.hpp"

TEST(TestGraphExperimentConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& graph_experiment_config = config.Get<config::GraphExperiment>();
  ASSERT_FALSE(graph_experiment_config.zones_for_graph_experiment["moscow"]);
  ASSERT_EQ(
      graph_experiment_config.graph_acquire_via_graph_experiment_zones.Get(
          "moscow"),
      false);
}
