#include "subvention_groups_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestSubventionGroupsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::SubventionGroupsConfig& subvention_groups_config =
      config.Get<config::SubventionGroupsConfig>();

  ASSERT_EQ(subvention_groups_config.filter_subventions_by_tags, false);
  ASSERT_EQ(subvention_groups_config.filter_subventions_by_branding, false);
  ASSERT_EQ(subvention_groups_config.filter_subventions_by_classes, false);
}
