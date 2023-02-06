#include <userver/utest/utest.hpp>

#include <userver/dump/test_helpers.hpp>

#include <caches/models/non_map_dumped_cache_data.hpp>
#include <caches/models/simple_dumped_cache_data.hpp>

TEST(SimpleDumpedCache, Serialization) {
  dump::TestWriteReadCycle(handlers::DummyValue{42, {false, true}, "foo"});

  // No need to test SimpleDumpedCacheData, because it's just an alias
  // for std::unordered_map, which has builtin serialization
}

UTEST(NonMapDumpedCache, Serialization) {
  // Needed because of engine::Sleep in Write/Read for NonMapDumpedCacheData

  caches::models::NonMapDumpedCacheData data(42, {"bar"});
  data.AddBaz("baz", 5);

  // If operator== was implemented for NonMapDumpedCacheData, the test would
  // just use dump::TestWriteReadCycle
  const auto restored = dump::FromBinary<caches::models::NonMapDumpedCacheData>(
      dump::ToBinary(data));

  EXPECT_EQ(restored.GetFoo(), 42);
  EXPECT_EQ(restored.GetBar(), (std::vector<std::string>{"bar"}));
  EXPECT_EQ(restored.GetBaz("baz"), 5);
}
