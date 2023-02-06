
#include <atomic>

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task_with_result.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <js/execution/mpmc_queue.hpp>

using Queue = js::execution::MpmcQueue<int>;

UTEST(MpmcQueueTest, Basic) {
  auto queue = Queue::Create(1, Queue::PushMode::kBlocking);

  auto producer = queue->GetProducer();
  auto consumer = queue->GetConsumer();

  {
    int expected = 1;
    EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(expected));
    int actual = 0;
    EXPECT_TRUE(consumer->Pop(actual));
    EXPECT_EQ(expected, actual);
  }
}

UTEST(MpmcQueueTest, Block) {
  auto queue = Queue::Create(2, Queue::PushMode::kBlocking);

  auto consumer_task =
      utils::Async("test", [consumer = queue->GetConsumer()]() mutable {
        int value{};
        EXPECT_TRUE(consumer->Pop(value));
        EXPECT_EQ(0, value);

        EXPECT_TRUE(consumer->Pop(value));
        EXPECT_EQ(1, value);

        EXPECT_FALSE(consumer->Pop(value));
      });

  engine::Yield();
  engine::Yield();

  {
    auto producer = queue->GetProducer();
    EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(0));
    engine::Yield();
    EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(1));
  }

  consumer_task.Get();
}

UTEST(MpmcQueueTest, NonBlocking) {
  auto queue = Queue::Create(2, Queue::PushMode::kNonBlocking);

  {
    auto producer = queue->GetProducer();
    EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(0));
    EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(1));
    EXPECT_EQ(Queue::PushStatus::kFailFull, producer->Push(2));
  }

  utils::Async("test", [consumer = queue->GetConsumer()]() mutable {
    int value{};
    EXPECT_TRUE(consumer->Pop(value));
    EXPECT_EQ(0, value);

    EXPECT_TRUE(consumer->Pop(value));
    EXPECT_EQ(1, value);

    EXPECT_FALSE(consumer->Pop(value));
  }).Get();
}

UTEST(MpmcQueueTest, MultipleProducersStarvation) {
  auto queue = Queue::Create(5, Queue::PushMode::kBlocking);

  std::atomic_int expected_sum = 0;
  {
    auto producer = Queue::ProducerSPtr(queue->GetProducer());
    for (int count = 10; count; --count) {
      utils::Async("test", [&expected_sum, producer]() mutable {
        for (int value = 1; value < 10; ++value) {
          EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(value));
          expected_sum += value;
        }
      }).Detach();
    }
  }

  int actual_sum = 0;
  {
    auto consumer = queue->GetConsumer();
    int value;
    while (consumer->Pop(value)) {
      actual_sum += value;
    }
  }

  ASSERT_EQ(/*sum(range(10)) * 10 ==*/450, expected_sum);
  ASSERT_EQ(expected_sum, actual_sum);
}

UTEST(MpmcQueueTest, MultipleConsumersStarvation) {
  auto queue = Queue::Create(5, Queue::PushMode::kBlocking);

  std::vector<engine::TaskWithResult<void>> consumer_tasks;
  std::atomic_int actual_sum = 0;
  {
    auto consumer = Queue::ConsumerSPtr(queue->GetConsumer());

    for (int count = 10; count; --count) {
      consumer_tasks.push_back(
          utils::Async("test", [&actual_sum, consumer]() mutable {
            int value;
            while (consumer->Pop(value)) {
              actual_sum += value;
            }
          }));
    }
  }

  int expected_sum = 0;
  {
    auto producer = queue->GetProducer();
    for (int value = 1; value < 10; ++value) {
      EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(value));
      expected_sum += value;
    }
  }

  for (auto& consumer_task : consumer_tasks) {
    consumer_task.Get();
  }

  ASSERT_EQ(/*sum(range(10)) ==*/45, expected_sum);
  ASSERT_EQ(expected_sum, actual_sum);
}

UTEST(MpmcQueueTest, MultipleProducersMultipleConsumers) {
  auto queue = Queue::Create(5, Queue::PushMode::kBlocking);

  std::atomic_int expected_sum = 0;
  {
    auto producer = Queue::ProducerSPtr(queue->GetProducer());
    for (int count = 10; count; --count) {
      utils::Async("test", [&expected_sum, producer]() mutable {
        for (int value = 1; value < 10; ++value) {
          EXPECT_EQ(Queue::PushStatus::kOk, producer->Push(value));
          expected_sum += value;
        }
      }).Detach();  // no need to wait producers: consumers will exit once
                    // all producers are dead
    }
  }

  std::vector<engine::TaskWithResult<void>> consumer_tasks;
  std::atomic_int actual_sum = 0;
  {
    auto consumer = Queue::ConsumerSPtr(queue->GetConsumer());

    for (int count = 10; count; --count) {
      consumer_tasks.push_back(
          utils::Async("test", [&actual_sum, consumer]() mutable {
            int value;
            while (consumer->Pop(value)) {
              actual_sum += value;
            }
          }));
    }
  }

  for (auto& consumer_task : consumer_tasks) {
    consumer_task.Get();
  }

  ASSERT_EQ(/*sum(range(10)) * 10 ==*/450, expected_sum);
  ASSERT_EQ(expected_sum, actual_sum);
}
