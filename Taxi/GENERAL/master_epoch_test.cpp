#include "master_epoch.hpp"
#include <gtest/gtest.h>
#include <statistics/instant_statistics.hpp>

TEST(master_epoch, base) {
  using Stats = driver_route_watcher::statistics::InstantStatistics;
  Stats stats;

  driver_route_watcher::internal::MasterEpoch counter(
      [&stats]() -> Stats& { return stats; });

  ASSERT_EQ(std::nullopt, counter.IsMaster());

  counter.Update(false);
  ASSERT_EQ(std::nullopt, counter.IsMaster());

  counter.Update(true);
  ASSERT_EQ(1ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);

  counter.Update(true);
  ASSERT_EQ(1ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);

  counter.Update(false);
  ASSERT_EQ(std::nullopt, counter.IsMaster());
  ASSERT_FALSE(stats.is_master);

  counter.Update(true);
  ASSERT_EQ(2ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);

  counter.Update(true);
  ASSERT_EQ(2ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);
}
