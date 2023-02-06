#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/save_tin_config.hpp>

TEST(TestSaveTinConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& save_tin = config.Get<config::SaveTin>();
  ASSERT_FALSE(save_tin.enabled);
}
