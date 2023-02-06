#include <clients/protocol-routestats/responses.hpp>
#include <endpoints/full/plugins/title/subplugins/title_shuttle.hpp>
#include <experiments3/shuttle_order_flow_settings.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/TARIFF_CATEGORIES_ORDER_FLOW.hpp>

namespace routestats::full::title {

namespace {

const inline std::string kOrderFlowSettingsJson{R"(
{
  "shuttle": {
    "order_flow": "shuttle"
  }
}
)"};

const inline std::string kShuttleOrderFlowSettingsJson{R"(
{
  "enabled": true,
  "selector": {
    "icon": "",
    "image": ""
  },
  "l10n_keys": {
    "name": "",
    "button_title": "foobar_title_key",
    "button_subtitle": "",
    "estimated_waiting_message": ""
  }
}
)"};

using plugins::top_level::ProtocolResponse;

core::Configs3 MockConfigs() {
  core::ExpMappedData experiments;
  experiments[experiments3::ShuttleOrderFlowSettings::kName] = {
      experiments3::ShuttleOrderFlowSettings::kName,
      formats::json::FromString(kShuttleOrderFlowSettingsJson),
      {},
  };
  return {{std::move(experiments)}};
}

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
      {taxi_config::TARIFF_CATEGORIES_ORDER_FLOW,
       formats::json::FromString(kOrderFlowSettingsJson)
           .As<taxi_config::tariff_categories_order_flow::
                   TariffCategoriesOrderFlow>()},
  });
  ctx.taxi_configs =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  ctx.experiments.uservices_routestats_configs = MockConfigs();
  return test::full::MakeTopLevelContext(std::move(ctx));
}

void TestTitleShuttlePlugin(const std::string& class_, bool translate_fail,
                            const std::optional<std::string>& expected_title) {
  TitleShuttlePlugin plugin;
  ProtocolResponse protocol_response = GetBasicTestProtocolResponse(class_);
  plugin.OnGotProtocolResponse(protocol_response);
  const auto result_title =
      plugin.GetTitle(class_, MakeContext(translate_fail));
  ASSERT_EQ(result_title.value_or("(none)"), expected_title.value_or("(none)"));
}

}  // namespace

TEST(TitleShuttlePlugin, ShuttleTariff) {
  TestTitleShuttlePlugin("shuttle", false, "foobar_title_key##ru");
}

TEST(TitleShuttlePlugin, TranslateFail) {
  TestTitleShuttlePlugin("shuttle", true, std::nullopt);
}

TEST(TitleShuttlePlugin, UnrelatedTariff) {
  TestTitleShuttlePlugin("econom", false, std::nullopt);
}

}  // namespace routestats::full::title
