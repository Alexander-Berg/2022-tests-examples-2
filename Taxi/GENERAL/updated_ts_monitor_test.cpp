#include "updated_ts_monitor.hpp"

#include <gtest/gtest.h>

TEST(ApiOverDataMetrics, IsAtomicInt64) {
  // expected to be lock free, use uservice's non-blocking
  // synchronization primitives instead
  std::atomic<int64_t> atomic;
  EXPECT_TRUE(atomic.is_lock_free());
}
