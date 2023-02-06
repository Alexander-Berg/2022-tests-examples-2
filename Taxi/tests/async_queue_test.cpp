#include <gtest/gtest.h>

#include <atomic>
#include <deque>
#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <vector>

#include <userver/engine/semaphore.hpp>
#include <userver/utils/async.hpp>

#include <utils/async_queue.hpp>

TEST(DeviceNotifyTasks, Throw) {
  class AsyncTaskException : public std::exception {
   public:
    using std::exception::exception;
  };

  RunInCoro(
      [] {
        EXPECT_THROW(
            utils::Async("throw_task", [] { throw AsyncTaskException(); })
                .Get(),
            AsyncTaskException);
      },
      2);
}

TEST(DeviceNotifyTasks, Semaphore) {
  RunInCoro(
      [] {
        const size_t expected = 1024, simultaneous = 4;
        std::atomic<size_t> counter(0);
        engine::Semaphore semaphore(simultaneous);
        std::vector<engine::TaskWithResult<void>> tasks;
        for (size_t i = 0; i < expected; ++i) {
          tasks.emplace_back(utils::Async("task_name", [&counter, &semaphore] {
            std::shared_lock<engine::Semaphore> lock(semaphore);
            ++counter;
          }));
        }
        for (auto& task : tasks) {
          task.Get();
        }
        EXPECT_EQ(counter.load(), expected);
      },
      2);
}

TEST(DeviceNotifyTasks, LockMove) {
  RunInCoro(
      [] {
        const size_t expected = 1024, simultaneous = 4;
        std::atomic<size_t> counter(0);
        engine::Semaphore semaphore(simultaneous);
        std::vector<engine::TaskWithResult<void>> tasks;
        for (size_t i = 0; i < expected; ++i) {
          std::shared_lock<engine::Semaphore> lock(semaphore);
          tasks.emplace_back(utils::Async(
              "task_name", [&counter, lock = std::move(lock)] { ++counter; }));
        }
        for (auto& task : tasks) {
          task.Get();
        }
        EXPECT_EQ(counter.load(), expected);
      },
      2);
}

TEST(DeviceNotifyTasks, Queue) {
  RunInCoro(
      [] {
        const size_t expected = 1024, simultaneous = 4;
        std::atomic<size_t> counter(0);
        utils::AsyncQueue<void> tasks("some_task", simultaneous);
        for (size_t i = 0; i < expected; ++i) {
          tasks.Execute([&counter] { ++counter; });
        }
        tasks.WaitAll();
        EXPECT_EQ(counter.load(), expected);
      },
      2);
}
