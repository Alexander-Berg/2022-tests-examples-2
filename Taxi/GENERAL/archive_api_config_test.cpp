#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/archive_api_config.hpp>
#include <config/config.hpp>

TEST(TestArchiveApiConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::ArchiveApi& archive_api_config =
      config.Get<config::ArchiveApi>();
  ASSERT_EQ(archive_api_config.yt_runtime_replication_delay, 43200);
  ASSERT_TRUE(archive_api_config.queue_mongo_rules.Get().empty());
}
