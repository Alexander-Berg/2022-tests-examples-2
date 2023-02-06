#include <geobus/channels/positions/listener.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <geobus/clients/listener_tank.hpp>
#include "channels/positions/listener_test.hpp"

#include <userver/utils/mock_now.hpp>

#include <userver/engine/condition_variable.hpp>
#include <userver/engine/single_consumer_event.hpp>
#include <userver/engine/sleep.hpp>

namespace geobus::clients {

class GeobusTankTest : public testing::Test,
                       public generators::PositionsGenerator {};

TEST_F(GeobusTankTest, Forward) {
  RunInCoro(
      []() {
        using Payload = PositionsListener::Payload;
        Payload received_payload;
        bool has_received = false;
        engine::SingleConsumerEvent resume_notification;

        ListenerTank<PositionsListener> tank(
            [&received_payload, &has_received, &resume_notification](
                const std::string&, Payload&& payload) {
              received_payload = std::move(payload);
              has_received = true;
              resume_notification.Send();
            },
            "test_channel");

        // We are not going to start this tank, so there is no need to
        // set it up correctly
        Payload payload;
        payload.data.push_back(CreateDriverPosition(2));
        payload.data.push_back(CreateDriverPosition(3));

        // forwarding must work even with disabled tank
        EXPECT_FALSE(tank.IsEnabled());
        tank.ForwardPayload("test_channel", Payload{payload});
        EXPECT_TRUE(resume_notification.WaitForEvent());
        EXPECT_TRUE(has_received);
        EXPECT_EQ(payload.data.size(), received_payload.data.size());
      },
      2);
}

TEST_F(GeobusTankTest, LocalGeneration) {
  RunInCoro(
      []() {
        using namespace std::chrono_literals;
        using Payload = PositionsListener::Payload;
        Payload received_payload;
        bool has_received = false;
        engine::SingleConsumerEvent resume_notification;

        ListenerTank<PositionsListener> tank(
            [&received_payload, &has_received, &resume_notification](
                const std::string&, Payload&& payload) {
              received_payload = std::move(payload);
              has_received = true;
              resume_notification.Send();
            },
            "test_channel");

        tank.SetFiringInterval(1ms);
        tank.SetPayloadSize(5);
        tank.Enable();
        tank.StartLocalFiring();

        ASSERT_TRUE(tank.IsEnabled());
        EXPECT_TRUE(
            resume_notification.WaitForEventFor(std::chrono::seconds{1}));
        EXPECT_TRUE(has_received);
        EXPECT_EQ(5, received_payload.data.size());
        EXPECT_TRUE(tank.IsLocalFiringRunning());
      },
      2);
}

}  // namespace geobus::clients
