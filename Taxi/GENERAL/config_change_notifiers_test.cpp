#include <listeners/config_change_notifiers.hpp>

#include <array>
#include <functional>
#include <optional>

#include <userver/utest/utest.hpp>

namespace {

using NoShardingConfig = geobus::subscription::NoShardingConfig;
using HashingShardingConfig = geobus::subscription::HashingShardingConfig;
using Config = geobus::subscription::Config;
using PartitioningConfig = geobus::subscription::PartitioningConfig;

using ConfigChangeNotifiers = geobus::listeners::ConfigChangeNotifiers;
using ConfigChangeReceiver = geobus::subscription::ConfigChangeReceiver;
using ChannelsAddresses = geobus::channels::ChannelsAddresses;
using RawAddresses = geobus::channels::impl::RawAddresses;
using AddressId = geobus::channels::AddressId;
using RedisName = geobus::channels::RedisName;
using ChannelName = geobus::channels::ChannelName;
using Address = geobus::channels::Address;

const AddressId InterestingAddressId{"address-id"};
const Address InterestingChannelAddress{RedisName{"redis-1"},
                                        ChannelName{"channel-1"}};

auto MakeAddresses() {
  RawAddresses raw_addresses{{InterestingAddressId, InterestingChannelAddress}};
  return std::make_shared<ChannelsAddresses>(std::move(raw_addresses));
}

struct TestConfigChangeReceiver : ConfigChangeReceiver {
  using CallbackType = std::function<void(const Config&)>;

  TestConfigChangeReceiver(CallbackType callback)
      : callback_{std::move(callback)} {}

  void OnChange(const Config& config) override { callback_(config); }

  CallbackType callback_;
};

auto MakeEmptyConfig() { return PartitioningConfig{{}}; }

auto MakeConfigWith(const Address& address, const Config& config) {
  // clang-format off
  return PartitioningConfig{
      {
          {
              address,
              config
          }
      }
  };
  // clang-format on
}

auto MakeConfigWithoutInterrestingChannel() {
  return MakeConfigWith(
      Address{RedisName{"some-unrelated-redis"},
              ChannelName{"some-unrelated-channel"}},
      HashingShardingConfig{(1 << 13) - 1}  // just some random number
  );
}

struct TestParam {
  std::optional<Config> expected;
  PartitioningConfig full_config;
};

struct SubscriptionToNotifiersTest : ::testing::TestWithParam<TestParam> {};

auto TestCaseWithEmptyConfig() {
  return TestParam{NoShardingConfig{}, MakeEmptyConfig()};
}

auto TestCaseWithConfigWithoutInterestingChannel() {
  return TestParam{NoShardingConfig{}, MakeConfigWithoutInterrestingChannel()};
}

auto TestCaseWithConfigWithInterestingChannel() {
  const Config config{HashingShardingConfig{666}};
  return TestParam{config, MakeConfigWith(InterestingChannelAddress, config)};
}

auto MakeTestData() {
  return std::array{TestCaseWithEmptyConfig(),
                    TestCaseWithConfigWithInterestingChannel(),
                    TestCaseWithConfigWithoutInterestingChannel()};
}

UTEST_P(SubscriptionToNotifiersTest, Simple) {
  ConfigChangeNotifiers notifiers{MakeAddresses()};
  const AddressId address_id{"address-id"};
  auto notifier = notifiers.GetNotifierFor(address_id);
  std::optional<Config> received_config{std::nullopt};
  TestConfigChangeReceiver receiver{
      [&received_config](const Config& config) { received_config = config; }};
  auto subscription =
      notifiers.GetNotifierFor(address_id)->RegisterReceiver(&receiver);

  notifiers.SetConfig(GetParam().full_config);

  ASSERT_EQ(GetParam().expected, received_config);
}

INSTANTIATE_UTEST_SUITE_P(SubscriptionToNotifiersTest,
                          SubscriptionToNotifiersTest,
                          ::testing::ValuesIn(MakeTestData()));

}  // namespace
