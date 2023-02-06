#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "eta_config.hpp"

TEST(TestEtaConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const EtaMlExperimentsConfig& eta_config =
      config.Get<EtaMlExperimentsConfig>();
  ASSERT_TRUE(eta_config.experiments_to_versions.empty());
}
