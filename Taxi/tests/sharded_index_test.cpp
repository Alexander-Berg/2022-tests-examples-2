#include <sharded-rcu-map/sharded-index.hpp>
#include <userver/utest/utest.hpp>

#include <string>

namespace {
size_t kShardsNumber = 128;
}

UTEST(ShardedIndexTests, UpdateValue) {
  sharded_map::ShardedIndex<std::string, int> index(kShardsNumber);
  EXPECT_EQ(index.GetEpochNumber(), 0);
  ASSERT_FALSE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(index.Size(), 0);

  ASSERT_TRUE(index.UpdateValue("first_epoch_key", 0));
  ASSERT_TRUE(index.UpdateValue("first_epoch_key", 1));
  EXPECT_EQ(index.Size(), 1);
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 1);

  index.SwitchToNextEpoch();
  EXPECT_EQ(index.GetEpochNumber(), 1);
  EXPECT_EQ(index.Size(), 1);
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 1);
  ASSERT_TRUE(index.UpdateValue("first_epoch_key", 2));
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 2);

  index.SwitchToNextEpoch();
  EXPECT_EQ(index.GetEpochNumber(), 2);
  EXPECT_EQ(index.Size(), 1);
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 2);

  index.SwitchToNextEpoch();
  EXPECT_EQ(index.GetEpochNumber(), 3);
  EXPECT_EQ(index.Size(), 0);
}

UTEST(ShardedIndexTests, Base) {
  sharded_map::ShardedIndex<std::string, int> index(kShardsNumber);
  EXPECT_EQ(index.GetEpochNumber(), 0);
  ASSERT_FALSE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(index.Size(), 0);

  ASSERT_TRUE(index.UpdateValue("first_epoch_key", 0));
  EXPECT_EQ(index.Size(), 1);
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 0);

  index.SwitchToNextEpoch();
  ASSERT_TRUE(index.UpdateValue("second_epoch_key", 1));
  EXPECT_EQ(index.Size(), 2);
  EXPECT_EQ(index.GetEpochNumber(), 1);
  ASSERT_TRUE(index.GetValue("first_epoch_key"));
  EXPECT_EQ(*index.GetValue("first_epoch_key"), 0);
  ASSERT_TRUE(index.GetValue("second_epoch_key"));
  EXPECT_EQ(*index.GetValue("second_epoch_key"), 1);

  index.SwitchToNextEpoch();
  EXPECT_EQ(index.Size(), 1);
  EXPECT_EQ(index.GetEpochNumber(), 2);
  ASSERT_FALSE(index.GetValue("first_epoch_key"));
  ASSERT_TRUE(index.GetValue("second_epoch_key"));
  EXPECT_EQ(index.GetValue("second_epoch_key"), 1);
  ASSERT_TRUE(index.UpdateValue("second_epoch_key", 2));
  EXPECT_EQ(index.Size(), 2);
  ASSERT_TRUE(index.GetValue("second_epoch_key"));
  EXPECT_EQ(index.GetValue("second_epoch_key"), 2);

  index.SwitchToNextEpoch();
  EXPECT_EQ(index.GetEpochNumber(), 3);
  ASSERT_FALSE(index.GetValue("first_epoch_key"));
  ASSERT_TRUE(index.GetValue("second_epoch_key"));
  EXPECT_EQ(index.GetValue("second_epoch_key"), 2);
  EXPECT_EQ(index.Size(), 1);

  index.Clear();
  EXPECT_EQ(index.Size(), 0);
}

UTEST(ShardedIndexTests, UpdateWithComparator) {
  struct Value {
    std::chrono::seconds time{0};
    size_t value = 0;
  };

  auto comp = [](const Value& storage_value, const Value& value) {
    return storage_value.time <= value.time;
  };

  std::string key = "first_epoch_key";
  Value first_v = {std::chrono::seconds(0), 0};
  Value second_v = {std::chrono::seconds(1), 1};
  Value third_v = {std::chrono::seconds(2), 2};

  /// Check that second_v is received before first_v. We need to store only
  /// the latest value.
  sharded_map::ShardedIndex<std::string, Value> index(kShardsNumber);
  ASSERT_TRUE(index.UpdateValue(key, second_v, comp));
  ASSERT_FALSE(index.UpdateValue(key, first_v, comp));
  EXPECT_EQ(index.Size(), 1);
  auto actual = index.GetValue(key);
  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->time, second_v.time);
  EXPECT_EQ(actual->value, second_v.value);

  /// Check that if we receive old value, we just skip it without changes in
  /// new epoch storage.
  index.SwitchToNextEpoch();
  actual = index.GetValue(key);
  EXPECT_EQ(index.Size(), 1);
  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->time, second_v.time);
  EXPECT_EQ(actual->value, second_v.value);
  ASSERT_FALSE(index.UpdateValue(key, first_v, comp));
  EXPECT_EQ(index.Size(), 1);
  EXPECT_EQ(index.GetEpochNumber(), 1);
  actual = index.GetValue(key);
  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->time, second_v.time);
  EXPECT_EQ(actual->value, second_v.value);

  /// Check that we store new value in new epoch storage, and old value is
  /// saved in old epoch storage.
  ASSERT_TRUE(index.UpdateValue(key, third_v, comp));
  EXPECT_EQ(index.Size(), 2);
  actual = index.GetValue(key);
  ASSERT_TRUE(actual);
  EXPECT_EQ(actual->time, third_v.time);
  EXPECT_EQ(actual->value, third_v.value);

  index.Clear();
  EXPECT_EQ(index.Size(), 0);
}
