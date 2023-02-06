#include "master_epoch_confirmed.hpp"
#include <gtest/gtest.h>
#include <statistics/instant_statistics.hpp>

TEST(master_epoch_confirmed, base) {
  using Stats = driver_route_watcher::statistics::InstantStatistics;
  Stats stats;

  driver_route_watcher::internal::MasterEpochConfirmed counter(
      [&stats]() -> Stats& { return stats; });

  // Initial state
  ASSERT_EQ(std::nullopt, counter.IsMaster());
  ASSERT_EQ(std::nullopt, counter.IsLockAcquired());

  // Not acquired lock
  counter.SetLockAcquired(false);
  ASSERT_EQ(std::nullopt, counter.IsMaster());
  ASSERT_EQ(std::nullopt, counter.IsLockAcquired());

  // Acquire lock
  counter.SetLockAcquired(true);
  ASSERT_EQ(1ul, counter.IsLockAcquired());
  ASSERT_EQ(std::nullopt,
            counter.IsMaster());  // Not master yet (not confirmed)
  ASSERT_TRUE(stats.is_master);
  ASSERT_FALSE(stats.is_master_confirmed);

  // Invalid confirm
  ASSERT_FALSE(counter.Confirm(42));  // fail to confirm
  ASSERT_EQ(1ul, counter.IsLockAcquired());
  ASSERT_EQ(std::nullopt,
            counter.IsMaster());  // Not master yet (not confirmed)
  ASSERT_TRUE(stats.is_master);
  ASSERT_FALSE(stats.is_master_confirmed);

  // Valid confirm
  ASSERT_TRUE(counter.Confirm(1));
  ASSERT_EQ(1ul, counter.IsLockAcquired());
  ASSERT_EQ(1ul, counter.IsMaster());  // Confirmed now
  ASSERT_TRUE(stats.is_master);
  ASSERT_TRUE(stats.is_master_confirmed);

  // Another succesfull lock without preceding loss (nothing must changed)
  counter.SetLockAcquired(true);
  ASSERT_EQ(1ul, counter.IsLockAcquired());
  ASSERT_EQ(1ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);
  ASSERT_TRUE(stats.is_master_confirmed);

  // Losing lock
  counter.SetLockAcquired(false);
  ASSERT_EQ(std::nullopt, counter.IsMaster());
  ASSERT_EQ(std::nullopt, counter.IsLockAcquired());
  ASSERT_FALSE(stats.is_master);
  ASSERT_FALSE(stats.is_master_confirmed);

  // Regain lock again
  counter.SetLockAcquired(true);
  ASSERT_EQ(2ul, counter.IsLockAcquired());
  ASSERT_EQ(std::nullopt,
            counter.IsMaster());  // Not master yet (not confirmed)
  ASSERT_TRUE(stats.is_master);
  ASSERT_FALSE(stats.is_master_confirmed);

  // Invalid confirm
  ASSERT_EQ(2ul, counter.IsLockAcquired());
  ASSERT_FALSE(counter.Confirm(1));  // fail to confirm
  ASSERT_EQ(std::nullopt,
            counter.IsMaster());  // Not master yet (not confirmed)
  ASSERT_TRUE(stats.is_master);
  ASSERT_FALSE(stats.is_master_confirmed);

  // Valid confirm
  ASSERT_EQ(2ul, counter.IsLockAcquired());
  ASSERT_TRUE(counter.Confirm(2));
  ASSERT_EQ(2ul, counter.IsMaster());  // Confirmed now
  ASSERT_TRUE(stats.is_master);
  ASSERT_TRUE(stats.is_master_confirmed);

  // Still holding lock (nothing changed)
  counter.SetLockAcquired(true);
  ASSERT_EQ(2ul, counter.IsLockAcquired());
  ASSERT_EQ(2ul, counter.IsMaster());
  ASSERT_TRUE(stats.is_master);
  ASSERT_TRUE(stats.is_master_confirmed);
}
