#include <google/protobuf/util/message_differencer.h>

#include <envoy/service/cluster/v3/cds_client.usrv.pb.hpp>
#include <envoy/service/endpoint/v3/eds_client.usrv.pb.hpp>
#include <envoy/service/route/v3/rds_client.usrv.pb.hpp>
#include <exa/models/discovery_request_id.hpp>
#include <exa/models/discovery_response.hpp>

#include <userver/dump/common_containers.hpp>
#include <userver/dump/test_helpers.hpp>
#include <userver/rcu/rcu_map.hpp>
#include <userver/utest/utest.hpp>

namespace envoy::service::discovery::v3 {

static bool operator==(const DiscoveryResponse& x, const DiscoveryResponse& y) {
  return google::protobuf::util::MessageDifferencer::Equals(x, y);
}

}  // namespace envoy::service::discovery::v3

namespace exa {
namespace {

const std::string kClusterUrl =
    "type.googleapis.com/envoy.config.cluster.v3.Cluster";

auto MakeTestDiscoveryResponse(std::string suffix = {}) {
  models::DiscoveryResponse response_base;
  response_base.set_version_info("{'meta':1,'something': 'bla'}" + suffix);

  // Making a response that holds 2 responses
  auto response = response_base;
  auto* resource = response.add_resources();
  resource->PackFrom(response_base);

  resource = response.add_resources();
  resource->PackFrom(response_base);

  return response;
}

TEST(Serialization, DiscoveryRequestId) {
  models::DiscoveryRequestId request{
      {"a long long key with \r\n\b\a special symbols", "short key"},
      kClusterUrl,
  };

  dump::TestWriteReadCycle(request);
}

TEST(Serialization, DiscoveryResponse) {
  auto response = MakeTestDiscoveryResponse();
  dump::TestWriteReadCycle(response);
}

TEST(Serialization, Map) {
  using MapData =
      std::unordered_map<models::DiscoveryRequestId, models::DiscoveryResponse>;

  MapData map;

  models::DiscoveryRequestId request1{
      {"a long long key with \r\n\b\a special symbols", "short key", "key2"},
      kClusterUrl + "42",
  };

  auto request2 = request1;
  map[std::move(request1)] = MakeTestDiscoveryResponse();

  request2.resources.push_back("new key");
  request2.type_url += "foo";
  map[std::move(request2)] = MakeTestDiscoveryResponse("second");

  dump::TestWriteReadCycle(map);
}

TEST(Serialization, MapSharedPtr) {
  using MapData =
      std::unordered_map<models::DiscoveryRequestId,
                         std::shared_ptr<models::DiscoveryResponse>>;

  MapData map;

  const models::DiscoveryRequestId request{
      {"some key", "key2"},
      kClusterUrl,
  };

  const auto response = MakeTestDiscoveryResponse();
  map[request] = std::make_shared<models::DiscoveryResponse>(response);

  const auto map_from_dump = dump::FromBinary<MapData>(dump::ToBinary(map));

  ASSERT_EQ(map.size(), map_from_dump.size());
  EXPECT_EQ(request, map_from_dump.begin()->first);
  EXPECT_EQ(response, *map_from_dump.begin()->second);
}

}  // namespace
}  // namespace exa
