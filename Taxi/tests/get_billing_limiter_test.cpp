
#include <functional>

#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>

#include <components/events_sender.hpp>
#include <models/metrics.hpp>
#include <userver/utils/mock_now.hpp>

namespace {
namespace limiters_cfg =
    taxi_config::subventions_activity_producer_billing_rate_limiters;

struct MetricsData {
  size_t billing_success_calls_count = 0;
  size_t billing_fail_calls_count = 0;
};

const auto kMetricsDataSet = ::testing::Values(
    MetricsData{1, 0}, MetricsData{0, 1}, MetricsData{10, 3},
    MetricsData{3, 10}, MetricsData{10, 5}, MetricsData{5, 10},
    MetricsData{100, 30}, MetricsData{30, 100}, MetricsData{100, 35},
    MetricsData{35, 100}, MetricsData{100, 50}, MetricsData{50, 100});

class DefaultTestCases : public ::testing::TestWithParam<MetricsData> {};

class FallbackTestCases
    : public ::testing::TestWithParam<std::tuple<
          MetricsData, std::optional<limiters_cfg::FallbackLimiter>>> {};

limiters_cfg::FallbackLimiter MakeFallback(int min_events_count,
                                           double error_threshold) {
  limiters_cfg::FallbackLimiter fallback;
  fallback.enabled = true;
  fallback.max_rps = 5;
  fallback.retries = 1;
  fallback.timeout_ms = std::chrono::milliseconds{1000};
  fallback.conditions.min_events_count = min_events_count;
  fallback.conditions.error_threshold = error_threshold;
  return fallback;
}

void SetMetrics(models::Metrics& metrics, const MetricsData& metrics_data) {
  const auto now = utils::datetime::Now();
  const std::chrono::seconds epoch{5};
  utils::datetime::MockNowSet(now + epoch);
  auto& current_billing_metrics = metrics.billing_metrics.GetCurrentCounter();
  current_billing_metrics.success_calls_count =
      metrics_data.billing_success_calls_count;
  current_billing_metrics.fail_calls_count =
      metrics_data.billing_fail_calls_count;
  utils::datetime::MockNowSet(now + 2 * epoch);
}

bool UseFallback(
    const MetricsData& metrics_data,
    const std::optional<limiters_cfg::FallbackLimiter>& fallback_limiter) {
  if (fallback_limiter && fallback_limiter->enabled &&
      metrics_data.billing_fail_calls_count != 0) {
    const auto billing_success = metrics_data.billing_success_calls_count;
    const auto billing_total =
        billing_success + metrics_data.billing_fail_calls_count;
    const auto& fallback_conditions = fallback_limiter->conditions;
    const double error_rate{
        static_cast<double>(metrics_data.billing_fail_calls_count) /
        billing_total};
    if (billing_total >
            static_cast<unsigned>(fallback_conditions.min_events_count) &&
        error_rate > fallback_conditions.error_threshold) {
      return true;
    }
  }
  return false;
}

using RateLimitConfig =
    ::taxi_config::subventions_activity_producer_billing_rate_limiters::
        SubventionsActivityProducerBillingRateLimiters;

void SetRateLimit(dynamic_config::StorageMock& config_storage,
                  dynamic_config::Snapshot& config,
                  std::function<void(RateLimitConfig&)> updater) {
  RateLimitConfig rl_config = config_storage.GetSource().GetCopy(
      taxi_config::SUBVENTIONS_ACTIVITY_PRODUCER_BILLING_RATE_LIMITERS);
  updater(rl_config);
  config_storage.Extend(
      {{taxi_config::SUBVENTIONS_ACTIVITY_PRODUCER_BILLING_RATE_LIMITERS,
        rl_config}});
  config = config_storage.GetSnapshot();
}

}  // namespace

TEST_P(DefaultTestCases, GetBillingLimitersTest) {
  const auto& metrics_data = GetParam();
  models::Metrics metrics;
  SetMetrics(metrics, metrics_data);

  auto config = dynamic_config::GetDefaultSnapshot();

  ASSERT_EQ(components::GetBillingLimits(config, metrics), std::nullopt)
      << "default config test";
}

INSTANTIATE_TEST_SUITE_P(DefaultBillingLimitersTest, DefaultTestCases,
                         kMetricsDataSet);

UTEST_P(FallbackTestCases, GetBillingLimitersTest) {
  const auto& metrics_data = std::get<0>(GetParam());
  const auto& fallback_limiter = std::get<1>(GetParam());
  models::Metrics metrics;
  SetMetrics(metrics, metrics_data);

  dynamic_config::StorageMock config_storage =
      dynamic_config::MakeDefaultStorage({});
  auto config = config_storage.GetSnapshot();
  SetRateLimit(config_storage, config, [&](RateLimitConfig& rl_config) {
    rl_config.fallback_limiter = fallback_limiter;
  });

  std::optional<models::BillingLimits> fallback_limits;
  if (UseFallback(metrics_data, fallback_limiter)) {
    fallback_limits.emplace(fallback_limiter->max_rps,
                            fallback_limiter->timeout_ms,
                            fallback_limiter->retries);
  }

  if (fallback_limits) {
    ASSERT_EQ(fallback_limits, components::GetBillingLimits(config, metrics))
        << "no default_limiter, used fallback test";
  } else {
    ASSERT_EQ(components::GetBillingLimits(config, metrics), std::nullopt)
        << "no default_limiter";
  }

  limiters_cfg::DefaultLimiter default_limiter;
  default_limiter.enabled = false;

  SetRateLimit(config_storage, config, [&](RateLimitConfig& rl_config) {
    rl_config.default_limiter = default_limiter;
  });

  if (fallback_limits) {
    ASSERT_EQ(fallback_limits, components::GetBillingLimits(config, metrics))
        << "disabled default_limiter, used fallback test";
  } else {
    ASSERT_EQ(components::GetBillingLimits(config, metrics), std::nullopt)
        << "disabled default_limiter";
  }

  default_limiter.enabled = true;
  default_limiter.max_rps = 10;
  default_limiter.timeout_ms = std::chrono::milliseconds{100};
  default_limiter.retries = 2;

  SetRateLimit(config_storage, config, [&](RateLimitConfig& rl_config) {
    rl_config.default_limiter = default_limiter;
  });

  if (fallback_limits) {
    ASSERT_EQ(fallback_limits, components::GetBillingLimits(config, metrics))
        << "enabled default_limiter, used fallback test";

  } else {
    const auto default_limits = std::make_optional<models::BillingLimits>(
        default_limiter.max_rps, default_limiter.timeout_ms,
        default_limiter.retries);
    ASSERT_EQ(default_limits, components::GetBillingLimits(config, metrics))
        << "enabled default_limiter";
  }
}

INSTANTIATE_UTEST_SUITE_P(
    FallbackBillingLimitersTest, FallbackTestCases,
    ::testing::Combine(
        kMetricsDataSet,
        ::testing::Values(std::nullopt, limiters_cfg::FallbackLimiter{},
                          MakeFallback(1, 0.0), MakeFallback(10, 0.0),
                          MakeFallback(100, 0.0), MakeFallback(1, 1.0),
                          MakeFallback(10, 1.0), MakeFallback(100, 1.0),
                          MakeFallback(1, 0.35), MakeFallback(10, 0.35),
                          MakeFallback(100, 0.35))));
