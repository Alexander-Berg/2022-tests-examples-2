#pragma once

#include <endpoints/full/plugins/brandings/summary_scenarios/experiment_wrapper.hpp>

#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

class ModifierDetectorBase;

// If we want extend final_price and original_price, we need to create internal
// structure
inline void ExtendServiceLevel(
    core::ServiceLevel& service_level,
    const std::optional<core::Decimal>& final_price = std::nullopt) {
  service_level.final_price = final_price;
}

inline void ExtendServiceLevel(
    core::ServiceLevel& service_level,
    const std::optional<core::Discount>& discount = std::nullopt) {
  service_level.discount = discount;
}

inline void ExtendServiceLevel(
    core::ServiceLevel& service_level,
    const std::optional<core::EstimatedWaiting>& eta = std::nullopt) {
  service_level.eta = eta;
}

inline void ExtendServiceLevel(
    core::ServiceLevel& service_level,
    const std::optional<core::Coupon>& coupon = std::nullopt) {
  service_level.coupon = coupon;
}

inline void ExtendServiceLevel(
    core::ServiceLevel& service_level,
    const std::optional<core::Surge>& surge = std::nullopt) {
  service_level.surge = surge;
}

template <typename T>
using ClassesInfo = std::unordered_map<std::string, std::optional<T>>;

template <typename T>
std::vector<core::ServiceLevel> PrepareServiceLevels(
    const ClassesInfo<T>& infos) {
  std::vector<core::ServiceLevel> results;
  results.reserve(infos.size());
  for (const auto& [class_name, info] : infos) {
    auto service_level = test::MockDefaultServiceLevel(class_name);
    ExtendServiceLevel(service_level, info);
    results.push_back(std::move(service_level));
  }
  return results;
}

void RunDetector(ModifierDetectorBase& detector,
                 const std::vector<core::ServiceLevel>& service_levels);

full::ContextData PrepareContext(
    const std::vector<std::string>& scenarios,
    const std::vector<std::string>& supported_classes = {},
    const std::optional<double>& surge_threshold = std::nullopt,
    const std::optional<int>& eta_threshold = std::nullopt);

OverrideSelectorExperimentWrapper MakeExpWrapper(
    const std::string& scenario_name,
    const std::vector<std::string>& supported_classes = {},
    const std::optional<double>& surge_threshold = std::nullopt,
    const std::optional<int>& eta_threshold = std::nullopt);

}  // namespace routestats::full::brandings
