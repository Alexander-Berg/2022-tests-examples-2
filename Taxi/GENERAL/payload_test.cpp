#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "payload.hpp"

namespace ucommunications {

namespace {

formats::json::Value MakeArray(
    const std::initializer_list<std::string>& values) {
  formats::json::ValueBuilder arr(formats::json::Type::kArray);
  for (const auto& value : values) arr.PushBack(value);
  return arr.ExtractValue();
}

}  // namespace

TEST(PayloadTest, CreateNewBulkId) {
  formats::json::ValueBuilder data;
  data["payload"]["event"] = "test";
  data["repack"]["fcm"]["repack_payload"] = MakeArray({"event", "nofield"});
  data["repack"]["apns"]["repack_payload"] = MakeArray({"event", "id"});

  std::string bulk_id = "9f6a949a74234ba69e51d5b006cb67de";
  const auto& actual = models::user::notification::EnsureDataContainsBulkId(
      data.ExtractValue(), bulk_id);

  formats::json::ValueBuilder expected;
  expected["payload"]["id"] = bulk_id;
  expected["payload"]["event"] = "test";
  expected["repack"]["fcm"]["repack_payload"] =
      MakeArray({"event", "nofield", "id"});
  expected["repack"]["apns"]["repack_payload"] = MakeArray({"event", "id"});

  EXPECT_EQ(expected.ExtractValue(), actual);
}

TEST(PayloadTest, UseExistingBulkId) {
  formats::json::ValueBuilder data_builder;
  data_builder["payload"]["id"] = "hexhexhex";
  data_builder["payload"]["event"] = "test";
  data_builder["repack"]["fcm"]["repack_payload"] =
      MakeArray({"event", "nofield"});
  data_builder["repack"]["apns"]["repack_payload"] = MakeArray({"event", "id"});
  const auto& data = data_builder.ExtractValue();

  std::string bulk_id = models::user::notification::GetBulkId(data);
  const auto& actual =
      models::user::notification::EnsureDataContainsBulkId(data, bulk_id);

  formats::json::ValueBuilder expected;
  expected["payload"]["id"] = "hexhexhex";
  expected["payload"]["event"] = "test";
  expected["repack"]["fcm"]["repack_payload"] =
      MakeArray({"event", "nofield", "id"});
  expected["repack"]["apns"]["repack_payload"] = MakeArray({"event", "id"});

  EXPECT_EQ(bulk_id, "hexhexhex");
  EXPECT_EQ(expected.ExtractValue(), actual);
}

TEST(PayloadTest, NoRepack) {
  formats::json::ValueBuilder data;
  data["payload"]["event"] = "test";

  std::string bulk_id = "9f6a949a74234ba69e51d5b006cb67de";
  const auto& actual = models::user::notification::EnsureDataContainsBulkId(
      data.ExtractValue(), bulk_id);

  formats::json::ValueBuilder expected;
  expected["payload"]["id"] = bulk_id;
  expected["payload"]["event"] = "test";

  EXPECT_EQ(expected.ExtractValue(), actual);
}

TEST(PayloadTest, MalformedPayloadIgnored) {
  formats::json::ValueBuilder data;
  data["payload"] = MakeArray({"payload", "must", "be", "object"});

  std::string bulk_id = "9f6a949a74234ba69e51d5b006cb67de";
  const auto& actual = models::user::notification::EnsureDataContainsBulkId(
      data.ExtractValue(), bulk_id);

  formats::json::ValueBuilder expected;
  expected["payload"] = MakeArray({"payload", "must", "be", "object"});

  EXPECT_EQ(expected.ExtractValue(), actual);
}

TEST(PayloadTest, MalformedRepackIgnored) {
  formats::json::ValueBuilder data;
  data["payload"]["event"] = "test";
  data["repack"] = MakeArray({"repack", "must", "be", "object"});

  std::string bulk_id = "9f6a949a74234ba69e51d5b006cb67de";
  const auto& actual = models::user::notification::EnsureDataContainsBulkId(
      data.ExtractValue(), bulk_id);

  formats::json::ValueBuilder expected;
  expected["payload"]["id"] = bulk_id;
  expected["payload"]["event"] = "test";
  expected["repack"] = MakeArray({"repack", "must", "be", "object"});

  EXPECT_EQ(expected.ExtractValue(), actual);
}

}  // namespace ucommunications
