#include <atomic>
#include <chrono>

#include <gtest/gtest.h>

TEST(ShardedDistlock, IsAtomicDuration) {
  std::atomic<std::chrono::milliseconds> atomic{};
  ASSERT_TRUE(atomic.is_lock_free());
}
