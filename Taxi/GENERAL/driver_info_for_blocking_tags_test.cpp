#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_info_for_blocking_tags.hpp>

TEST(TestDriverInfoForBlockingTags, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& keys_by_tags = config.Get<config::DriverInfoForBlockingTags>();
  ASSERT_TRUE(keys_by_tags.tanker_keys_by_tags_.GetMap().empty());
}
