#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tags_config.hpp>

namespace {

constexpr size_t kBulkThreshold = 256u;
constexpr std::chrono::milliseconds kBulkTimeout{200};
constexpr uint32_t kBulkRetries = 1;
constexpr std::chrono::milliseconds kV2MatchInterval{100};
constexpr uint32_t kV2MatchRequestSize = 8192;
constexpr std::chrono::seconds kDumpInterval{300};
constexpr std::chrono::seconds kValidRestoreInterval{1800};

}  // namespace

TEST(TestTags, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tags_config = config.Get<config::Tags>();

  const auto& v2_match_config = tags_config.v2_match_timeout_override;
  ASSERT_EQ(v2_match_config.size(), 1u);
  ASSERT_EQ(v2_match_config.front().threshold, kBulkThreshold);
  ASSERT_EQ(v2_match_config.front().timeout, kBulkTimeout);
  ASSERT_EQ(v2_match_config.front().retries, kBulkRetries);

  const auto& tags_cache_settings = tags_config.tags_cache_settings.Get();
  ASSERT_FALSE(tags_cache_settings.enabled);
  ASSERT_EQ(tags_cache_settings.request_interval, kV2MatchInterval);
  ASSERT_EQ(tags_cache_settings.request_size, kV2MatchRequestSize);
  ASSERT_EQ(tags_cache_settings.dump_interval, kDumpInterval);
  ASSERT_EQ(tags_cache_settings.valid_restore_interval, kValidRestoreInterval);
  ASSERT_TRUE(tags_cache_settings.dump_restore_enabled);
  ASSERT_EQ(tags_cache_settings.request_max_count, boost::none);
}

TEST(TestTags, V2MatchClientOverride) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tags_config = config.Get<config::Tags>();

  auto params = tags_config.GetGroupMatchOverrideParams(1u);
  ASSERT_FALSE(params.timeout.is_initialized());
  ASSERT_FALSE(params.retries.is_initialized());

  params = tags_config.GetGroupMatchOverrideParams(kBulkThreshold);
  ASSERT_EQ(*params.timeout, kBulkTimeout);
  ASSERT_EQ(*params.retries, kBulkRetries);

  params = tags_config.GetGroupMatchOverrideParams(180000u);
  ASSERT_EQ(*params.timeout, kBulkTimeout);
  ASSERT_EQ(*params.retries, kBulkRetries);
}
