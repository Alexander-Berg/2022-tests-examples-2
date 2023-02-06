#include <fstream>

#include <boost/filesystem.hpp>

#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <endpoints/common/builders/service_level_builder.hpp>
#include <endpoints/common/core/alternative/extender.hpp>
#include <endpoints/common/presenters/alternatives.hpp>
#include <endpoints/full/plugins/combo/plugin.hpp>

#include <experiments3/people_combo_buffer_search.hpp>
#include <experiments3/people_combo_order.hpp>
#include <experiments3/people_combo_order_inner.hpp>
#include <experiments3/people_combo_order_passengers_number_alert.hpp>
#include <experiments3/people_combo_remove_tooltip.hpp>

#include <taxi_config/variables/ROUTESTATS_COMBO_USE_NEW_CANDIDATES_FILTER.hpp>

namespace routestats::plugins::top_level {

namespace {

const boost::filesystem::path kTestFilePath(
    utils::CurrentSourcePath("src/tests/endpoints/full/plugins/combo"));
const std::string kTestDataDir = kTestFilePath.string() + "/static";

const std::string kMulticlass = "multiclass";
const std::string kComboInner = "combo_inner";
const std::string kComboOuter = "combo_outer";

const std::string kProtocolResponseFilename = "protocol_response.json";
const std::string kOuterProtocolResponseFilename =
    "outer_protocol_response.json";
const std::string kPeopleComboOrderExpFilename = "people_combo_order_exp.json";
const std::string kPeopleComboOrderPassengerNumberAlertExpFilename =
    "people_combo_order_passengers_number_alert_exp.json";
const std::string kBufferSearchExpFilename = "people_combo_buffer_search.json";
const std::string kRemoveTooltipExpFilename = "remove_tooltip.json";

const std::string kEconom = "econom";
const std::string kBusiness = "business";

formats::json::Value LoadJsonFromFile(const std::string& filename) {
  auto filepath = kTestDataDir + "/" + filename;
  std::ifstream f(filepath);
  if (!f.is_open()) {
    throw std::runtime_error(
        fmt::format("Couldn't open file '{}' ({})", filename, filepath));
  }
  return formats::json::FromString(std::string(
      std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()));
}

struct DiscountBounds {
  double lower_bound;
  double upper_bound;
};

struct Experiment {
  std::string name;
  formats::json::Value value;
};

using ExperimentsMaker = std::function<std::vector<Experiment>()>;

std::vector<Experiment> DummyExperimentsMaker() { return {}; }

core::Experiments BuildExperiments(
    std::optional<DiscountBounds> discount_bounds,
    ExperimentsMaker exps_maker) {
  core::ExpMappedData experiments;

  // PeopleComboOrder
  auto people_combo_order = LoadJsonFromFile(kPeopleComboOrderExpFilename);
  if (discount_bounds) {
    auto builder = formats::json::ValueBuilder(people_combo_order);
    auto combo_discount_builder = builder["filters"]["discount_bounds"];
    combo_discount_builder["enabled"] = true;
    combo_discount_builder["lower_bound"] = discount_bounds->lower_bound;
    combo_discount_builder["upper_bound"] = discount_bounds->upper_bound;
    people_combo_order = builder.ExtractValue();
  }
  experiments[experiments3::PeopleComboOrder::kName] =
      experiments3::models::ExperimentResult{
          experiments3::PeopleComboOrder::kName, people_combo_order, {}};

  // PeopleComboOrderInner
  formats::json::ValueBuilder pco_inner_builder;
  pco_inner_builder["enabled"] = true;
  experiments[experiments3::PeopleComboOrderInner::kName] = {
      experiments3::PeopleComboOrderInner::kName,
      pco_inner_builder.ExtractValue(),
      {}};

  // PeopleComboOrderPassengerNumberAlert
  auto people_combo_order_passengers_number_alert =
      LoadJsonFromFile(kPeopleComboOrderPassengerNumberAlertExpFilename);
  experiments[experiments3::PeopleComboOrderPassengersNumberAlert::kName] =
      experiments3::models::ExperimentResult{
          experiments3::PeopleComboOrderPassengersNumberAlert::kName,
          people_combo_order_passengers_number_alert,
          {}};

  for (auto& [name, value] : exps_maker()) {
    experiments[name] =
        experiments3::models::ExperimentResult{name, std::move(value), {}};
  }

  return {experiments};
}

full::RoutestatsInput GetDefaultRoutestatsInput() {
  full::RoutestatsInput result;
  result.tariff_requirements = {{kEconom, {}}, {kBusiness, {}}};
  result.original_request.route = {
      geometry::Position{geometry::Longitude(37.587569),
                         geometry::Latitude(55.733393)},
      geometry::Position{geometry::Longitude(37.687569),
                         geometry::Latitude(55.633393)}};
  return result;
}

std::shared_ptr<const plugins::top_level::Context> BuildContext(
    std::optional<DiscountBounds> discount_bounds,
    ExperimentsMaker exps_maker = DummyExperimentsMaker,
    full::RoutestatsInput input = GetDefaultRoutestatsInput()) {
  full::ContextData context = test::full::GetDefaultContext();

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::ROUTESTATS_COMBO_USE_NEW_CANDIDATES_FILTER, true},
  });
  context.taxi_configs =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  context.experiments.uservices_routestats_exps =
      BuildExperiments(discount_bounds, exps_maker);
  context.input = input;
  context.get_experiments_mapped_data =
      [experiments = context.experiments.uservices_routestats_exps](
          const experiments3::models::KwargsBuilderWithConsumer&)
      -> experiments3::models::ClientsCache::MappedData {
    return experiments.mapped_data;
  };
  return test::full::MakeTopLevelContext(context);
}

void ComboCheckDiscountBounds(std::optional<DiscountBounds> discount_bounds,
                              std::set<std::string> final_alternatives) {
  ComboPlugin plugin;

  auto context = BuildContext(discount_bounds);
  plugin.OnContextBuilt(context);

  auto response =
      LoadJsonFromFile(kProtocolResponseFilename).As<ProtocolResponse>();
  plugin.OnGotProtocolResponse(context, response);

  // ModifyAlternatives
  auto [_, alternatives] = routestats::common::BuildModels(response);

  auto extensions = plugin.ModifyAlternatives(alternatives, context);
  auto to_apply_extensions =
      std::vector<std::optional<core::AlternativeExtensionsMap>>({extensions});
  core::ApplyAlternativesExtensions<ComboPlugin*>(
      {&plugin}, to_apply_extensions, alternatives);

  // Check
  std::set<std::string> result_alternatives;
  for (auto& alt_option : alternatives.options) {
    if (alt_option) {
      result_alternatives.insert(alt_option->Type());
    }
  }

  ASSERT_EQ(result_alternatives, final_alternatives);
}

}  // namespace

UTEST(ComboCheckDiscountBounds, Valid) {
  ComboCheckDiscountBounds({}, {kComboInner, kMulticlass});
}

UTEST(ComboCheckDiscountBounds, TooHigh) {
  ComboCheckDiscountBounds(DiscountBounds{0.0, 0.1}, {kMulticlass});
}

UTEST(ComboCheckDiscountBounds, TooLow) {
  ComboCheckDiscountBounds(DiscountBounds{0.3, 0.7}, {kMulticlass});
}

UTEST(ComboBufferSearch, Enabled) {
  ComboPlugin plugin;

  auto context = BuildContext({}, []() -> std::vector<Experiment> {
    auto buffer_search_builder =
        formats::json::ValueBuilder(LoadJsonFromFile(kBufferSearchExpFilename));
    return {Experiment{experiments3::PeopleComboBufferSearch::kName,
                       buffer_search_builder.ExtractValue()}};
  });
  plugin.OnContextBuilt(context);

  auto response =
      LoadJsonFromFile(kOuterProtocolResponseFilename).As<ProtocolResponse>();
  plugin.OnGotProtocolResponse(context, response);

  // ModifyAlternatives
  auto [service_levels, alternatives] =
      routestats::common::BuildModels(response);

  auto extensions = plugin.ModifyAlternatives(alternatives, context);
  auto to_apply_extensions =
      std::vector<std::optional<core::AlternativeExtensionsMap>>({extensions});
  core::ApplyAlternativesExtensions<ComboPlugin*>(
      {&plugin}, to_apply_extensions, alternatives);

  // Check alternatives include only outer
  std::set<std::string> result_alternatives;
  for (auto& alt_option : alternatives.options) {
    if (alt_option) {
      result_alternatives.insert(alt_option->Type());
    }
  }
  ASSERT_EQ(result_alternatives, std::set<std::string>{kComboOuter});

  plugin.OnOfferCreated(context, "", service_levels, alternatives, response);
  auto serializable = plugin.OnAlternativeOptionServiceLevelRendering(
      alternatives.options[0].value(),
      alternatives.options[0].value().service_levels[0], context);

  handlers::AlternativesOption option;
  core::alternatives::SerializeInView(alternatives.options[0].value(), option,
                                      {} /* protocol_extra */);

  // check that buffer search properties exist
  handlers::AlternativesOptionServiceLevel aosl;
  auto result_wrapper = routestats::plugins::common::ResultWrapper<
      handlers::AlternativesOptionServiceLevel>(aosl);
  serializable->SerializeInPlace(result_wrapper);

  ASSERT_TRUE(aosl.extra.HasMember("combo_order"));
  ASSERT_TRUE(aosl.extra["combo_order"].HasMember("alert_properties"));
  ASSERT_TRUE(aosl.extra["combo_order"]["alert_properties"].HasMember(
      "buffer_list_item"));
  auto buffer_list_item =
      aosl.extra["combo_order"]["alert_properties"]["buffer_list_item"];

  ASSERT_EQ(buffer_list_item, formats::json::FromString(R"({
        "title": "people_combo_order.outer.alert.buffer_list_item.title##",
        "subtitle": "people_combo_order.outer.alert.buffer_list_item.subtitle##"})"));

  auto alert = aosl.extra["combo_order"]["alert_properties"];
  ASSERT_TRUE(alert.HasMember("fake_passengers_number_selector"));
  auto selector = alert["fake_passengers_number_selector"];
  ASSERT_EQ(selector["title"].As<std::string>(),
            "people_combo_order.outer.alert.only_one_allowed.title##");
  ASSERT_EQ(selector["subtitle"].As<std::string>(),
            "people_combo_order.outer.alert.only_one_allowed.subtitle##");

  // Check buffer search properties in altoffer
  ASSERT_TRUE(!!alternatives.options[0]->prepared_altoffer);
  auto altoffer =
      alternatives.options[0]->prepared_altoffer->offer_doc.ExtractValue();
  ASSERT_TRUE(altoffer.HasMember("buffer_combo"));
  ASSERT_TRUE(altoffer["buffer_combo"].HasMember("approx_eta_min"));
  ASSERT_EQ(altoffer["buffer_combo"]["approx_eta_min"].As<int>(), 9);
  ASSERT_TRUE(altoffer["buffer_combo"].HasMember("search_subtitle"));
  ASSERT_EQ(altoffer["buffer_combo"]["search_subtitle"].As<std::string>(),
            "people_combo_order.search_screen.subtitle##");
}

UTEST(ComboRemoveTooltip, Enabled) {
  ComboPlugin plugin;

  auto context = BuildContext({}, []() -> std::vector<Experiment> {
    auto buffer_search_builder = formats::json::ValueBuilder(
        LoadJsonFromFile(kRemoveTooltipExpFilename));
    return {Experiment{experiments3::PeopleComboRemoveTooltip::kName,
                       buffer_search_builder.ExtractValue()}};
  });
  plugin.OnContextBuilt(context);

  auto response =
      LoadJsonFromFile(kOuterProtocolResponseFilename).As<ProtocolResponse>();
  plugin.OnGotProtocolResponse(context, response);

  auto core_models = routestats::common::BuildModels(response);
  auto& alternatives = core_models.alternatives;
  auto& service_levels = core_models.service_levels;

  const auto check_service_levels = [](const auto& service_levels,
                                       const auto checker) {
    for (const auto& sl : service_levels) {
      checker(sl);
    }
  };

  // Check alternative options and service_levels exist
  ASSERT_TRUE(!alternatives.options.empty());
  ASSERT_TRUE(alternatives.options.front().has_value());
  ASSERT_TRUE(!alternatives.options.front()->service_levels.empty());

  // Check alternatives have tooltip
  check_service_levels(alternatives.options.front()->service_levels,
                       [](const auto& sl) {
                         ASSERT_TRUE(sl.selector.has_value());
                         ASSERT_TRUE(sl.selector->tooltip.has_value());
                       });

  auto extensions = plugin.ModifyAlternatives(alternatives, context);
  auto to_apply_extensions =
      std::vector<std::optional<core::AlternativeExtensionsMap>>({extensions});
  core::ApplyAlternativesExtensions<ComboPlugin*>(
      {&plugin}, to_apply_extensions, alternatives);

  plugin.OnOfferCreated(context, "", service_levels, alternatives, response);
  auto serializable = plugin.OnAlternativeOptionServiceLevelRendering(
      alternatives.options[0].value(),
      alternatives.options[0].value().service_levels[0], context);

  handlers::AlternativesOption option;
  option.service_levels.emplace();
  core::alternatives::SerializeInView(alternatives.options[0].value(), option,
                                      {} /* protocol_extra */);

  // Check alternatives don't have tooltip
  check_service_levels(*option.service_levels, [](const auto& sl) {
    ASSERT_TRUE(sl.selector.has_value());
    ASSERT_TRUE(!sl.selector->tooltip.has_value());
  });
}

UTEST(ComboSurgeTest, MinMaxValue) {
  auto context = BuildContext({});

  std::unordered_map<double, bool> surge_allowed = {
      {1, false}, {3, true}, {7, false}};
  for (const auto& [surge, allowed] : surge_allowed) {
    ComboPlugin plugin;
    plugin.OnContextBuilt(context);
    ASSERT_EQ(plugin.ComboOuterAllowed(), true);
    ServiceLevel service_level;
    service_level.class_ = "econom";
    service_level.surge.emplace();
    service_level.surge->value = decimal64::Decimal<4>::FromFloatInexact(surge);
    plugin.ExtendServiceLevels(context, {service_level});
    ASSERT_EQ(plugin.ComboOuterAllowed(), allowed);
  }
}

UTEST(ComboReqTest, UnavailabilityWithReqInCategory) {
  auto context = BuildContext({});
  ComboPlugin plugin;
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  auto input = GetDefaultRoutestatsInput();
  input.tariff_requirements = {{kEconom, {}},
                               {kBusiness, {{"yellowcarnumber", true}}}};
  auto& reqs = input.original_request.tariff_requirements.emplace();
  reqs = {{kEconom, {}}, {kBusiness, {}}};
  reqs[1].requirements.emplace().extra.insert({"yellowcarnumber", true});
  context = BuildContext({}, DummyExperimentsMaker, input);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  input.tariff_requirements = {{kEconom, {{"yellowcarnumber", true}}},
                               {kBusiness, {}}};
  reqs = {{kEconom, {}}, {kBusiness, {}}};
  reqs[0].requirements.emplace().extra.insert({"yellowcarnumber", true});
  context = BuildContext({}, DummyExperimentsMaker, input);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), false);
  ASSERT_EQ(plugin.ComboInnerAllowed(), false);
}

UTEST(ComboReqTest, UnavailabilityWithReq) {
  auto context = BuildContext({});
  ComboPlugin plugin;
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  auto input = GetDefaultRoutestatsInput();
  auto& reqs = input.original_request.requirements.emplace();
  reqs.extra.insert({"childchair", true});
  context = BuildContext({}, DummyExperimentsMaker, input);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), false);
  ASSERT_EQ(plugin.ComboInnerAllowed(), false);
}

UTEST(ComboPointsTest, NotEnough) {
  auto context = BuildContext({});
  ComboPlugin plugin;
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  auto input = GetDefaultRoutestatsInput();
  input.original_request.route = {geometry::Position{
      geometry::Longitude(37.587569), geometry::Latitude(55.733393)}};
  context = BuildContext({}, DummyExperimentsMaker, input);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), false);
  ASSERT_EQ(plugin.ComboInnerAllowed(), false);
}

UTEST(ComboPointsTest, TooMuch) {
  auto context = BuildContext({});
  ComboPlugin plugin;
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), true);
  ASSERT_EQ(plugin.ComboInnerAllowed(), true);
  auto input = GetDefaultRoutestatsInput();
  input.original_request.route = {
      geometry::Position{geometry::Longitude(37.587569),
                         geometry::Latitude(55.733393)},
      geometry::Position{geometry::Longitude(37.687569),
                         geometry::Latitude(55.833393)},
      geometry::Position{geometry::Longitude(37.787569),
                         geometry::Latitude(55.933393)}};
  context = BuildContext({}, DummyExperimentsMaker, input);
  plugin.OnContextBuilt(context);
  ASSERT_EQ(plugin.ComboOuterAllowed(), false);
  ASSERT_EQ(plugin.ComboInnerAllowed(), false);
}

UTEST(ComboDistanceTest, NotEnough) {
  ComboPlugin plugin;

  auto context = BuildContext({});
  plugin.OnContextBuilt(context);

  auto response =
      LoadJsonFromFile(kProtocolResponseFilename).As<ProtocolResponse>();
  plugin.OnGotProtocolResponse(context, response);
  ASSERT_TRUE(plugin.ComboOuterAllowed());
  response.internal_data.route_info->distance = "9001";  // over nine thousand!
  plugin.OnGotProtocolResponse(context, response);
  ASSERT_FALSE(plugin.ComboOuterAllowed());
}

}  // namespace routestats::plugins::top_level
