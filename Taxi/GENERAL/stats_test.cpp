#include "stats.hpp"

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/cancel.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace yt_replica_reader::models {
namespace {
int GetTimingsCount(const TimingsStats& stats) {
  return stats.GetStatsForPeriod(TimingsStats::Duration::min(), true).Count();
}
}  // namespace

UTEST(TestStats, Success) {
  ClusterStats stats;
  { StatsScope scope(stats); }

  EXPECT_EQ(1, stats.total.load());
  EXPECT_EQ(1, stats.success.load());
  EXPECT_EQ(0, stats.error.load());
  EXPECT_EQ(0, stats.cancelled.load());
  EXPECT_EQ(1, GetTimingsCount(stats.total_timings));
  EXPECT_EQ(1, GetTimingsCount(stats.success_timings));
}

UTEST(TestStats, Error) {
  ClusterStats stats;
  try {
    StatsScope scope(stats);
    throw std::runtime_error{"error"};
  } catch (const std::exception&) {
  }

  EXPECT_EQ(1, stats.total.load());
  EXPECT_EQ(0, stats.success.load());
  EXPECT_EQ(1, stats.error.load());
  EXPECT_EQ(0, stats.cancelled.load());
  EXPECT_EQ(1, GetTimingsCount(stats.total_timings));
  EXPECT_EQ(0, GetTimingsCount(stats.success_timings));
}

UTEST(TestStats, Cancel) {
  ClusterStats stats;
  {
    auto task = ::utils::Async("test", [&stats] {
      StatsScope scope(stats);
      engine::InterruptibleSleepFor(std::chrono::seconds{10});
    });
    engine::Yield();
    task.RequestCancel();
  }

  EXPECT_EQ(1, stats.total.load());
  EXPECT_EQ(0, stats.success.load());
  EXPECT_EQ(0, stats.error.load());
  EXPECT_EQ(1, stats.cancelled.load());
  EXPECT_EQ(1, GetTimingsCount(stats.total_timings));
  EXPECT_EQ(0, GetTimingsCount(stats.success_timings));
}

}  // namespace yt_replica_reader::models
