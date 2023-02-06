#include <gtest/gtest.h>

#include <userver/engine/run_in_coro.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/utils/async.hpp>

#include <utils/n_priority_mpsc_queue.hpp>

TEST(NPriorityMpscQueue, PushPopNoblock) {
  RunInCoro(
      []() {
        const size_t n_priorities = 3;
        utils::NPriorityMpscQueue<int> queue(n_priorities);

        queue.Push(3, 1);
        queue.Push(1, 0);

        int last_value;
        size_t last_priority = -1;

        ASSERT_TRUE(queue.PopNoblock(last_value, last_priority));
        ASSERT_EQ(1, last_value);
        ASSERT_EQ(0, last_priority);

        queue.Push(2, 0);
        queue.Push(4, 2);

        ASSERT_TRUE(queue.PopNoblock(last_value, last_priority));
        ASSERT_EQ(2, last_value);
        ASSERT_EQ(0, last_priority);

        ASSERT_TRUE(queue.PopNoblock(last_value, last_priority));
        ASSERT_EQ(3, last_value);
        ASSERT_EQ(1, last_priority);

        ASSERT_TRUE(queue.PopNoblock(last_value, last_priority));
        ASSERT_EQ(4, last_value);
        ASSERT_EQ(2, last_priority);

        ASSERT_FALSE(queue.PopNoblock(last_value, last_priority));
      },
      4);
}

TEST(NPriorityMpscQueue, MaxLength) {
  RunInCoro([]() {
    const size_t n_priorities = 3;
    utils::NPriorityMpscQueue<int> queue(n_priorities);

    queue.SetMaxLengthPerPriority(1);

    for (size_t p = 0; p < n_priorities; ++p) {
      ASSERT_TRUE(queue.Push(0, p));
    }

    for (size_t p = 0; p < n_priorities; ++p) {
      ASSERT_FALSE(queue.Push(
          1, p, engine::Deadline::FromDuration(std::chrono::milliseconds(20))));
    }
  });
}

TEST(NPriorityMpscQueue, PushPopBlock) {
  RunInCoro(
      []() {
        const size_t n_priorities = 3;
        utils::NPriorityMpscQueue<char> queue(n_priorities);

        queue.Push('a', 1);
        queue.Push('b', 0);

        auto task = utils::Async("popping_thread", [&queue]() {
          char v = '0';
          size_t priority = -1;

          ASSERT_TRUE(queue.Pop(
              v, priority,
              engine::Deadline::FromDuration(std::chrono::milliseconds(2))));
          ASSERT_EQ('b', v);

          ASSERT_TRUE(queue.Pop(
              v, priority,
              engine::Deadline::FromDuration(std::chrono::milliseconds(2))));
          ASSERT_EQ('a', v);

          ASSERT_FALSE(queue.Pop(
              v, priority,
              engine::Deadline::FromDuration(std::chrono::milliseconds(2))));

          ASSERT_TRUE(queue.Pop(
              v, priority,
              engine::Deadline::FromDuration(std::chrono::milliseconds(100))));
        });

        engine::SleepFor(std::chrono::milliseconds(50));
        queue.Push('c', 2);

        task.Wait();
      },
      4);
}
