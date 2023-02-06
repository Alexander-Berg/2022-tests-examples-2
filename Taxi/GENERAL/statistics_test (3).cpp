#include <cargo-distlock-worker/statistics.hpp>

#include <gtest/gtest.h>

TEST(CargoDistlockWorker, IsAtomicSteadyClock) {
  // expected to be lock free, use uservice's non-blocking
  // synchronization primitives instead
  std::atomic<std::chrono::steady_clock::time_point> atomic;
  EXPECT_TRUE(atomic.is_lock_free());
}
