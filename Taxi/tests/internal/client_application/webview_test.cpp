#include "internal/client_application/client_application.hpp"

#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include <taxi_config/variables/PLUS_SWEET_HOME_WEBVIEW_MENU_BASE_URL.hpp>

#include <experiments3/sweet_home_menu_global_config.hpp>

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/action_button_repository.hpp"
#include "tests/mocks/application_repository.hpp"
#include "tests/mocks/countries_service.hpp"
#include "tests/mocks/setting_definition_repository.hpp"

namespace sweet_home::client_application {
namespace {

const core::SDKClient kSdkClient{
    kDefaultClientId, kDefaultServiceId, kDefaultPlatform, {}, {}, {}};

class TestWebviewMenu : public ::testing::Test {
 protected:
  dynamic_config::StorageMock PrepareConfig() {
    return dynamic_config::MakeDefaultStorage(
        {{taxi_config::PLUS_SWEET_HOME_WEBVIEW_MENU_BASE_URL,
          "https://plus.yandex.ru"}});
  }

  Deps PrepareDeps() {
    auto application_repo = std::make_shared<mocks::ApplicationRepositoryMock>(
        [](const core::SDKClient&) -> SDKMenu { return {}; });
    auto settings_repo =
        std::make_shared<mocks::SettingDefinitionRepositoryMock>();

    return {application_repo, settings_repo};
  }

  Context PrepareContext() {
    auto user_subscription = tests::MakePlusSubscription(
        "ya_plus", subscription::PurchaseStatus::kAvailable, false);

    auto wallet = tests::MakeWallet("RUB_wallet", "138");
    return {user_subscription,
            config_storage_.GetSnapshot(),
            tests::MakeExperiments(),
            wallet,
            kSdkClient,
            std::nullopt};
  }

  dynamic_config::StorageMock config_storage_ = PrepareConfig();
  Deps deps_ = PrepareDeps();
  Context context_ = PrepareContext();
};

}  // namespace

TEST_F(TestWebviewMenu, WebviewParams) {
  struct Expected {
    std::string url;
    bool need_authorization{false};
  };

  struct TestCase {
    std::string name;
    formats::json::Value exp_value;
    Expected expected;
  };

  std::vector<TestCase> test_cases;

  // test cases setup
  formats::json::ValueBuilder exp_value{};

  const auto kMenuGlobalConfigValue = formats::json::FromString(R"(
  {
    "enabled": true,
    "menu_type": "WEBVIEW",
    "webview_params": {
      "need_authorization": true,
      "target": "myTarget",
      "message": "myMessage"
    }
  }
)");

  exp_value = kMenuGlobalConfigValue;
  test_cases.push_back(
      {"base", exp_value.ExtractValue(),
       Expected{"https://plus.yandex.ru/?target=myTarget&message=myMessage",
                true}});

  exp_value = kMenuGlobalConfigValue;
  exp_value["webview_params"]["need_authorization"] = false;
  test_cases.push_back(
      {"need_authorization: false", exp_value.ExtractValue(),
       Expected{"https://plus.yandex.ru/?target=myTarget&message=myMessage",
                false}});

  exp_value = kMenuGlobalConfigValue;
  exp_value.Remove("webview_params");
  exp_value["webview_params"] = std::unordered_map<std::string, std::string>{};
  test_cases.push_back({"no webview object args", exp_value.ExtractValue(),
                        Expected{"https://plus.yandex.ru/?", false}});

  exp_value = kMenuGlobalConfigValue;
  exp_value.Remove("webview_params");
  exp_value["webview_params"]["need_authorization"] = true;
  test_cases.push_back({"only need_authorization", exp_value.ExtractValue(),
                        Expected{"https://plus.yandex.ru/?", true}});

  // actual test
  for (const auto& test_case : test_cases) {
    SCOPED_TRACE(test_case.name);

    context_.experiments =
        tests::MakeExperiments({{experiments3::SweetHomeMenuGlobalConfig::kName,
                                 test_case.exp_value}});

    // call
    auto result = GetMenuForApplication(deps_, context_);

    ASSERT_EQ(result.type, MenuType::kWebview);
    ASSERT_TRUE(result.webview_params);
    ASSERT_EQ(result.webview_params->url, test_case.expected.url);
    ASSERT_EQ(result.webview_params->need_authorization,
              test_case.expected.need_authorization);
  }
}

TEST_F(TestWebviewMenu, NoWebviewParams) {
  const auto exp_value = formats::json::FromString(R"(
    {
      "enabled": true,
      "menu_type": "WEBVIEW"
    }
  )");

  context_.experiments = tests::MakeExperiments(
      {{experiments3::SweetHomeMenuGlobalConfig::kName, exp_value}});

  auto result = GetMenuForApplication(deps_, context_);

  ASSERT_EQ(result.type, client_application::MenuType::kNative);
  ASSERT_FALSE(result.webview_params);
}

}  // namespace sweet_home::client_application
