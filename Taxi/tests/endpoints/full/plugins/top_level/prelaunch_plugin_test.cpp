#include <clients/protocol-routestats/responses.hpp>
#include <endpoints/full/plugins/prelaunch/plugin.hpp>
#include <experiments3/prelaunch_settings.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::plugins::top_level {

namespace {

core::Configs3 MockConfigs(bool enabled, bool with_bk, bool with_exp) {
  core::ExpMappedData experiments;
  formats::json::ValueBuilder exp_json{};
  exp_json["enabled"] = enabled;
  if (with_bk) {
    exp_json["button_key"] = "bk";
  }
  if (with_exp) {
    exp_json["launch_exp"] = "nor_launch";
  }
  experiments[experiments3::PrelaunchSettings::kName] = {
      experiments3::PrelaunchSettings::kName,
      exp_json.ExtractValue(),
      {},
  };
  return {{std::move(experiments)}};
}

core::Experiments MockExperiments(bool exp_enabled) {
  core::ExpMappedData experiments;
  if (exp_enabled) {
    experiments["nor_launch"] = {
        "nor_launch",
        formats::json::FromString("{\"enabled\": true}"),
        {},
    };
  }
  return {std::move(experiments)};
}

std::shared_ptr<const plugins::top_level::Context> MakeContext(
    bool translate_fail, bool ps_enabled, bool with_bk, bool with_exp,
    bool exp_enabled) {
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
  ctx.experiments.uservices_routestats_configs =
      MockConfigs(ps_enabled, with_bk, with_exp);
  ctx.experiments.uservices_routestats_exps = MockExperiments(exp_enabled);
  return test::full::MakeTopLevelContext(std::move(ctx));
}

std::vector<core::ServiceLevel> MockServiceLevels(
    const std::unordered_map<std::string, std::optional<std::string>>&
        service_levels) {
  std::vector<core::ServiceLevel> result;

  for (const auto& [class_, unavailability] : service_levels) {
    core::ServiceLevel service_level;
    service_level.class_ = class_;
    if (unavailability) {
      auto& ta = service_level.tariff_unavailable.emplace();
      ta.code = ta.message = *unavailability;
    }
    result.push_back(std::move(service_level));
  }
  return result;
}

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  return MockServiceLevels(
      {{"econom", std::nullopt}, {"ultima", "other_reason"}});
}

void TestPlugin(bool translate_fail, bool ps_enabled, bool with_bk,
                bool with_exp, bool exp_enabled, bool changed,
                const std::string& expected_key) {
  PrelaunchPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto extensions = plugin.ExtendServiceLevels(
      MakeContext(translate_fail, ps_enabled, with_bk, with_exp, exp_enabled),
      service_levels);
  if (!changed) {
    ASSERT_EQ(extensions.size(), 0);
    return;
  }
  ASSERT_EQ(extensions.size(), service_levels.size());
  for (auto& level : service_levels) {
    ASSERT_EQ(extensions.count(level.class_), 1);
    extensions.at(level.class_)->Apply("prelaunch_plugin", level);
  }
  for (const auto& level : service_levels) {
    ASSERT_NE(level.tariff_unavailable, std::nullopt);
    ASSERT_EQ(level.tariff_unavailable->code, "prelaunch");
    ASSERT_EQ(level.tariff_unavailable->message, expected_key);
  }
}

}  // namespace

TEST(PrelaunchPlugin, SettingsOff) {
  TestPlugin(false, false, true, true, true, false, "");
}

TEST(PrelaunchPlugin, PrelaunchToLaunchExp) {
  TestPlugin(false, true, true, true, true, false, "");
}

TEST(PrelaunchPlugin, TestDifferentKeys) {
  TestPlugin(true, true, true, false, false, true, "Available soon");
  TestPlugin(false, true, false, false, false, true,
             "routestats.tariff_unavailable.prelaunch##ru");
  TestPlugin(false, true, true, false, false, true, "bk##ru");
}

TEST(PrelaunchPlugin, WithExpButNoExpMatched) {
  TestPlugin(false, true, true, true, false, true, "bk##ru");
}

}  // namespace routestats::plugins::top_level
