#include "message.hpp"

#include <gtest/gtest.h>
#include <utils/helpers/json.hpp>

using models::driver::notification::Message;

void TestSerialization(const Json::Value& payload) {
  Message message;
  message.id = "id";
  message.request_id = "request_id";
  message.drivers = {models::DriverId::FromDbidUuid("dbid1_uuid1"),
                     models::DriverId::FromDbidUuid("dbid2_uuid2")};
  message.code = 123;
  message.action = "abc";
  message.collapse_key = "collapse_key";
  message.payload = payload;

  Message deserialized;
  deserialized.Deserialize(message.Serialize());

  const std::string& diagnostics =
      "\n    Original payload (type=" + std::to_string(message.payload.type()) +
      "): " + utils::helpers::WriteStyledJson(message.payload) +
      "\n    Deserialized payload (type=" +
      std::to_string(deserialized.payload.type()) +
      "): " + utils::helpers::WriteStyledJson(deserialized.payload);

  EXPECT_EQ(message.id, deserialized.id) << diagnostics;
  EXPECT_EQ(message.request_id, deserialized.request_id) << diagnostics;
  EXPECT_EQ(message.drivers, deserialized.drivers) << diagnostics;
  EXPECT_EQ(message.action, deserialized.action) << diagnostics;
  EXPECT_EQ(message.code, deserialized.code) << diagnostics;
  EXPECT_EQ(message.collapse_key, deserialized.collapse_key) << diagnostics;
  EXPECT_EQ(message.payload, deserialized.payload) << diagnostics;
}

TEST(Message, Serialization) {
  TestSerialization(utils::helpers::CreateJsonObject({
      {"text", "message here"},
      {"silent", true},
      {"array", utils::helpers::CreateJsonArray({100, "test", true, false})},
      {"ttl", 10},
  }));
  TestSerialization(
      utils::helpers::CreateJsonArray({100, "test", true, false}));
  TestSerialization(Json::Value(Json::ValueType::objectValue));
  TestSerialization(Json::Value(Json::ValueType::arrayValue));
  TestSerialization(Json::Value(Json::ValueType::nullValue));
  TestSerialization(Json::Value(10.24));
  TestSerialization(Json::Value(1024));
  TestSerialization(Json::Value("some string value"));
  TestSerialization(Json::Value(true));
  TestSerialization(Json::Value(false));
}
