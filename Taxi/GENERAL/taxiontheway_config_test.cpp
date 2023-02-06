#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taxiontheway_config.hpp>

TEST(TestDeafDriverSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::TaxiOnTheWay& tow_cfg = config.Get<config::TaxiOnTheWay>();

  {
    const auto& icon = tow_cfg.deaf_driver_icon.Get();
    EXPECT_EQ(icon, "");
  }

  {
    const auto& statuses = tow_cfg.deaf_driver_show_icon_on_status.Get();
    std::unordered_set<std::string> expected_statuses({"waiting"});
    EXPECT_EQ(statuses, expected_statuses);
  }
  {
    const auto& statuses =
        tow_cfg.deaf_driver_force_destination_on_status.Get();
    std::unordered_set<std::string> expected_statuses(
        {"driving", "waiting", "transporting"});
    EXPECT_EQ(statuses, expected_statuses);
  }
  {
    const auto& statuses = tow_cfg.deaf_driver_button_modifiers_on_status.Get();
    std::unordered_set<std::string> expected_statuses({"driving", "waiting"});
    EXPECT_EQ(statuses, expected_statuses);
  }
}
