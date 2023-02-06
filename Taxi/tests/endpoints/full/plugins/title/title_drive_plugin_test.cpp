#include <endpoints/full/plugins/title/subplugins/title_drive.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <clients/protocol-routestats/responses.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/DRIVE_ORDER_FLOW_SETTINGS.hpp>

namespace routestats::full::title {

namespace {

using plugins::top_level::ProtocolResponse;

const inline std::string kDriveOrderFlowSettingsJson{R"(
{
  "car_icons": {
    "__default__": "class_drive_icon_7"
  },
  "l10n_keys": {
    "button_subtitle": "summary.drive.button.subtitle",
    "button_title": "foobar_title_key",
    "cashback_title": "summary.drive.cashback.title",
    "cashback_tooltip_text": "summary.drive.cashback.tooltip.text",
    "description": "summary.drive.description",
    "estimated_waiting_message": "summary.drive.estimated_waiting.message"
  }
}
)"};

ProtocolResponse GetBasicTestProtocolResponse(const std::string& class_) {
  ProtocolResponse protocol_response;
  clients::protocol_routestats::ServiceLevel service_level;
  service_level.class_ = class_;
  protocol_response.service_levels.push_back(service_level);
  return protocol_response;
}

std::shared_ptr<const plugins::top_level::Context> MakeContext(
    bool translate_fail) {
  auto ctx = test::full::GetDefaultContext();
  ctx.user.auth_context.locale = "ru";
  ctx.rendering = test::full::GetDefaultRendering();
  test::TranslationHandler handler =
      [translate_fail](
          const core::Translation& translation,
          const std::string& locale) -> std::optional<std::string> {
    if (translate_fail) {
      return std::nullopt;
    }
    return translation->main_key.key + "##" + locale;
  };
  ctx.rendering.translator = std::make_shared<test::TranslatorMock>(handler);

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::DRIVE_ORDER_FLOW_SETTINGS,
       formats::json::FromString(kDriveOrderFlowSettingsJson)
           .As<taxi_config::drive_order_flow_settings::
                   DriveOrderFlowSettings>()},
  });
  ctx.taxi_configs =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  return test::full::MakeTopLevelContext(std::move(ctx));
}

void TestTitleDrivePlugin(const std::string& class_, bool translate_fail,
                          const std::optional<std::string>& expected_title) {
  TitleDrivePlugin plugin;
  ProtocolResponse protocol_response = GetBasicTestProtocolResponse(class_);
  plugin.OnGotProtocolResponse(protocol_response);
  const auto result_title =
      plugin.GetTitle(class_, MakeContext(translate_fail));
  ASSERT_EQ(result_title.value_or("(none)"), expected_title.value_or("(none)"));
}

}  // namespace

TEST(TitleDrivePlugin, DriveTariff) {
  TestTitleDrivePlugin("drive", false, "foobar_title_key##ru");
}

TEST(TitleDrivePlugin, TranslateFail) {
  TestTitleDrivePlugin("drive", true, std::nullopt);
}

TEST(TitleDrivePlugin, UnrelatedTariff) {
  TestTitleDrivePlugin("econom", false, std::nullopt);
}

}  // namespace routestats::full::title
