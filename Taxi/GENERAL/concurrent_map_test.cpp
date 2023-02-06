#include "concurrent_map.hpp"

#include <gtest/gtest.h>
#include <atomic>
#include <thread>

namespace {

struct Value {
  std::atomic_int i{0};
  std::atomic_int j{0};
};

}  // namespace

TEST(ConcurrentMap, Simple) {
  utils::ConcurrentMap<std::string, Value> map;
  std::string key = "key";

  std::thread t1{[&map, &key] {
    auto& value_1 = map.Get(key);
    value_1.i += 1;
    value_1.j += 1;
  }};

  std::thread t2{[&map, &key] {
    auto& value_1 = map.Get(key);
    value_1.i += 1;
  }};

  t1.join();
  t2.join();

  auto& value_1 = map.Get(key);
  ASSERT_EQ(value_1.i.load(), 2);
  ASSERT_EQ(value_1.j.load(), 1);
}

TEST(ConcurrentMap, MultyThreads) {
  utils::ConcurrentMap<std::string, Value> map;
  const auto kSharedKeys = {"shared0", "shared1", "shared2", "shared3"};
  const std::vector<std::string> kSelfKeys = {"self0", "self1", "self2",
                                              "self3"};
  constexpr int kThreadsCount{4};

  const auto Inc = [&map](const std::string& key) {
    auto& value = map.Get(key);
    ++value.i;
    ++value.j;
  };

  const auto Func = [&kSharedKeys, &Inc](const std::string& self_key) {
    for (const auto& key : kSharedKeys) {
      Inc(key);
    }

    Inc(self_key);
  };

  std::vector<std::thread> threads;

  for (int i = 0; i < kThreadsCount; ++i) {
    threads.emplace_back(Func, kSelfKeys[i]);
  }

  for (auto& thread : threads) {
    thread.join();
  }

  for (const auto& key : kSharedKeys) {
    EXPECT_EQ(map.Get(key).i, 4);
    EXPECT_EQ(map.Get(key).j, 4);
  }

  for (const auto& key : kSelfKeys) {
    EXPECT_EQ(map.Get(key).i, 1);
    EXPECT_EQ(map.Get(key).j, 1);
  }
}

TEST(ConcurrentMap, ForEach) {
  utils::ConcurrentMap<std::string, Value> map;
  for (int i = 0; i < 100; ++i) {
    auto& value = map.Get("key" + std::to_string(i));
    ++value.i;
    ++value.j;
  }

  map.ForEach([](const auto&, const auto& value) {
    EXPECT_EQ(value.i, 1);
    EXPECT_EQ(value.j, 1);
  });

  auto& value = map.Get("key");
  EXPECT_EQ(value.i, 0);
  EXPECT_EQ(value.j, 0);
}

TEST(ConcurrentMap, ConstGet) {
  utils::ConcurrentMap<std::string, Value> map;
  auto& value = map.Get("key");
  ++value.i;

  const auto get = [](const utils::ConcurrentMap<std::string, Value>& map,
                      const std::string& key) -> const Value& {
    return map.Get(key);
  };

  auto& value2 = get(map, "key");
  EXPECT_EQ(value2.i, 1);
  EXPECT_THROW(get(map, "new_key"), std::runtime_error);
}
