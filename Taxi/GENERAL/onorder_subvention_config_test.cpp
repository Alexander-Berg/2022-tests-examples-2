#include "onorder_subvention_config.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(TestOnorderSubventionConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::OnorderSubventionConfig& subvention_config =
      config.Get<config::OnorderSubventionConfig>();

  ASSERT_EQ(subvention_config.min_version_for_subvention_requirement_status,
            ParseTaximeterVersion("8.60"));
  ASSERT_EQ(subvention_config.subvention_schedule_taximeter_displaying_days.Get(
                "some_zone"),
            7u);
  ASSERT_EQ(subvention_config.enable_tag_filtering_by_billling, false);
  ASSERT_EQ(subvention_config.requst_only_required_subvention_types, false);
  ASSERT_EQ(subvention_config.fetch_tariff_classes_from_mongo, true);
  ASSERT_EQ(subvention_config.enable_subventions_sort_before_merge, false);
}
