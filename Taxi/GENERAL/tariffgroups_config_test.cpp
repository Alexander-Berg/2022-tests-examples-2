#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tariffgroups_config.hpp>

TEST(TestTariffGroups, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& groups_by_zones =
      config.Get<config::TariffGroups>().groups_by_zone;
  const auto& groups_list = groups_by_zones.GetDefaultValue();
  ASSERT_FALSE(groups_list.empty());
  const auto& groups_it = groups_list.begin();
  ASSERT_FALSE(groups_it->tariffs.empty());
}
