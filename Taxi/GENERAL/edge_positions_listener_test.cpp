#include "channels/edge_positions/edge_positions_listener_test.hpp"

namespace geobus::clients {

//! [ListenerTesterSnippet]
TEST_F(EdgePositionsListenerFixture, TestPayload) {
  EdgePositionsListenerTester::Payload received_payload;
  bool has_received = false;

  // Create tester
  EdgePositionsListenerTester tester;
  auto listener = tester.CreateTestListener(
      [&received_payload, &has_received](
          const std::string&, EdgePositionsListenerTester::Payload&& payload) {
        received_payload = std::move(payload);
        has_received = true;
      });

  std::vector<types::DriverEdgePosition> payload;
  payload.push_back(CreateValidEdgePosition(2));
  payload.push_back(CreateValidEdgePosition(3));

  // Send message to specified listener
  tester.SendTestPayload(*listener, payload);

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  EXPECT_EQ(payload, received_payload.data);
}
//! [ListenerTesterSnippet]

}  // namespace geobus::clients
