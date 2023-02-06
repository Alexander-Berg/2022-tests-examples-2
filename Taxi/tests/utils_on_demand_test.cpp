#include <gtest/gtest.h>

#include <userver/engine/future.hpp>
#include <userver/engine/run_in_coro.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <utils/on_demand.hpp>

TEST(OnDemand, SetSync) {
  RunInCoro(
      []() {
        utils::OnDemand<int> v("v", 10);
        EXPECT_EQ(10, v.Get());
        EXPECT_EQ(10, v.Get());
      },
      4);
}

struct GetFunc {
  static size_t cnt;

  static void reset() { cnt = 0; }

  int operator()() {
    ++cnt;
    return 5;
  }
};

size_t GetFunc::cnt = 0;

TEST(OnDemand, SetOnGet) {
  RunInCoro(
      []() {
        GetFunc getter;
        GetFunc::reset();

        utils::OnDemand<int> v("v", getter);

        EXPECT_EQ(5, v.Get());
        EXPECT_EQ(5, v.Get());
        EXPECT_EQ(5, v.Get());

        EXPECT_EQ(1, GetFunc::cnt);
      },
      4);
}

TEST(OnDemand, Request) {
  RunInCoro(
      []() {
        engine::Promise<bool> promise;
        auto future = promise.get_future();

        utils::OnDemand<int> v("v", [&promise]() {
          promise.set_value(true);
          return 5;
        });

        v.Request();

        ASSERT_EQ(engine::FutureStatus::kReady,
                  future.wait_for(std::chrono::milliseconds(100)));
        EXPECT_TRUE(future.get());

        EXPECT_EQ(5, v.Get());
      },
      4);
}

TEST(OnDemand, Exception) {
  RunInCoro(
      []() {
        utils::OnDemand<int> v(
            "v", []() -> int { throw std::runtime_error("exception"); });

        ASSERT_THROW(v.Get(), std::runtime_error);
        ASSERT_THROW(v.Get(), std::runtime_error);
      },
      4);
}
