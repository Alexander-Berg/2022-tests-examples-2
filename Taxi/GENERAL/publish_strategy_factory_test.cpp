#include <sharding/publish_strategy_factory.hpp>

#include <array>
#include <functional>

#include <userver/utest/utest.hpp>

#include <sharding/hashing_sharding_publish_strategy.hpp>
#include <sharding/no_sharding_publish_strategy.hpp>
#include <sharding/publish_strategy.hpp>

namespace {

using Config = geobus::subscription::Config;
using NoShardingConfig = geobus::subscription::NoShardingConfig;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;

using PublishStrategy = geobus::sharding::PublishStrategy;
using NoShardingPublishStrategy = geobus::sharding::NoShardingPublishStrategy;
using HashingShardingPublishStrategy =
    geobus::sharding::HashingShardingPublishStrategy;

struct TestParam {
  Config input_config;
  std::function<bool(PublishStrategy*)> check_type;
};

template <typename StrategyType>
bool Is(PublishStrategy* strategy) {
  return dynamic_cast<StrategyType*>(strategy) != nullptr;
}

struct PublishStrategyFactoryTest : ::testing::TestWithParam<TestParam> {};

TEST_P(PublishStrategyFactoryTest, Simple) {
  auto strategy = geobus::sharding::MakeStrategy(GetParam().input_config);

  ASSERT_PRED1(GetParam().check_type, strategy.get());
}

auto MakeTestData() {
  return std::array{
      // clang-format off
    TestParam{NoShardingConfig{}, Is<NoShardingPublishStrategy>},
    TestParam{HashingShardingConfig{2}, Is<HashingShardingPublishStrategy>}
      // clang-format on
  };
}

INSTANTIATE_TEST_SUITE_P(PublishStrategyFactoryTest, PublishStrategyFactoryTest,
                         ::testing::ValuesIn(MakeTestData()));

}  // namespace
