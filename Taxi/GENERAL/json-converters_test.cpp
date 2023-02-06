#include <gtest/gtest.h>

#include <userver/formats/bson/inline.hpp>
#include <userver/formats/bson/serialize.hpp>
#include <userver/formats/bson/value_builder.hpp>
#include <userver/formats/json/inline.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/datetime.hpp>

#include <json-converters/json-converters.hpp>

using formats::bson::MakeArray;
using formats::bson::MakeDoc;

namespace bson = formats::bson;
namespace json = formats::json;

namespace {

using time_point = std::chrono::system_clock::time_point;

double TimePointToSeconds(const time_point value) {
  using double_seconds = std::chrono::duration<double>;
  return std::chrono::duration_cast<double_seconds>(value.time_since_epoch())
      .count();
}

std::string TimePointToDefaultFormatString(const time_point value) {
  return utils::datetime::Timestring(value);
}

}  // namespace

TEST(BsonToJson, SpecialCases) {
  ASSERT_EQ(json::Value{}, json_converters::BsonToJson(bson::Value{}));
  ASSERT_EQ(json::ValueBuilder(formats::json::Type::kObject).ExtractValue(),
            json_converters::BsonToJson(MakeDoc()));
  ASSERT_EQ(json::ValueBuilder(formats::json::Type::kArray).ExtractValue(),
            json_converters::BsonToJson(MakeArray()));
}

TEST(BsonToJson, BasicTypes) {
  bson::ValueBuilder bson;
  bson["int_t"] = 1;
  bson["float_t"] = 33.33333;
  bson["string_t"] = "I'm a string\"";
  bson["null_t"] = bson::Value{};
  bson["time_t"] = std::chrono::system_clock::from_time_t(0);
  bson["bool_t"] = true;
  bson["oid_t"] = bson::Oid("507f191e810c19729de860ea");

  json::ValueBuilder json;
  json["int_t"] = 1;
  json["float_t"] = 33.33333;
  json["string_t"] = "I'm a string\"";
  json["null_t"] = json::Value{};
  json["time_t"] =
      TimePointToSeconds(std::chrono::system_clock::from_time_t(0));
  json["bool_t"] = true;
  json["oid_t"] = "507f191e810c19729de860ea";

  const auto& expected_json = json.ExtractValue();
  const auto& actual_json = json_converters::BsonToJson(bson.ExtractValue());

  ASSERT_EQ(expected_json, actual_json)
      << "Expected: " << formats::json::ToString(expected_json)
      << "\nActual:   " << formats::json::ToString(actual_json);
}

TEST(BsonToJson, DateType) {
  // Since BSON Date type keeps only milliseconds, higher resolution timestamps
  // get truncated, so for simplicity we will test milliseconds as input here.
  const auto moment = std::chrono::system_clock::time_point(
      std::chrono::milliseconds(1234567891));

  const auto bson = MakeDoc("time_t", moment);

  {
    const auto actual_json = json_converters::BsonToJson(bson);
    const auto expected_json =
        formats::json::MakeObject("time_t", TimePointToSeconds(moment));

    ASSERT_EQ(expected_json, actual_json)
        << "Expected: " << formats::json::ToString(expected_json)
        << "\nActual:   " << formats::json::ToString(actual_json);
  }

  {
    const auto conversion_options = json_converters::BsonToJsonOptions{
        json_converters::BsonToJsonDateConversion::kToDefaultFormatString,
    };
    const auto actual_json =
        json_converters::BsonToJson(bson, conversion_options);
    const auto expected_json = formats::json::MakeObject(
        "time_t", TimePointToDefaultFormatString(moment));

    ASSERT_EQ(expected_json, actual_json)
        << "Expected: " << formats::json::ToString(expected_json)
        << "\nActual:   " << formats::json::ToString(actual_json);
  }
}

TEST(BsonToJson, ComplexTypes) {
  bson::ValueBuilder bson;
  bson["array_t"] = MakeArray(1, "str", false);
  bson["object_t"] = MakeDoc("subfield", "Here it goes", "more_subfield",
                             MakeDoc("subfield_of_subobj", 3456));

  json::ValueBuilder json;
  json::ValueBuilder arr;
  arr.PushBack(1);
  arr.PushBack("str");
  arr.PushBack(false);
  json["array_t"] = arr.ExtractValue();
  json::ValueBuilder obj;
  obj["subfield"] = "Here it goes";
  obj["more_subfield"]["subfield_of_subobj"] = 3456;
  json["object_t"] = obj.ExtractValue();

  const auto& expected_json = json.ExtractValue();
  const auto& actual_json = json_converters::BsonToJson(bson.ExtractValue());

  ASSERT_EQ(expected_json, actual_json)
      << "Expected: " << formats::json::ToString(expected_json)
      << "\nActual:   " << formats::json::ToString(actual_json);
}

TEST(JsonToBson, SpecialCases) {
  ASSERT_EQ(bson::Value{}, json_converters::JsonToBson(json::Value{}));
  ASSERT_EQ(bson::ValueBuilder(formats::bson::ValueBuilder::Type::kObject)
                .ExtractValue(),
            json_converters::JsonToBson(
                formats::json::ValueBuilder(formats::json::Type::kObject)
                    .ExtractValue()));
  ASSERT_EQ(bson::ValueBuilder(formats::bson::ValueBuilder::Type::kArray)
                .ExtractValue(),
            json_converters::JsonToBson(
                formats::json::ValueBuilder(formats::json::Type::kArray)
                    .ExtractValue()));
}

TEST(JsonToBson, BasicTypes) {
  auto tp = std::chrono::system_clock::time_point(
      std::chrono::microseconds(1234567890));
  json::ValueBuilder json;
  json["int_t"] = 1;
  json["float_t"] = 33.33333;
  json["string_t"] = "I'm a string\"";
  json["null_t"] = json::Value{};
  json["time_t"] = TimePointToSeconds(tp);
  json["bool_t"] = true;
  json["oid_t"] = "507f191e810c19729de860ea";

  bson::ValueBuilder bson;
  bson["int_t"] = 1;
  bson["float_t"] = 33.33333;
  bson["string_t"] = "I'm a string\"";
  bson["null_t"] = bson::Value{};
  bson["time_t"] = TimePointToSeconds(tp);
  bson["bool_t"] = true;
  bson["oid_t"] = "507f191e810c19729de860ea";

  const auto& expected_bson = bson.ExtractValue();
  const auto& actual_bson = json_converters::JsonToBson(json.ExtractValue());

  ASSERT_EQ(expected_bson, actual_bson)
      << "Expected: " << formats::bson::ToCanonicalJsonString(expected_bson)
      << "\nActual:   " << formats::bson::ToCanonicalJsonString(actual_bson);
}

TEST(JsonToBson, ComplexTypes) {
  formats::json::ValueBuilder json_array;
  json_array.PushBack(1);
  json_array.PushBack("str");
  json_array.PushBack(false);

  formats::json::ValueBuilder json_object;
  json_object["subfield"] = "Here it goes";
  json_object["more_subfield"]["subfield_of_subobj"] = 3456;

  json::ValueBuilder json;
  json["array_t"] = json_array.ExtractValue();
  json["object_t"] = json_object.ExtractValue();

  bson::ValueBuilder bson;
  bson["array_t"] = MakeArray(1, "str", false);
  bson["object_t"] = MakeDoc("subfield", "Here it goes", "more_subfield",
                             MakeDoc("subfield_of_subobj", 3456));

  const auto& expected_bson = bson.ExtractValue();
  const auto& actual_bson = json_converters::JsonToBson(json.ExtractValue());

  ASSERT_EQ(expected_bson, actual_bson)
      << "Expected: " << formats::bson::ToCanonicalJsonString(expected_bson)
      << "\nActual:   " << formats::bson::ToCanonicalJsonString(actual_bson);
}
