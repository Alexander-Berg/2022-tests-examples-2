
#include <array>

#include <userver/utest/utest.hpp>

#include <subscription/partitioning_config_conversion.hpp>

namespace {

using GroupChannels = taxi_config::geobus_partitions_settings::GroupChannels;
using ChannelGroup = taxi_config::geobus_partitions_settings::Group;
using PartitionsSettings = std::vector<ChannelGroup>;
using taxi_config::geobus_partitions_settings::HashingParamsType;
using HashingParams = taxi_config::geobus_partitions_settings::HashingParams;
using NoPartitioningParams =
    taxi_config::geobus_partitions_settings::NoPartitioningParams;

using PartitioningConfig = geobus::subscription::PartitioningConfig;
using Address = geobus::channels::Address;
using RedisName = geobus::channels::RedisName;
using ChannelName = geobus::channels::ChannelName;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;
using NoShardingConfig = geobus::subscription::NoShardingConfig;

struct TestParam {
  PartitioningConfig reference;
  PartitionsSettings partitions_settings;
};

struct PartitionedConfigConversionTest : ::testing::TestWithParam<TestParam> {};

TEST_P(PartitionedConfigConversionTest, Simple) {
  ASSERT_EQ(GetParam().reference,
            geobus::subscription::ToLocal(GetParam().partitions_settings));
}

auto MakePartitioningConfig() { return PartitioningConfig{{}}; }

auto MakePartitionsSettings() { return PartitionsSettings{}; }

auto MakeEmptyTestParam() {
  return TestParam{MakePartitioningConfig(), MakePartitionsSettings()};
}

auto MakeSimplePartitioningConfig() {
  // clang-format off
  return PartitioningConfig{
      {
          {
              Address{RedisName{"redis-1"}, ChannelName{"channel-1"}},
              HashingShardingConfig{2ull}
          }
      }
  };
  // clang-format on
}

auto MakeSimplePartitionsSettings() {
  // clang-format off
    return PartitionsSettings{
        ChannelGroup { // Group
            GroupChannels {
                {
                    std::pair{
                        std::string{ "redis-1" },
                        std::vector{
                            std::string{"channel-1"}
                        }
                    }
                }
            },
            { // settings
                HashingParams{HashingParamsType::kHashing, 2}
            }
        }
    };
  // clang-format on
}

auto MakeSimpleTestParam() {
  return TestParam{MakeSimplePartitioningConfig(),
                   MakeSimplePartitionsSettings()};
}

auto MakeOrdinaryPartitioningConfig() {
  // clang-format off
  return PartitioningConfig{
      {
          {
              Address{RedisName{"redis-1"}, ChannelName{"channel-1"}},
              HashingShardingConfig{2ull}
          },
          {
              Address{RedisName{"redis-1"}, ChannelName{"channel-2"}},
              HashingShardingConfig{2ull}
          },
          {
              Address{RedisName{"redis-2"}, ChannelName{"channel-3"}},
              HashingShardingConfig{2ull}
          },
          {
              Address{RedisName{"redis-3"}, ChannelName{"channel-4"}},
              NoShardingConfig{}
          }
      }
  };
  // clang-format on
}

auto MakeOrdinaryPartitionsSettings() {
  // clang-format off
    return PartitionsSettings{
        ChannelGroup { // Group
            GroupChannels{
                {
                    {
                        std::string{ "redis-1" },
                        std::vector{
                            std::string{"channel-1"},
                            std::string{"channel-2"}
                        }
                    },
                    {
                        std::string{ "redis-2" },
                        std::vector{
                            std::string{"channel-3"},
                        }
                    }
                }
            },
            { // settings
                HashingParams{HashingParamsType::kHashing, 2}
            }
        },
        ChannelGroup { // Group
            GroupChannels{
                {
                    {
                        std::string{ "redis-3" },
                        std::vector{
                            std::string{"channel-4"},
                        }
                    }
                }
            },
            { // settings
                NoPartitioningParams{}
            }
        }
    };
  // clang-format on
}

auto MakeOrdinaryTestParam() {
  return TestParam{MakeOrdinaryPartitioningConfig(),
                   MakeOrdinaryPartitionsSettings()};
}

auto MakeTestData() {
  return std::array{MakeEmptyTestParam(), MakeSimpleTestParam(),
                    MakeOrdinaryTestParam()};
}

INSTANTIATE_TEST_SUITE_P(PartitionedConfigConversionTest,
                         PartitionedConfigConversionTest,
                         ::testing::ValuesIn(MakeTestData()));

}  // namespace
