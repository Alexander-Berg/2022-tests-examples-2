#include <fstream>
#include <functional>

#include <boost/filesystem.hpp>

#include <testing/source_path.hpp>

#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/plugins/sdc/plugin.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <experiments3/enable_sdc_2.hpp>
#include <experiments3/sdc_routestats_summary_settings.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/plugins/sdc"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(filename);
  if (!f.is_open()) {
    throw std::runtime_error("Couldn't open file");
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

formats::json::Value GetEnableSdc2Exp(bool out_of_schedule,
                                      bool emergency_disabled) {
  formats::json::ValueBuilder exp_builder{};
  if (out_of_schedule) {
    return LoadJsonFromFile(kTestDataDir +
                            "/exp_enable_sdc_2_out_of_schedule.json");
  } else if (emergency_disabled) {
    return LoadJsonFromFile(kTestDataDir +
                            "/exp_enable_sdc_2_emergency_disabled.json");
  } else {
    return LoadJsonFromFile(kTestDataDir + "/exp_enable_sdc_2.json");
  }

  return exp_builder.ExtractValue();
}

formats::json::Value GetSdcRoutestatsSummarySettingsCfg() {
  return LoadJsonFromFile(kTestDataDir +
                          "/exp_sdc_routestats_summary_settings.json");
}

formats::json::Value GetRoutestatsTariffUnavailableBrandingsCfg() {
  return LoadJsonFromFile(kTestDataDir +
                          "/exp_sdc_routestats_summary_settings.json");
}

routestats::core::Configs3 MakeConfigs() {
  experiments3::models::ExperimentResult
      routestats_tariff_unavailable_brandings{
          "routestats_tariff_unavailable_brandings",
          GetRoutestatsTariffUnavailableBrandingsCfg(),
          {}};
  std::unordered_map<std::string, experiments3::models::ExperimentResult>
      mapped_data{{"routestats_tariff_unavailable_brandings",
                   routestats_tariff_unavailable_brandings}};
  return routestats::core::Configs3{{mapped_data}};
}

}  // namespace

namespace routestats::full {

namespace {

routestats::full::ContextData MakeContext(bool out_of_schedule,
                                          bool emergency_disabled,
                                          std::string payment_type) {
  auto context = routestats::test::full::GetDefaultContext();
  context.input.original_request.payment =
      handlers::RequestPayment{payment_type};
  context.input.original_request.supported_features = {
      handlers::SupportedFeature{"order_button_actions", {"deeplink"}}};
  context.user.auth_context.locale = "ru";
  context.user.auth_context.yandex_taxi_phoneid = "+11111111111";
  context.experiments = {{}, MakeConfigs()};

  using EnableSdc2Exp = experiments3::EnableSdc2;

  core::ExpMappedData exp_mapped_data;
  exp_mapped_data[EnableSdc2Exp::kName] = {
      EnableSdc2Exp::kName,
      GetEnableSdc2Exp(out_of_schedule, emergency_disabled),
      {}};
  context.get_experiments_mapped_data =
      [exps = std::move(exp_mapped_data)](
          const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return exps;
  };

  using SdcRoutestatsSummarySettings =
      experiments3::SdcRoutestatsSummarySettings;

  core::ExpMappedData cfg_mapped_data;
  cfg_mapped_data[SdcRoutestatsSummarySettings::kName] = {
      SdcRoutestatsSummarySettings::kName,
      GetSdcRoutestatsSummarySettingsCfg(),
      {}};

  context.get_configs_mapped_data =
      [cfgs = std::move(cfg_mapped_data)](
          const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return cfgs;
  };

  auto& request = context.input.original_request;

  const auto point_a =
      ::geometry::Position{36.0 * ::geometry::lat, 55.0 * ::geometry::lon};
  const auto point_b =
      ::geometry::Position{36.2 * ::geometry::lat, 55.2 * ::geometry::lon};

  request.route = std::vector<::geometry::Position>{point_a, point_b};
  request.is_lightweight = false;

  const auto& input = context.input;
  context.input = routestats::full::BuildRoutestatsInput(
      request, input.tariff_requirements, input.supported_options);

  return context;
}

}  // namespace

TEST(TestSdcPlugin, SdcWorking) {
  RunInCoro([]() {
    auto context = MakeContext(false, false, "card");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_FALSE(level.tariff_unavailable);
  });
}

TEST(TestSdcPlugin, SdcOutOfSchedule) {
  RunInCoro([]() {
    // 11 Apr 2022 10:37:00 UTC (schedule is against UTC)
    utils::datetime::MockNowSet(std::chrono::system_clock::time_point{
        std::chrono::seconds{1649673420}});

    auto context = MakeContext(true, false, "card");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_TRUE(level.tariff_unavailable.has_value());
    auto& tariff_unavailable = level.tariff_unavailable.value();
    ASSERT_EQ(tariff_unavailable.message,
              "routestats.sdc.tariff_unavailable.out_of_schedule.title##ru");
    ASSERT_EQ(tariff_unavailable.code, "out_of_schedule");

    ASSERT_TRUE(level.summary_style);
    auto& summary_style = level.summary_style.value();
    ASSERT_TRUE(summary_style.order_button.has_value());

    ASSERT_EQ(tariff_unavailable.branding_id,
              "sdc_out_of_schedule_branding_id");

    ASSERT_TRUE(tariff_unavailable.order_button_action.has_value());
    auto& order_button_action = tariff_unavailable.order_button_action.value();
    ASSERT_TRUE(
        std::holds_alternative<core::TypedDeeplinkAction>(order_button_action));

    ASSERT_TRUE(level.title.has_value());
    ASSERT_EQ(level.title.value(),
              "routestats.sdc.tariff_unavailable.out_of_schedule.title##ru");

    ASSERT_TRUE(level.subtitle.has_value());
    ASSERT_EQ(level.subtitle.value(),
              "routestats.sdc.tariff_unavailable.out_of_schedule.subtitle##ru");
  });
}

TEST(TestSdcPlugin, SdcEmergencyDisabled) {
  RunInCoro([]() {
    auto context = MakeContext(false, true, "card");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_TRUE(level.tariff_unavailable.has_value());
    auto& tariff_unavailable = level.tariff_unavailable.value();
    ASSERT_EQ(tariff_unavailable.message,
              "routestats.sdc.tariff_unavailable.emergency_disabled.title##ru");
    ASSERT_EQ(tariff_unavailable.code, "emergency_disabled");

    ASSERT_TRUE(level.summary_style);
    auto& summary_style = level.summary_style.value();
    ASSERT_TRUE(summary_style.order_button.has_value());

    ASSERT_EQ(tariff_unavailable.branding_id,
              "sdc_emergency_disabled_branding_id");

    ASSERT_TRUE(tariff_unavailable.order_button_action.has_value());
    auto& order_button_action = tariff_unavailable.order_button_action.value();
    ASSERT_TRUE(
        std::holds_alternative<core::TypedDeeplinkAction>(order_button_action));

    ASSERT_TRUE(level.title.has_value());
    ASSERT_EQ(level.title.value(),
              "routestats.sdc.tariff_unavailable.emergency_disabled.title##ru");

    ASSERT_TRUE(level.subtitle.has_value());
    ASSERT_EQ(
        level.subtitle.value(),
        "routestats.sdc.tariff_unavailable.emergency_disabled.subtitle##ru");
  });
}

TEST(TestSdcPlugin, CashPaymentUnavailable) {
  RunInCoro([]() {
    auto context = MakeContext(false, false, "cash");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_TRUE(level.tariff_unavailable.has_value());
    auto& tariff_unavailable = level.tariff_unavailable.value();
    ASSERT_EQ(
        tariff_unavailable.message,
        "routestats.sdc.tariff_unavailable.cash_payment_not_available##ru");
    ASSERT_EQ(tariff_unavailable.code, "cash_payment_not_available");

    ASSERT_TRUE(level.summary_style);
    auto& summary_style = level.summary_style.value();
    ASSERT_TRUE(summary_style.order_button.has_value());
  });
}

TEST(TestSdcPlugin, SdcDisabledAndCashPayment) {
  RunInCoro([]() {
    auto context = MakeContext(false, true, "cash");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_TRUE(level.tariff_unavailable.has_value());
    auto& tariff_unavailable = level.tariff_unavailable.value();
    ASSERT_EQ(tariff_unavailable.message,
              "routestats.sdc.tariff_unavailable.emergency_disabled.title##ru");
    ASSERT_EQ(tariff_unavailable.code, "emergency_disabled");

    ASSERT_TRUE(level.summary_style);
    auto& summary_style = level.summary_style.value();
    ASSERT_TRUE(summary_style.order_button.has_value());

    ASSERT_EQ(tariff_unavailable.branding_id,
              "sdc_emergency_disabled_branding_id");

    ASSERT_TRUE(tariff_unavailable.order_button_action.has_value());
    auto& order_button_action = tariff_unavailable.order_button_action.value();
    ASSERT_TRUE(
        std::holds_alternative<core::TypedDeeplinkAction>(order_button_action));

    ASSERT_TRUE(level.title.has_value());
    ASSERT_EQ(level.title.value(),
              "routestats.sdc.tariff_unavailable.emergency_disabled.title##ru");

    ASSERT_TRUE(level.subtitle.has_value());
    ASSERT_EQ(
        level.subtitle.value(),
        "routestats.sdc.tariff_unavailable.emergency_disabled.subtitle##ru");
  });
}

TEST(TestSdcPlugin, TariffCardBullets) {
  RunInCoro([]() {
    auto context = MakeContext(false, false, "card");

    auto plugin_ctx = test::full::MakeTopLevelContext(context);
    SdcPlugin plugin;

    plugin.OnContextBuilt(plugin_ctx);

    routestats::core::ServiceLevel level;
    level.class_ = "selfdriving";

    const auto extensions = plugin.ExtendServiceLevels(plugin_ctx, {level});
    if (extensions.find("selfdriving") != extensions.end()) {
      extensions.at("selfdriving")->Apply("selfdriving", level);
    }

    ASSERT_TRUE(level.tariff_card);
    ASSERT_TRUE(level.tariff_card.has_value());
    ASSERT_EQ(level.tariff_card.value().bullets.size(), 2);
  });
}

}  // namespace routestats::full
