#include "use_cases/client_application_menu/client_application_menu.hpp"

#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/action_button_repository.hpp"
#include "tests/mocks/application_repository.hpp"
#include "tests/mocks/countries_service.hpp"
#include "tests/mocks/setting_definition_repository.hpp"

namespace sweet_home::client_application_menu {

namespace {
const core::SDKClientConfig kClientConfig{
    core::SDKPurchaseType::kNative, {}, true};
const core::SDKClient kSdkClient{kDefaultClientId, kDefaultServiceId,
                                 kDefaultPlatform, {},
                                 kClientConfig,    {}};
const std::string kCountry = "rus";
const std::string kDefaultCurrency = "RUB";
}  // namespace

namespace {

MenuDeps PrepareDeps(
    const mocks::GetMenuForApplicationHandler& get_menu_handler) {
  MenuDeps deps;

  deps.application_repository =
      std::make_shared<mocks::ApplicationRepositoryMock>(get_menu_handler);

  auto get_currency_handler = [](const std::string&) {
    return kDefaultCurrency;
  };

  deps.countries_service =
      std::make_shared<mocks::CountriesServiceMock>(get_currency_handler);

  deps.action_button_repository =
      std::make_shared<mocks::ActionButtonRepositoryMock>();

  auto definitions_handler = [](const std::string&) {
    return tests::MakeSettingDefinitionMap(
        {tests::MakeDefinition("global_setting_id", "global_default_value"),
         tests::MakeDefinition("boolean_setting_id",
                               setting::SettingType::kBoolean, true, true)});
  };

  auto setting_definition_repository_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  setting_definition_repository_mock->SetStub_GetDefinitions(
      definitions_handler);
  deps.setting_repository = setting_definition_repository_mock;

  return deps;
}

MenuContext PrepareContext(bool wallet_visible = true) {
  auto user_subscription = tests::MakePlusSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false);
  auto config = dynamic_config::GetDefaultSnapshot();
  auto experiments = tests::MakeExperiments();
  core::HideableWallet wallet = {tests::MakeWallet("RUB_wallet", "138"),
                                 wallet_visible};

  return {user_subscription,
          config,
          experiments,
          wallet,
          std::optional<burning_balance::BurnEvent>{},
          std::nullopt};
}

}  // namespace

TEST(TestGetMenuForApplication, HappyPath) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    client_application::SDKMenu menu;

    // plain element -> would be added
    auto normal_element = tests::MakeListItem(
        tests::MakeChangeSettingAction("boolean_setting_id"));

    // no lead -> filtered out
    auto no_lead = tests::MakeListItem(
        tests::MakeOpenDeeplinkAction("yandextaxi://qr_scanner"), std::nullopt);

    auto hidden_would_be_removed = tests::MakeListItem(
        tests::MakeChangeSettingAction("boolean_setting_id"));
    hidden_would_be_removed.hidden = true;

    auto with_subtitle = tests::MakeListItem(
        tests::MakeChangeSettingAction("boolean_setting_id"),
        tests::MakeElement("title", "subtitle_should_have_balance"));

    menu.sections = {tests::MakeSection(
        {normal_element, no_lead, hidden_would_be_removed, with_subtitle})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto context = PrepareContext();

  // call
  auto result = GetMenuForApplication(deps, context, kSdkClient, kCountry);

  // assert
  ASSERT_EQ(result.currency, "RUB");
  // TODO: check badge
  ASSERT_TRUE(result.action_button);

  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_FALSE(result.webview_params);
  ASSERT_EQ(result.sections.size(), 1);

  // only normal_element added
  ASSERT_EQ(result.sections[0].items.size(), 2);

  {
    const auto& section = result.sections[0];
    ASSERT_EQ(section.items.size(), 2);

    ASSERT_TRUE(section.items[0].list_item);
    ASSERT_EQ(section.items[0].list_item->lead.title->main_key->key,
              "boolean_setting_id_key");

    const auto& with_subtitle = section.items[1].list_item;
    ASSERT_TRUE(with_subtitle);
    ASSERT_EQ(with_subtitle->lead.title->main_key->key, "title");

    // no balance arg
    ASSERT_TRUE(with_subtitle->lead.subtitle);
    ASSERT_EQ(with_subtitle->lead.subtitle->main_key->key,
              "subtitle_should_have_balance");
    ASSERT_EQ(
        with_subtitle->lead.subtitle->main_key->args.count("wallet_balance"),
        1);
  }
}

TEST(TestGetMenuForApplication, EmptySectionsOnRepoError) {
  auto get_menu_handler = [](const core::SDKClient&) {
    throw client_application::ApplicationNotFound("i am error");
    return client_application::SDKMenu{};
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto context = PrepareContext();

  auto result = GetMenuForApplication(deps, context, kSdkClient, kCountry);
  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_TRUE(result.sections.empty());
}

TEST(TestGetMenuForApplication, RemoveSectionWithoutItems) {
  // prepare
  auto context = PrepareContext();

  auto get_menu_handler = [](const core::SDKClient&) {
    client_application::SDKMenu menu;
    auto action = tests::MakeChangeSettingAction("boolean_setting_id");
    auto plain_item = tests::MakeListItem(action);

    auto unknown_setting = tests::MakeChangeSettingAction("unknown_setting_id");
    auto would_be_skipped = tests::MakeListItem(unknown_setting);

    menu.sections = {
        tests::MakeSection({plain_item}),
        tests::MakeSection({would_be_skipped}),  // would be skipped
        tests::MakeSection({})                   // would be skipped
    };
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);

  auto setting_definition_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();

  setting_definition_mock->SetStub_GetDefinitions([](const std::string&) {
    auto setting_definition = tests::MakeDefinition(
        "boolean_setting_id", setting::SettingType::kBoolean, true);
    return tests::MakeSettingDefinitionMap({setting_definition});
  });
  deps.setting_repository = setting_definition_mock;

  // call
  auto result = GetMenuForApplication(deps, context, kSdkClient, kCountry);

  // assert
  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_EQ(result.sections.size(), 1);
  ASSERT_EQ(result.sections[0].items.size(), 1);
}

TEST(TestGetMenuForApplication, WalletHidden) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    client_application::SDKMenu menu;

    // plain element -> would be added
    auto normal_element = tests::MakeListItem(
        tests::MakeChangeSettingAction("boolean_setting_id"));

    auto with_subtitle = tests::MakeListItem(
        tests::MakeChangeSettingAction("boolean_setting_id"),
        tests::MakeElement("title", "subtitle_should_have_balance"));

    menu.sections = {tests::MakeSection({normal_element, with_subtitle})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);

  const bool wallet_visible = false;
  auto context = PrepareContext(wallet_visible);

  // we could advise upgrade, but wallet hidden
  context.user_subscription = tests::MakePlusSubscription(
      "ya_plus", subscription::PurchaseStatus::kActive, false);

  // call
  auto result = GetMenuForApplication(deps, context, kSdkClient, kCountry);

  // assert
  ASSERT_EQ(result.currency, "RUB");

  // TODO: balance badge

  // we could advise upgrade, but wallet hidden
  ASSERT_FALSE(result.action_button);

  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_EQ(result.sections.size(), 1);

  {
    const auto& section = result.sections[0];
    ASSERT_EQ(section.items.size(), 2);

    ASSERT_TRUE(section.items[0].list_item);
    ASSERT_EQ(section.items[0].list_item->lead.title->main_key->key,
              "boolean_setting_id_key");

    const auto& with_subtitle = section.items[1].list_item;
    ASSERT_TRUE(with_subtitle);
    ASSERT_EQ(with_subtitle->lead.title->main_key->key, "title");

    // no balance arg
    ASSERT_TRUE(with_subtitle->lead.subtitle);
    ASSERT_EQ(with_subtitle->lead.subtitle->main_key->key,
              "subtitle_should_have_balance");
    ASSERT_EQ(
        with_subtitle->lead.subtitle->main_key->args.count("wallet_balance"),
        0);
  }
}

}  // namespace sweet_home::client_application_menu
