#include <publishers/client_aggregating_publisher_tester.hpp>
#include <publishers/publishers_impl.hpp>

#include <userver/formats/yaml/serialize.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/periodic_task.hpp>

#include <geobus/subscription/partitioning_config.hpp>
#include <userver/storages/redis/mock_client_google.hpp>

using GMockClient = storages::redis::GMockClient;

namespace geobus::publishers {

using RedisName = channels::RedisName;
using ChannelName = channels::ChannelName;
using Address = channels::Address;
using ChannelsAddresses = channels::ChannelsAddresses;
using NoShardingConfig = subscription::NoShardingConfig;

auto MakeMockClient() { return std::make_shared<GMockClient>(); }

subscription::PartitioningConfig MakePartitioningConfig() {
  return subscription::impl::Configs{
      {Address{RedisName{"test-redis"}, ChannelName{"test:channel"}},
       NoShardingConfig{}}};
}

auto MakeStrategies(std::shared_ptr<const ChannelsAddresses> addresses) {
  return std::make_shared<PublishStrategies>(std::move(addresses),
                                             MakePartitioningConfig());
}

auto MakePublishersConfigYaml() {
  auto yaml_data = formats::yaml::FromString(R"yaml(
    channel-types:
        positions-channels:
          - address-id: test-channel
  )yaml");
  return yaml_config::YamlConfig{yaml_data, {}};
}

auto MakeAddressesConfigYaml() {
  auto yaml = formats::yaml::FromString(R"yaml(
    test-channel:
        channel-name: test:channel
        redis-name: test-redis
  )yaml");
  return yaml_config::YamlConfig{yaml, {}};
}

const channels::AddressId test_address_id{"test-channel"};

auto MakeAddresses(const yaml_config::YamlConfig& config) {
  return std::make_shared<const ChannelsAddresses>(config);
}

auto MakePublishersConfig(const ChannelsAddresses& addresses) {
  return PublisherChannelsConfig{
      channels::GetChannelTypesConfig(MakePublishersConfigYaml()), addresses};
}

UTEST(PublishersTest, Publishers) {
  auto addresses = MakeAddresses(MakeAddressesConfigYaml());
  Context context(channels::RedisName{"test-redis"}, MakeMockClient(),
                  MakeStrategies(addresses));
  PublishersImpl publishers_impl{MakePublishersConfig(*addresses), context};

  EXPECT_NO_THROW(
      publishers_impl.GetAggregatingPublisherForChannel<types::DriverPosition>(
          test_address_id));
}

UTEST(PublishersTest, PublishersRunningAfterClear) {
  auto addresses = MakeAddresses(MakeAddressesConfigYaml());
  Context context(channels::RedisName{"test-redis"}, MakeMockClient(),
                  MakeStrategies(addresses));
  PublishersImpl publishers_impl{MakePublishersConfig(*addresses), context};
  EXPECT_EQ(ClientAggregatingPublisherTester::PeriodicTaskOfChannelIsRunning<
                types::DriverPosition>(publishers_impl, test_address_id),
            true);

  publishers_impl.CleanCache();
  EXPECT_EQ(ClientAggregatingPublisherTester::PeriodicTaskOfChannelIsRunning<
                types::DriverPosition>(publishers_impl, test_address_id),
            true);
  ClientAggregatingPublisherTester::StopPeriodicTask<types::DriverPosition>(
      publishers_impl, test_address_id),
      publishers_impl.CleanCache();

  EXPECT_EQ(ClientAggregatingPublisherTester::PeriodicTaskOfChannelIsRunning<
                types::DriverPosition>(publishers_impl, test_address_id),
            false);
}

}  // namespace geobus::publishers
