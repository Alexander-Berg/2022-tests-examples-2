#include "channels/positions/listener_test.hpp"

#include <channels/positions/positions_conversion.hpp>

#include <channels/positions/lowlevel.hpp>
#include <channels/positions/traits.hpp>
#include <listeners/client_listener_impl.hpp>
#include <lowlevel/channel_message.hpp>
#include <statistics/client_listener_statistics.hpp>

#include <iostream>

namespace geobus::clients {

using PositionsSpan = utils::Span<types::DriverPosition>;
using Traits = types::DataTypeTraits<types::DriverPosition>;

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceCheckerTooOld) {
  const auto timestamp = ::utils::datetime::Now();
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

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
  std::vector<types::DriverPosition> payload_data;
  payload_data.push_back(CreateDriverPosition(1));
  PositionsSpan payload{payload_data};

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 1);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 2);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 25);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 40);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);

  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 60);
  tester.SendTestMessage(*listener, payload_msg);

  EXPECT_EQ(*listener->GetMissedMessageCount(), 8);
}

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceNotAddOldOnStart) {
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

  PositionsListener::Payload received_payload;
  bool has_received = false;
  const auto timestamp = ::utils::datetime::Now();

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
  payload.push_back(CreateDriverPosition(1));

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      101);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      102);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      125);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      140);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);

  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      160);
  tester.SendTestMessage(*listener, payload_msg);

  EXPECT_EQ(*listener->GetMissedMessageCount(), 8);
}

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceBigGap) {
  const auto timestamp = ::utils::datetime::Now();
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

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
  std::vector<types::DriverPosition> payload_data;
  payload_data.push_back(CreateDriverPosition(1));
  PositionsSpan payload{payload_data};

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 1);
  tester.SendTestMessage(*listener, payload_msg);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      payload, timestamp, clients::CompressionType::kGzip, 0, 1000000);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 999949);
}

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceSmallAndBigGap) {
  const auto timestamp = ::utils::datetime::Now();
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

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
  payload.push_back(CreateDriverPosition(1));

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0, 1);
  tester.SendTestMessage(*listener, payload_msg);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      25);
  tester.SendTestMessage(*listener, payload_msg);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      1000000);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 999948);
}

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceStartNotFromZero) {
  const auto timestamp = ::utils::datetime::Now();
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

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
  payload.push_back(CreateDriverPosition(1));

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, timestamp, clients::CompressionType::kGzip, 0,
      1000000);
  tester.SendTestMessage(*listener, payload_msg);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
}

/// Use PositionListener for this case
TEST_F(PositionsListenerFixture, CheckMessageSequenceMixedOk) {
  // explicitly set this congif
  listeners::DebugOptions::check_messages_ids = true;

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
  payload.push_back(CreateDriverPosition(1));

  // !!! Expect Checker::max_age_threshold = 50 !!!
  // Send it
  auto payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 0);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 2);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 1);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 40);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);
  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 25);
  tester.SendTestMessage(*listener, payload_msg);
  EXPECT_EQ(*listener->GetMissedMessageCount(), 0);

  // Send it
  payload_msg = lowlevel::GenerateFbsChannelMessage(
      PositionsSpan{payload}, ::utils::datetime::Now(),
      clients::CompressionType::kGzip, 0, 60);
  tester.SendTestMessage(*listener, payload_msg);

  EXPECT_EQ(*listener->GetMissedMessageCount(), 8);
}

}  // namespace geobus::clients
