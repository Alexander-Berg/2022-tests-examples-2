#pragma once

#include <segmented_dict/segmented_dict.hpp>
#include <userver/concurrent/variable.hpp>
#include <userver/dynamic_config/source.hpp>
#include <userver/utils/scope_guard.hpp>
#include <userver/utils/statistics/min_max_avg.hpp>
#include <userver/utils/statistics/percentile.hpp>
#include <userver/utils/statistics/recentperiod.hpp>
#include <userver/utils/statistics/relaxed_counter.hpp>

#include <metrix/labels.hpp>
#include <metrix/types.hpp>

namespace metrix {

class Writer {
 public:
  Writer(const dynamic_config::Source& taxi_cfg)
      : taxi_cfg_(taxi_cfg)
  {}
  Writer() = delete;

  void PushMetric0(
      std::uint64_t value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric1(
      std::chrono::microseconds value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& dispatch_statuses = std::nullopt,
      const std::optional<std::string>& tariff_group = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric2(
      std::uint64_t value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric2(
      const types::PercentileType& value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric3(
      std::chrono::milliseconds value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& dispatch_statuses = std::nullopt,
      const std::optional<std::string>& tariff_group = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric3(
      const types::TimePercentileType& value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& dispatch_statuses = std::nullopt,
      const std::optional<std::string>& tariff_group = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  void PushMetric4(
      std::chrono::seconds value,
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  ::utils::ScopeGuard LapMetric5(
      const std::optional<std::string>& agglomeration = std::nullopt,
      const std::optional<std::string>& service = std::nullopt);

  ::utils::ScopeGuard LapMetric6();

  ::utils::ScopeGuard PercentileLapMetric7();

  void PushLabels0AvgCounter(std::chrono::seconds value, labels::Labels0 descr);

  void PushLabels0Counter(std::uint64_t value, labels::Labels0 descr);

  void PushLabels0Percentile(std::uint64_t value, labels::Labels0 descr);

  void PushLabels0Percentile(const types::PercentileType& value,
                             labels::Labels0 descr);

  void Invalidate();

  segmented_dict::SegmentedDict<labels::EmptyLabels, types::MilliLap>
      empty_labels_milli_lap_container_;
  segmented_dict::SegmentedDict<labels::EmptyLabels, types::PercentileLap>
      empty_labels_percentile_lap_container_;
  segmented_dict::SegmentedDict<labels::Labels0, types::AvgCounter>
      labels0_avg_counter_container_;
  segmented_dict::SegmentedDict<labels::Labels0, types::Counter>
      labels0_counter_container_;
  segmented_dict::SegmentedDict<labels::Labels0, types::MilliLap>
      labels0_milli_lap_container_;
  segmented_dict::SegmentedDict<labels::Labels0, types::Percentile>
      labels0_percentile_container_;
  segmented_dict::SegmentedDict<labels::Labels1, types::TimeCounter>
      labels1_time_counter_container_;
  segmented_dict::SegmentedDict<labels::Labels1, types::TimePercentile>
      labels1_time_percentile_container_;

 private:
  const dynamic_config::Source taxi_cfg_;
};

}  // namespace metrix
