#include "common/gps_storage/gps_archive_stats.hpp"

#include <gtest/gtest.h>

#include <utils/helpers/json.hpp>

TEST(gps_archive_stats, ReturnJson) {
  gps_storage::GpsArchiveStats stats(nullptr);
  stats.AddStat("stat1", 42);
  stats.AddStat("stat1", 42);
  stats.AddStat("stat2", 42);
  stats.AddStat("stat_ave", 47, gps_storage::GpsArchiveStats::Action::kAve);
  stats.AddStat("stat_ave", 37, gps_storage::GpsArchiveStats::Action::kAve);
  const auto result = stats.GetStatsJson();

  Json::Value js = utils::helpers::ParseJson(result);
  ASSERT_EQ(js["stat1"], 84);
  ASSERT_EQ(js["stat2"], 42);
  ASSERT_EQ(js["stat_ave"], 42);
  ASSERT_EQ(js.size(), 3u);
}
