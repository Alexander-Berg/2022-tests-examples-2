#include <geobus/channels_meta/channels_addresses.hpp>
#include <geobus/channels_meta/types.hpp>

#include <listeners/context.hpp>

namespace storages::redis {
class SubscribeClient;
}

namespace geobus::test {

/// Create ChannelsAddresses object with two test channels - edge_positions
/// and positions
channels::ChannelsAddresses MakeTestChannelsAddresses();

/// Create context. Channels are same as in MakeTestChannelAddresses
listeners::Context MakeTestListenersContext(
    std::shared_ptr<storages::redis::SubscribeClient> client);

}  // namespace geobus::test
