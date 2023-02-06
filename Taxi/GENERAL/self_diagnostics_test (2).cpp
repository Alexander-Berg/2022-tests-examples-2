#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <taxi_config/variables/RATE_LIMITER_UPSTREAM_FALLBACK.hpp>

#include "self_diagnostics.hpp"

namespace {

constexpr std::string_view kFallbackConfig = R"({
  "enabled": true,
  "interval": 60,
  "threshold": 30,
  "critical_time": 60,
  "rate_share_samples": 60,
  "rate_share_margin": 5,
  "rate_share_margin_ralative": 10
})";

dynamic_config::StorageMock GetConfig() {
  return {{taxi_config::RATE_LIMITER_UPSTREAM_FALLBACK,
           formats::json::FromString(kFallbackConfig)}};
}

void MockTime(const int seconds) {
  utils::datetime::MockNowSet(
      std::chrono::system_clock::time_point{std::chrono::seconds{seconds}});
}

}  // namespace

TEST(SelfDiagnostics, Sample) {
  const auto& disabled_config = dynamic_config::GetDefaultSnapshot();
  const auto config = GetConfig();
  const auto enabled_config = config.GetSnapshot();
  rate_limiter::SelfDiagnostics diag;

  int time = 10000;
  MockTime(10000);

  EXPECT_FALSE(diag.CheckUpstreamFallback(disabled_config));
  EXPECT_FALSE(diag.CheckUpstreamFallback(enabled_config));

  models::Statistics stats;
  diag.Monitor(stats, enabled_config);
  time += 50;
  MockTime(time);
  stats.upstream_sync_success += 10;
  diag.Monitor(stats, enabled_config);

  // error percent > 80, but not enough samples
  EXPECT_FALSE(diag.CheckUpstreamFallback(disabled_config));
  EXPECT_FALSE(diag.CheckUpstreamFallback(enabled_config));

  time += 10;
  MockTime(time);
  stats.upstream_sync_success += 1;
  diag.Monitor(stats, enabled_config);

  // error percent > 80, should be enough samples
  EXPECT_FALSE(diag.CheckUpstreamFallback(disabled_config));
  EXPECT_TRUE(diag.CheckUpstreamFallback(enabled_config));

  // store stats with about 20% error rate
  time += 60;
  MockTime(time);
  stats.upstream_sync_success += 48;
  diag.Monitor(stats, enabled_config);

  EXPECT_FALSE(diag.CheckUpstreamFallback(disabled_config));
  EXPECT_FALSE(diag.CheckUpstreamFallback(enabled_config));

  // store stats with about 30% error rate
  time += 60;
  MockTime(time);
  stats.upstream_sync_success += 42;
  diag.Monitor(stats, enabled_config);

  EXPECT_FALSE(diag.CheckUpstreamFallback(disabled_config));
  EXPECT_TRUE(diag.CheckUpstreamFallback(enabled_config));

  time += 60;
  MockTime(time);
  EXPECT_FALSE(diag.CheckUpstreamFallback(enabled_config));
}
