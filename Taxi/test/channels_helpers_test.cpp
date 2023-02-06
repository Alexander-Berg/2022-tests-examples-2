#include "channels_helpers.hpp"

#include <userver/formats/yaml/serialize.hpp>
#include <userver/yaml_config/yaml_config.hpp>

#include <listeners/context.hpp>

namespace geobus::test {

channels::ChannelsAddresses MakeTestChannelsAddresses() {
  formats::yaml::Value channel_addresses_yaml = formats::yaml::FromString(
      R"yaml(
            edge_positions:
                channel-name: channel:yaga:edge_positions
                redis-name: taxi-test
            positions:
                channel-name: channel:yagr:position
                redis-name: taxi-test
                )yaml");
  return channels::ChannelsAddresses(
      yaml_config::YamlConfig{channel_addresses_yaml, {}});
}

listeners::Context MakeTestListenersContext(
    std::shared_ptr<storages::redis::SubscribeClient> client) {
  return listeners::Context{
      channels::impl::MakeClients<storages::redis::SubscribeClient>(
          channels::RedisName{"taxi-test"}, std::move(client))};
}

}  // namespace geobus::test
