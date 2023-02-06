#include <gtest/gtest.h>

#include <ml/common/datetime.hpp>
#include <ml/common/json.hpp>
#include <ml/example/objects.hpp>

#include <userver/utils/datetime.hpp>

TEST(Dummy, from_json_string) {
  auto obj = ml::common::FromJsonString<ml::example::Dummy>("{\"i\": 54}");
  ASSERT_EQ(obj.i, 54);
}

template <class T, class U>
void CheckTypesEqual() {
  auto cond = std::is_same<T, U>::value;
  ASSERT_TRUE(cond);
}

TEST(DefaultRequired, types) {
  CheckTypesEqual<decltype(ml::example::DefaultRequired::required_no_default),
                  std::string>();
  CheckTypesEqual<decltype(ml::example::DefaultRequired::optional_no_default),
                  std::optional<std::string>>();
  CheckTypesEqual<decltype(ml::example::DefaultRequired::optional_default),
                  std::string>();
}

TEST(DefaultRequiredVector, types) {
  using BaseType = std::vector<int64_t>;
  CheckTypesEqual<decltype(
                      ml::example::DefaultRequiredVector::required_no_default),
                  BaseType>();
  CheckTypesEqual<decltype(
                      ml::example::DefaultRequiredVector::optional_no_default),
                  std::optional<BaseType>>();
  CheckTypesEqual<decltype(
                      ml::example::DefaultRequiredVector::optional_default),
                  BaseType>();
}

TEST(TimePoint, types) {
  CheckTypesEqual<decltype(ml::example::TimePoint::field),
                  ml::common::TimePoint>();
  CheckTypesEqual<decltype(ml::example::TimePoint::arr),
                  std::vector<ml::common::TimePoint>>();
}

TEST(TimePoint, conversion) {
  auto tp =
      utils::datetime::FromRfc3339StringSaturating("1970-01-01T03:00:00+03:00");
  auto ts = ml::common::datetime::Timestamp(tp);
  ASSERT_EQ(ts, 0);
}

TEST(TimePoint, json_load) {
  std::string json_str =
      "{\"field\": \"1970-01-01T03:00:00+03:00\",\"arr\": []}";
  auto obj = ml::common::FromJsonString<ml::example::TimePoint>(json_str);
  auto ts = ml::common::datetime::Timestamp(obj.field);
  ASSERT_EQ(ts, 0);
  auto str = ml::common::ToJsonString(obj);
  ASSERT_EQ(str, "{\"field\":\"1970-01-01T00:00:00+00:00\",\"arr\":[]}");
}

TEST(GeoPoint, types) {
  CheckTypesEqual<decltype(ml::example::GeoPointExample::point),
                  ml::common::GeoPoint>();
  CheckTypesEqual<decltype(ml::example::GeoPointExample::optional_point),
                  std::optional<ml::common::GeoPoint>>();
  CheckTypesEqual<decltype(ml::example::GeoPointExample::point_vector),
                  std::vector<ml::common::GeoPoint>>();
}

TEST(GeoPoint, json_load) {
  std::string json_str =
      "{\"point\": {\"lon\": 33, \"lat\": 55},\"point_vector\": []}";
  auto obj = ml::common::FromJsonString<ml::example::GeoPointExample>(json_str);
  ASSERT_EQ(obj.point.lon, 33);
}

TEST(Aliase, types) {
  CheckTypesEqual<decltype(ml::example::AliasExample::ref),
                  ml::example::Dummy>();
}

TEST(DuckAssign, content) {
  std::string time_point_json =
      "{\"field\": \"1970-01-01T03:00:00+03:00\",\"arr\": "
      "[\"1970-01-01T03:00:00+03:00\"]}";
  std::string geopoint_example_json =
      "{\"point\": {\"lon\": 33, \"lat\": 55},\"point_vector\": [{\"lon\": 34, "
      "\"lat\": 51}, {\"lon\": 31, \"lat\": 59}]}";

  using namespace ml::common;
  using namespace ml::example;

  ExampleObject example_object = {"sample_string", 42, 42.0, true, 25};
  auto time_point = FromJsonString<ml::example::TimePoint>(time_point_json);
  auto geopoint_example =
      FromJsonString<GeoPointExample>(geopoint_example_json);
  ComplexObjectExample complex_object = {example_object, time_point,
                                         geopoint_example};
  ComplexObjectExample complex_object_copy{complex_object};

  ExampleObjectV2 example_object_v2 = {"sample_string", 42, 42.0, true, 25};
  auto time_point_v2 = FromJsonString<TimePointV2>(time_point_json);
  auto geopoint_example_v2 =
      FromJsonString<GeoPointExampleV2>(geopoint_example_json);
  ComplexObjectExampleV2 complex_object_v2 = {example_object_v2, time_point_v2,
                                              geopoint_example_v2};
  ComplexObjectExampleV2 complex_object_v2_copy{complex_object_v2};

  ComplexObjectExampleV2 complex_object_v2_from_origin{};
  DuckAssign(complex_object, complex_object_v2_from_origin);
  ASSERT_EQ(complex_object_v2_from_origin, complex_object_v2);
  ASSERT_EQ(complex_object, complex_object_copy);

  DuckAssign(std::move(complex_object_copy), complex_object_v2_from_origin);
  ASSERT_EQ(complex_object_v2_from_origin, complex_object_v2);
  ASSERT_FALSE(complex_object == complex_object_copy);

  ComplexObjectExample complex_object_origin_from_v2{};
  DuckAssign(complex_object_v2, complex_object_origin_from_v2);
  ASSERT_EQ(complex_object_origin_from_v2, complex_object);
  ASSERT_EQ(complex_object_v2, complex_object_v2_copy);

  DuckAssign(std::move(complex_object_v2_copy), complex_object_origin_from_v2);
  ASSERT_EQ(complex_object_origin_from_v2, complex_object);
  ASSERT_FALSE(complex_object_v2 == complex_object_v2_copy);
}

TEST(ExampleUnorderedMap, serialize_to_json) {
  std::string json_str = "{\"key_value_collection\":{\"key2\":20,\"key1\":10}}";
  auto obj =
      ml::common::FromJsonString<ml::example::ExampleUnorderedMap>(json_str);
  ASSERT_EQ(obj.key_value_collection["key2"], 20);
}

TEST(ExampleUnorderedMap, parse_json) {
  ml::example::ExampleUnorderedMap obj;
  obj.key_value_collection["key1"] = 10;
  obj.key_value_collection["key2"] = 20;
  auto str = ml::common::ToJsonString(obj);
  ASSERT_EQ(str, "{\"key_value_collection\":{\"key2\":20,\"key1\":10}}");
}

TEST(ExampleUnorderedMap, serialize_parse) {
  ml::example::ExampleUnorderedMap obj{{{"key1", 10}, {"key2", 20}}};
  auto value = ml::example::Serialize(
      obj, ::formats::serialize::To<::formats::json::Value>());
  auto parsed_obj = ml::example::Parse(
      value, formats::parse::To<ml::example::ExampleUnorderedMap>());
  ASSERT_EQ(obj, parsed_obj);
}

TEST(ExampleUnorderedSet, serialize_to_json) {
  std::string json_str = "{\"setitems\": [10, 20, 30, 40, 50]}";
  auto obj =
      ml::common::FromJsonString<ml::example::ExampleUnorderedSet>(json_str);
  ASSERT_NE(obj.setitems.find(30), obj.setitems.end());
}

TEST(ExampleUnorderedSet, parse_json) {
  ml::example::ExampleUnorderedSet obj{std::unordered_set<int64_t>{1, 2, 3}};
  auto str = ml::common::ToJsonString(obj);
  ASSERT_EQ(str, "{\"setitems\":[3,2,1]}");
}

TEST(ExampleUnorderedSet, serialize_parse) {
  ml::example::ExampleUnorderedSet obj{std::unordered_set<int64_t>{1, 2, 3}};
  auto value = ml::example::Serialize(
      obj, ::formats::serialize::To<::formats::json::Value>());
  auto parsed_obj = ml::example::Parse(
      value, formats::parse::To<ml::example::ExampleUnorderedSet>());
  ASSERT_EQ(obj, parsed_obj);
}
