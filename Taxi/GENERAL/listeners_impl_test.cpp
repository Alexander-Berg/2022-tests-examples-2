#include <listeners/listeners_impl.hpp>

#include <functional>

#include <userver/components/component_config.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/storages/redis/mock_subscribe_client.hpp>

#include <taxi_config/geobus/taxi_config.hpp>
#include "geobus/channels_meta/channels_addresses.hpp"

namespace {

auto CreateAddresses() {
  using namespace std::string_literals;
  auto config_string = R"yaml(
        positions_channel:
            redis-name: test_redis
            channel-name: channel:yagr:positions
        edge_positions_channel:
            redis-name: test_redis
            channel-name: channel:yaga:edge_positions
      )yaml"s;

  auto yaml = formats::yaml::FromString(config_string);
  components::ComponentConfig config{{std::move(yaml), {}}};
  return geobus::channels::ChannelsAddresses{config};
}

const geobus::channels::AddressId positions_address_id{"positions_channel"};
const geobus::channels::AddressId edge_positions_address_id{
    "edge_positions_channel"};

}  // namespace

namespace geobus::listeners {

class GeobusListenersFixture : public ::testing::Test {
 public:
  using RedisPubSubAutoSubscribe = geobus::clients::RedisPubSubAutoSubscribe;
  using PositionsListener = geobus::clients::PositionsListener;
  using EdgePositionsListener = geobus::clients::EdgePositionsListener;
  using ListenerNotFound = geobus::components::ListenerNotFound;
  using SecondChannelListenerRequest =
      geobus::components::SecondChannelListenerRequest;
  struct GeobusListenersData {
    std::unique_ptr<ListenersImpl> listeners;
    std::shared_ptr<storages::redis::MockSubscribeClient> subscribe_client_mock;
  };
  GeobusListenersData CreateGeobusListeners(
      std::string config, bool ignore_uninteresting_calls = true);

  template <typename ListenerType>
  static inline std::function<void(const std::string&,
                                   typename ListenerType::Payload&&)>
  IgnoreCallback() {
    /// Because MacOS has some weird C++ compiler, we can use neither
    /// auto nor deduction guides for std::function
    return std::function<void(const std::string&,
                              typename ListenerType::Payload&&)>{
        [](const std::string&, typename ListenerType::Payload&&) {}};
  };
};

auto GeobusListenersFixture::CreateGeobusListeners(
    std::string config, bool ignore_uninteresting_calls)
    -> GeobusListenersData {
  using namespace std::string_literals;
  auto yaml = formats::yaml::FromString(config);
  ::components::ComponentConfig channels_config{{yaml, {}}};
  std::shared_ptr<storages::redis::MockSubscribeClient> redis_mock;
  if (ignore_uninteresting_calls) {
    redis_mock = std::make_shared<
        ::testing::NiceMock<storages::redis::MockSubscribeClient>>();
  } else {
    redis_mock = std::make_shared<storages::redis::MockSubscribeClient>();
  }
  impl::ContextClients redis_clients;
  redis_clients[channels::RedisName{"test_redis"}] = redis_mock;
  const auto& listeners_config =
      listeners::ParseConfig(channels_config, CreateAddresses());
  const auto listeners_context = listeners::Context(redis_clients);

  return {std::make_unique<ListenersImpl>(listeners_config, listeners_context,
                                          "test-section"),
          redis_mock};
}

UTEST_F_MT(GeobusListenersFixture, ChannelBasicConfig, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
            - address-id: positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  auto& channel_data = data.listeners->GetChannelDataFor<PositionsListener>(
      positions_address_id);
  auto& channel_config = channel_data.GetConfig();

  EXPECT_EQ(channel_config.redis_name, channels::RedisName{"test_redis"});
  EXPECT_EQ(channel_config.address_id, positions_address_id);
  EXPECT_EQ(channel_config.channel_name,
            channels::ChannelName{"channel:yagr:positions"});
}

UTEST_F_MT(GeobusListenersFixture, PositionsChannel, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
            - address-id: positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock,
              Psubscribe("channel:yagr:positions*", _, _))
      .Times(1);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());
}

UTEST_F_MT(GeobusListenersFixture, EdgePositionsChannel, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          edge-positions-channels:
          - address-id: edge_positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock,
              Psubscribe("channel:yaga:edge_positions*", _, _))
      .Times(1);
  auto token =
      data.listeners->CreateSubscriptionForChannel<EdgePositionsListener>(
          edge_positions_address_id,
          IgnoreCallback<clients::EdgePositionsListener>());
}

UTEST_F_MT(GeobusListenersFixture, MissingChannelConfig, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          edge-positions-channels:
            - address-id: edge_positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock, Psubscribe(_, _, _)).Times(0);
  EXPECT_CALL(*data.subscribe_client_mock, Subscribe(_, _, _)).Times(0);
  EXPECT_THROW(
      auto token =
          data.listeners->CreateSubscriptionForChannel<PositionsListener>(
              positions_address_id,
              IgnoreCallback<clients::PositionsListener>()),
      ListenerNotFound);
}

UTEST_F_MT(GeobusListenersFixture, IncorrectChannelType, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          edge-positions-channels:
            - address-id: edge_positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock, Subscribe(_, _, _)).Times(0);
  EXPECT_CALL(*data.subscribe_client_mock, Psubscribe(_, _, _)).Times(0);
  EXPECT_THROW(
      auto token =
          data.listeners->CreateSubscriptionForChannel<PositionsListener>(
              edge_positions_address_id,
              IgnoreCallback<clients::PositionsListener>()),
      ListenerNotFound);
}

UTEST_F_MT(GeobusListenersFixture, SecondAttempt, 2) {
  using namespace std::string_literals;
  using namespace std::string_literals;
  using ::testing::_;
  using ::testing::AtLeast;

  auto config = R"yaml(
        channel-types:
          edge-positions-channels:
            - address-id: edge_positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock,
              Psubscribe("channel:yaga:edge_positions*"s, _, _))
      .Times(AtLeast(1));
  EXPECT_CALL(*data.subscribe_client_mock, Subscribe(_, _, _)).Times(0);
  auto token =
      data.listeners->CreateSubscriptionForChannel<EdgePositionsListener>(
          edge_positions_address_id,
          IgnoreCallback<clients::EdgePositionsListener>());
  EXPECT_THROW(
      (void)data.listeners->CreateSubscriptionForChannel<EdgePositionsListener>(
          edge_positions_address_id,
          IgnoreCallback<clients::EdgePositionsListener>()),
      SecondChannelListenerRequest);
}

UTEST_F_MT(GeobusListenersFixture, NoQueue, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock, Psubscribe(_, _, _)).Times(1);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  EXPECT_EQ(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());
}

UTEST_F_MT(GeobusListenersFixture, WithQueue, 2) {
  using namespace std::string_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            queue:
              enable: true
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  EXPECT_CALL(*data.subscribe_client_mock, Psubscribe(_, _, _)).Times(1);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  EXPECT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());
}

UTEST_F_MT(GeobusListenersFixture, QueueConfig, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            queue:
              enable: true
              enable-tracking: true
              max-task-time: 50
              max-elements-count: 5
              max-tracked-tasks: 2
              max-payload-age: 5
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  const auto& queue_config =
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetConfig()
          .queue_config;
  // Check that settings were parsed correctly from config
  EXPECT_TRUE(queue_config.enabled);
  EXPECT_TRUE(queue_config.enable_tracking);
  EXPECT_EQ(50ms, queue_config.max_task_time);
  EXPECT_EQ(5, queue_config.max_elements_count);
  EXPECT_EQ(2, queue_config.max_tracked_tasks);
  EXPECT_EQ(5s, queue_config.max_payload_age);

  // Check that settings were correctly used in setting up queue

  EXPECT_CALL(*data.subscribe_client_mock, Psubscribe(_, _, _)).Times(1);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());
  const auto& queue = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());

  EXPECT_EQ(50ms, queue.GetMaxTaskTime());
  EXPECT_EQ(5, queue.GetMaxElementsCount());
  EXPECT_EQ(2, queue.GetTasksControl().GetMaxTasksCount());
  EXPECT_EQ(5s, queue.GetMaxPayloadAge());
}

UTEST_F_MT(GeobusListenersFixture, QueueTaxiConfig, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            queue:
              enable: true
              enable-tracking: true
              max-task-time: 50
              max-elements-count: 5
              max-tracked-tasks: 2
              max-payload-age: 5
        )yaml"s;

  auto data = CreateGeobusListeners(config, true);

  // Check that queue was set up by service config
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());
  const auto& queue = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetQueuePtr());

  EXPECT_EQ(50ms, queue.GetMaxTaskTime());
  EXPECT_EQ(5, queue.GetMaxElementsCount());
  EXPECT_TRUE(queue.IsTrackingEnabled());
  EXPECT_EQ(2, queue.GetTasksControl().GetMaxTasksCount());
  EXPECT_EQ(5s, queue.GetMaxPayloadAge());

  // Now, give it taxi_config
  ::taxi_config::geobus::geobus_client::GeobusClient geobus_taxi_config;
  geobus_taxi_config.extra["channel:yagr:positions"].queue =
      taxi_config::geobus::geobus_client::QueueSettings{};
  auto& queue_taxi_config =
      *(geobus_taxi_config.extra["channel:yagr:positions"].queue);
  queue_taxi_config.enable_tracking = false;
  queue_taxi_config.max_task_time = std::chrono::milliseconds{100};
  queue_taxi_config.max_elements_count = 10;
  queue_taxi_config.max_tracked_tasks = 10;
  queue_taxi_config.max_payload_age = std::chrono::seconds{10};

  data.listeners->OnTaxiConfigUpdate(geobus_taxi_config);
  EXPECT_EQ(100ms, queue.GetMaxTaskTime());
  EXPECT_EQ(10, queue.GetMaxElementsCount());
  EXPECT_FALSE(queue.IsTrackingEnabled());
  EXPECT_EQ(10, queue.GetTasksControl().GetMaxTasksCount());
  EXPECT_EQ(10s, queue.GetMaxPayloadAge());

  // Now, unset optional memebrs and check that values are restored
  // to default - default are the one in yaml config
  queue_taxi_config.max_tracked_tasks = std::nullopt;
  queue_taxi_config.max_payload_age = std::nullopt;
  data.listeners->OnTaxiConfigUpdate(geobus_taxi_config);
  EXPECT_EQ(100ms, queue.GetMaxTaskTime());
  EXPECT_EQ(10, queue.GetMaxElementsCount());
  EXPECT_FALSE(queue.IsTrackingEnabled());
  EXPECT_EQ(2, queue.GetTasksControl().GetMaxTasksCount());
  EXPECT_EQ(5s, queue.GetMaxPayloadAge());

  // Now, unset all config
  ::taxi_config::geobus_client::GeobusClient geobus_empty_taxi_config;
  data.listeners->OnTaxiConfigUpdate(geobus_empty_taxi_config);
  // everything should be as in yaml file
  EXPECT_EQ(50ms, queue.GetMaxTaskTime());
  EXPECT_EQ(5, queue.GetMaxElementsCount());
  EXPECT_TRUE(queue.IsTrackingEnabled());
  EXPECT_EQ(2, queue.GetTasksControl().GetMaxTasksCount());
  EXPECT_EQ(5s, queue.GetMaxPayloadAge());
}

UTEST_F_MT(GeobusListenersFixture, TankMissing, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  const auto& tank_config =
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetConfig()
          .tank_config;
  // Check that settings were parsed correctly from config
  EXPECT_FALSE(tank_config.enabled);

  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_EQ(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
}

UTEST_F_MT(GeobusListenersFixture, TankDisabled, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            tank:
              enabled: false
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  const auto& tank_config =
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetConfig()
          .tank_config;
  // Check that settings were parsed correctly from config
  EXPECT_FALSE(tank_config.enabled);

  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_EQ(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
}

UTEST_F_MT(GeobusListenersFixture, TankConfig, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            tank:
              enable: true
              mode: service-config
              firing-interval: 50
              payload-size: 5
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  const auto& tank_config =
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetConfig()
          .tank_config;
  // Check that settings were parsed correctly from config
  EXPECT_TRUE(tank_config.enabled);
  EXPECT_EQ(50ms, tank_config.period);
  EXPECT_EQ(5, tank_config.payload_size);

  // Check that settings were correctly used in setting up queue

  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  const auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());

  EXPECT_TRUE(tank.IsLocalFiringRunning());

  EXPECT_EQ(50ms, tank.GetFiringInterval());
  EXPECT_EQ(5, tank.GetPayloadSize());
}

UTEST_F_MT(GeobusListenersFixture, TankConfigNoAutoSubscribe, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            tank:
              enable: true
              mode: service-config
              firing-interval: 50
              payload-size: 5
        )yaml"s;

  auto data = CreateGeobusListeners(config);

  auto subscription_token =
      data.listeners->CreateSubscriptionForChannel<PositionsListener>(
          positions_address_id, IgnoreCallback<clients::PositionsListener>(),
          RedisPubSubAutoSubscribe::kNo);

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  const auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());

  // Without auto_subscribe == kYes, tank should not be firing
  EXPECT_FALSE(tank.IsLocalFiringRunning());

  subscription_token.Subscribe();

  // Now, it should be firing
  EXPECT_TRUE(tank.IsLocalFiringRunning());
}

UTEST_F_MT(GeobusListenersFixture, TankTaxiConfigNoEffect, 2) {
  // Check that taxi config doesn't affect tanks that are running
  // in service config modes
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  namespace ged = taxi_config::geobus_embeded_tank;
  using ::testing::_;

  auto config = R"yaml(
        channel-types:
          positions-channels:
          - address-id: positions_channel
            tank:
              tank-section-name: test-section
              enable: true
              mode: service-config
              firing-interval: 50
              payload-size: 5
        )yaml"s;

  auto data = CreateGeobusListeners(config);
  const auto& tank_config =
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetConfig()
          .tank_config;

  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  const auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  EXPECT_TRUE(tank.IsLocalFiringRunning());

  // Now, we pass it taxi-config object
  ged::ServiceTanks service_tanks;
  ged::Tank tank_taxi_config;
  tank_taxi_config.payload_per_sec = 100;
  tank_taxi_config.messages_per_sec = 10;
  tank_taxi_config.drivers_count = 100;
  service_tanks.extra["positions_channel"] = tank_taxi_config;

  taxi_config::geobus_embeded_tank::GeobusEmbededTank geobus_config;
  geobus_config.extra["test-section"] = service_tanks;
  data.listeners->OnTaxiConfigUpdate(geobus_config);

  // and check that settings from taxi-config object were NOT
  // used
  EXPECT_EQ(50ms, tank_config.period);
  EXPECT_EQ(5, tank_config.payload_size);
  EXPECT_TRUE(tank.IsLocalFiringRunning());
}

UTEST_F_MT(GeobusListenersFixture, TankTaxiConfig, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;
  namespace ged = taxi_config::geobus_embeded_tank;

  auto config = R"yaml(
        tank-section-name: test-section
        channel-types:
          positions-channels:
          - address-id: positions_channel
            tank:
              enable: true
              mode: taxi-config
              firing-interval: 50
              payload-size: 5
              drivers_count: 10
        )yaml"s;

  ged::ServiceTanks service_tanks;
  ged::Tank tank_config;
  tank_config.payload_per_sec = 100;
  tank_config.messages_per_sec = 10;
  tank_config.drivers_count = 1017;
  service_tanks.extra["channel:yagr:positions"] = tank_config;

  taxi_config::geobus_embeded_tank::GeobusEmbededTank geobus_config;
  geobus_config.extra["test-section"] = service_tanks;

  auto data = CreateGeobusListeners(config);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  data.listeners->OnTaxiConfigUpdate(geobus_config);
  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  const auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  // Check that settings were parsed correctly from config
  EXPECT_TRUE(tank.IsLocalFiringRunning());
  EXPECT_EQ(100ms, tank.GetFiringInterval());
  EXPECT_EQ(10, tank.GetPayloadSize());
  EXPECT_EQ(1017, tank.GetRandomPayloadGenerator().GetDriversCount());
}

UTEST_F_MT(GeobusListenersFixture, TankTaxiNoConfig, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;
  namespace ged = taxi_config::geobus_embeded_tank;

  auto config = R"yaml(
        tank-section-name: test-section
        channel-types:
          positions-channels:
            - address-id: positions_channel
              tank:
                enable: true
                mode: taxi-config
                firing-interval: 50
                payload-size: 5
        )yaml"s;

  ged::ServiceTanks service_tanks;
  ged::Tank tank_config;
  tank_config.payload_per_sec = 100;
  tank_config.messages_per_sec = 10;
  tank_config.drivers_count = 100;

  service_tanks.extra["no_such_channel"] = tank_config;

  taxi_config::geobus_embeded_tank::GeobusEmbededTank geobus_config;
  geobus_config.extra["test-section"] = service_tanks;

  auto data = CreateGeobusListeners(config);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());

  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  // First, we start tank - to make sure that when section is absent,
  // the tank is actually stopped
  tank.StartLocalFiring();

  EXPECT_TRUE(tank.IsLocalFiringRunning());

  // Now, after config is parsed, tank should be disabled
  data.listeners->OnTaxiConfigUpdate(geobus_config);
  // Check that settings were parsed correctly from config
  EXPECT_FALSE(tank.IsLocalFiringRunning());
}

UTEST_F_MT(GeobusListenersFixture, TankTaxiNoSection, 2) {
  using namespace std::string_literals;
  using namespace std::literals::chrono_literals;
  using ::testing::_;
  namespace ged = taxi_config::geobus_embeded_tank;

  auto config = R"yaml(
      tank-section-name: test-section
      channel-types:
        positions-channels:
        - address-id: positions_channel
          tank:
            enable: true
            mode: taxi-config
            firing-interval: 50
            payload-size: 5
      )yaml"s;

  ged::ServiceTanks service_tanks;
  ged::Tank tank_config;
  tank_config.payload_per_sec = 100;
  tank_config.messages_per_sec = 10;
  tank_config.drivers_count = 100;
  service_tanks.extra["no_such_channel"] = tank_config;

  taxi_config::geobus_embeded_tank::GeobusEmbededTank geobus_config;
  geobus_config.extra["wrong-section"] = service_tanks;

  auto data = CreateGeobusListeners(config);
  auto token = data.listeners->CreateSubscriptionForChannel<PositionsListener>(
      positions_address_id, IgnoreCallback<clients::PositionsListener>());
  ASSERT_NE(
      nullptr,
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  auto& tank = *(
      data.listeners->GetChannelDataFor<PositionsListener>(positions_address_id)
          .GetTankPtr());
  // First, we start tank - to make sure that when section is absent,
  // the tank is actually stopped
  tank.StartLocalFiring();

  data.listeners->OnTaxiConfigUpdate(geobus_config);
  // Check that settings were parsed correctly from config
  EXPECT_FALSE(tank.IsLocalFiringRunning());
}

}  // namespace geobus::listeners
