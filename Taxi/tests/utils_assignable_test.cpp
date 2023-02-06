#include <gtest/gtest.h>

#include <userver/engine/run_in_coro.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <utils/assignable.hpp>

TEST(Assignable, Assign) {
  RunInCoro(
      []() {
        utils::Assignable<int> v{"v"};
        v.Assign(5);
        EXPECT_TRUE(v.IsAssigned());
        EXPECT_EQ(5, v.Get());
        EXPECT_EQ(5, v.GetNonconcurrent());
      },
      4);
}

TEST(Assignable, WakeupAfterAssign) {
  RunInCoro(
      []() {
        utils::Assignable<int> v{"v"};

        auto task = utils::Async("subtask", [&v]() {
          engine::SleepFor(std::chrono::milliseconds(100));
          v.Assign(1);
        });

        v.Get();
        ASSERT_EQ(1, v.Get());
      },
      4);
}

TEST(Assignable, AssignAsync) {
  RunInCoro(
      []() {
        utils::Assignable<int> v{"v"};
        v.AssignAsync([]() {
          engine::SleepFor(std::chrono::milliseconds(10));
          return 5;
        });
        ASSERT_EQ(5, v.Get());
      },
      4);
}

TEST(Assignable, Reject) {
  RunInCoro(
      []() {
        utils::Assignable<int> v{"v"};
        v.Reject("because I want to");

        ASSERT_FALSE(v.IsAssigned());

        EXPECT_THROW(v.Get(), utils::RejectedError);
        EXPECT_EQ(v.GetNonconcurrent(), std::nullopt);
      },
      4);
}

class MyExc : public std::runtime_error {
  using std::runtime_error::runtime_error;
};

TEST(Assignable, AsyncAssignFailed) {
  RunInCoro(
      []() {
        utils::Assignable<int> v{"v"};
        v.AssignAsync([]() -> int { throw MyExc{"drasti"}; });

        EXPECT_THROW(v.Get(), MyExc);
        EXPECT_THROW(v.Get(), MyExc);
        EXPECT_THROW(v.Get(), MyExc);
        EXPECT_EQ(v.GetNonconcurrent(), std::nullopt);
      },
      4);
}
