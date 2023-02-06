#pragma once

#include <flatbuffers/flatbuffers.h>

#include <geobus/channels/positions/plugin_test.hpp>
#include <geobus/generators/payload_generator.hpp>
#include <lowlevel/channel_message.hpp>
#include <statistics/client_listener_statistics.hpp>
#include <test/data_type_test_traits.hpp>
#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace geobus::lowlevel {

template <typename HighLevelType>
class FlatbuffersSerializationTest : public ::testing::Test {
 protected:
  using TypeTraits = test::DataTypeTestTraits<HighLevelType>;
  using Payload = typename TypeTraits::Payload;
  using Elements = typename TypeTraits::Elements;
  using ParseStats =
      statistics::PayloadStatistics<typename TypeTraits::ParseInvalidStats>;
  using PayloadGenerator =
      generators::PayloadGenerator<typename TypeTraits::Generator>;

  PayloadGenerator generator;
};

TYPED_TEST_SUITE_P(FlatbuffersSerializationTest);

TYPED_TEST_P(FlatbuffersSerializationTest, TestValidPayload) {
  using TypeTraits = test::DataTypeTestTraits<TypeParam>;
  using Payload = typename TypeTraits::Payload;
  using Elements = typename TypeTraits::Elements;
  using ParseStats =
      statistics::PayloadStatistics<typename TypeTraits::ParseInvalidStats>;
  Payload payload = this->generator.GeneratePayload(12 /*seed*/, 100 /*count*/);
  Elements reference_data = payload.data;

  // Serialize payload. Those methods only test 'data' part of payload
  std::string fb_data = TypeTraits::SerializeMessage(payload.data);

  // Now, parse it back
  ParseStats parse_stats;
  auto unpacked_data = TypeTraits::DeserializeMessage(fb_data, parse_stats);

  TypeTraits::TestElementsAreEqual(reference_data.begin(), reference_data.end(),
                                   unpacked_data.begin(), unpacked_data.end(),
                                   test::ComparisonPrecision::FbsPrecision);
}

TYPED_TEST_P(FlatbuffersSerializationTest, TestValidMessage) {
  using TypeTraits = test::DataTypeTestTraits<TypeParam>;
  using Payload = typename TypeTraits::Payload;
  using Elements = typename TypeTraits::Elements;
  using PayloadSpan = utils::Span<TypeParam>;
  using ClientStats = statistics::ClientListenerStatistics<
      typename TypeTraits::ParseInvalidStats>;
  Payload payload = this->generator.GeneratePayload(12 /*seed*/, 100 /*count*/);
  Elements reference_data = payload.data;

  std::string fb_data = lowlevel::GenerateFbsChannelMessage(
      PayloadSpan{payload.data}, ::utils::datetime::Now(),
      ::geobus::clients::CompressionType::kGzip, 42, 53);

  // Now, parse it back
  ClientStats parse_stats;
  auto unpacked_data = lowlevel::ParseFbsChannelMessage<TypeParam, ClientStats>(
      fb_data, parse_stats);

  TypeTraits::TestElementsAreEqual(
      reference_data.begin(), reference_data.end(), unpacked_data.data.begin(),
      unpacked_data.data.end(), test::ComparisonPrecision::FbsPrecision);
}

// TODO(TAXIGRAPH-2845) enable testback!
TYPED_TEST_P(FlatbuffersSerializationTest, DISABLED_TestInvalidMessage) {
  using TypeTraits = test::DataTypeTestTraits<TypeParam>;
  using ClientStats = statistics::ClientListenerStatistics<
      typename TypeTraits::ParseInvalidStats>;

  std::string data = "NOT_FLATBUFFER_STRING";
  std::string fb_data = lowlevel::GenerateFbsChannelMessage(
      data, ::utils::datetime::Now(), ::geobus::clients::CompressionType::kGzip,
      42, 53, geobus::fbs::Protocol_Legacy);

  // Now, parse it back
  ClientStats parse_stats;
  auto unpacked_data = lowlevel::ParseFbsChannelMessage<TypeParam, ClientStats>(
      fb_data, parse_stats);

  ASSERT_EQ(1, parse_stats.channel_msg_parse_errors);
}

TYPED_TEST_P(FlatbuffersSerializationTest, DISABLED_TestValidPayloadFuzzy) {
  using TypeTraits = test::DataTypeTestTraits<TypeParam>;
  using Payload = typename TypeTraits::Payload;
  using Elements = typename TypeTraits::Elements;
  using ParseStats =
      statistics::PayloadStatistics<typename TypeTraits::ParseInvalidStats>;
  for (size_t coeff = 1; coeff <= 100; ++coeff) {
    ::utils::datetime::MockNowSet(::utils::datetime::Now());
    Payload payload = this->generator.GeneratePayload(coeff * coeff /*seed*/,
                                                      100 * coeff /*count*/);
    Elements reference_data = payload.data;

    // Serialize payload. Those methods only test 'data' part of payload
    std::string fb_data = TypeTraits::SerializeMessage(payload.data);

    // Now, parse it back
    ParseStats parse_stats;
    auto unpacked_data = TypeTraits::DeserializeMessage(fb_data, parse_stats);

    TypeTraits::TestElementsAreEqual(
        reference_data.begin(), reference_data.end(), unpacked_data.begin(),
        unpacked_data.end(), test::ComparisonPrecision::FbsPrecision);
  }
}

REGISTER_TYPED_TEST_SUITE_P(FlatbuffersSerializationTest, TestValidPayload,
                            DISABLED_TestValidPayloadFuzzy, TestValidMessage,
                            DISABLED_TestInvalidMessage);

}  // namespace geobus::lowlevel
