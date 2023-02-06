#include <gtest/gtest.h>

#include <random>

#include "db/partition.hpp"
#include "taxi_config/taxi_config.hpp"
#include "test_helpers.hpp"

namespace routehistory::db {
bool operator==(const PartitionShardSet& lhs, const PartitionShardSet& rhs) {
  return lhs.read_write == rhs.read_write && lhs.write_only == rhs.write_only;
}
}  // namespace routehistory::db

namespace routehistory::test {
using namespace ::routehistory::db;

using ConfigPartType = ::taxi_config::routehistory_partition::PartType;
using ConfigPartition = ::taxi_config::routehistory_partition::Partition;

std::ostream& operator<<(std::ostream& s, const IOWrap<PartitionRanges>& self) {
  s << "PartitionRanges[";
  for (const auto& [key, shards] : self.ref) {
    s << "{key=" << key << ":{rw=[";
    for (const auto& shard : shards.read_write) {
      s << shard << ",";
    }
    s << "],w=[";
    for (const auto& shard : shards.write_only) {
      s << shard << ",";
    }
    s << "]}},";
  }
  s << "]";
  return s;
}

namespace partition {

TEST(Partition, Simple1) {
  ConfigPartition config{
      {0, 100, ConfigPartType::kReadWrite, 1},
  };
  const PartitionRanges expected{
      {0, {{1}, {1}}},  //
      {100, {}},        //
  };
  Partition partition(config, 0, 100, 2);
  ASSERT_EQ(IOWrap(partition.GetRanges()), IOWrap(expected));
}

TEST(Partition, Simple2) {
  ConfigPartition config{
      {0, 50, ConfigPartType::kReadWrite, 1},
      {50, 100, ConfigPartType::kReadWrite, 0},
  };
  const PartitionRanges expected{
      {0, {{1}, {1}}},   //
      {50, {{0}, {0}}},  //
      {100, {}},         //
  };
  Partition partition(config, 0, 100, 2);
  ASSERT_EQ(IOWrap(partition.GetRanges()), IOWrap(expected));
}

struct WithShuffle : testing::TestWithParam<unsigned> {};

TEST_P(WithShuffle, Default) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kWriteOnly, 1},
      {25, 75, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
      {0, 50, ConfigPartType::kReadWrite, 5},
      {50, 100, ConfigPartType::kReadWrite, 6},
      {50, 75, ConfigPartType::kReadWrite, 7},
  };
  if (GetParam() != 0u) {
    std::shuffle(config.begin(), config.end(), std::mt19937{GetParam()});
  }
  const PartitionRanges expected{
      {0, {{1, 5}, {5}}},            //
      {25, {{2, 5}, {2, 5}}},        //
      {50, {{2, 6, 7}, {2, 6, 7}}},  //
      {75, {{3, 6}, {3, 6}}},        //
      {100, {}},                     //
  };
  Partition partition(config, 0, 100, 8);
  ASSERT_EQ(IOWrap(partition.GetRanges()), IOWrap(expected));
}

INSTANTIATE_TEST_SUITE_P(Partition, WithShuffle, testing::Range(0u, 16u));

std::string DoExceptionTest(const ConfigPartition& partition,
                            db::ShardKey key_min, db::ShardKey key_max,
                            db::ShardNumber shard_count) {
  std::string what;
  try {
    Partition(partition, key_min, key_max, shard_count);
  } catch (const std::exception& ex) {
    what = ex.what();
  }
  return what;
}

TEST(Partition, Bad1) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kWriteOnly, 1},
      {25, 75, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
      {0, 50, ConfigPartType::kWriteOnly, 5},
      {50, 100, ConfigPartType::kReadWrite, 6},
      {50, 75, ConfigPartType::kReadWrite, 7},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 100, 8),
            "Not all ranges have an RW shard in partition");
}

TEST(Partition, Bad2) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kReadWrite, 1},
      {25, 100, ConfigPartType::kReadWrite, 2},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 100, 2),
            "Invalid shard number in partition");
}

TEST(Partition, Bad3) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kReadWrite, 1},
      {75, 25, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 100, 4), "Invalid range in partition");
}

TEST(Partition, Bad4) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kReadWrite, 1},
      {25, 75, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
      {24, 26, ConfigPartType::kReadWrite, 1},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 100, 4),
            "Overlapping ranges with same shard number in partition");
}

TEST(Partition, Bad5) {
  ConfigPartition config{
      {10, 25, ConfigPartType::kReadWrite, 1},
      {25, 75, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 100, 4),
            "Partition does not cover all possible shard keys");
}

TEST(Partition, Bad6) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kReadWrite, 1},
      {25, 75, ConfigPartType::kReadWrite, 1},
      {75, 100, ConfigPartType::kReadWrite, 1},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 110, 4),
            "Partition does not cover all possible shard keys");
}

TEST(Partition, Bad7) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kReadWrite, 1},
      {25, 75, ConfigPartType::kReadWrite, 1},
      {75, 100, ConfigPartType::kReadWrite, 1},
  };
  ASSERT_EQ(DoExceptionTest(config, 0, 90, 4), "Invalid range in partition");
}

std::string DoGetShardsExceptionTest(const Partition& partition,
                                     db::ShardKey key) {
  std::string what;
  try {
    partition.GetShardsForKey(key);
  } catch (const std::exception& ex) {
    what = ex.what();
  }
  return what;
}

TEST(Partition, GetShardsForKey) {
  ConfigPartition config{
      {0, 25, ConfigPartType::kWriteOnly, 1},
      {25, 75, ConfigPartType::kReadWrite, 2},
      {75, 100, ConfigPartType::kReadWrite, 3},
      {0, 50, ConfigPartType::kReadWrite, 5},
      {50, 100, ConfigPartType::kReadWrite, 6},
      {55, 75, ConfigPartType::kReadWrite, 10, 7},
  };
  Partition partition(config, 0, 100, 8);
  EXPECT_EQ(DoGetShardsExceptionTest(partition, -1), "Invalid shard key");
  EXPECT_EQ(&partition.GetShardsForKey(0), &partition.GetRanges().at(0));
  EXPECT_EQ(&partition.GetShardsForKey(1), &partition.GetRanges().at(0));
  EXPECT_EQ(&partition.GetShardsForKey(24), &partition.GetRanges().at(0));
  EXPECT_EQ(&partition.GetShardsForKey(25), &partition.GetRanges().at(25));
  EXPECT_EQ(&partition.GetShardsForKey(26), &partition.GetRanges().at(25));
  EXPECT_EQ(&partition.GetShardsForKey(49), &partition.GetRanges().at(25));
  EXPECT_EQ(&partition.GetShardsForKey(50), &partition.GetRanges().at(50));
  EXPECT_EQ(&partition.GetShardsForKey(51), &partition.GetRanges().at(50));
  EXPECT_EQ(&partition.GetShardsForKey(54), &partition.GetRanges().at(50));
  EXPECT_EQ(&partition.GetShardsForKey(55), &partition.GetRanges().at(55));
  EXPECT_EQ(&partition.GetShardsForKey(56), &partition.GetRanges().at(55));
  EXPECT_EQ(&partition.GetShardsForKey(74), &partition.GetRanges().at(55));
  EXPECT_EQ(&partition.GetShardsForKey(75), &partition.GetRanges().at(75));
  EXPECT_EQ(&partition.GetShardsForKey(76), &partition.GetRanges().at(75));
  EXPECT_EQ(&partition.GetShardsForKey(99), &partition.GetRanges().at(75));
  EXPECT_EQ(DoGetShardsExceptionTest(partition, 100), "Invalid shard key");
  EXPECT_EQ(DoGetShardsExceptionTest(partition, 101), "Invalid shard key");
}

}  // namespace partition
}  // namespace routehistory::test
