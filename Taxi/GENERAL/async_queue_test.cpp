#include <utils/async_queue.hpp>

#include <gtest/gtest.h>

#include <array>
#include <atomic>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/mutex.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

UTEST(AsyncQueue, Sample) {
  std::atomic_int cnt{0};
  std::atomic_int max_cnt{0};

  utils::AsyncQueue<void> queue("test", 3);
  for (int i = 0; i < 128; ++i) {
    queue.Execute([&cnt, &max_cnt]() {
      auto val = ++cnt;
      max_cnt = std::max<int>(val, max_cnt);  // admissible race
      engine::SleepFor(std::chrono::microseconds(10));
      --cnt;
    });
    engine::Yield();
  }

  ASSERT_EQ(0, queue.WaitAll());
  ASSERT_TRUE(queue.IsEmpty());
  EXPECT_GE(3, max_cnt.load());
  EXPECT_LE(1, max_cnt.load());
}

UTEST(AsyncQueueThrowing, ThrowWaitAll) {
  utils::AsyncQueue<void, utils::AsyncQueueMode::kPassRoutineException> queue(
      "", 1);
  engine::Semaphore semaphore(1);
  {
    std::shared_lock<engine::Semaphore> lock(semaphore);
    EXPECT_NO_THROW(queue.Execute([&semaphore]() mutable {
      std::shared_lock<engine::Semaphore> lock(semaphore);
      throw std::runtime_error("");
    }));
  }
  EXPECT_THROW(queue.WaitAll(), std::runtime_error);
}

UTEST(AsyncQueuePassingRoutineExcept, WaitAllCallAfterThrow) {
  utils::AsyncQueue<void, utils::AsyncQueueMode::kPassRoutineException> queue(
      "", 1);
  engine::Semaphore semaphore(1);
  {
    std::shared_lock<engine::Semaphore> lock(semaphore);
    EXPECT_NO_THROW(queue.Execute([&semaphore]() mutable {
      std::shared_lock<engine::Semaphore> lock(semaphore);
      throw std::runtime_error("");
    }));
  }
  EXPECT_THROW(queue.WaitAll(), std::runtime_error);

  {
    std::shared_lock<engine::Semaphore> lock(semaphore);
    EXPECT_NO_THROW(queue.Execute([&semaphore]() mutable {
      std::shared_lock<engine::Semaphore> lock(semaphore);
      throw std::runtime_error("");
    }));
  }
  EXPECT_THROW(queue.WaitAll(), std::runtime_error);
  EXPECT_NO_THROW(queue.WaitAll());
}

UTEST(AsyncQueuePassingRoutineExcept, ThrowingPopFinished) {
  utils::AsyncQueue<void, utils::AsyncQueueMode::kPassRoutineException> queue(
      "", 1);
  engine::Mutex mutex;
  engine::ConditionVariable cv;
  bool finished = false;
  {
    std::lock_guard<engine::Mutex> lock(mutex);
    EXPECT_NO_THROW(queue.Execute([&mutex, &cv, &finished]() mutable {
      std::lock_guard<engine::Mutex> lock(mutex);
      finished = true;
      cv.NotifyOne();
      throw std::runtime_error("");
    }));
    engine::Yield();
    EXPECT_NO_THROW(queue.PopFinished());
  }
  std::unique_lock<engine::Mutex> lock(mutex);
  while (!cv.Wait(lock, [&finished] { return finished; }))
    ;
  EXPECT_THROW(queue.PopFinished(), std::runtime_error);
}

UTEST(AsyncQueuePassingRoutineExcept, SeveralThrowingPopFinished) {
  const unsigned kRoutinesCount = 10;
  utils::AsyncQueue<void, utils::AsyncQueueMode::kPassRoutineException> queue(
      "", kRoutinesCount);
  engine::Mutex mutex;
  engine::ConditionVariable cv;
  std::array<bool, kRoutinesCount> finished;
  finished.fill(false);
  {
    std::lock_guard<engine::Mutex> lock(mutex);
    for (unsigned i = 0; i < kRoutinesCount; ++i) {
      EXPECT_NO_THROW(queue.Execute([&mutex, &cv, &finished, i]() mutable {
        std::lock_guard<engine::Mutex> lock(mutex);
        finished[i] = true;
        cv.NotifyOne();
        throw std::runtime_error("");
      }));
      engine::Yield();
      EXPECT_NO_THROW(queue.PopFinished());
    }
  }
  for (unsigned i = 0; i < kRoutinesCount; ++i) {
    std::unique_lock<engine::Mutex> lock(mutex);
    while (!cv.Wait(lock, [&finished, i] { return finished[i]; }))
      ;
    EXPECT_THROW(queue.PopFinished(), std::runtime_error);
  }
}

UTEST(AsyncQueuePassingRoutineExcept, ExecuteThrowing) {
  const unsigned kRoutinesCount = 10;
  utils::AsyncQueue<void, utils::AsyncQueueMode::kPassRoutineException> queue(
      "", 1);
  engine::Mutex mutex;
  {
    std::lock_guard<engine::Mutex> lock(mutex);
    EXPECT_NO_THROW(queue.Execute([&mutex]() mutable {
      std::lock_guard<engine::Mutex> lock(mutex);
      throw std::runtime_error("");
    }));
  }
  for (unsigned i = 0; i < kRoutinesCount; ++i) {
    EXPECT_THROW(queue.Execute([&mutex]() mutable {
      std::lock_guard<engine::Mutex> lock(mutex);
      throw std::runtime_error("");
    }),
                 std::runtime_error);
  }
}
