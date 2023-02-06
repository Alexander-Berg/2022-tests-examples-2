#include "statistics.hpp"

#include <gtest/gtest.h>

const time_t kTimestamp = 1394956800;

TEST(Statistics, DiagnosticStorage) {
  using statistics::DiagnosticStorage;
  DiagnosticStorage storage;

  for (const char* const name : {"abc", "def"}) {
    for (int i = 0; i < 10; ++i)
      storage.StoreResult(name, DiagnosticStorage::Ok);
    storage.StoreResult(name, DiagnosticStorage::Warning);
    storage.StoreResult(name, DiagnosticStorage::Error);

    storage.StoreTime(name, std::chrono::system_clock::from_time_t(kTimestamp));
  }

  Json::Value values(Json::objectValue);
  storage.Store(values);

  const Json::Value& results = values["results"];
  ASSERT_TRUE(results.isObject());

  const Json::Value& times = values["times"];
  ASSERT_TRUE(times.isObject());

  for (const char* const name : {"abc", "def"}) {
    const Json::Value& result = results[name];
    ASSERT_TRUE(result.isObject());

    const Json::Value& time = times[name];
    ASSERT_TRUE(time.isObject());

    EXPECT_EQ(10, result["ok"].asInt());
    EXPECT_EQ(1, result["warn"].asInt());
    EXPECT_EQ(1, result["err"].asInt());

    EXPECT_EQ(kTimestamp, time["timestamp"].asInt64());
  }
}

TEST(AggregatedValues, Empty) {
  statistics::AggregatedValues<3> av;
  EXPECT_EQ(0, av.Get(0));
  EXPECT_EQ(0, av.Get(1));
  EXPECT_EQ(0, av.Get(2));
}

TEST(AggregatedValues, SetGet) {
  statistics::AggregatedValues<3> av;
  av.Add(0, 1);
  av.Add(1, 2);
  av.Add(2, 4);
  av.Add(4, 8);
  av.Add(6, 16);

  EXPECT_EQ(3, av.Get(0));
  EXPECT_EQ(4, av.Get(1));
  EXPECT_EQ(24, av.Get(2));
}
