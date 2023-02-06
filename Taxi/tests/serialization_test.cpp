#include <gtest/gtest.h>

#include <common/include/exception.h>
#include <common/include/serialization.h>

namespace maps::rate_limiter2::tests {

TEST(SerializationTest, ParseEmptyCountersMessage) {
  CountersMessage empty_msg{};
  const auto& data = SerializeCountersMessage(empty_msg);
  EXPECT_EQ(data.size(), 12u);  // min fb object size
  const auto& parsed_msg = ParseCountersMessage(data);
  EXPECT_EQ(parsed_msg.counters, empty_msg.counters);
  EXPECT_EQ(parsed_msg.limitsVersion, empty_msg.limitsVersion);
  EXPECT_EQ(parsed_msg.lamport, empty_msg.lamport);
}

TEST(SerializationTest, ParseCountersMessage) {
  {
    CountersMessage msg;
    msg.counters = {
        {"resource 1", {{"client1", 1}, {"client2", 2}}},
        {"resource 2", {{"client3", 42}}},
        {"resource 3", {}},
    };
    msg.limitsVersion = 42;
    const auto& data = SerializeCountersMessage(msg);
    const auto& parsed_msg = ParseCountersMessage(data);
    EXPECT_EQ(parsed_msg.counters, msg.counters);
    EXPECT_EQ(parsed_msg.limitsVersion, msg.limitsVersion);
    EXPECT_EQ(parsed_msg.lamport, msg.lamport);
  }
  {
    CountersMessage msg;
    msg.counters = {
        {"resource1", {{"client1", 1}}},
        {"resource2", {{"client1", 153}, {"client2", 2}}},
        {"resource3", {{"client1", 11}, {"client33", 33}, {"client153", 37}}},
    };
    const auto& data = SerializeCountersMessage(msg);
    const auto& parsed_msg = ParseCountersMessage(data);
    EXPECT_EQ(msg.counters, parsed_msg.counters);
  }

  EXPECT_THROW(ParseCountersMessage("invalid data"), RuntimeError);
}

// limits serialization tests

TEST(Serialization, ParseLimitsRegistry) {
  const auto& data = SerializeLimitsRegistry(
      {{
           {
               "super.client.1",
               {
                   {"", LimitInfo{50000, 1000, 1}},
               },
           },
           {
               "client.2",
               {
                   {"resource.1", LimitInfo{1000, 1000, 1 * 60 * 60}},
                   {"resource.2", LimitInfo{300, 300, 24 * 60 * 60}},
               },
           },
           {
               "client.3",
               {
                   {"resource.2", LimitInfo{500, 500, 1}},
               },
           },
           {
               "",
               {
                   {"resource.3", LimitInfo{100, 500, 1}},
               },
           },
       },
       153});
  const auto& registry = ParseLimitsRegistry(data);
  LimitsRegistry::Storage expected = {
      {"super.client.1", {{"", LimitInfo(50000, 1000, 1)}}},
      {"client.2",
       {{"resource.1", LimitInfo(1000, 1000, 1 * 60 * 60)},
        {"resource.2", LimitInfo(300, 300, 24 * 60 * 60)}}},
      {"", {{"resource.3", LimitInfo(100, 500, 1)}}},
      {"client.3", {{"resource.2", LimitInfo(500, 500, 1)}}}};

  EXPECT_EQ(registry.storage(), expected);
  EXPECT_EQ(registry.version(), 153);

  EXPECT_THROW(ParseLimitsRegistry("invalid data"), RuntimeError);
}

}  // namespace maps::rate_limiter2::tests
