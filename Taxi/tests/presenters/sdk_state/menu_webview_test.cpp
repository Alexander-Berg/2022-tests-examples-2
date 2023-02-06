#include <userver/utest/utest.hpp>

#include <json-diff/json_diff.hpp>

#include "presenters/sdk-state/sdk-state-v2/menu.hpp"

#include "tests/mocks/price_formatter_service.hpp"
#include "tests/mocks/translator_service.hpp"
#include "tests/use_cases/client_application_menu/output_models_test.hpp"

namespace sweet_home::presenters::sdk_state_v2 {

namespace {

namespace output_models = client_application_menu::output_models;

output_models::MenuData PrepareModel() {
  output_models::MenuData menu;
  menu.type = client_application::MenuType::kWebview;
  menu.currency = "RUB";
  menu.balance_badge.subtitle =
      core::MakeTranslation(core::MakeClientKey("badge"));
  return menu;
}

MenuContext PrepareContext() { return {}; }

}  // namespace

TEST(TestBuildMenuWebview, HappyPath) {
  auto context = PrepareContext();
  auto model = PrepareModel();

  model.webview_params = {"https://plus.yandex.ru/?", true};

  auto result = BuildMenuWebview(context, model);

  const std::string kExpectedJson = R"(
    {
      "url": "https://plus.yandex.ru/?",
      "need_authorization": true
    }
  )";

  const auto& response = formats::json::ValueBuilder(result).ExtractValue();
  const auto& expected = formats::json::FromString(kExpectedJson);
  EXPECT_PRED_FORMAT2(json_diff::AreValuesEqual, response, expected);
}

}  // namespace sweet_home::presenters::sdk_state_v2
