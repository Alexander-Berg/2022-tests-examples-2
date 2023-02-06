#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>
#include <userver/utils/mock_now.hpp>

#include <js/execution/internal/load_counter.hpp>

using js::execution::LoadCounter;

using namespace std::chrono_literals;

TEST(LoadCounterTest, Basic) {
  LoadCounter counter{/*thread_count=*/4, 100ms};

  auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);
  {
    auto scope = counter.MeasureScope(3);
    {
      auto scope = counter.MeasureScope(2);
      {
        auto scope0 = counter.MeasureScope(0);
        auto scope1 = counter.MeasureScope(1);

        // close 2 scopes after 50ms -> +100ms busy; total: 100ms busy
        utils::datetime::MockNowSet(now + 50ms);
      }

      // close scope after 101ms -> +101ms busy; total: 201ms busy
      // close window at 101ms (>100) with 1 scope opened at 0 -> +101ms busy
      // total: 302ms busy
      utils::datetime::MockNowSet(now + 101ms);
    }
    // close scope 49ms after window close (150ms - 101ms)
    // add 49ms of busy time to next window
    utils::datetime::MockNowSet(now + 150ms);
  }

  {
    auto load_factor = counter.GetLoadFactor(100);

    // 302ms total; 4 threads * 101ms resulting window; precision to 0.001
    auto expected_load_factor = round((302.f / 404) * 1000) / 1000;

    ASSERT_FLOAT_EQ(load_factor, expected_load_factor)
        << ToString(counter.ToJsonPercentiles());
  }

  // new window
  {
    // go back to the last window's end
    // to open scope "concurrently" with sliced scope 3
    utils::datetime::MockNowSet(now + 101ms);

    auto scope = counter.MeasureScope(0);
    // close scope after 101ms -> +101ms busy
    // close window at 101ms (>100)
    // total: 150ms busy (49ms + 101ms)
    utils::datetime::MockSleep(101ms);
  }

  {
    // new load factor is lower, so get by lower percentile
    auto load_factor = counter.GetLoadFactor(50);

    // 150ms total; 4 threads * 101ms resulting window; precision to 0.001
    auto expected_load_factor = round((150.f / 404) * 1000) / 1000;

    ASSERT_FLOAT_EQ(load_factor, expected_load_factor)
        << ToString(counter.ToJsonPercentiles());
  }
}

UTEST(LoadCounterTest, Concurrent) {
  LoadCounter counter{/*thread_count=*/4, 100ms};
  auto task1 = utils::Async("t1", [&counter] {
    auto scope = counter.MeasureScope(0);
    engine::SleepFor(50ms);
  });
  auto task2 = utils::Async("t2", [&counter] {
    auto scope = counter.MeasureScope(1);
    engine::SleepFor(50ms);
  });
  auto task3 = utils::Async("t3", [&counter] {
    auto scope = counter.MeasureScope(2);
    // provoke window closure
    engine::SleepFor(101ms);
  });
  auto task4 = utils::Async("t4", [&counter] {
    auto scope = counter.MeasureScope(3);
    // slice scope
    engine::SleepFor(150ms);
  });

  task1.Get();
  task2.Get();
  task3.Get();
  task4.Get();

  auto load_factor = counter.GetLoadFactor(100);

  ASSERT_GT(load_factor, 0.0) << ToString(counter.ToJsonPercentiles());
  ASSERT_LT(load_factor, 1.0) << ToString(counter.ToJsonPercentiles());
}
