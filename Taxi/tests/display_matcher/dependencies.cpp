#include "dependencies.hpp"

#include <userver/utils/assert.hpp>

namespace eats_orders_tracking::tests::display_matcher {

std::chrono::minutes DependenciesForTest::GetConfigVeryLateAfter() const {
  return std::chrono::minutes(1);
}

std::chrono::minutes
DependenciesForTest::GetConfigMcdonaldsPickupDisposalTtlMinutes() const {
  return std::chrono::minutes(1);
}

std::optional<EatsOrdersTrackingDmLayerAb::Value>
DependenciesForTest::GetExp3LayerAb(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

std::optional<dm::Dependencies::ExperimentResult>
DependenciesForTest::GetExp3ConfigByName(
    const std::string& /*config_name*/,
    const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
DependenciesForTest::GetExp3Rover(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
DependenciesForTest::GetExp3Car(const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

::utils::statistics::MetricsStoragePtr DependenciesForTest::GetMetrics() const {
  return nullptr;
}

std::optional<EatsOrdersTrackingDmLayerAb::Value>
DependenciesForTestNotNull::GetExp3LayerAb(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return {{"experiment_layer_order_type_name"}};
}

std::optional<dm::Dependencies::ExperimentResult>
DependenciesForTestNotNull::GetExp3ConfigByName(
    const std::string& config_name,
    const KwargsBuilder& /*kwargs_builder*/) const {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  if (config_name == "experiment_layer_order_type_name") {
    builder["experiment_layer_order_status_name"] =
        "experiment_layer_order_status_name";
  } else {
    UASSERT(config_name == "experiment_layer_order_status_name");

    const auto build_display_template = []() {
      formats::json::ValueBuilder builder_default(formats::json::Type::kObject);

      builder_default["show_car_info"] = true;
      builder_default["show_eta"] = true;
      builder_default["show_courier"] = true;
      builder_default["icons"] =
          formats::json::ValueBuilder(formats::json::Type::kArray);
      builder_default["buttons"] =
          formats::json::ValueBuilder(formats::json::Type::kArray);
      builder_default["title_key"] = "title_key";
      builder_default["short_title_key"] = "short_title_key";

      return builder_default;
    };

    builder["courier_rover"] = build_display_template();
    builder["courier_hard_of_hearing"] = build_display_template();
    builder["courier_on_car"] = build_display_template();
    builder["default"] = build_display_template();
  }

  dm::Dependencies::ExperimentResult result;
  result.value = builder.ExtractValue();

  return result;
}

std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
DependenciesForTestNotNull::GetExp3Rover(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return {{true}};
}

std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
DependenciesForTestNotNull::GetExp3Car(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return {{true}};
}

::utils::statistics::MetricsStoragePtr DependenciesForTestNotNull::GetMetrics()
    const {
  return nullptr;
}

std::chrono::minutes DependenciesForTestFallback::GetConfigVeryLateAfter()
    const {
  return std::chrono::minutes(1);
}

std::chrono::minutes
DependenciesForTestFallback::GetConfigMcdonaldsPickupDisposalTtlMinutes()
    const {
  return std::chrono::minutes(1);
}

std::optional<EatsOrdersTrackingDmLayerAb::Value>
DependenciesForTestFallback::GetExp3LayerAb(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

std::optional<dm::Dependencies::ExperimentResult>
DependenciesForTestFallback::GetExp3ConfigByName(
    const std::string& /*config_name*/,
    const KwargsBuilder& /*kwargs_builder*/) const {
  return std::nullopt;
}

std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
DependenciesForTestFallback::GetExp3Rover(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return {{true}};
}

std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
DependenciesForTestFallback::GetExp3Car(
    const KwargsBuilder& /*kwargs_builder*/) const {
  return {{true}};
}

::utils::statistics::MetricsStoragePtr DependenciesForTestFallback::GetMetrics()
    const {
  return nullptr;
}

}  // namespace eats_orders_tracking::tests::display_matcher
