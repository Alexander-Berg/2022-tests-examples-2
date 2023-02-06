#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include "internal/client_application/client_application.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/application_repository.hpp"
#include "tests/mocks/setting_definition_repository.hpp"

namespace sweet_home::client_application {

namespace {
const core::SDKClient kSdkClient{
    kDefaultClientId, kDefaultServiceId, kDefaultPlatform, {}, {}, {}};
}  // namespace

namespace {

auto default_definitions_handler = [](const std::string&) {
  return tests::MakeSettingDefinitionMap(
      {tests::MakeDefinition("global_setting_id", "global_default_value"),
       tests::MakeDefinition("service_setting_id",
                             setting::SettingType::kString,
                             "another_default_value", true)});
};

formats::json::Value MakeMenuGlobalConfig(std::string menu_type = "NATIVE",
                                          bool enabled = true,
                                          bool is_forcing = false) {
  formats::json::ValueBuilder builder(formats::common::Type::kObject);
  builder["enabled"] = enabled;
  builder["menu_type"] = menu_type;

  formats::json::ValueBuilder webview_params(formats::common::Type::kObject);
  webview_params["need_authorization"] = true;

  builder["webview_params"] = webview_params;
  if (is_forcing) builder["force_native_on_country_mismatch"] = true;

  return builder.ExtractValue();
}

helpers::ExtendedRegion MakeExtendedRegion(
    std::string base_country_code = "ru",
    std::string remote_country_code = "ru") {
  helpers::ExtendedRegion extended_region{};
  extended_region.region = {base_country_code, 1, "1"};
  extended_region.region_by_ip = {remote_country_code, 2, "2"};
  return extended_region;
}

Deps PrepareDeps(const mocks::GetMenuForApplicationHandler& get_menu_handler) {
  Deps deps;

  deps.application_repository =
      std::make_shared<mocks::ApplicationRepositoryMock>(get_menu_handler);

  auto setting_definition_repository_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  setting_definition_repository_mock->SetStub_GetDefinitions(
      default_definitions_handler);
  deps.setting_repository = setting_definition_repository_mock;

  return deps;
}

Context PrepareContext(
    bool add_wallet = true, bool plus_active = true,
    bool has_cashback_offer = true,
    std::optional<core::SubscriptionInfo> subscription_info = std::nullopt,
    const std::unordered_map<std::string, formats::json::Value>&
        mapped_experiments = {},
    std::optional<helpers::ExtendedRegion> extended_region = {}) {
  auto config = dynamic_config::GetDefaultSnapshot();
  auto experiments = tests::MakeExperiments(mapped_experiments);
  Context context{{}, config, experiments, {std::nullopt}, {}, extended_region};
  if (add_wallet) {
    context.user_wallet = {tests::MakeWallet("RUB_wallet", "138")};
  }

  subscription::PlusSubscription subscription;
  if (plus_active) {
    subscription.status = subscription::PurchaseStatus::kActive;
  }
  if (has_cashback_offer) {
    subscription.is_cashback = true;
  }
  subscription.subscription_info = subscription_info;
  context.user_subscription = subscription;

  context.sdk_client = kSdkClient;

  return context;
}

void AssertTextArgs(
    const core::TankerKey& tanker_key, const std::string& expected_key,
    const std::unordered_map<std::string, std::string>& expected_args,
    int expected_count = 1) {
  ASSERT_EQ(tanker_key.key, expected_key);
  ASSERT_EQ(tanker_key.args.size(), expected_args.size());
  ASSERT_EQ(tanker_key.args, expected_args);
  ASSERT_EQ(tanker_key.count, expected_count);
}

void AssertHiddenItems(
    const std::vector<Section>& sections,
    const std::vector<std::pair<std::string, bool>>& expected_hidden_items) {
  // NOTE: only one section supported
  AssertSizes(sections, {expected_hidden_items.size()});

  int i = 0;
  for (const auto& [expected_key, expect_hidden] : expected_hidden_items) {
    auto& item = sections[0].items[i++];

    // check if it is an item we want to assert
    AssertElementWithText(item.list_item->lead, expected_key);

    // actual check
    ASSERT_EQ(item.hidden, expect_hidden)
        << "Incorrect hidden state of item #" << i - 1 << ": " << expected_key;
  }
}

}  // namespace

TEST(TestGetMenuForApplication, SettingItem) {
  // prepare
  auto definitions_handler = [](const std::string&) {
    auto setting_definition = tests::MakeDefinition(
        "boolean_setting_id", setting::SettingType::kBoolean, true);
    return tests::MakeSettingDefinitionMap({setting_definition});
  };

  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    auto action = tests::MakeChangeSettingAction("boolean_setting_id");

    auto no_lead_no_trail = tests::MakeListItem(action);

    auto only_lead =
        tests::MakeListItem(action, tests::MakeLead("custom_text_key"));

    auto only_trail = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kDefault));

    auto custom_trail = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kNav));

    auto unknown_setting = tests::MakeChangeSettingAction("unknown_setting_id");
    auto would_be_hidden = tests::MakeListItem(unknown_setting);

    menu.sections = {
        tests::MakeSection({no_lead_no_trail, only_lead, only_trail,
                            custom_trail, would_be_hidden})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto setting_definition_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  setting_definition_mock->SetStub_GetDefinitions(definitions_handler);
  deps.setting_repository = setting_definition_mock;

  auto context = PrepareContext();

  // call
  auto result = GetMenuForApplication(deps, context);

  // assert
  AssertSizes(result.sections, {5});

  // unknown setting not included

  auto& no_lead_no_trail = result.sections[0].items[0].list_item.value();
  AssertAction(no_lead_no_trail.action, actions::ActionType::kChangeSetting,
               "boolean_setting_id");
  // lead added
  AssertElementWithText(no_lead_no_trail.lead, "boolean_setting_id_key");
  // trail added
  AssertElement(no_lead_no_trail.trail, ElementStyle::kSwitch);

  auto& only_lead = result.sections[0].items[1].list_item.value();
  // lead not changed
  AssertElementWithText(only_lead.lead, "custom_text_key");
  // trail added
  AssertElement(only_lead.trail, ElementStyle::kSwitch);

  auto& only_trail = result.sections[0].items[2].list_item.value();
  // trail changed
  AssertElement(only_trail.trail, ElementStyle::kSwitch);

  auto& custom_trail = result.sections[0].items[3].list_item.value();
  // trail not changed
  AssertElement(custom_trail.trail, ElementStyle::kNav);

  auto& would_be_hidden = result.sections[0].items[4];
  ASSERT_TRUE(would_be_hidden.hidden);
}

TEST(TestGetMenuForApplication, UrlItem) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    auto action = tests::MakeOpenUrlAction("http://plus.yandex.ru", true);

    auto no_trail =
        tests::MakeListItem(action, tests::MakeLead("url_text_key"));

    auto trail_with_default = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kDefault));

    auto custom_trail = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kSwitch));

    menu.sections = {
        tests::MakeSection({no_trail, trail_with_default, custom_trail})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto context = PrepareContext();

  // call
  auto result = GetMenuForApplication(deps, context);

  // assert
  AssertSizes(result.sections, {3});

  auto& no_trail = result.sections[0].items[0].list_item.value();
  AssertAction(no_trail.action, actions::ActionType::kOpenUrl,
               "http://plus.yandex.ru");
  ASSERT_EQ(no_trail.action.need_authorization, true);
  // lead not changed
  AssertElementWithText(no_trail.lead, "url_text_key");
  // trail added
  AssertElement(no_trail.trail, ElementStyle::kNav);

  auto& trail_with_default = result.sections[0].items[1].list_item.value();
  // lead not added
  ASSERT_FALSE(trail_with_default.lead);
  // trail changed
  AssertElement(trail_with_default.trail, ElementStyle::kNav);

  auto& custom_trail = result.sections[0].items[2].list_item.value();
  // trail not changed
  AssertElement(custom_trail.trail, ElementStyle::kSwitch);
}

TEST(TestGetMenuForApplication, DeeplinkItem) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    auto action = tests::MakeOpenDeeplinkAction("yandextaxi://qr_scanner");

    auto no_trail =
        tests::MakeListItem(action, tests::MakeLead("open_scanner_key"));

    auto trail_with_default = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kDefault));

    auto custom_trail = tests::MakeListItem(
        action, std::nullopt, tests::MakeTrail(ElementStyle::kSwitch));

    menu.sections = {
        tests::MakeSection({no_trail, trail_with_default, custom_trail})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);
  auto context = PrepareContext();

  // call
  auto result = GetMenuForApplication(deps, context);

  // assert
  AssertSizes(result.sections, {3});

  auto& no_trail = result.sections[0].items[0].list_item.value();
  AssertAction(no_trail.action, actions::ActionType::kOpenDeeplink,
               "yandextaxi://qr_scanner");
  // lead not changed
  AssertElementWithText(no_trail.lead, "open_scanner_key");
  // trail added
  AssertElement(no_trail.trail, ElementStyle::kNav);

  auto& trail_with_default = result.sections[0].items[1].list_item.value();
  // lead not added
  ASSERT_FALSE(trail_with_default.lead);
  // trail changed
  AssertElement(trail_with_default.trail, ElementStyle::kNav);

  auto& custom_trail = result.sections[0].items[2].list_item.value();
  // trail not changed
  AssertElement(custom_trail.trail, ElementStyle::kSwitch);
}

TEST(TestGetMenuForApplication, TextsProcessing) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    auto action = tests::MakeOpenDeeplinkAction("yandextaxi://qr_scanner");

    auto subtitle_need_balance = tests::MakeListItem(
        action, tests::MakeElement("key_without_balance", "key_with_balance"));

    menu.sections = {tests::MakeSection({subtitle_need_balance})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);

  // test with wallet -> subtitle added with arguments
  auto context_with_wallet = PrepareContext();
  auto result1 = GetMenuForApplication(deps, context_with_wallet);
  AssertSizes(result1.sections, {1});

  auto subtitle_need_balance = result1.sections[0].items[0].list_item.value();
  ASSERT_TRUE(subtitle_need_balance.lead->subtitle_key);
  AssertTextArgs(*subtitle_need_balance.lead->subtitle_key, "key_with_balance",
                 {{"wallet_balance", "138"}}, 138);

  // test without wallet -> item is not hidden, subtitle args not substituted
  auto context_without_wallet = PrepareContext(false);
  auto result2 = GetMenuForApplication(deps, context_without_wallet);
  AssertSizes(result2.sections, {1});

  subtitle_need_balance = result2.sections[0].items[0].list_item.value();
  ASSERT_TRUE(subtitle_need_balance.lead->subtitle_key);
  AssertTextArgs(*subtitle_need_balance.lead->subtitle_key, "key_with_balance",
                 {}, 1);
}

TEST(TestGetMenuForApplication, ApplicationRepoThrow) {
  auto context = PrepareContext();

  auto deps1 = PrepareDeps([](const core::SDKClient&) {
    throw ApplicationNotFound("error");
    return SDKMenu{};
  });
  ASSERT_THROW(GetMenuForApplication(deps1, context), ApplicationNotFound);

  auto deps2 = PrepareDeps([](const core::SDKClient&) {
    throw ApplicationMenuNotFound("error");
    return SDKMenu{};
  });
  ASSERT_THROW(GetMenuForApplication(deps2, context), ApplicationMenuNotFound);
}

TEST(TestGetMenuForApplication, MenuItemHiddenByError) {
  // prepare
  auto context = PrepareContext();

  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    auto action = tests::MakeChangeSettingAction("boolean_setting_id");
    auto plain_item =
        tests::MakeListItem(action, tests::MakeElement("plain_item"));

    auto hidden_item =
        tests::MakeListItem(action, tests::MakeElement("hidden_item"));
    hidden_item.hidden = true;

    auto unknown_setting = tests::MakeChangeSettingAction("unknown_setting_id");
    auto hidden_by_error = tests::MakeListItem(
        unknown_setting, tests::MakeElement("hidden_by_error"));

    menu.sections = {
        tests::MakeSection({plain_item, hidden_item, hidden_by_error})};
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
  auto result = GetMenuForApplication(deps, context);

  // assert
  std::vector<std::pair<std::string, bool>> expected_hidden_items{
      {"plain_item", false},
      {"hidden_item", true},
      {"hidden_by_error", true},
  };
  AssertHiddenItems(result.sections, expected_hidden_items);
}

TEST(TestGetMenuForApplication, MenuItemHiddenByRequirements) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;

    auto action = tests::MakeChangeSettingAction("boolean_setting_id");
    auto plain_item = tests::MakeListItem(  //
        action, tests::MakeElement("plain_item"));

    auto hidden_by_balance = tests::MakeListItem(  //
        action, tests::MakeElement("hidden_by_balance"));
    hidden_by_balance.visibility_requirements =
        tests::MakeRequirements({{"has_positive_balance", true}});

    auto hidden_by_cashback_offer = tests::MakeListItem(  //
        action, tests::MakeElement("hidden_by_cashback_offer"));
    hidden_by_cashback_offer.visibility_requirements =
        tests::MakeRequirements({{"has_cashback_offer", true}});

    auto hidden_by_subscription = tests::MakeListItem(  //
        action, tests::MakeElement("hidden_by_subscription"));
    hidden_by_subscription.visibility_requirements =
        tests::MakeRequirements({{"has_plus", true}});

    auto subscription_renewal_for_points_action =
        tests::MakeChangeSettingAction("subscription_renewal_for_points");
    auto hidden_by_ability_renew_sub_by_points = tests::MakeListItem(  //
        subscription_renewal_for_points_action,
        tests::MakeElement("hidden_by_ability_renew_sub_by_points"));
    hidden_by_ability_renew_sub_by_points.visibility_requirements
        .has_ability_renew_sub_by_points = true;

    auto not_hidden = tests::MakeListItem(  //
        action, tests::MakeElement("not_hidden"));
    not_hidden.visibility_requirements = tests::MakeRequirements(
        {{"has_cashback_offer", false}, {"has_plus", false}});

    menu.sections = {tests::MakeSection(
        {plain_item, hidden_by_balance, hidden_by_cashback_offer,
         hidden_by_subscription, hidden_by_ability_renew_sub_by_points,
         not_hidden})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);

  auto setting_definition_mock =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();

  setting_definition_mock->SetStub_GetDefinitions([](const std::string&) {
    auto setting_definition = tests::MakeDefinition(
        "boolean_setting_id", setting::SettingType::kBoolean, true);

    auto subscription_renewal_for_points_setting =
        tests::MakeDefinition("subscription_renewal_for_points",
                              setting::SettingType::kBoolean, false);

    return tests::MakeSettingDefinitionMap(
        {setting_definition, subscription_renewal_for_points_setting});
  });

  deps.setting_repository = setting_definition_mock;

  auto context = PrepareContext(false, false, false);

  // call
  auto result = GetMenuForApplication(deps, context);

  // assert
  std::vector<std::pair<std::string, bool>> expected_hidden_items{
      {"plain_item", false},
      {"hidden_by_balance", true},
      {"hidden_by_cashback_offer", true},
      {"hidden_by_subscription", true},
      {"hidden_by_ability_renew_sub_by_points", true},
      {"not_hidden", false},
  };
  AssertHiddenItems(result.sections, expected_hidden_items);
}

TEST(TestGetMenuForApplication, MenuItemHiddenByFeatures) {
  // prepare
  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;

    auto action = tests::MakeOpenUrlAction("some_url");

    auto plain_item = tests::MakeListItem(  //
        action, tests::MakeElement("plain_item"));

    auto one_feature = tests::MakeListItem(  //
        action, tests::MakeElement("one_feature"));
    one_feature.required_client_features = {"feature1"};

    auto many_features = tests::MakeListItem(  //
        action, tests::MakeElement("many_features"));
    many_features.required_client_features = {"feature1", "feature2"};

    menu.sections = {
        tests::MakeSection({plain_item, one_feature, many_features})};
    return menu;
  };

  auto deps = PrepareDeps(get_menu_handler);

  // no features
  auto context = PrepareContext();
  context.sdk_client.client_features.supported_features = {};
  auto result = GetMenuForApplication(deps, context);
  AssertHiddenItems(result.sections, {
                                         {"plain_item", false},
                                         {"one_feature", true},
                                         {"many_features", true},
                                     });

  // one feature
  context.sdk_client.client_features.supported_features = {"feature1"};
  result = GetMenuForApplication(deps, context);
  AssertHiddenItems(result.sections, {
                                         {"plain_item", false},
                                         {"one_feature", false},
                                         {"many_features", true},
                                     });

  // many features
  context.sdk_client.client_features.supported_features = {"feature1",
                                                           "feature2"};
  result = GetMenuForApplication(deps, context);
  AssertHiddenItems(result.sections, {
                                         {"plain_item", false},
                                         {"one_feature", false},
                                         {"many_features", false},
                                     });

  // extra feature
  context.sdk_client.client_features.supported_features = {"another_feature"};
  result = GetMenuForApplication(deps, context);
  AssertHiddenItems(result.sections, {
                                         {"plain_item", false},
                                         {"one_feature", true},
                                         {"many_features", true},
                                     });

  // many features + extra feature
  context.sdk_client.client_features.supported_features = {
      "feature1", "feature2", "another_feature"};
  result = GetMenuForApplication(deps, context);
  AssertHiddenItems(result.sections, {
                                         {"plain_item", false},
                                         {"one_feature", false},
                                         {"many_features", false},
                                     });
}

TEST(TestGetMenuForApplication, ForcingNativeHomeOnCountryMismatch) {
  // prepare
  auto native_menu_type = client_application::MenuType::kNative;
  auto webview_menu_type = client_application::MenuType::kWebview;

  auto get_menu_handler = [](const core::SDKClient&) {
    SDKMenu menu;
    return menu;
  };
  const std::unordered_map<std::string, formats::json::Value>
      mapped_experiments = {{"sweet-home:menu:global-config",
                             MakeMenuGlobalConfig("WEBVIEW", true, true)}};
  auto deps = PrepareDeps(get_menu_handler);

  // mismatch extended_region
  const helpers::ExtendedRegion extended_region_mismatch =
      MakeExtendedRegion("ru", "kaz");
  auto context = PrepareContext(true, true, true, {}, mapped_experiments,
                                extended_region_mismatch);

  // call mismatch
  auto result = GetMenuForApplication(deps, context);
  ASSERT_EQ(result.type, native_menu_type);

  // match extended_region
  const helpers::ExtendedRegion extended_region_match = MakeExtendedRegion();
  context.extended_region = extended_region_match;

  // call match
  result = GetMenuForApplication(deps, context);
  ASSERT_EQ(result.type, webview_menu_type);
}

}  // namespace sweet_home::client_application
