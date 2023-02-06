#include <userver/utest/utest.hpp>

#include <map>
#include <string>

#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/serialize/common_containers.hpp>

#include <common/utils/json.hpp>

namespace {
using JsonBuilder = formats::json::ValueBuilder;
using Json = formats::json::Value;
using Ints = std::vector<int>;
using Strs = std::vector<std::string>;
using StrToInt = std::map<std::string, int>;
using StrToJson = std::map<std::string, Json>;
}  // namespace

TEST(TestMergeJson, OkIfArraysOfTheSameType) {
  using namespace billing_time_events;
  auto a = JsonBuilder{Strs{"a", "b", "c"}}.ExtractValue();
  auto b = JsonBuilder{Strs{"c", "d", "e"}}.ExtractValue();
  auto c = a + b;
  auto expected =
      JsonBuilder{Strs{"a", "b", "c", "c", "d", "e"}}.ExtractValue();
  ASSERT_EQ(c, expected);
}

TEST(TestMergeJson, OkIfArraysOfDifferentTypes) {
  using namespace billing_time_events;
  auto a = JsonBuilder{Strs{"a", "b", "c"}}.ExtractValue();
  auto b = JsonBuilder{Ints{1, 2}}.ExtractValue();
  auto c = a + b;
  auto expected = JsonBuilder{Strs{"a", "b", "c"}};
  expected.PushBack(1);
  expected.PushBack(2);
  ASSERT_EQ(c, expected.ExtractValue());
}

TEST(TestMergeJson, OkIfSimpleObjects) {
  using namespace billing_time_events;
  auto a = JsonBuilder{StrToInt{{"a", 1}}}.ExtractValue();
  auto b = JsonBuilder{StrToInt{{"b", 2}}}.ExtractValue();
  auto c = a + b;
  auto expected = JsonBuilder{StrToInt{{"a", 1}, {"b", 2}}}.ExtractValue();
  ASSERT_EQ(c, expected);
}

TEST(TestMergeJson, MergeNestedObjects) {
  using namespace billing_time_events;
  auto nested_a = JsonBuilder{StrToInt{{"a", 1}}}.ExtractValue();
  auto nested_b = JsonBuilder{StrToInt{{"b", 2}}}.ExtractValue();
  auto a = JsonBuilder{StrToJson{{"c", nested_a}}}.ExtractValue();
  auto b = JsonBuilder{StrToJson{{"c", nested_b}}}.ExtractValue();
  auto c = a + b;
  auto expected_nested =
      JsonBuilder{StrToInt{{"a", 1}, {"b", 2}}}.ExtractValue();
  auto expected = JsonBuilder{StrToJson{{"c", expected_nested}}}.ExtractValue();
  ASSERT_EQ(c, expected);
}

TEST(TestMergeJson, MergeNestedArrays) {
  using namespace billing_time_events;
  auto nested_a = JsonBuilder{StrToInt{{"a", 1}}}.ExtractValue();
  auto nested_b = JsonBuilder{StrToInt{{"b", 2}}}.ExtractValue();
  auto a = JsonBuilder{StrToJson{{"c", nested_a}}}.ExtractValue();
  auto b = JsonBuilder{StrToJson{{"c", nested_b}}}.ExtractValue();
  auto c = a + b;
  auto expected_nested =
      JsonBuilder{StrToInt{{"a", 1}, {"b", 2}}}.ExtractValue();
  auto expected = JsonBuilder{StrToJson{{"c", expected_nested}}}.ExtractValue();
  ASSERT_EQ(c, expected);
}

TEST(TestMergeJson, OtherIfOneEmpty) {
  using namespace billing_time_events;
  auto a = JsonBuilder{StrToInt{{"a", 1}}}.ExtractValue();
  Json b{};
  EXPECT_EQ(a + b, a);
}

TEST(TestMergeJson, EmptyIfBothEmpty) {
  using namespace billing_time_events;
  EXPECT_EQ(Json{} + Json{}, Json{});
}

TEST(TestMergeJson, DieForSimpleTypes) {
  using namespace billing_time_events;

  auto a = JsonBuilder{1}.ExtractValue();
  auto b = JsonBuilder{2}.ExtractValue();
  ASSERT_THROW(a + b, std::invalid_argument);
}
