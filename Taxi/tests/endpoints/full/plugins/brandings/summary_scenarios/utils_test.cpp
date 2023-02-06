#include "utils_test.hpp"

#include <endpoints/full/plugins/brandings/summary_scenarios/detectors/modifier_detector_base.hpp>
#include <tests/context_mock_test.hpp>
#include <userver/utest/utest.hpp>

namespace routestats::full::brandings {
namespace {
formats::json::Value MakeDefinition(const std::string& tanker_key) {
  formats::json::ValueBuilder show_modes{formats::common::Type::kArray};
  show_modes.PushBack("selected");
  show_modes.PushBack("unselected");

  formats::json::ValueBuilder result;
  result["name"] = "modifier_field";
  result["show_modes"] = show_modes;
  result["tanker_key"] = tanker_key;
  return result.ExtractValue();
}

formats::json::Value MakeSupportedScenariosExp(
    const std::vector<std::string>& scenarios,
    const std::vector<std::string>& supported_classes,
    const std::optional<double>& surge_threshold,
    const std::optional<int>& eta_threshold) {
  formats::json::ValueBuilder builder;
  builder["enabled"] = true;
  builder["scenarios"] =
      formats::json::ValueBuilder(formats::common::Type::kArray);

  for (const auto& scenario_name : scenarios) {
    formats::json::ValueBuilder scenario;
    scenario["name"] = scenario_name;

    formats::json::ValueBuilder definitions{formats::common::Type::kArray};
    definitions.PushBack(MakeDefinition(scenario_name));
    scenario["definitions"] = definitions;

    if (!supported_classes.empty()) {
      scenario["supported_tariffs"] = supported_classes;
    }

    if (surge_threshold) {
      scenario["threshold_surge"] = surge_threshold.value();
    }

    if (eta_threshold) {
      scenario["threshold_eta_min"] = eta_threshold;
    }
    builder["scenarios"].PushBack(scenario.ExtractValue());
  }

  return builder.ExtractValue();
}

core::Experiments MockExperiments(
    const std::vector<std::string>& scenarios,
    const std::vector<std::string>& supported_classes,
    const std::optional<double>& surge_threshold,
    const std::optional<int>& eta_threshold) {
  core::ExpMappedData experiments;
  using BrandingExp = experiments3::SummaryScenarios;
  experiments[BrandingExp::kName] = {
      BrandingExp::kName,
      MakeSupportedScenariosExp(scenarios, supported_classes, surge_threshold,
                                eta_threshold),
      {}};

  return {std::move(experiments)};
}
}  // namespace

void RunDetector(ModifierDetectorBase& detector,
                 const std::vector<core::ServiceLevel>& service_levels) {
  for (const auto& service_level : service_levels) {
    detector.Handle(service_level);
  }
  detector.Complete();
}

full::ContextData PrepareContext(
    const std::vector<std::string>& scenarios,
    const std::vector<std::string>& supported_classes,
    const std::optional<double>& surge_threshold,
    const std::optional<int>& eta_threshold) {
  full::ContextData context = test::full::GetDefaultContext();
  context.experiments.uservices_routestats_exps = MockExperiments(
      scenarios, supported_classes, surge_threshold, eta_threshold);
  return context;
}

OverrideSelectorExperimentWrapper MakeExpWrapper(
    const std::string& scenario_name,
    const std::vector<std::string>& supported_classes,
    const std::optional<double>& surge_threshold,
    const std::optional<int>& eta_threshold) {
  const auto context =
      PrepareContext(std::vector<std::string>{scenario_name}, supported_classes,
                     surge_threshold, eta_threshold);
  const auto top_level_context = test::full::MakeTopLevelContext(context);
  const auto local_context =
      top_level_context->Get<SummaryScenariosPluginContext>();
  return OverrideSelectorExperimentWrapper(local_context);
}

}  // namespace routestats::full::brandings
