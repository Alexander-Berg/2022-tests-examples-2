#include "channels/positions/listener_test.hpp"

#include <channels/positions/positions_conversion.hpp>

#include <channels/positions/lowlevel.hpp>
#include <channels/positions/traits.hpp>
#include <listeners/client_listener_impl.hpp>
#include <lowlevel/channel_message.hpp>
#include <statistics/client_listener_statistics.hpp>

#include <iostream>

namespace geobus::lowlevel {

bool operator==(const TrackPoint& point1, const TrackPoint& point2);
bool operator!=(const TrackPoint& point1, const TrackPoint& point2);
bool operator==(const Positions& pos1, const Positions& pos2);
}  // namespace geobus::lowlevel

namespace geobus::clients {

using PositionsSpan = utils::Span<types::DriverPosition>;

/////////////////////////////////////////////////////////////////////////
// Tests

// just in case - this is not 'just' example ,this is the real test that is also
// used as snippet/example

//! [GeneratorExample]
TEST_F(PositionsListenerFixture, TestPayload) {
  PositionsListener::Payload received_payload;
  bool has_received = false;

  // Let's create a tester
  PositionsListenerTester tester;
  std::shared_ptr<clients::PositionsListener> listener =
      tester.CreateTestListener(
          [&received_payload, &has_received](
              const std::string&, PositionsListener::Payload&& payload) {
            received_payload = std::move(payload);
            has_received = true;
          });

  // And create some payload. Note that here we call method
  // PositionsGenerator::CreateDriverPosition with some arbitrary salts
  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  // Send it
  tester.SendTestPayload(*listener, payload);

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  TestDriverPositionsArrayAreEqual(
      payload.begin(), payload.end(), received_payload.data.begin(),
      received_payload.data.end(), test::ComparisonPrecision::FbsPrecision);
}
//! [GeneratorExample]

TEST_F(PositionsListenerFixture, TestMessage) {
  PositionsListener::Payload received_payload;
  bool has_received = false;

  // Let's create a tester
  PositionsListenerTester tester;
  std::shared_ptr<clients::PositionsListener> listener =
      tester.CreateTestListener(
          [&received_payload, &has_received](
              const std::string&, PositionsListener::Payload&& payload) {
            received_payload = std::move(payload);
            has_received = true;
          });

  // And create some payload. Note that here we call method
  // PositionsGenerator::CreateDriverPosition with some arbitrary salts
  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  uint32_t host_id = 42;
  uint32_t message_id = 57;
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, host_id, message_id);
  tester.SendTestMessage(*listener, payload_msg);

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  TestDriverPositionsArrayAreEqual(
      payload.begin(), payload.end(), received_payload.data.begin(),
      received_payload.data.end(), test::ComparisonPrecision::FbsPrecision);
}

TEST_F(PositionsListenerFixture, TestStatistics) {
  PositionsListener::Payload received_payload;
  bool has_received = false;

  // Let's create a tester
  PositionsListenerTester tester;
  std::shared_ptr<clients::PositionsListener> listener =
      tester.CreateTestListener(
          [&received_payload, &has_received](
              const std::string&, PositionsListener::Payload&& payload) {
            received_payload = std::move(payload);
            has_received = true;
          });

  // And create some payload. Note that here we call method
  // PositionsGenerator::CreateDriverPosition with some arbitrary salts
  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  uint32_t host_id = 42;
  uint32_t message_id = 57;
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, host_id, message_id);
  tester.SendTestMessage(*listener, payload_msg);

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  const auto& stats = listener->GetStats();
  EXPECT_EQ(1, stats.payload_msg_processed);
  EXPECT_EQ(2, stats.payload_statistics.payload_common_stats.elements_count);
  EXPECT_EQ(2,
            stats.payload_statistics.payload_common_stats.valid_elements_count);
}

TEST_F(PositionsListenerFixture, TestPayloadDeprecated) {
  PositionsListener::Payload received_payload;
  bool has_received = false;

  // Let's create a tester
  PositionsListenerTester tester;
  auto listener = tester.CreateTestListener(
      [&received_payload, &has_received](const std::string&,
                                         PositionsListener::Payload&& payload) {
        received_payload = std::move(payload);
        has_received = true;
      });

  // And create some payload. Note that here we call method
  // PositionsGenerator::CreateDriverPosition with some arbitrary salts
  std::vector<types::DriverPosition> payload;
  payload.push_back(CreateDriverPosition(2));
  payload.push_back(CreateDriverPosition(3));

  // Send it
  tester.SendTestPayload(*listener, payload);

  EXPECT_TRUE(has_received);
  EXPECT_EQ(payload.size(), received_payload.data.size());
  TestDriverPositionsArrayAreEqual(
      payload.begin(), payload.end(), received_payload.data.begin(),
      received_payload.data.end(), test::ComparisonPrecision::FbsPrecision);
}
}  // namespace geobus::clients
