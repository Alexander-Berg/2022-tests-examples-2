#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include "recent_failures.hpp"

namespace {

const std::string failure_A{"failure_A"};
const std::string failure_B{"failure_B"};

class TestTimer {
 public:
  using duration = std::chrono::system_clock::duration;

  static std::chrono::system_clock::time_point now() {
    return std::chrono::system_clock::time_point(timer_);
  }

  static void sleep(duration duration) { timer_ += duration; }

  static void reset() { timer_ = duration{0}; }

 private:
  static duration timer_;
};

TestTimer::duration TestTimer::timer_{0};

using TestFailuresHolder = cargo_dispatch::workers::FailuresHolder<TestTimer>;
using TestRecentFailures = cargo_dispatch::workers::RecentFailures<TestTimer>;

}  // namespace

UTEST(FailuresHolder, BaseTest) {
  TestFailuresHolder holder;
  TestRecentFailures recent_failures(holder);

  recent_failures.AddFailure(failure_A);

  EXPECT_TRUE(recent_failures.IsRecentFailure(failure_A));
  EXPECT_FALSE(recent_failures.IsRecentFailure(failure_B));
}

UTEST(FailuresHolder, OutdatedFailure) {
  TestFailuresHolder holder;
  TestRecentFailures recent_failures(holder);

  recent_failures.AddFailure(failure_A);

  TestTimer::sleep(holder.GetThrottling());
  holder.RemoveOldFailures();

  EXPECT_FALSE(recent_failures.IsRecentFailure(failure_A));
}
