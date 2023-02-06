#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "utils/json_repack.hpp"

namespace utils::json {

const auto kEmptyObject =
    formats::json::ValueBuilder{formats::json::Type::kObject}.ExtractValue();

TEST(JsonRepack, Basic) {
  formats::json::ValueBuilder source;
  source["id"] = "hexhexhex";
  source["apns"]["title"] = "Apns Title";
  source["apns"]["message"] = "Apns Message";
  source["apns"]["numeric"] = 10.9991;
  source["apns"]["boolean"] = true;
  source["apns"]["null"] = formats::json::Value{};

  formats::json::ValueBuilder templat;
  templat["id"] = "$id";
  templat["payload"]["title"] = "$apns/title";
  templat["payload"]["numeric"] = "$apns/numeric";
  templat["payload"]["boolean"] = "$apns/boolean";
  templat["payload"]["null"] = "$apns/null";
  templat["payload"]["not_exists"] = "$not_exists";
  templat["payload"]["escaped"] = "$$escaped";
  templat["payload"]["items"].PushBack("string const");
  templat["payload"]["items"].PushBack(12321);
  templat["payload"]["items"].PushBack(0.9999991);
  templat["payload"]["items"].PushBack(true);
  templat["payload"]["items"].PushBack(formats::json::Value{});
  templat["payload"]["items"].PushBack("$apns/message");
  templat["data"]["a"]["b"]["c"]["d"] = "$apns/numeric";

  formats::json::ValueBuilder expected_;
  expected_["id"] = "hexhexhex";
  expected_["payload"]["numeric"] = 10.9991;
  expected_["payload"]["boolean"] = true;
  expected_["payload"]["null"] = formats::json::Value{};
  expected_["payload"]["title"] = "Apns Title";
  expected_["payload"]["not_exists"] = formats::json::Value{};
  expected_["payload"]["escaped"] = "$escaped";
  expected_["payload"]["items"].PushBack("string const");
  expected_["payload"]["items"].PushBack(12321);
  expected_["payload"]["items"].PushBack(0.9999991);
  expected_["payload"]["items"].PushBack(true);
  expected_["payload"]["items"].PushBack(formats::json::Value{});
  expected_["payload"]["items"].PushBack("Apns Message");
  expected_["data"]["a"]["b"]["c"]["d"] = 10.9991;

  const auto& expected = expected_.ExtractValue();
  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), source.ExtractValue());

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, TimestampGenerator) {
  formats::json::ValueBuilder templat;
  templat["payload"]["ts"] = "#timestamp";

  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), formats::json::Value{});

  ASSERT_NO_THROW(actual["payload"]["ts"].As<size_t>());
}

TEST(JsonRepack, StringifyGenerator) {
  formats::json::ValueBuilder source;
  source["payload"]["id"] = "hexhexhex";

  formats::json::ValueBuilder stringify_recursive_object;
  stringify_recursive_object["#stringify"]["id"] = "$payload/id";

  formats::json::ValueBuilder obj;
  obj["#stringify"]["id"] = "$payload/id";

  formats::json::ValueBuilder stringify_recursive_array;
  stringify_recursive_array.PushBack(obj.ExtractValue());

  formats::json::ValueBuilder object_in_array;
  object_in_array["test"]["me"] = "value";

  formats::json::ValueBuilder array;
  array.PushBack("1");
  array.PushBack(2);
  array.PushBack(object_in_array.ExtractValue());

  formats::json::ValueBuilder object;
  object["push_id"] = "$payload/id";

  formats::json::ValueBuilder templat;
  templat["string"]["#stringify"] = "just_string";
  templat["int"]["#stringify"] = 10;
  templat["float"]["#stringify"] = 10.2;
  templat["zero"]["#stringify"] = 0.0;
  templat["true"]["#stringify"] = true;
  templat["false"]["#stringify"] = false;
  templat["null"]["#stringify"] = formats::json::Value{};
  templat["object"]["#stringify"] = object.ExtractValue();
  templat["array"]["#stringify"] = array.ExtractValue();
  templat["recursive_object"]["#stringify"] =
      stringify_recursive_object.ExtractValue();
  templat["recursive_array"]["#stringify"] =
      stringify_recursive_array.ExtractValue();

  formats::json::ValueBuilder expected_;
  expected_["string"] = "\"just_string\"";
  expected_["int"] = "10";
  expected_["float"] = "10.2";
  expected_["zero"] = "0.0";
  expected_["true"] = "true";
  expected_["false"] = "false";
  expected_["null"] = "null";
  expected_["object"] = "{\"push_id\":\"hexhexhex\"}";
  expected_["array"] = "[\"1\",2,{\"test\":{\"me\":\"value\"}}]";
  expected_["recursive_object"] = "\"{\\\"id\\\":\\\"hexhexhex\\\"}\"";
  expected_["recursive_array"] = "[\"{\\\"id\\\":\\\"hexhexhex\\\"}\"]";
  const auto& expected = expected_.ExtractValue();

  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), source.ExtractValue());

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, ConcatGenerator) {
  formats::json::ValueBuilder source;
  source["payload"]["id"] = "hexhexhex";

  formats::json::ValueBuilder array;
  array.PushBack("just_string");
  array.PushBack("$payload/id");
  array.PushBack(0);
  array.PushBack(123);
  array.PushBack(0.0);
  array.PushBack(1.23);
  array.PushBack(true);
  array.PushBack(false);
  array.PushBack(formats::json::Value{});

  formats::json::ValueBuilder concatObj;
  concatObj["#concat"] = array.ExtractValue();

  formats::json::ValueBuilder templat;
  templat["concatenated_value"] = concatObj.ExtractValue();

  formats::json::ValueBuilder expected_;
  expected_["concatenated_value"] =
      "just_string"
      "hexhexhex"
      "0"
      "123"
      "0.0"
      "1.23"
      "true"
      "false"
      "null";
  const auto& expected = expected_.ExtractValue();

  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), source.ExtractValue());

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, GeneratorsEscapedAndMissing) {
  formats::json::ValueBuilder templat;
  templat["payload"]["ts_not_exists"] = "#timestamp_not_exists";
  templat["payload"]["ts_escapted"] = "##timestamp";
  templat["payload"]["##escaped_key"] = "value";

  formats::json::ValueBuilder expected_;
  expected_["payload"]["ts_not_exists"] = formats::json::Value{};
  expected_["payload"]["ts_escapted"] = "#timestamp";
  expected_["payload"]["#escaped_key"] = "value";

  const auto& expected = expected_.ExtractValue();
  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), formats::json::Value{});

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, Null) {
  const auto expected = formats::json::Value{};
  const auto& actual =
      utils::json::Repack(formats::json::Value{}, formats::json::Value{});

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, EmptyObject) {
  const auto expected = kEmptyObject;
  const auto& actual = utils::json::Repack(kEmptyObject, kEmptyObject);

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

TEST(JsonRepack, TopLevelArray) {
  formats::json::ValueBuilder templat;
  templat.PushBack("test");

  formats::json::ValueBuilder expected_;
  expected_.PushBack("test");

  const auto expected = expected_.ExtractValue();
  const auto& actual =
      utils::json::Repack(templat.ExtractValue(), formats::json::Value{});

  EXPECT_EQ(expected, actual)
      << "Expected: " << formats::json::ToString(expected) << std::endl
      << "Actual:   " << formats::json::ToString(actual);
}

}  // namespace utils::json
