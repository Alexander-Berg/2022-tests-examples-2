#include <metrix/component.hpp>

#include <taxi_config/taxi_config.hpp>
#include <userver/components/component.hpp>
#include <userver/components/component_config.hpp>
#include <userver/testsuite/testsuite_support.hpp>
#include <userver/utils/statistics/percentile_format_json.hpp>

namespace metrix {

Component::Component(const ::components::ComponentConfig& config,
                     const ::components::ComponentContext& context)
    : ::components::LoggableComponentBase(config, context),
      writer_(context.FindComponent<::components::DynamicConfig>().GetSource()),
      invalidator_holder_(
          context.FindComponent<::components::TestsuiteSupport>()
              .GetComponentControl(), *this, &Component::Invalidate)
{
  auto& statistics_storage =
      context.FindComponent<::components::StatisticsStorage>().GetStorage();
  statistics_holder_ = statistics_storage.RegisterExtender(
      "test_service_metrics",
      [this](const ::utils::statistics::StatisticsRequest&) {
        return CollectMetrics();
      });
}

Writer& Component::GetWriter() { return writer_; }

Component::~Component() { statistics_holder_.Unregister(); }

formats::json::Value Component::CollectMetrics() {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);

  writer_.empty_labels_milli_lap_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) =
        stats_for_period.GetCurrent().average;
  });

  writer_.empty_labels_percentile_lap_container_.ForEach(
      [&builder](const auto& kv) {
        const auto& stats_for_period = kv.second.GetStatsForPeriod();

        labels::ValueBuilderAt(builder, kv.first) =
            ::utils::statistics::PercentileToJson(
                stats_for_period,
                {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100});
      });

  writer_.labels0_avg_counter_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) =
        stats_for_period.GetCurrent().average;
  });

  writer_.labels0_counter_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) = stats_for_period;
  });

  writer_.labels0_milli_lap_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) =
        stats_for_period.GetCurrent().average;
  });

  writer_.labels0_percentile_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) =
        ::utils::statistics::PercentileToJson(
            stats_for_period,
            {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100});
  });

  writer_.labels1_time_counter_container_.ForEach([&builder](const auto& kv) {
    const auto& stats_for_period = kv.second.GetStatsForPeriod();

    labels::ValueBuilderAt(builder, kv.first) = stats_for_period;
  });

  writer_.labels1_time_percentile_container_.ForEach(
      [&builder](const auto& kv) {
        const auto& stats_for_period = kv.second.GetStatsForPeriod();

        labels::ValueBuilderAt(builder, kv.first) =
            ::utils::statistics::PercentileToJson(
                stats_for_period,
                {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 99, 100});
      });

  return builder.ExtractValue();
}

void Component::Invalidate() { writer_.Invalidate(); }

}  // namespace metrix
