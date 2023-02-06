#include <chrono>
#include <unordered_set>

#include <userver/utest/utest.hpp>

#include <core/backoff.hpp>

namespace core = billing_wallet::core;

namespace {
constexpr auto kMinDelay = std::chrono::milliseconds(1000);
constexpr auto kMaxDelay = std::chrono::milliseconds(10000);
}  // namespace

TEST(BackoffTest, ValueIsInCorrectRange) {
  for (int count = 0; count < 10; ++count) {
    auto delay = core::CalcBackoff(count, kMinDelay, kMaxDelay);
    if (count == 0) {
      EXPECT_LE(delay, kMinDelay);
    }
    EXPECT_LE(delay, kMaxDelay);
  }
}

TEST(BackoffTest, ValueChangesBetweenCalls) {
  std::unordered_set<std::chrono::milliseconds::rep> results;
  constexpr int kNumCalls = 100;
  for (int call_number = 0; call_number < kNumCalls; ++call_number) {
    results.insert(core::CalcBackoff(0, kMinDelay, kMaxDelay).count());
  }
  EXPECT_GT(results.size(), 1);
}
