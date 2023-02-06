#include <channels_meta/config.hpp>
#include <publishers/channel_config.hpp>

#include <userver/formats/yaml/serialize.hpp>
#include <userver/formats/yaml/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <geobus/channels/positions/publisher.hpp>
#include <geobus/channels_meta/channels_addresses.hpp>
#include "userver/yaml_config/yaml_config.hpp"

namespace {

using ChannelsAddresses = geobus::channels::ChannelsAddresses;
using Config =
    geobus::channels::Config<geobus::publishers::PublisherChannelConfig,
                             geobus::types::DriverPosition>;

auto PublishersConfigStr() {
  using namespace std::string_literals;
  return R"yaml(
          positions-channels:
            - address-id: positions-channel
              max-message-size: 73
              max-publish-delay: 112ms
         )yaml"s;
}

auto AddressesConfigStr() {
  using namespace std::string_literals;
  return R"yaml(
          positions-channel:
            channel-name: channel-name
            redis-name: redis-name
         )yaml"s;
}

auto AddressesConfig() {
  return yaml_config::YamlConfig{
      formats::yaml::FromString(AddressesConfigStr()), {}};
}

auto PublishersConfig() {
  return yaml_config::YamlConfig{
      formats::yaml::FromString(PublishersConfigStr()), {}};
}

Config CreateChannelsConfig() {
  const ChannelsAddresses addresses{AddressesConfig()};
  return {PublishersConfig(), addresses};
}

TEST(GeobusPublishersConfig, TestParse) {
  const Config config{CreateChannelsConfig()};

  using namespace std::string_literals;

  const auto& channels = config.Get<geobus::types::DriverPosition>().channels;
  ASSERT_EQ(channels.size(), 1u);
  const auto& channel = channels.front();
  ASSERT_EQ(channel.address_id,
            geobus::channels::AddressId{"positions-channel"s});
  ASSERT_EQ(channel.channel_name,
            geobus::channels::ChannelName{"channel-name"s});
  ASSERT_EQ(channel.redis_name, geobus::channels::RedisName{"redis-name"s});
  ASSERT_EQ(73, channel.max_message_size);
  ASSERT_EQ(std::chrono::milliseconds{112}, channel.max_publish_delay);
}

TEST(GeobusPublishersConfig, TestGetRedisNames) {
  const Config config{CreateChannelsConfig()};

  using namespace std::string_literals;

  const auto redis_names = GetRedisNames(config);
  ASSERT_EQ(redis_names,
            std::vector{geobus::channels::RedisName{"redis-name"s}});
}

}  // namespace
