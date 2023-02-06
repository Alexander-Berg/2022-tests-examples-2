
#include <set>

#include <userver/utest/utest.hpp>

#include <boost/algorithm/string.hpp>

#include <testing/taxi_config.hpp>
#include <userver/http/url.hpp>

#include "internal/subscription/models.hpp"
#include "use_cases/user_state/user_state.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/setting_definition_repository.hpp"
#include "tests/mocks/user_preferences_repository.hpp"
#include "tests/use_cases/user_state/output_models_test.hpp"

namespace sweet_home::user_state {
namespace {

const std::string kServiceId = "some_id";

UserStateDeps PrepareDeps() {
  UserStateDeps deps;

  deps.user_preferences_repository =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();

  deps.setting_repository =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  return deps;
}

UserStateContext PrepareContext(bool add_wallet = true,
                                bool has_cashback = false) {
  auto user_subscription = tests::MakePlusSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, has_cashback);
  auto experiments = tests::MakeExperiments();

  std::optional<core::Wallet> wallet{};
  if (add_wallet) wallet = tests::MakeWallet("RUB_wallet", "138");

  return {user_subscription,
          kDefaultSdkClient,
          experiments,
          dynamic_config::GetDefaultSnapshot(),
          core::HideableWallet{wallet},
          tests::defaults::kDefaultLocale,
          std::optional<burning_balance::BurnEvent>{}};
}

void AssertUrl(const std::string& url, const std::string& expected_base,
               const std::set<std::string>& expected_args) {
  std::vector<std::string> parts;
  boost::split(parts, url, boost::is_any_of("?"));

  const auto& base = parts[0];
  ASSERT_EQ(base, expected_base);

  if (parts.size() < 1) {
    FAIL() << "url " << url << " has no arguments";
    return;
  }

  const auto& args = parts[1];
  std::set<std::string> parsed_args;
  boost::split(parsed_args, args, boost::is_any_of("&"));
  ASSERT_EQ(parsed_args, expected_args);
}

}  // namespace

TEST(TestUserState, HappyPath) {
  // deps
  auto deps = PrepareDeps();

  // context
  auto context = PrepareContext();

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  // assertions
  auto expected_subscription = tests::output_models::MakeSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false);
  ASSERT_EQ(result.subscription, expected_subscription);

  ASSERT_EQ(result.settings.version, "some_version");
  ASSERT_EQ(result.settings.settings.size(), 2);

  output_models::AssertSetting(
      result.settings.settings[0],
      tests::output_models::MakeSetting("global_setting_id", "some_value"));

  // this setting must be added in result
  output_models::AssertSetting(
      result.settings.settings[1],
      tests::output_models::MakeSetting("service_setting_id",
                                        "another_default_value", true, true));

  ASSERT_EQ(result.wallets.size(), 1);
  AssertWallet(result.wallets[0],
               tests::output_models::MakeWallet("RUB_wallet", "138"));

  auto expected_notifications = tests::output_models::MakeNotifications(1);
  ASSERT_EQ(result.notifications, expected_notifications);
}

TEST(TestUserState, EmptyWalletReturnNoWallet) {
  // deps
  auto deps = PrepareDeps();

  // context
  auto context = PrepareContext(false);

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  // assertions
  auto expected_subscription = tests::output_models::MakeSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false);
  ASSERT_EQ(result.subscription, expected_subscription);

  ASSERT_EQ(result.settings.version, "some_version");
  ASSERT_EQ(result.settings.settings.size(), 2);

  output_models::AssertSetting(
      result.settings.settings[0],
      tests::output_models::MakeSetting("global_setting_id", "some_value"));

  // this setting must be added in result
  output_models::AssertSetting(
      result.settings.settings[1],
      tests::output_models::MakeSetting("service_setting_id",
                                        "another_default_value", true, true));

  // we passed no wallets, so there must be no wallets
  ASSERT_EQ(result.wallets.size(), 0);

  auto expected_notifications = tests::output_models::MakeNotifications(1);
  ASSERT_EQ(result.notifications, expected_notifications);
}

TEST(TestUserState, WalletHidden) {
  // deps
  auto deps = PrepareDeps();

  // context
  auto context = PrepareContext();
  const bool wallet_visible = false;
  context.user_wallet = core::HideableWallet{
      tests::MakeWallet("RUB_wallet", "138"), wallet_visible};

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  ASSERT_EQ(result.wallets.size(), 0);
}

TEST(TestUserState, UnknownPreferences) {
  // deps
  auto user_preferences_handler = [](const std::string&, const std::string&) {
    // currently we store globals on clients, so no global setting
    return tests::MakeUserPreferences({
        tests::MakePreference("global_setting_id", "some_value"),
        // this preference would be ignored
        tests::MakePreference("unknown_setting_id", "some_value"),
    });
  };

  auto deps = PrepareDeps();
  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_GetPreferences(user_preferences_handler);
  deps.user_preferences_repository = user_preferences_mock;

  // context
  auto context = PrepareContext();

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  // assertions
  auto expected_subscription = tests::output_models::MakeSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false);
  ASSERT_EQ(result.subscription, expected_subscription);

  ASSERT_EQ(result.settings.version, "some_version");
  ASSERT_EQ(result.settings.settings.size(), 2);

  output_models::AssertSetting(
      result.settings.settings[0],
      tests::output_models::MakeSetting("global_setting_id", "some_value"));

  // this setting must be added in result
  output_models::AssertSetting(
      result.settings.settings[1],
      tests::output_models::MakeSetting("service_setting_id",
                                        "another_default_value", true, true));

  ASSERT_EQ(result.wallets.size(), 1);
  AssertWallet(result.wallets[0],
               tests::output_models::MakeWallet("RUB_wallet", "138"));

  auto expected_notifications = tests::output_models::MakeNotifications(1);
  ASSERT_EQ(result.notifications, expected_notifications);
}

TEST(TestUserState, RepositoryReturnErrorDuringGetPreferences) {
  // deps
  auto user_preferences_handler =
      [](const std::string&,
         const std::string&) -> user_preferences::UserPreferences {
    throw user_preferences::RepositoryError("");
  };

  auto deps = PrepareDeps();
  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_GetPreferences(user_preferences_handler);
  deps.user_preferences_repository = user_preferences_mock;

  // context
  auto context = PrepareContext();

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  // assertions
  ASSERT_EQ(result.settings.version, "");
  ASSERT_EQ(result.settings.settings.size(), 1);

  output_models::AssertSetting(
      result.settings.settings[0],
      tests::output_models::MakeSetting("service_setting_id",
                                        "another_default_value", true, true));
}

TEST(TestUserState, SettingsDisabled) {
  // deps
  auto deps = PrepareDeps();

  auto setting_repository =
      std::make_shared<mocks::SettingDefinitionRepositoryMock>();
  setting_repository->SetStub_GetDefinitions([](const std::string&) {
    return tests::MakeSettingDefinitionMap({
        tests::MakeDefinition(  //
            "disabled_setting", "value", false, false),
        tests::MakeDefinition(  //
            "disabled_by_balance", "value", false, true,
            tests::MakeRequirements({{"has_positive_balance", true}})),
        tests::MakeDefinition(  //
            "disabled_by_cashback_offer", "value", false, true,
            tests::MakeRequirements({{"has_cashback_offer", true}})),
        tests::MakeDefinition(  //
            "disabled_by_subscription", "value", false, true,
            tests::MakeRequirements({{"has_plus", false}})),
        tests::MakeDefinition(  //
            "enabled_by_subscription", "value", false, true,
            tests::MakeRequirements(
                {{"has_cashback_offer", false}, {"has_plus", true}})),
    });
  });
  deps.setting_repository = setting_repository;

  auto user_preferences_mock =
      std::make_shared<mocks::UserPreferencesRepositoryMock>();
  user_preferences_mock->SetStub_GetPreferences(
      [](const std::string&, const std::string&) {
        return tests::MakeUserPreferences({
            tests::MakePreference("disabled_setting", "some_value"),
            tests::MakePreference("disabled_by_balance", "some_value"),
            tests::MakePreference("disabled_by_cashback_offer", "some_value"),
            tests::MakePreference("disabled_by_subscription", "some_value"),
            tests::MakePreference("enabled_by_subscription", "some_value"),
        });
      });
  deps.user_preferences_repository = user_preferences_mock;

  // context
  auto context = PrepareContext(false, false);

  // call
  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);

  // assertions
  output_models::AssertSetting(  //
      result.settings.settings[0],
      tests::output_models::MakeSetting("disabled_setting", "some_value",
                                        false));

  // this setting must be added in result
  output_models::AssertSetting(  //
      result.settings.settings[1],
      tests::output_models::MakeSetting("disabled_by_balance", "some_value",
                                        false));

  output_models::AssertSetting(  //
      result.settings.settings[2],
      tests::output_models::MakeSetting("disabled_by_cashback_offer",
                                        "some_value", false));

  output_models::AssertSetting(  //
      result.settings.settings[3],
      tests::output_models::MakeSetting("disabled_by_subscription",
                                        "some_value", false));

  output_models::AssertSetting(  //
      result.settings.settings[4],
      tests::output_models::MakeSetting("enabled_by_subscription", "some_value",
                                        true));
}

TEST(TestUserState, WebviewPurchaseParams) {
  auto deps = PrepareDeps();
  auto context = PrepareContext();

  const std::string kExpectedBase = "base_url/";

  // 1. webview params exist -> url created
  core::SDKClientConfig client_config;
  client_config.purchase_type = core::SDKPurchaseType::kWebview;
  client_config.webview_params = core::WebviewParams{
      "base_url", "some_widget_service_name", "some_widget_sub_service_name"};
  context.sdk_client.config = client_config;

  auto result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);
  ASSERT_TRUE(result.subscription.webview_purchase_params);

  std::string expected_url;
  AssertUrl(result.subscription.webview_purchase_params->url, kExpectedBase,
            {"lang=ru",                                            //
             "widgetSubServiceName=some_widget_sub_service_name",  //
             "widgetServiceName=some_widget_service_name",         //
             "productIds=product_ya_plus",                         //
             "target=landing-taxi"});

  // 2. additional args
  context.sdk_client.config.webview_params->additional_args = {
      {"someAdditionalArg", "someValue"},
      {"target", "overriddenValue"},  // additional arg overrides dynamic
  };
  result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);
  ASSERT_TRUE(result.subscription.webview_purchase_params);

  AssertUrl(result.subscription.webview_purchase_params->url, kExpectedBase,
            {"someAdditionalArg=someValue",                        //
             "lang=ru",                                            //
             "widgetSubServiceName=some_widget_sub_service_name",  //
             "widgetServiceName=some_widget_service_name",         //
             "productIds=product_ya_plus",                         //
             "target=overriddenValue"});

  // reset back additional args
  context.sdk_client.config.webview_params->additional_args = {};

  // 3. subservice absent -> url created
  context.sdk_client.config.webview_params->widgetSubServiceName = std::nullopt;
  result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);
  ASSERT_TRUE(result.subscription.webview_purchase_params);

  AssertUrl(result.subscription.webview_purchase_params->url, kExpectedBase,
            {"lang=ru",                                     //
             "widgetServiceName=some_widget_service_name",  //
             "productIds=product_ya_plus",                  //
             "target=landing-taxi"});

  // 4. webview params absent -> no url created
  context.sdk_client.config.webview_params = std::nullopt;
  result =
      GetStateOfUser(deps, context, tests::defaults::kYandexUid, kServiceId);
  ASSERT_FALSE(result.subscription.webview_purchase_params);
}

}  // namespace sweet_home::user_state
