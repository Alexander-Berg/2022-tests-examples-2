#include <gtest/gtest.h>

#include <atomic>

#include <userver/engine/run_in_coro.hpp>

#include <utils/n_priority_rps_limiter.hpp>

TEST(NPriorityRpsLimiter, Add) {
  RunInCoro(
      []() {
        const size_t kNPriorities = 3;
        utils::NPriorityRpsLimiter pool(
            "test_limiter", kNPriorities,
            utils::NPriorityRpsLimiter::Settings{{1000}, {100}});

        std::atomic<int> cnt = 0;

        auto future1 = pool.Add(
            [&cnt]() {
              ++cnt;
              return true;
            },
            0);

        auto future2 = pool.Add(
            [&cnt]() {
              ++cnt;
              return true;
            },
            1);

        ASSERT_EQ(future1.wait(), engine::FutureStatus::kReady);
        ASSERT_EQ(future2.wait(), engine::FutureStatus::kReady);

        ASSERT_EQ(2, cnt);
      },
      4);
}

TEST(NPriorityRpsLimiter, RpsLimit) {
  RunInCoro(
      [] {
        const size_t kNPriorities = 3;
        const double kPriority0Rps = 100;
        const double kPriority1Rps = 10;
        const double kPriority2Rps = 5;
        const double kPeriod0 = 1.0 / kPriority0Rps;
        const double kPeriod1 = 1.0 / kPriority1Rps;
        const double kPeriod2 = 1.0 / kPriority2Rps;

        utils::NPriorityRpsLimiter pool(
            "test_limiter", kNPriorities,
            utils::NPriorityRpsLimiter::Settings{
                {kPriority0Rps, kPriority1Rps, kPriority2Rps}, {100}});

        std::vector<engine::Future<void>> futures;

        const auto start = std::chrono::steady_clock::now();

        //           request                    wait time after request
        futures.push_back(pool.Add([]() {}, 0));  // kPeriod 0
        futures.push_back(pool.Add([]() {}, 0));  // kPeriod 0
        futures.push_back(pool.Add([]() {}, 0));  // kPeriod 0
        futures.push_back(pool.Add([]() {}, 1));  // kPeriod 1
        futures.push_back(pool.Add([]() {}, 1));  // kPeriod 1
        futures.push_back(pool.Add([]() {}, 1));  // kPeriod 1
        futures.push_back(pool.Add([]() {}, 2));  // kPeriod 2
        futures.push_back(pool.Add([]() {}, 2));  // kPeriod 2
        futures.push_back(pool.Add([]() {}, 2));  // doesn't matter

        for (auto& f : futures) {
          ASSERT_EQ(f.wait(), engine::FutureStatus::kReady);
        }

        const auto time_spent = std::chrono::steady_clock::now() - start;
        const auto expected_time_spent = std::chrono::duration<double>(
            3 * kPeriod0 + 3 * kPeriod1 + 3 * kPeriod2);
        ASSERT_GT(time_spent.count(), expected_time_spent.count());
      },
      4);
}

TEST(NPriorityRpsLimiter, RpsSettings) {
  RunInCoro([]() {
    const size_t kNPriorities = 3;
    utils::NPriorityRpsLimiter pool("test_limiter", kNPriorities,
                                    utils::NPriorityRpsLimiter::Settings{});

    pool.ApplySettings(
        utils::NPriorityRpsLimiter::Settings{{10, 5, 1}, {100, 50, 10}});
    EXPECT_EQ((std::vector<double>{10, 5, 1}),
              pool.GetSettings().max_rps_by_priority);
    EXPECT_EQ((std::vector<size_t>{100, 50, 10}),
              pool.GetSettings().max_length_per_priority);

    pool.ApplySettings(
        utils::NPriorityRpsLimiter::Settings{{10, 5}, {100, 50}});
    EXPECT_EQ((std::vector<double>{10, 5, 5}),
              pool.GetSettings().max_rps_by_priority);
    EXPECT_EQ((std::vector<size_t>{100, 50, 50}),
              pool.GetSettings().max_length_per_priority);

    pool.ApplySettings(
        utils::NPriorityRpsLimiter::Settings{{10, 5, 4, 3, 2, 1}, {}});
    EXPECT_EQ((std::vector<double>{10, 5, 4}),
              pool.GetSettings().max_rps_by_priority);
    EXPECT_EQ((std::vector<size_t>{-1UL, -1UL, -1UL}),
              pool.GetSettings().max_length_per_priority);

    EXPECT_THROW(
        pool.ApplySettings(utils::NPriorityRpsLimiter::Settings{{}, {100}}),
        utils::BadRpsValue);

    EXPECT_THROW(
        pool.ApplySettings(utils::NPriorityRpsLimiter::Settings{{0}, {100}}),
        utils::BadRpsValue);
  });
}
