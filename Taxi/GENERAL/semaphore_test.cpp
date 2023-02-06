#include "semaphore.hpp"

#include <atomic>
#include <condition_variable>
#include <future>
#include <thread>
#include <vector>

#include <gtest/gtest.h>
#include <boost/optional.hpp>
#include <boost/utility/in_place_factory.hpp>

using Semaphore = utils::Semaphore;

constexpr size_t kTestThreads = 16;
constexpr auto kPause = std::chrono::milliseconds{10};

constexpr auto kNoWait = std::chrono::seconds{0};
constexpr auto kWait = std::chrono::seconds{10};

TEST(Semaphore, Empty) {
  Semaphore sem(0);
  EXPECT_EQ(sem.Limit(), 0ul);
  EXPECT_FALSE(sem.Acquire(kNoWait));
  EXPECT_FALSE(sem.Acquire(kNoWait).IsValid());
}

TEST(Semaphore, Binary) {
  constexpr uint64_t kLimit = 1;

  Semaphore sem(kLimit);
  EXPECT_EQ(sem.Limit(), kLimit);
  std::atomic<size_t> counter{0};

  std::vector<std::future<void>> futures;
  for (size_t i = 0; i < kTestThreads; ++i) {
    futures.push_back(std::async(std::launch::async, [&] {
      auto ticket = sem.Acquire(kWait);
      ASSERT_TRUE(ticket);
      EXPECT_LE(++counter, kLimit);
      std::this_thread::sleep_for(kPause);
      --counter;
    }));
  }
  for (auto& f : futures) f.get();
}

TEST(Semaphore, Ternary) {
  constexpr uint64_t kLimit = 2;

  Semaphore sem(kLimit);
  EXPECT_EQ(sem.Limit(), kLimit);
  std::atomic<size_t> counter{0};

  std::vector<std::future<void>> futures;
  for (size_t i = 0; i < kTestThreads; ++i) {
    futures.push_back(std::async(std::launch::async, [&] {
      auto ticket = sem.Acquire(kWait);
      ASSERT_TRUE(ticket);
      EXPECT_LE(++counter, kLimit);
      std::this_thread::sleep_for(kPause);
      --counter;
    }));
  }
  for (auto& f : futures) f.get();
}

TEST(Semaphore, HighLimit) {
  Semaphore sem(kTestThreads);
  EXPECT_EQ(sem.Limit(), kTestThreads);

  std::vector<std::future<void>> futures;
  for (size_t i = 0; i < kTestThreads; ++i) {
    futures.push_back(std::async(std::launch::async, [&] {
      auto ticket = sem.Acquire(kNoWait);
      EXPECT_TRUE(ticket);
    }));
  }
  for (auto& f : futures) f.get();
}

TEST(Semaphore, Shutdown) {
  std::mutex mutex;
  std::condition_variable cv;
  int stage = 0;

  // HACK to allow somewhat predictable memory reads after destruction
  // because of race condition in skipped_task
  boost::optional<Semaphore> sem(boost::in_place(1));

  auto long_task = std::async(std::launch::async, [&] {
    auto ticket = sem->Acquire(kNoWait);
    ASSERT_TRUE(ticket.IsValid());
    {
      std::unique_lock<std::mutex> lock(mutex);
      ASSERT_EQ(stage, 0);
      ++stage;
      cv.notify_all();
    }
    {
      std::unique_lock<std::mutex> lock(mutex);
      ASSERT_TRUE(cv.wait_for(lock, kWait, [&] { return stage == 3; }));
    }
  });
  auto skipped_task = std::async(std::launch::async, [&] {
    {
      std::unique_lock<std::mutex> lock(mutex);
      ASSERT_TRUE(cv.wait_for(lock, kWait, [&] { return stage == 1; }));
      ++stage;
      cv.notify_all();
    }
    EXPECT_FALSE(sem->Acquire(kWait));
  });

  // Give skipped_task a chance to enter Acquire()
  std::this_thread::sleep_for(kPause);
  {
    std::unique_lock<std::mutex> lock(mutex);
    ASSERT_TRUE(cv.wait_for(lock, kWait, [&] { return stage == 2; }));
    ++stage;
    cv.notify_all();
  }

  sem = boost::none;
  skipped_task.get();
  long_task.get();
}

TEST(Semaphore, Ownership) {
  Semaphore sem(2);

  auto ticket1 = sem.Acquire(kNoWait);
  ASSERT_TRUE(ticket1);
  {
    auto ticket2 = sem.Acquire(kNoWait);
    ASSERT_TRUE(ticket2);
    ASSERT_FALSE(sem.Acquire(kNoWait));
    ticket1 = std::move(ticket2);
  }
  auto ticket3 = sem.Acquire(kNoWait);
  ASSERT_TRUE(ticket3);
  ASSERT_FALSE(sem.Acquire(kNoWait));
  ticket3.Invalidate();
  ASSERT_FALSE(ticket3);
  ticket3 = sem.Acquire(kNoWait);
  ASSERT_TRUE(ticket3);
  ASSERT_FALSE(sem.Acquire(kNoWait));
}
