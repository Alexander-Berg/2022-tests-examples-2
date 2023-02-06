#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/csh_metadata_storage_config.hpp>

TEST(TestCSHMetadataStorageConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::CSHMetadataStorageConfig& msc_config =
      config.Get<config::CSHMetadataStorageConfig>();
  ASSERT_EQ(msc_config.enabled, false);
  ASSERT_EQ(msc_config.timeout_ms->count(), 50);
  ASSERT_EQ(msc_config.retries, 2u);
}
