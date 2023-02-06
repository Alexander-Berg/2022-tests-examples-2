#include <gtest/gtest.h>

#include <ostream>

#include <userver/utest/parameter_names.hpp>

#include <db/sharding.hpp>

namespace db::sharding {

namespace config {

namespace invalid_config {

struct TestParams {
  ShardMapper source;

  std::string test_name;
};

class TestInvalidShardingConfig : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kInvalidConfigs = {
    {{}, "Empty"},
    {{{10, 0}, {20, 1}}, "NoZeroKey"},
    {{{0, 0}, {1024, 1}}, "MaxKeyPlusOne"},
    {{{0, 0}, {100500, 0}}, "BigKey"},
};

TEST_P(TestInvalidShardingConfig, InvalidConfig) {
  EXPECT_THROW(ShardingConfig(GetParam().source), std::invalid_argument);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestInvalidShardingConfig,
                         testing::ValuesIn(kInvalidConfigs),
                         ::utest::PrintTestName());

}  // namespace invalid_config

namespace valid_config {

struct TestParams {
  size_t virtual_shard;
  size_t real_shard;
};

void PrintTo(const TestParams& params, std::ostream* output_stream) {
  *output_stream << "VShard" << params.virtual_shard;
}

class TestShardingConfig : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kValidConfigParams = {
    {0, 0},   {100, 0}, {199, 0}, {200, 1},
    {300, 1}, {499, 1}, {500, 2}, {1023, 2},
};

TEST_P(TestShardingConfig, ValidConfig) {
  const ShardingConfig config{{
      {0, 0},
      {200, 1},
      {500, 2},
  }};

  EXPECT_EQ(config.GetRealShardForVirtual(GetParam().virtual_shard),
            GetParam().real_shard);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestShardingConfig,
                         testing::ValuesIn(kValidConfigParams),
                         ::utest::PrintTestName());

}  // namespace valid_config

TEST(TestVirtualShards, InvalidVirtualShard) {
  const ShardingConfig config{{
      {0, 0},
      {200, 1},
      {500, 3},
  }};

  EXPECT_THROW(config.GetRealShardForVirtual(1024), std::invalid_argument);
  EXPECT_THROW(config.GetRealShardForVirtual(2000), std::invalid_argument);
  EXPECT_THROW(config.GetRealShardForVirtual(100500), std::invalid_argument);
}

namespace parse {

struct ShardConfigItem {
  int virtual_shard_from;
  int real_shard;
};

TEST(TestParseShardingConfig, CorrectConfig) {
  const std::vector<ShardConfigItem> config = {{0, 0}, {512, 1}};
  EXPECT_NO_THROW(ParseShardingConfig(config));
}

TEST(TestParseShardingConfig, DuplicateVirtualShards) {
  const std::vector<ShardConfigItem> config = {{0, 0}, {0, 1}};
  EXPECT_THROW(ParseShardingConfig(config), std::logic_error);
}

struct TestParams {
  std::vector<ShardConfigItem> source;

  std::string test_name;
};

class TestParseInvalidShardingConfig
    : public testing::TestWithParam<TestParams> {};

const std::vector<TestParams> kInvalidConfigs = {
    {{{-1, 0}, {512, 1}}, "NegativeVirtualShards"},
    {{{0, -1}, {512, 1}}, "NegativeRealShards"},
    {{{0, 0}, {10000, 1}}, "BigVirtualShards"},
    {{{0, 0}, {1, 10000}}, "BigRealShards"},
};

TEST_P(TestParseInvalidShardingConfig, InvalidValues) {
  EXPECT_THROW(ParseShardingConfig(GetParam().source), std::invalid_argument);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestParseInvalidShardingConfig,
                         testing::ValuesIn(kInvalidConfigs),
                         ::utest::PrintTestName());

}  // namespace parse

}  // namespace config

}  // namespace db::sharding
