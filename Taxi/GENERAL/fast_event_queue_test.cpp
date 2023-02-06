#include "fast_event_queue.hpp"

#include <gtest/gtest.h>

#include <algorithm>
#include <array>
#include <numeric>
#include <random>
#include <userver/logging/log.hpp>
#include <userver/utils/mock_now.hpp>

// I am not going to test concurrency here, it looks almost impossible due to
// very fast operations. Test logic instead

namespace event_queue::tests {

TEST(FastEventQueue, TestBasic) {
  FastEventQueue q(std::chrono::seconds(60));
  auto now = std::chrono::system_clock::now();
  for (std::chrono::seconds delta(0); delta < std::chrono::seconds(156);
       ++delta) {
    utils::datetime::MockNowSet(now + delta);
    q.Append();
  }
  EXPECT_EQ(60, q.Get());
}

TEST(FastEventQueue, TestGrow) {
  FastEventQueue q(std::chrono::seconds(60));
  auto now = std::chrono::system_clock::now();
  for (int i = 0; i <= 156; ++i) {
    utils::datetime::MockNowSet(now + std::chrono::seconds(i));
    q.Append(i);
  }
  EXPECT_EQ(((156 - 60 + 1) + 156) * 60 / 2, q.Get());
}

TEST(FastEventQueue, TestRandomShuffle) {
  std::array<int, 60> d;
  std::generate(d.begin(), d.end(), [] {
    static int i = 0;
    return ++i;
  });

  auto seed = std::chrono::system_clock::now().time_since_epoch().count();
  LOG_INFO() << "Shuffle seed: " << seed;
  std::default_random_engine rd(seed);
  std::mt19937 g(rd());
  std::shuffle(d.begin(), d.end(), g);

  auto now = std::chrono::system_clock::now();

  FastEventQueue q(std::chrono::seconds(60));
  for (size_t i = 0; i < d.size(); ++i) {
    utils::datetime::MockNowSet(now + std::chrono::seconds(i));
    q.Append(d[i]);
  }
  EXPECT_EQ(std::accumulate(d.begin(), d.end(), 0), q.Get());
}

TEST(FastEventQueue, IsLockFree) {
  FastEventQueue<std::chrono::seconds>::EventStorage events1(60);
  for (auto& e : events1) {
    EXPECT_TRUE(e.is_lock_free());
  }
  constexpr auto is_lock_free1 = FastEventQueue<
      std::chrono::seconds>::EventStorage::value_type::is_always_lock_free;
  EXPECT_TRUE(is_lock_free1);

  FastEventQueue<std::chrono::milliseconds>::EventStorage events2(60);
  for (auto& e : events2) {
    EXPECT_TRUE(e.is_lock_free());
  }
  constexpr auto is_lock_free2 = FastEventQueue<
      std::chrono::milliseconds>::EventStorage::value_type::is_always_lock_free;
  EXPECT_TRUE(is_lock_free2);
}

TEST(FastEventQueue, TestAnotherUnit) {
  FastEventQueue q(std::chrono::milliseconds(1000));
  auto now = std::chrono::system_clock::now();
  for (int i = 0; i < 5000; ++i) {
    utils::datetime::MockNowSet(now + std::chrono::milliseconds(i));
    q.Append();
  }
  EXPECT_EQ(1000, q.Get());
}

TEST(FastEventQueue, TestGetIntervalSums) {
  FastEventQueue q(std::chrono::seconds(10));
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  for (auto i = 1; i < 11; i++) {
    utils::datetime::MockSleep(std::chrono::seconds(1));
    q.Append(i * 10);
  }
  EXPECT_EQ(q.GetIntervalSums(std::chrono::seconds(1)),
            std::vector<int64_t>({100, 90, 80, 70, 60, 50, 40, 30, 20, 10}));

  utils::datetime::MockSleep(std::chrono::seconds(1));
  q.Append(110);
  EXPECT_EQ(q.GetIntervalSums(std::chrono::seconds(1)),
            std::vector<int64_t>({110, 100, 90, 80, 70, 60, 50, 40, 30, 20}));

  utils::datetime::MockSleep(std::chrono::seconds(1));
  EXPECT_EQ(q.GetIntervalSums(std::chrono::seconds(1)),
            std::vector<int64_t>({0, 110, 100, 90, 80, 70, 60, 50, 40, 30}));
}

TEST(FastEventQueue, TestGetIntervalSums2) {
  // FastEventQueue q(std::chrono::milliseconds(5000));
  auto now = std::chrono::system_clock::now();
  utils::datetime::MockNowSet(now);

  FastEventQueue q(std::chrono::milliseconds(10));
  for (int i = 0; i < 10; ++i) {
    utils::datetime::MockSleep(std::chrono::milliseconds(1));
    q.Append();
  }
  auto result2 = q.GetIntervalSums(std::chrono::milliseconds(4));
  EXPECT_EQ(3, result2.size());
  EXPECT_EQ(result2, std::vector<int64_t>({4, 4, 2}));
}

TEST(FastEventQueue, TestGetIntervalSums3) {
  FastEventQueue q(std::chrono::milliseconds(5000));
  auto now = std::chrono::system_clock::now();
  for (int i = 0; i < 5000; ++i) {
    utils::datetime::MockNowSet(now + std::chrono::milliseconds(i));
    q.Append();
  }
  auto result = q.GetIntervalSums(std::chrono::milliseconds(1000));
  EXPECT_EQ(5, result.size());
  for (auto value : result) {
    EXPECT_EQ(1000, value);
  }

  auto result2 = q.GetIntervalSums(std::chrono::milliseconds(400));
  EXPECT_EQ(13, result2.size());
  for (unsigned i = 0; i < 12; ++i) {
    EXPECT_EQ(400, result2[i]);
  }
  EXPECT_EQ(200, result2[12]);
}

TEST(FastEventQueue, TestCopy) {
  FastEventQueue q(std::chrono::milliseconds(500));
  auto now = std::chrono::system_clock::now();
  for (int i = 0; i < 500; ++i) {
    utils::datetime::MockNowSet(now + std::chrono::milliseconds(i));
    q.Append();
  }

  FastEventQueue q2(std::chrono::milliseconds(300));
  q2.CopyEvents(q);
  EXPECT_EQ(300, q2.Get());
}

TEST(FastEventQueue, Negative) {
  FastEventQueue q(std::chrono::milliseconds(500));
  auto now = std::chrono::system_clock::now();
  for (int i = 0; i < 500; ++i) {
    utils::datetime::MockNowSet(now + std::chrono::milliseconds(i));
    q.Append(i * (i % 2 ? -1 : 1));
  }
  EXPECT_EQ(-250, q.Get());
  auto values = q.GetIntervalSums(std::chrono::milliseconds{100});
  EXPECT_EQ(values.size(), static_cast<size_t>(5));
  EXPECT_EQ(values[4], -50);
}

}  // namespace event_queue::tests
