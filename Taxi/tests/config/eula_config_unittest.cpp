#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/eula_config.hpp>
#include <utils/jsonfixtures.hpp>

TEST(TestEulaDefinitions, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& eula_cfg = config.Get<config::EulaConfig>();

  ASSERT_EQ(eula_cfg.eula_definitions.size(), 0u);
}

TEST(TestEulaActionsInTariff, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& eula_cfg = config.Get<config::EulaConfig>();

  ASSERT_EQ(eula_cfg.actions_in_tariff.size(), 0u);
}

TEST(TestEulaDefinitions, StandardParsingConfig) {
  const auto& eula_definitions_bson =
      JSONFixtures::GetFixtureBSON("eula_definitions_standard_parse.json");
  const auto eula_definitions =
      config::ParseEulaDefinitions(eula_definitions_bson["EULA_DEFINITIONS"]);

  ASSERT_EQ(eula_definitions.size(), 3u);

  const auto& eula_0 = eula_definitions[0];
  ASSERT_EQ(eula_0.type, "sdc_eula");
  ASSERT_EQ(eula_0.title.get(), "tanker_key.title");
  ASSERT_EQ(eula_0.content.get(), "tanker_key.content");
  ASSERT_EQ(eula_0.accept_button_title.get(), "tanker_key.accept_button_title");
  ASSERT_EQ(eula_0.cancel_button_title.get(), "tanker_key.cancel_button_title");
  ASSERT_EQ(eula_0.header_image_tag.get(), "header_image_tag");
  ASSERT_EQ(eula_0.show_on_demand.get(), true);

  const auto& eula_1 = eula_definitions[1];
  ASSERT_EQ(eula_1.type, "part_eula");
  ASSERT_EQ(eula_1.title.get(), "tanker_key.title");
  ASSERT_EQ(eula_1.content.get(), "tanker_key.content");
  ASSERT_EQ(eula_1.accept_button_title.get(), "tanker_key.accept_button_title");
  ASSERT_EQ(eula_1.show_on_demand.get(), false);

  const auto& eula_2 = eula_definitions[2];
  ASSERT_EQ(eula_2.type, "only_title_eula");
  EXPECT_FALSE(eula_2.title.is_initialized());
  EXPECT_FALSE(eula_2.content.is_initialized());
  EXPECT_FALSE(eula_2.accept_button_title.is_initialized());
  EXPECT_FALSE(eula_2.cancel_button_title.is_initialized());
  EXPECT_FALSE(eula_2.header_image_tag.is_initialized());
  EXPECT_FALSE(eula_2.show_on_demand.is_initialized());
}

TEST(TestEulaActionsInTariff, StandardParsingConfig) {
  const auto& eula_definitions_bson =
      JSONFixtures::GetFixtureBSON("eula_definitions_standard_parse.json");
  const auto eula_definitions =
      config::ParseEulaDefinitions(eula_definitions_bson["EULA_DEFINITIONS"]);

  const auto& actions_in_tariff_bson = JSONFixtures::GetFixtureBSON(
      "eula_actions_in_tariffs_standard_parse.json");
  const auto actions_in_tariff = config::ParseActionsInTariff(
      actions_in_tariff_bson["EULA_ACTIONS_IN_TARIFF"], eula_definitions);

  ASSERT_EQ(actions_in_tariff.size(), 3u);

  ASSERT_EQ(actions_in_tariff.at("econom").size(), 0u);

  const auto& sdc_actions = actions_in_tariff.at("sdc");
  ASSERT_EQ(sdc_actions.size(), 2u);

  const auto& sdc_action_0 = sdc_actions[0];
  ASSERT_EQ(sdc_action_0.type, "show_eula_and_wait_for_accept");
  ASSERT_EQ(sdc_action_0.eula_type, "sdc_eula");
  ASSERT_EQ(sdc_action_0.on, "order_button_tap");

  const auto& sdc_action_1 = sdc_actions[1];
  ASSERT_EQ(sdc_action_1.type, "show_eula_and_wait_for_accept");
  ASSERT_EQ(sdc_action_1.eula_type, "only_title_eula");
  ASSERT_EQ(sdc_action_1.on, "order_button_tap");

  const auto& vip_actions = actions_in_tariff.at("vip");
  ASSERT_EQ(vip_actions.size(), 1u);

  const auto& vip_action = vip_actions[0];
  ASSERT_EQ(vip_action.type, "show_eula_and_wait_for_accept");
  ASSERT_EQ(vip_action.eula_type, "only_title_eula");
  ASSERT_EQ(vip_action.on, "order_button_tap");
}

TEST(TestEulaActionsInTariff, ParsingNoAllDefinedEulasConfig) {
  const auto& eula_definitions_bson =
      JSONFixtures::GetFixtureBSON("eula_definitions_not_all_parse.json");
  const auto eula_definitions =
      config::ParseEulaDefinitions(eula_definitions_bson["EULA_DEFINITIONS"]);

  const auto& actions_in_tariff_bson = JSONFixtures::GetFixtureBSON(
      "eula_actions_in_tariffs_standard_parse.json");
  const auto actions_in_tariff = config::ParseActionsInTariff(
      actions_in_tariff_bson["EULA_ACTIONS_IN_TARIFF"], eula_definitions);

  ASSERT_EQ(actions_in_tariff.size(), 3u);

  ASSERT_EQ(actions_in_tariff.at("econom").size(), 0u);

  const auto& sdc_actions = actions_in_tariff.at("sdc");
  ASSERT_EQ(sdc_actions.size(), 1u);

  const auto& sdc_action_0 = sdc_actions[0];
  ASSERT_EQ(sdc_action_0.type, "show_eula_and_wait_for_accept");
  ASSERT_EQ(sdc_action_0.eula_type, "sdc_eula");
  ASSERT_EQ(sdc_action_0.on, "order_button_tap");

  ASSERT_EQ(actions_in_tariff.at("vip").size(), 0u);
}
