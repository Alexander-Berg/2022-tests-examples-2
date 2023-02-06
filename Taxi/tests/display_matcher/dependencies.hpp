#pragma once

#include <userver/formats/json/value_builder.hpp>

#include <display_matcher/display_matcher.hpp>
#include <userver/utils/statistics/metrics_storage.hpp>

namespace eats_orders_tracking::tests::display_matcher {

namespace dm = eats_orders_tracking::display_matcher;

using KwargsBuilder =
    experiments3::kwargs_builders::EatsOrdersTrackingDisplayMatcher;
using experiments3::EatsOrdersTrackingDmCarCourierExperiment;
using experiments3::EatsOrdersTrackingDmLayerAb;
using experiments3::EatsOrdersTrackingDmRoverCourierExperiment;

class DependenciesForTest : public dm::Dependencies {
 public:
  virtual std::chrono::minutes GetConfigVeryLateAfter() const override;
  virtual std::chrono::minutes GetConfigMcdonaldsPickupDisposalTtlMinutes()
      const override;

  virtual std::optional<EatsOrdersTrackingDmLayerAb::Value> GetExp3LayerAb(
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<ExperimentResult> GetExp3ConfigByName(
      const std::string& config_name,
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
  GetExp3Rover(const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
  GetExp3Car(const KwargsBuilder& kwargs_builder) const override;

  virtual ::utils::statistics::MetricsStoragePtr GetMetrics() const override;
};

class DependenciesForTestNotNull : public DependenciesForTest {
 public:
  virtual std::optional<EatsOrdersTrackingDmLayerAb::Value> GetExp3LayerAb(
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<ExperimentResult> GetExp3ConfigByName(
      const std::string& config_name,
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
  GetExp3Rover(const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
  GetExp3Car(const KwargsBuilder& kwargs_builder) const override;

  virtual ::utils::statistics::MetricsStoragePtr GetMetrics() const override;
};

class DependenciesForTestFallback : public dm::Dependencies {
 public:
  virtual std::chrono::minutes GetConfigVeryLateAfter() const override;
  virtual std::chrono::minutes GetConfigMcdonaldsPickupDisposalTtlMinutes()
      const override;

  virtual std::optional<EatsOrdersTrackingDmLayerAb::Value> GetExp3LayerAb(
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<ExperimentResult> GetExp3ConfigByName(
      const std::string& config_name,
      const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmRoverCourierExperiment::Value>
  GetExp3Rover(const KwargsBuilder& kwargs_builder) const override;
  virtual std::optional<EatsOrdersTrackingDmCarCourierExperiment::Value>
  GetExp3Car(const KwargsBuilder& kwargs_builder) const override;

  virtual ::utils::statistics::MetricsStoragePtr GetMetrics() const override;
};

}  // namespace eats_orders_tracking::tests::display_matcher
