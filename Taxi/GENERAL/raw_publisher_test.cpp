#include <publishers/raw_publisher.hpp>

#include <channels/positions/traits.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <geobus/generators/payload_generator.hpp>
#include <userver/storages/redis/mock_client_google.hpp>
#include <userver/utest/utest.hpp>

namespace {

auto MakeMockClient() {
  return std::make_shared<storages::redis::GMockClient>();
}

}  // namespace

namespace geobus::clients {

UTEST(RawPublisher, Publish) {
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;
  using ::testing::_;

  generators::PayloadGenerator<generators::PositionsGenerator>
      payload_generator;
  auto redis_mock = MakeMockClient();
  auto channel_name = std::string{"test-channel"};
  EXPECT_CALL(*redis_mock, Publish(channel_name, _, _, _)).Times(1);

  std::shared_ptr<RawPublisher> raw_publisher(
      std::make_shared<RawPublisher>(redis_mock));

  auto payload = payload_generator.GeneratePayload(5, 5);

  raw_publisher->Publish(payload.data, channel_name);
}

UTEST(RawPublisher, PublishEmpty) {
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;
  using ::testing::_;

  auto redis_mock = MakeMockClient();
  auto channel_name = std::string{"test-channel"};
  EXPECT_CALL(*redis_mock, Publish(channel_name, _, _, _)).Times(0);

  std::shared_ptr<RawPublisher> raw_publisher(
      std::make_shared<RawPublisher>(redis_mock));

  utils::Span<types::DriverPosition> empty_span;

  raw_publisher->Publish(empty_span, channel_name);

  const auto stats = raw_publisher->GetStats();
  EXPECT_EQ(1, stats["invalid-messages"].As<int>());
}

UTEST(RawPublisher, Stats) {
  using RawPublisher = geobus::clients::RawPublisher<types::DriverPosition>;
  using ::testing::_;

  generators::PayloadGenerator<generators::PositionsGenerator>
      payload_generator;
  auto redis_mock = MakeMockClient();
  auto channel_name = std::string{"test-channel"};
  EXPECT_CALL(*redis_mock, Publish(channel_name, _, _, _)).Times(1);

  std::shared_ptr<RawPublisher> raw_publisher(
      std::make_shared<RawPublisher>(redis_mock));

  auto payload = payload_generator.GeneratePayload(5, 5);

  raw_publisher->Publish(payload.data, channel_name);

  const auto stats = raw_publisher->GetStats();
  EXPECT_EQ(1, stats["published-messages"].As<int>());
  EXPECT_EQ(5, stats["published-positions"].As<int>());
}

}  // namespace geobus::clients
