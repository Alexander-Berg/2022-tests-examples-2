#include <mutex>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/sleep.hpp>

#include <userver/utest/utest.hpp>

#include <userver/utils/async.hpp>

#include <tasks-control/deposing_tasks_control.hpp>

namespace tasks_control {

TEST(DeposeTasksControlTest, OverloadByTasks) {
  RunInCoro(
      []() {
        // Tests checks that if we try to put more tasks than it is allowed,
        // then old tasks are cancelled

        engine::Mutex pause_control_mutex;
        int pause_control{1};
        engine::ConditionVariable pause_control_cv;

        auto blocking_fn = [&pause_control_mutex, &pause_control_cv,
                            &pause_control]() {
          // pause_control will never fire, instead we should be
          // waked up by cancellation
          std::unique_lock pause_lock{pause_control_mutex};
          pause_control = 0;             // Give control back to main thread
          pause_control_cv.NotifyAll();  // Notify main thread

          // Now wait while pause_control become 1 - and it never should
          EXPECT_FALSE(pause_control_cv.Wait(
              pause_lock, [&pause_control]() { return pause_control == 1; }));
        };

        DeposingTasksControl<> tasks_control;
        tasks_control.SetMaxTasksCount(1);

        // Place 3 tasks. 2 should be cancelled
        // Placing and cancelling is synchronious
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));
        EXPECT_EQ(0, tasks_control.GetStatistics().cancelled_tasks);
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));
        EXPECT_EQ(1, tasks_control.GetStatistics().cancelled_tasks);
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));

        EXPECT_EQ(2, tasks_control.GetStatistics().cancelled_tasks);

        tasks_control.Clear();
        EXPECT_EQ(3, tasks_control.GetStatistics().cancelled_tasks);
      },
      2);
}

TEST(DeposeTasksControlTest, Clear) {
  RunInCoro(
      []() {
        // Tests checks that if we try to put more tasks than it is allowed,
        // then old tasks are cancelled

        engine::Mutex pause_control_mutex;
        int pause_control{0};
        engine::ConditionVariable pause_control_cv;

        auto blocking_fn = [&pause_control_mutex, &pause_control_cv,
                            &pause_control]() {
          // pause_control will never fire, instead we should be
          // waked up by cancellation
          std::unique_lock<engine::Mutex> pause_lock{pause_control_mutex};
          EXPECT_FALSE(pause_control_cv.Wait(
              pause_lock, [&pause_control]() { return pause_control == 1; }));
        };

        DeposingTasksControl<> tasks_control;
        tasks_control.SetMaxTasksCount(100);

        // Place 3 tasks. 2 should be cancelled
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));
        tasks_control.PlaceTask(utils::Async("test", blocking_fn));

        // We don't really have to do that
        engine::InterruptibleSleepFor(std::chrono::milliseconds{1});

        tasks_control.Clear();
        EXPECT_EQ(3, tasks_control.GetStatistics().cancelled_tasks);
      },
      2);
}

}  // namespace tasks_control
