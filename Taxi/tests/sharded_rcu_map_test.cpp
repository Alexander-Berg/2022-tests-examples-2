#include <sharded-rcu-map/sharded-rcu-map.hpp>
#include <userver/utest/utest.hpp>
namespace {
constexpr const size_t kWorkerThreadsCount = 1;
}

UTEST_MT(shard_map_tests, insert_one, kWorkerThreadsCount) {
  sharded_rcu_map::ShardedRcuMap<size_t, size_t> map(256);

  // store
  {
    const size_t key = 5;
    const size_t value = 25;
    *(map[key]) = value;
  }
  // retrieve
  {
    const size_t key = 5;
    const size_t value = *(map.Get(key));
    const size_t should_be = 25;
    ASSERT_EQ(value, should_be);
  }

  ASSERT_EQ(map.SizeApprox(), 1);
}

UTEST_MT(shard_map_tests, insert_two, kWorkerThreadsCount) {
  sharded_rcu_map::ShardedRcuMap<size_t, size_t> map(256);
  std::vector<std::pair<size_t, size_t>> values{{5, 10}, {13, 26}};
  // store values
  for (const auto& [key, value] : values) {
    *(map[key]) = value;
  }
  // retrieve values
  for (const auto& [key, value] : values) {
    ASSERT_EQ(*(map.Get(key)), value);
  }

  ASSERT_EQ(map.SizeApprox(), 2);
}

UTEST_MT(shard_map_tests, insert_many, kWorkerThreadsCount) {
  sharded_rcu_map::ShardedRcuMap<size_t, size_t> map(256);
  constexpr size_t many = 10e2;

  // store many values
  for (size_t i = 0; i < many; ++i) {
    const size_t key = i;
    const size_t value = i * i;
    *(map[key]) = value;
  }

  // retrieve many values
  for (size_t i = 0; i < many; ++i) {
    const size_t key = i;
    const size_t value = *(map.Get(key));
    const size_t should_be = i * i;
    ASSERT_EQ(value, should_be);
  }

  ASSERT_EQ(map.SizeApprox(), many);
}
