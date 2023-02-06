#include <gtest/gtest.h>
#include <atomic>
#include <chrono>
#include <functional>
#include <vector>

#include <userver/engine/task/task.hpp>
#include <userver/utest/utest.hpp>

#include <userver/engine/deadline.hpp>
#include <userver/engine/future.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <leaky-bucket-queue/queue.hpp>

namespace {

using Queue = leaky_bucket_queue::Queue;
using QueuePolicy = leaky_bucket_queue::QueuePolicy;

constexpr size_t kDefaultWorkerThreads = 4;

void RunInCoroMultithreaded(std::function<void()> payload) {
  RunInCoro(payload, kDefaultWorkerThreads);
}

UTEST(LeakyBucketQueue, Add) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 100;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
  const auto f1 = q.Add([]() {});
  ASSERT_EQ(f1.wait(), engine::FutureStatus::kReady);

  auto f2 = q.Add([]() { return true; });
  ASSERT_TRUE(f2.get());
}

UTEST(LeakyBucketQueue, AddDetailed) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 100;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
  const auto f1 = q.AddDetailed([]() {});
  ASSERT_EQ(f1.result.wait(), engine::FutureStatus::kReady);

  auto f2 = q.AddDetailed([]() { return true; });
  ASSERT_EQ(f2.result.wait(), engine::FutureStatus::kReady);

  policy.execution_rate = 0.1;
  q.SetPolicy(policy);
  for (size_t i = 0; i < 10; ++i) {
    q.Add([]() {});
  }
  const auto f = q.AddDetailed([]() {});
  ASSERT_GE(f.approx_scheduled_for, std::chrono::seconds(100));
  ASSERT_LE(f.approx_scheduled_for, std::chrono::seconds(110));
}

UTEST(LeakyBucketQueue, AddWithSpan) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 100;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
  const auto f1 = q.AddWithSpan([]() {});
  ASSERT_EQ(f1.wait(), engine::FutureStatus::kReady);

  auto f2 = q.AddWithSpan([]() { return true; });
  ASSERT_TRUE(f2.get());
}

UTEST(LeakyBucketQueue, AddDetailedWithSpan) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 100;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
  const auto f1 = q.AddDetailedWithSpan([]() {});
  ASSERT_EQ(f1.result.wait(), engine::FutureStatus::kReady);

  auto f2 = q.AddDetailedWithSpan([]() { return true; });
  ASSERT_EQ(f2.result.wait(), engine::FutureStatus::kReady);

  policy.execution_rate = 0.1;
  q.SetPolicy(policy);
  for (size_t i = 0; i < 10; ++i) {
    q.Add([]() {});
  }
  const auto f = q.AddDetailedWithSpan([]() {});
  ASSERT_GE(f.approx_scheduled_for, std::chrono::seconds(100));
  ASSERT_LE(f.approx_scheduled_for, std::chrono::seconds(110));
}

TEST(LeakyBucketQueue, AddMultithread) {
  RunInCoroMultithreaded([] {
    constexpr int kTasksPerCoro = 20;
    constexpr int kCoroCount = 3;
    constexpr std::chrono::microseconds kTaskTime{100};
    QueuePolicy policy;
    policy.execution_rate = 1000000 / kTaskTime.count();
    policy.max_queue_size = kTasksPerCoro * kCoroCount;
    Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
    std::vector<engine::Future<size_t>> futures[kCoroCount];

    const auto add_tasks = [&q](size_t task_number,
                                std::vector<engine::Future<size_t>>& futures) {
      futures.reserve(kTasksPerCoro);
      for (size_t i = 0; i < kTasksPerCoro; ++i) {
        auto f = q.Add([i, task_number]() { return i + task_number; });
        futures.emplace_back(std::move(f));
      }
    };

    const auto start = std::chrono::steady_clock::now();

    engine::Task coros[kCoroCount];
    for (size_t i = 0; i < kCoroCount; ++i) {
      coros[i] = utils::Async("coro1", add_tasks, kTasksPerCoro * i,
                              std::ref(futures[i]));
    }

    for (size_t i = 0; i < kCoroCount; ++i) {
      coros[i].Wait();
      ASSERT_EQ(futures[i].size(), kTasksPerCoro);
      for (size_t j = 0; j < kTasksPerCoro; ++j) {
        ASSERT_EQ(futures[i][j].get(), i * kTasksPerCoro + j);
      }
    }

    const auto time_spent = std::chrono::steady_clock::now() - start;
    ASSERT_GT(time_spent, (kTasksPerCoro - 1) * kCoroCount * kTaskTime);
  });
}

TEST(LeakyBucketQueue, AddAfterBeenBlocked) {
  RunInCoroMultithreaded([] {
    constexpr size_t kIterations = 4;
    constexpr std::chrono::milliseconds kBlockedTime{3};
    constexpr std::chrono::milliseconds kTaskTime{1};

    QueuePolicy policy;
    policy.execution_rate = 1000. / kTaskTime.count();
    policy.max_queue_size = 2;
    Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

    const auto start = std::chrono::steady_clock::now();

    for (size_t i = 0; i < kIterations; ++i) {
      auto f1 = q.Add([]() {});  // should be processed as fast as possible
      auto f2 = q.Add([]() {});  // should be processed after kTaskTime timeout
      ASSERT_EQ(f1.wait(), engine::FutureStatus::kReady);
      ASSERT_EQ(f2.wait(), engine::FutureStatus::kReady);

      const auto deadline = engine::Deadline::FromDuration(kBlockedTime);
      engine::InterruptibleSleepUntil(deadline);
    }

    const auto time_spent = std::chrono::steady_clock::now() - start;
    ASSERT_GT(time_spent, (kBlockedTime + kTaskTime) * kIterations);
  });
}

TEST(LeakyBucketQueue, Cancel) {
  RunInCoroMultithreaded([] {
    QueuePolicy policy;
    policy.execution_rate = 0.1;
    policy.max_queue_size = 1;
    Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
    engine::Promise<void> running_func_promise;
    auto running_func_result_future = q.Add([&running_func_promise]() {
      running_func_promise.set_value();
      while (true) {
        engine::current_task::CancellationPoint();
      }
    });

    std::atomic<bool> pending_func_executed{false};
    auto pending_func_result_future =
        q.Add([&pending_func_executed]() { pending_func_executed.store(true); },
              leaky_bucket_queue::OnQueueOverflow::kBlock);

    const auto running_func_future = running_func_promise.get_future();
    ASSERT_EQ(running_func_future.wait(), engine::FutureStatus::kReady);

    q.Cancel();

    bool running_func_future_cancelled = false;
    try {
      running_func_result_future.get();
    } catch (const std::future_error& e) {
      running_func_future_cancelled = true;
    }
    ASSERT_TRUE(running_func_future_cancelled);

    bool pending_func_future_cancelled = false;
    try {
      pending_func_result_future.get();
    } catch (const std::future_error& e) {
      pending_func_future_cancelled = true;
    }
    ASSERT_TRUE(pending_func_future_cancelled);
    ASSERT_FALSE(pending_func_executed.load());
  });
}

UTEST(LeakyBucketQueue, MaxQueueSizeException) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 0;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

  bool overflow_exception_thrown = false;
  try {
    const auto f = q.Add([]() {}, leaky_bucket_queue::OnQueueOverflow::kThrow);
  } catch (leaky_bucket_queue::QueueOverflowError) {
    overflow_exception_thrown = true;
  }
  ASSERT_TRUE(overflow_exception_thrown);
}

UTEST(LeakyBucketQueue, MaxQueueSizeInvalidFuture) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 0;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

  const auto f =
      q.Add([]() {}, leaky_bucket_queue::OnQueueOverflow::kReturnInvalidFuture);
  ASSERT_FALSE(f.valid());
}

UTEST(LeakyBucketQueue, MaxQueueSizeBlock) {
  QueuePolicy policy;
  policy.execution_rate = 10000;
  policy.max_queue_size = 0;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

  std::atomic<bool> started{false};
  const auto t = utils::Async("", [&q, &started]() {
    auto blocked_f = q.Add([&started]() { started.store(true); },
                           leaky_bucket_queue::OnQueueOverflow::kBlock);
    ASSERT_EQ(blocked_f.wait(), engine::FutureStatus::kReady);
  });

  engine::InterruptibleSleepFor(std::chrono::milliseconds(2));
  ASSERT_FALSE(started.load());

  policy.max_queue_size = 1;
  q.SetPolicy(policy);

  t.Wait();
}

UTEST(LeakyBucketQueue, MaxQueueSizeBlockWithDeadline) {
  QueuePolicy policy;
  policy.execution_rate = 10000;
  policy.max_queue_size = 0;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

  const engine::Deadline deadline =
      engine::Deadline::FromDuration(std::chrono::milliseconds(5));

  ASSERT_THROW(
      q.Add([]() {}, leaky_bucket_queue::OnQueueOverflow::kBlock, deadline),
      leaky_bucket_queue::QueueOverflowError);
}

UTEST(LeakyBucketQueue, BlockWithDeadlineTimeout) {
  QueuePolicy policy;
  policy.execution_rate = 1;
  policy.max_queue_size = 1;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());

  std::atomic<bool> pending_func_should_exit{false};
  const auto pending_func = [&pending_func_should_exit]() {
    while (!pending_func_should_exit) {
      engine::SleepFor(std::chrono::milliseconds(10));
    }
  };

  auto executing_func_result_future =
      q.Add(pending_func, leaky_bucket_queue::OnQueueOverflow::kBlock);

  auto pending_func_result_future =
      q.Add(pending_func, leaky_bucket_queue::OnQueueOverflow::kBlock);

  std::atomic<bool> blocked_func_executed{false};
  const engine::Deadline deadline =
      engine::Deadline::FromDuration(std::chrono::milliseconds(5));
  ASSERT_THROW(
      q.Add([&blocked_func_executed]() { blocked_func_executed.store(true); },
            leaky_bucket_queue::OnQueueOverflow::kBlock, deadline),
      leaky_bucket_queue::QueueOverflowError);

  pending_func_should_exit.store(true);
  ASSERT_EQ(executing_func_result_future.wait(), engine::FutureStatus::kReady);
  ASSERT_EQ(pending_func_result_future.wait(), engine::FutureStatus::kReady);
  ASSERT_FALSE(blocked_func_executed.load());
}

UTEST(LeakyBucketQueue, CheckErrorFlagRaised) {
  QueuePolicy policy;
  policy.execution_rate = 100;
  policy.max_queue_size = 100;
  Queue q("test_queue", policy, engine::current_task::GetTaskProcessor());
  auto f = q.Add([]() { throw std::runtime_error("test"); });

  bool exception_set = false;
  try {
    f.get();
  } catch (std::exception& e) {
    exception_set = true;
  }
  ASSERT_TRUE(exception_set);

  ASSERT_TRUE(q.GetErrorFlag());
  q.ClearErrorFlag();
  ASSERT_FALSE(q.GetErrorFlag());

  const auto f2 = q.Add([]() { throw std::runtime_error("test"); });
  ASSERT_EQ(f2.wait(), engine::FutureStatus::kReady);
  ASSERT_TRUE(q.GetAndClearErrorFlag());
  ASSERT_FALSE(q.GetErrorFlag());

  const auto f3 = q.Add([]() { throw std::runtime_error("test"); });
  ASSERT_EQ(f3.wait(), engine::FutureStatus::kReady);
  ASSERT_TRUE(q.GetErrorFlag());
  q.Cancel();
  ASSERT_FALSE(q.GetErrorFlag());

  auto f4 = q.Add([]() { throw std::runtime_error("test"); });
  ASSERT_EQ(f4.wait(), engine::FutureStatus::kReady);
  ASSERT_TRUE(q.GetErrorFlag());
  q.Cancel(false);
  ASSERT_TRUE(q.GetErrorFlag());
}

}  // namespace
