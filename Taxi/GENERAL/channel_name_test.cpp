#include <geobus/sharding/channel_name.hpp>

#include <array>

#include <userver/utest/utest.hpp>

namespace sharding_case {

struct TestParam {
  std::string channel_base_name;
  size_t shard;
  std::string shard_name;
};

struct TestChannelName : public ::testing::TestWithParam<TestParam> {};

auto MakeTestData() {
  const std::array base_names{"channel:yagr:position",
                              "channel:yaga:edge_positions"};
  const std::array shards{0u, 1u, 10u};
  const std::string delimeter{"@"};

  auto shard_name = [&delimeter](const std::string base_name, size_t shard) {
    return base_name + delimeter + std::to_string(shard);
  };

  std::vector<TestParam> result;
  result.reserve(base_names.size() * shards.size());
  for (const auto& base_name : base_names) {
    for (const auto shard : shards) {
      result.push_back({base_name, shard, shard_name(base_name, shard)});
    }
  }
  return result;
}

TEST_P(TestChannelName, GetShardName) {
  const auto& [channel_base_name, shard, shard_name] = GetParam();
  ASSERT_EQ(geobus::sharding::GetShardName(channel_base_name, shard),
            shard_name);
}

TEST_P(TestChannelName, GetChannelBaseName) {
  const auto& [channel_base_name, _, shard_name] = GetParam();
  ASSERT_EQ(geobus::sharding::GetChannelBaseName(shard_name),
            channel_base_name);
}

TEST_P(TestChannelName, GetShard) {
  const auto& [_, shard, shard_name] = GetParam();
  ASSERT_EQ(geobus::sharding::GetShard(shard_name), shard);
}

INSTANTIATE_TEST_SUITE_P(ShardingCase, TestChannelName,
                         ::testing::ValuesIn(MakeTestData()));

}  // namespace sharding_case

namespace no_sharding_case {

struct TestParam {
  std::string channel_name;
};

struct TestChannelNameNoSharding : public ::testing::TestWithParam<TestParam> {
};

auto MakeTestData() {
  return std::array{TestParam{"channel:yagr:position"},
                    TestParam{"channel:yaga:edge_position"},
                    TestParam{"channel:tracker:adjust_track"}};
}

TEST_P(TestChannelNameNoSharding, TestChannelNameWithoutSharding) {
  const auto& channel_name = GetParam().channel_name;

  ASSERT_EQ(geobus::sharding::GetChannelBaseName(channel_name), channel_name);
  ASSERT_EQ(geobus::sharding::GetShard(channel_name), 0u);
}

INSTANTIATE_TEST_SUITE_P(NoShardingCase, TestChannelNameNoSharding,
                         ::testing::ValuesIn(MakeTestData()));
}  // namespace no_sharding_case

namespace is_sharding_enabled {

struct TestParam {
  std::string channel_name;
  bool sharding_enabled;
};

struct TestIsShardingEnabled : public ::testing::TestWithParam<TestParam> {};

auto MakeTestData() {
  return std::array{TestParam{"channel:yagr:position", false},
                    TestParam{"channel:yagr:position@0", true},
                    TestParam{"channel:yagr:position@10", true},
                    TestParam{"channel:yaga:edge_positions", false},
                    TestParam{"channel:yaga:edge_positions@6", true},
                    TestParam{"channel:yaga:edge_positions@66", true}};
}

TEST_P(TestIsShardingEnabled, Test) {
  const auto& [channel_name, sharding_enabled] = GetParam();
  ASSERT_EQ(geobus::sharding::IsShardingEnabled(channel_name),
            sharding_enabled);
}

INSTANTIATE_TEST_SUITE_P(TestIsShardingEnabled, TestIsShardingEnabled,
                         ::testing::ValuesIn(MakeTestData()));

}  // namespace is_sharding_enabled
