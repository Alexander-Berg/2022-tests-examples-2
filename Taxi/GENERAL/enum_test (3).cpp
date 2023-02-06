#include <serialization/enum.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

/// Test that everything works across namespaces
namespace test {

namespace definitions {

enum class ScopedEnum { Value1 = 20, Value2 = 10, ValueWithoutAName };

enum UnscopedEnum { Value1 = 17, Value2 = 19, ValueWithoutAName };

static const char kValue1[] = "value_1";
static const char kValue2[] = "value_2";

using ScopedEnumHelper = serialization::EnumSerialization<
    serialization::EnumRecord<ScopedEnum::Value1, kValue1>,
    serialization::EnumRecord<ScopedEnum::Value2, kValue2> >;

using UnscopedEnumHelper = serialization::EnumSerialization<
    serialization::EnumRecord<UnscopedEnum::Value1, kValue1>,
    serialization::EnumRecord<UnscopedEnum::Value2, kValue2> >;

ScopedEnum Parse(const formats::json::Value& source,
                 formats::parse::To<ScopedEnum>) {
  return ScopedEnumHelper::ParseEnumFrom<ScopedEnum, formats::json::Value>(
      source);
}

UnscopedEnum Parse(const formats::json::Value& source,
                   formats::parse::To<UnscopedEnum>) {
  return UnscopedEnumHelper::ParseEnumFrom<UnscopedEnum, formats::json::Value>(
      source);
}

formats::json::Value Serialize(ScopedEnum value,
                               formats::serialize::To<formats::json::Value>) {
  return ScopedEnumHelper::SerializeEnumToJson(value);
}

formats::json::Value Serialize(UnscopedEnum value,
                               formats::serialize::To<formats::json::Value>) {
  return UnscopedEnumHelper::SerializeEnumToJson(value);
}

}  // namespace definitions

// Invoke them in different namespace
namespace execution {

TEST(EnumSerialization, ScopedSerialization) {
  auto json_object =
      formats::json::ValueBuilder(definitions::ScopedEnum::Value1)
          .ExtractValue();
  EXPECT_EQ(definitions::kValue1, json_object.As<std::string>());
}

TEST(EnumSerialization, ScopedParse) {
  auto json_object =
      formats::json::ValueBuilder(definitions::kValue2).ExtractValue();
  EXPECT_EQ(definitions::ScopedEnum::Value2,
            json_object.As<definitions::ScopedEnum>());
}

TEST(EnumSerialization, ScopedSerializationMissing) {
  EXPECT_ANY_THROW(
      formats::json::ValueBuilder(definitions::ScopedEnum::ValueWithoutAName)
          .ExtractValue());
}

TEST(EnumSerialization, UnscopedSerialization) {
  auto json_object =
      formats::json::ValueBuilder(definitions::Value1).ExtractValue();
  EXPECT_EQ(definitions::kValue1, json_object.As<std::string>());
}

TEST(EnumSerialization, UnscopedParse) {
  auto json_object =
      formats::json::ValueBuilder(definitions::kValue2).ExtractValue();
  EXPECT_EQ(definitions::Value2, json_object.As<definitions::UnscopedEnum>());
}

TEST(EnumSerialization, UnscopedSerializationMissing) {
  EXPECT_ANY_THROW(formats::json::ValueBuilder(definitions::ValueWithoutAName)
                       .ExtractValue());
}

}  // namespace execution

}  // namespace test
