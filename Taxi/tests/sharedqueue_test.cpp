#include <gtest/gtest.h>
#include <chrono>

#include <utils/shared_queue.hpp>

TEST(SharedQueue, Empty) {
  SharedQueue<int> queue;

  EXPECT_EQ(0u, queue.GetSize());

  int item;
  EXPECT_EQ(queue.Pop(item, std::chrono::milliseconds(1)), false);
}

TEST(SharedQueue, Single) {
  SharedQueue<int> queue;

  int value = 12;
  queue.Push(value);
  EXPECT_EQ(1u, queue.GetSize());

  int item = 3;
  EXPECT_EQ(queue.Pop(item, std::chrono::milliseconds(1)), true);
  EXPECT_EQ(item, value);

  EXPECT_EQ(0u, queue.GetSize());
  EXPECT_EQ(queue.Pop(item, std::chrono::milliseconds(1)), false);
}

TEST(SharedQueue, Double) {
  SharedQueue<int> queue;

  int value = 12, value2 = 22;
  queue.Push(value);
  queue.Push(value2);
  EXPECT_EQ(2u, queue.GetSize());

  int item = 3;
  EXPECT_EQ(queue.Pop(item, std::chrono::milliseconds(1)), true);
  EXPECT_EQ(item, value);
  EXPECT_EQ(1u, queue.GetSize());

  EXPECT_EQ(queue.Pop(item, std::chrono::milliseconds(1)), true);
  EXPECT_EQ(value2, item);
  EXPECT_EQ(0u, queue.GetSize());
}

// TODO: MT tests
