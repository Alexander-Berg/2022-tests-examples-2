#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <statistics-rps-limiter/utils.hpp>

using namespace statistics_rps_limiter::quota_based_limiter;

namespace {
RuntimeConfig MakeRuntimeConfig() {
  RuntimeConfig config;
  config.counter_intervals = kDefaultCounterIntervals;
  config.fallback_quota_min_events = 30;
  config.fallback_quota_multiplier = 1.5;
  config.fallback_quota_supplement = 5;
  config.concurrent_refresh_attempts = 3;
  config.minimal_quota = 10;
  config.reject_time = std::chrono::milliseconds(850);
  config.fallback_reject_time = std::chrono::milliseconds(1000);
  config.wait_request_duration = std::chrono::milliseconds(200);
  return config;
}
}  // namespace

UTEST(LimiterUtils, FallbackQuotaCalculationIfServerIsDown) {
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  auto config = MakeRuntimeConfig();

  EventQueue queue(std::chrono::seconds(100));
  // fill queue with enough events for fallback quota calculation
  for (auto i = 0; i < 100; i++) {
    utils::datetime::MockSleep(std::chrono::seconds(1));
    queue.Append(20);
  }

  for (auto i = 0; i < 1000; i++) {
    auto quota = CalculateFallbackQuota(queue, false, config, "test-resource");
    EXPECT_EQ(quota.avg, 20);
    EXPECT_EQ(quota.quota, quota.avg * config.fallback_quota_multiplier +
                               config.fallback_quota_supplement);
    utils::datetime::MockSleep(std::chrono::seconds(1));
    queue.Append(quota.avg);
  }

  // now add quota with slightly bigger interval than 1 second. It will make
  // some buckets to contain 0, which would affect avg calculation
  for (auto i = 0; i < 1000; i++) {
    auto quota = CalculateFallbackQuota(queue, false, config, "test-resource");
    EXPECT_EQ(quota.avg, 20);
    EXPECT_EQ(quota.quota, quota.avg * config.fallback_quota_multiplier +
                               config.fallback_quota_supplement);
    utils::datetime::MockSleep(std::chrono::milliseconds(1050));
    queue.Append(quota.avg);
  }
}
