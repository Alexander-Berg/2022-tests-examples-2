#include <gtest/gtest.h>

#include <clients/graphite.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <handlers/context.hpp>
#include "common.hpp"

static clients::Graphite graphite;
static LogExtra log_extra;

TEST(PrepareTimes, ErrorsCase) {
  config::Config cfg(config::DocsMapForTest());
  handlers::Context ctx{cfg, graphite, log_extra};
  EXPECT_THROW(geohistory::utils::PrepareTimes(0, 0, 0, ctx), BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(1319500800, 0, 0, ctx),
               BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(0, 1319500800, 0, ctx),
               BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(1, 5, 0, ctx), BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(-1, 0, 0, ctx), BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(-1, -1, 0, ctx), BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(0, 0, -10, ctx), BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(1319500805, 1319500800, 0, ctx),
               BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(1319500798, 1319500799, 0, ctx),
               BadRequest);
  EXPECT_THROW(
      geohistory::utils::PrepareTimes(1319500800, 1319500805, 100, ctx),
      BadRequest);
  EXPECT_THROW(geohistory::utils::PrepareTimes(
                   1319500800, 1319500800 + 100 * 60 * 60 + 1, 0, ctx),
               BadRequest);
}

TEST(PrepareTimes, NormalCase) {
  config::Config cfg(config::DocsMapForTest());
  handlers::Context ctx{cfg, graphite, log_extra};
  geohistory::utils::TimePoint to, from;

  std::tie(from, to) =
      geohistory::utils::PrepareTimes(1319500800, 1319500805, 0, ctx);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(from), 1319500800);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(to), 1319500805);

  std::tie(from, to) =
      geohistory::utils::PrepareTimes(1319500700, 1319500805, 0, ctx);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(from), 1319500800);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(to), 1319500805);

  std::tie(from, to) = geohistory::utils::PrepareTimes(1, 1319500805, 0, ctx);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(from), 1319500800);
  EXPECT_EQ(std::chrono::system_clock::to_time_t(to), 1319500805);

  const auto now =
      std::chrono::system_clock::to_time_t(utils::datetime::Now()) + 1;
  const long kAbsError = 2;
  std::tie(from, to) =
      geohistory::utils::PrepareTimes(now - 100, now + 100, 0, ctx);
  EXPECT_NEAR(std::chrono::system_clock::to_time_t(from), now - 100, kAbsError);
  EXPECT_NEAR(std::chrono::system_clock::to_time_t(to), now, kAbsError);
}

TEST(GetBucketsListForDateRange, DayRange) {
  geohistory::utils::TimePoint to, from;
  // 2018-01-10T10:24:00+00:00
  from = std::chrono::system_clock::from_time_t(1515579840);
  // 2018-10-05T12:49:00+00:00
  to = std::chrono::system_clock::from_time_t(1538743740);
  auto res = geohistory::utils::GetBucketsListForDateRange(from, to);
  ASSERT_EQ(res.size(), static_cast<size_t>(269));
  EXPECT_EQ(res[0].start_hour, 10);
  EXPECT_EQ(res[0].end_hour, 23);
  EXPECT_EQ(res[268].start_hour, 0);
  EXPECT_EQ(res[268].end_hour, 12);
  EXPECT_EQ(res[100].start_hour, 0);
  EXPECT_EQ(res[100].end_hour, 23);
}

TEST(GetBucketsListForDateRange, OneDay) {
  geohistory::utils::TimePoint to, from;
  // 2018-01-10T10:24:00+00:00
  from = std::chrono::system_clock::from_time_t(1515579840);
  // 2018-01-10T13:39:00+00:00
  to = std::chrono::system_clock::from_time_t(1515591540);
  auto res = geohistory::utils::GetBucketsListForDateRange(from, to);
  ASSERT_EQ(res.size(), static_cast<size_t>(1));
  EXPECT_EQ(res[0].start_hour, 10);
  EXPECT_EQ(res[0].end_hour, 13);
}
