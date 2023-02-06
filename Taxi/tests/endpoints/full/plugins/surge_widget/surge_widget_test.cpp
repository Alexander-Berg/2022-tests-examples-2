#include <gtest/gtest.h>
#include <fstream>

#include <boost/filesystem.hpp>
#include <geometry/position.hpp>

#include <testing/source_path.hpp>

#include <userver/utest/utest.hpp>

#include <experiments3/surge_widget.hpp>

#include <core/context/clients/clients_impl.hpp>
#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/full/plugins/surge_widget/plugin.hpp>
#include <experiments3/surge_widget_weather.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <weather-client-wrapper/weather_client_wrapper.hpp>

namespace routestats::full {

namespace {
static const double kSecToHr = 1.0 / 3600.0;

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/plugins/surge_widget"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  std::ifstream f(kTestDataDir + "/" + filename);
  if (!f.is_open()) {
    throw std::runtime_error("Couldn't open file");
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

experiments3::models::ClientsCache::MappedData LoadExperiment(
    const std::string& name, const std::string& filename) {
  return {{name, experiments3::models::ExperimentResult{
                     name, LoadJsonFromFile(filename),
                     experiments3::models::ResultMetaInfo{}}}};
}

using Kwargs = experiments3::models::KwargsBuilderWithConsumer;
using clients::protocol_routestats::Alternatives;
using clients::protocol_routestats::AlternativesOption;
using clients::protocol_routestats::AlternativesOptionServiceLevel;

namespace weather_defs = ::handlers::libraries::weather_client_wrapper;

class WeatherClientMock final
    : public weather_client_wrapper::WeatherClientWrapper {
 public:
  WeatherClientMock(
      std::optional<weather_defs::WeatherConditionWithIcon> weather)
      : weather_(std::move(weather)) {}

  weather_defs::WeatherConditionWithIcon GetWeatherConditionWithIcon(
      const ::geometry::Position&) const {
    return weather_.value();
  };

  weather_defs::WeatherCurrentState GetWeatherCurrentState(
      const ::geometry::Position&) const {
    throw std::runtime_error("not implemented");
  };

 private:
  std::optional<weather_defs::WeatherConditionWithIcon> weather_;
};

handlers::RoutestatsResponse TestSurgeWidgetPlugin(
    const experiments3::models::ClientsCache::MappedData& experiments,
    const std::optional<std::string_view>& surge,
    const std::optional<clients::protocol_routestats::InternalDataRouteinfo>&
        route_info,
    const std::optional<weather_defs::WeatherConditionWithIcon>& weather,
    const std::function<void(const experiments3::models::KwargsBase&)>&
        kwarg_checker) {
  handlers::RoutestatsResponse result;

  full::ContextData test_ctx = test::full::GetDefaultContext();
  test_ctx.get_experiments_mapped_data = [&kwarg_checker,
                                          &experiments](const Kwargs& kwargs)
      -> experiments3::models::ClientsCache::MappedData {
    kwarg_checker(kwargs.Build());
    return experiments;
  };
  WeatherClientMock weather_client_mock(weather);
  test_ctx.clients.weather = routestats::core::MakeClient(
      static_cast<weather_client_wrapper::WeatherClientWrapper&>(
          std::ref(weather_client_mock)));
  test_ctx.experiments.uservices_routestats_configs.mapped_data =
      LoadExperiment(
          experiments3::SurgeWidgetWeather::kName,
          weather ? "cfg_widget_weather.json" : "cfg_widget_no_weather.json");
  test_ctx.input.original_request.route = {
      geometry::Position::FromGeojsonArray({55, 37})};
  auto plugin_ctx = test::full::MakeTopLevelContext(test_ctx);
  SurgeWidgetPlugin plugin;
  plugin.OnContextBuilt(plugin_ctx);

  ProtocolResponse response;
  response.internal_data.route_info = route_info;
  std::vector<AlternativesOptionServiceLevel> alt_service_levels = {{"econom"}};
  AlternativesOption alt_opt{"explicit_antisurge", std::nullopt,
                             alt_service_levels};
  response.alternatives = Alternatives{};
  response.alternatives->options = std::vector<AlternativesOption>{};
  response.alternatives->options->push_back(std::move(alt_opt));

  auto [_, alternatives] = common::BuildModels(response);

  auto input_sl = test::MockDefaultServiceLevel("econom");
  if (surge) {
    core::PaidOptions po;
    po.value = decimal64::Decimal<4>(*surge);
    input_sl.paid_options = po;
  }

  plugin.OnGotProtocolResponse(plugin_ctx, response);
  plugin.OnServiceLevelsReady(plugin_ctx, {input_sl});

  auto sl_patch = plugin.OnServiceLevelRendering(input_sl, plugin_ctx);
  if (sl_patch) {
    handlers::ServiceLevel sl;
    plugins::common::ResultWrapper<handlers::ServiceLevel> wrapper(sl);
    sl_patch->SerializeInPlace(wrapper);
    result.service_levels.push_back(std::move(sl));
  }

  const auto& alternative = alternatives.options.at(0);
  auto alt_patch = plugin.OnAlternativeOptionServiceLevelRendering(
      *alternative, alternative->service_levels.at(0), plugin_ctx);
  if (alt_patch) {
    handlers::AlternativesOptionServiceLevel alt_sl;
    plugins::common::ResultWrapper<handlers::AlternativesOptionServiceLevel>
        wrapper(alt_sl);
    alt_patch->SerializeInPlace(wrapper);

    handlers::AlternativesOption alt_option;
    alt_option.type = alternative->type;
    alt_option.service_levels.emplace().push_back(std::move(alt_sl));

    result.alternatives.emplace().options.emplace().push_back(
        std::move(alt_option));
  }

  return result;
}

void AssertDoubleOpt(const experiments3::models::KwargsBase& kwarg,
                     const std::string& key,
                     const std::optional<double>& value) {
  const auto& arg = kwarg.FindOptional(key);
  if (value) {
    const auto actual = arg ? std::get<double>(*arg) : 0;
    ASSERT_DOUBLE_EQ(actual, *value);
  } else {
    ASSERT_EQ(arg, nullptr);
  }
}

template <typename T>
void AssertEqualsOpt(const experiments3::models::KwargsBase& kwarg,
                     const std::string& key, const std::optional<T>& value) {
  const auto& arg = kwarg.FindOptional(key);
  if (value) {
    const auto actual = arg ? std::get<T>(*arg) : T{};
    ASSERT_EQ(actual, *value);
  } else {
    ASSERT_EQ(arg, nullptr);
  }
}

void AssertKwargs(
    const experiments3::models::KwargsBase& kwarg,
    const std::optional<double>& surge,
    const std::optional<double>& distance_km,
    const std::optional<double>& time_h,
    const std::optional<std::string>& weather_condition = std::nullopt) {
  AssertDoubleOpt(kwarg, "surge", surge);
  AssertDoubleOpt(kwarg, "route_distance_km", distance_km);
  AssertDoubleOpt(kwarg, "route_time_h", time_h);
  AssertDoubleOpt(kwarg, "route_avg_speed_kmh",
                  (distance_km && time_h && *time_h)
                      ? std::make_optional(*distance_km / *time_h)
                      : std::nullopt);
  AssertEqualsOpt(kwarg, "weather_condition", weather_condition);
}

}  // namespace

UTEST(SurgeWidgetPlugin, Enabled) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      "123.456", {{"1206", "30"}}, {{"windy", "wind.img"}},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, 123.456, 1.206, 30.0 * kSecToHr, "windy");
      });

  const auto& sl = response.service_levels[0];
  ASSERT_EQ(sl.widget->type, "test");

  ASSERT_EQ(sl.widget->content.balance.balance, 100);
  ASSERT_EQ(sl.widget->content.balance.color, "#E0DEDA");
  ASSERT_EQ(sl.widget->content.balance.leading_icon,
            "surge_widget_leading_icon_default");
  ASSERT_EQ(sl.widget->content.balance.trail_icon,
            "surge_widget_trail_icon_default");
  ASSERT_EQ(sl.widget->content.balance.value_icon,
            "surge_widget_value_icon_default");
}

UTEST(SurgeWidgetPlugin, Balance) {
  for (const auto& t : std::vector<std::pair<std::string, int>>{
           {"0.1", 0},    // < min
           {"1.3", 50},   // min..mid
           {"10", 100},   // mid..max
           {"300", 100},  // > max
       }) {
    const auto& response = TestSurgeWidgetPlugin(
        LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
        t.first, {}, {},

        [](const auto&) {});

    const auto& sl = response.service_levels[0];
    const auto& actual = sl.widget->content.balance.balance;
    ASSERT_DOUBLE_EQ(actual, t.second);
  }
}

UTEST(SurgeWidgetPlugin, EnabledNoSurge) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      std::nullopt, {{"1206", "30"}}, {},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, std::nullopt, 1.206, 30.0 * kSecToHr);
      });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget->type, "test");
  ASSERT_EQ(sl.widget->content.balance.balance, 0);
}

UTEST(SurgeWidgetPlugin, EnabledNoDistance) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      "2.13", {{"", "40"}}, {},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, 2.13, std::nullopt, 40 * kSecToHr);
      });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget->type, "test");
}

UTEST(SurgeWidgetPlugin, EnabledNoTime) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      "2.13", {{"500", ""}}, {},

      [](const auto& kwarg) { AssertKwargs(kwarg, 2.13, 0.5, std::nullopt); });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget->type, "test");
}

UTEST(SurgeWidgetPlugin, EnabledZeroTime) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      "2.13", {{"500", "0"}}, {},

      [](const auto& kwarg) { AssertKwargs(kwarg, 2.13, 0.5, 0); });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget->type, "test");
}

UTEST(SurgeWidgetPlugin, Disabled) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_disabled.json"), "1",
      {{"1206", "60"}}, {},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, 1, 1.206, 60.0 * kSecToHr);
      });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget.has_value(), false);
}

UTEST(SurgeWidgetPlugin, EnabledButNoWidget) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget",
                     "exp_surge_widget_enabled_but_no_widget.json"),
      "1", {{"1206", "60"}}, {},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, 1, 1.206, 60.0 * kSecToHr);
      });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget.has_value(), false);
}

UTEST(SurgeWidgetPlugin, NoExperiment) {
  const auto& response =
      TestSurgeWidgetPlugin({},  //
                            "0.123", {{"1", "1"}}, {},

                            [](const auto& kwarg) {
                              AssertKwargs(kwarg, 0.123, 0.001, 1 * kSecToHr);
                            });
  const auto& sl = response.service_levels[0];

  ASSERT_EQ(sl.widget.has_value(), false);
}

UTEST(SurgeWidgetPlugin, EmptyRange) {
  try {
    TestSurgeWidgetPlugin(
        LoadExperiment("surge_widget",
                       "exp_surge_widget_empty_range.json"),  //
        "2.13", {{"1", "1"}}, {},

        [](const auto&) {});
    EXPECT_TRUE(false);  // must throw
  } catch (const std::exception& ex) {
    ASSERT_EQ(std::string(ex.what()),
              "Cannot map value from empty interval: 10 - 10");
  }
}

UTEST(SurgeWidgetPlugin, ExplicitAntisurge) {
  const auto& response = TestSurgeWidgetPlugin(
      LoadExperiment("surge_widget", "exp_surge_widget_enabled.json"),  //
      "123.456", {{"1206", "30"}}, {{"windy", "wind.img"}},

      [](const auto& kwarg) {
        AssertKwargs(kwarg, 123.456, 1.206, 30.0 * kSecToHr, "windy");
      });

  ASSERT_TRUE(response.alternatives->options);
  const auto& alternative = response.alternatives->options->front();
  ASSERT_EQ(alternative.type, "explicit_antisurge");
  ASSERT_TRUE(alternative.service_levels);
  ASSERT_EQ(alternative.service_levels->size(), 1);
  ASSERT_TRUE(alternative.service_levels->at(0).widget);

  const auto& sl = response.service_levels[0];
  ASSERT_EQ(sl.widget->type, "test");
}

}  // namespace routestats::full
