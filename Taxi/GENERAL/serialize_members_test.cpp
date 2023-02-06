#include <serialization/serialize_members.hpp>
#include <userver/formats/json/serialize_container.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/formats/yaml/value.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace test {

// We also check that everything is working across multiple namespaces
namespace definition {

struct ComplicatedType {
  double value{0.0};
};

struct CombinedType {
  double another_value{0.0};
  ComplicatedType complication;
  std::optional<int> optional_value{std::nullopt};
};

struct DerivedType : public CombinedType {
  double derived_value{0.0};
};

constexpr const char kComplication[] = "complication";
constexpr const char kAnotherValue[] = "another_value";
constexpr const char kOptionalValue[] = "optional_value";
constexpr const char kDerivedValue[] = "derived_value";

// It should work this way - defining MemberSerialization before
// any Serialize() members
using TestSerializationHelper = serialization::MembersSerialization<
    serialization::NamedMember<&CombinedType::another_value, kAnotherValue>,
    serialization::NamedMember<&CombinedType::complication, kComplication>,
    serialization::NamedMember<&CombinedType::optional_value, kOptionalValue> >;

// This one must be in the same namespace as ComplicatedType
template <typename ValueType>
inline ValueType Serialize(const ComplicatedType& obj,
                           formats::serialize::To<ValueType>) {
  using ValueBuilder = typename ValueType::Builder;
  return ValueBuilder(obj.value).ExtractValue();
}

/// Support any incoming source
template <typename ValueType>
inline ComplicatedType Parse(const ValueType& source,
                             formats::parse::To<ComplicatedType>) {
  return ComplicatedType{source.template As<double>()};
}

/// Support any incoming source
template <typename ValueType>
inline CombinedType Parse(const ValueType& source,
                          formats::parse::To<CombinedType>) {
  return TestSerializationHelper::ParseObjectFrom<CombinedType>(source);
}

template <typename ValueType>
inline ValueType Serialize(const CombinedType& obj,
                           formats::serialize::To<ValueType>) {
  return TestSerializationHelper::SerializeObjectTo<CombinedType, ValueType>(
      obj);
}

using TestDerivedHelper = serialization::MembersAndSingleBaseSerialization<
    CombinedType,
    serialization::NamedMember<&DerivedType::derived_value, kDerivedValue> >;

template <typename ValueType>
inline ValueType Serialize(const DerivedType& obj,
                           formats::serialize::To<ValueType>) {
  return TestDerivedHelper::SerializeObjectTo<DerivedType, ValueType>(obj);
}

/// Support any incoming source
template <typename ValueType>
inline DerivedType Parse(const ValueType& source,
                         formats::parse::To<DerivedType>) {
  return TestDerivedHelper::ParseObjectFrom<DerivedType>(source);
}

}  // namespace definition

/// Let's try calling it from different namespace
namespace execution {

TEST(SerializeMembers, Serialization) {
  definition::CombinedType obj{5.0, {10.0}};
  auto json_object = formats::json::ValueBuilder(obj).ExtractValue();
  EXPECT_TRUE(json_object.HasMember(definition::kComplication));
  EXPECT_TRUE(json_object.HasMember(definition::kAnotherValue));
  EXPECT_EQ(json_object[definition::kAnotherValue].As<double>(), 5.0);
  EXPECT_EQ(json_object[definition::kComplication].As<double>(), 10.0);
}

TEST(SerializeMembers, SerializationCycle) {
  definition::CombinedType obj{5.0, {10.0}};
  auto json_object = formats::json::ValueBuilder(obj).ExtractValue();
  definition::CombinedType test_obj =
      json_object.As<definition::CombinedType>();

  EXPECT_EQ(obj.another_value, test_obj.another_value);
  EXPECT_EQ(obj.complication.value, test_obj.complication.value);
  EXPECT_EQ(obj.optional_value, test_obj.optional_value);
}

TEST(SerializeMembers, Parse) {
  auto json_object = formats::json::FromString(
      R"json({"complication" : 10, "another_value" : 5})json");
  auto test_value = json_object.As<definition::CombinedType>();
  EXPECT_EQ(test_value.another_value, 5.0);
  EXPECT_EQ(test_value.complication.value, 10.0);
}

TEST(SerializeMembers, Parse2) {
  auto json_object = formats::json::FromString(
      R"json({"complication" : 10, "another_value" : 5, "optional_value": 10})json");
  auto test_value = json_object.As<definition::CombinedType>();
  EXPECT_EQ(test_value.another_value, 5.0);
  EXPECT_EQ(test_value.complication.value, 10.0);
}

TEST(SerializeMembers, ParseMissingThrows) {
  auto json_object = formats::json::FromString(
      R"json({"complication" : 10, "optional_value": 10})json");
  EXPECT_ANY_THROW(json_object.As<definition::CombinedType>());
}

TEST(SerializeMembers, ParseYaml) {
  auto yaml_object = formats::yaml::FromString(
      R"yaml(
    complication : 10.0
    another_value : 5.0
    )yaml");
  auto test_value = yaml_object.As<definition::CombinedType>();
  EXPECT_EQ(test_value.another_value, 5.0);
  EXPECT_EQ(test_value.complication.value, 10.0);
}

TEST(SerializeMembersAndBase, Serialization) {
  definition::DerivedType obj{{5.0, {10.0}, {std::nullopt}}, 20.0};
  auto json_object = formats::json::ValueBuilder(obj).ExtractValue();
  EXPECT_TRUE(json_object.HasMember(definition::kComplication));
  EXPECT_TRUE(json_object.HasMember(definition::kAnotherValue));
  EXPECT_TRUE(json_object.HasMember(definition::kDerivedValue));
  EXPECT_EQ(json_object[definition::kAnotherValue].As<double>(), 5.0);
  EXPECT_EQ(json_object[definition::kComplication].As<double>(), 10.0);
  EXPECT_EQ(json_object[definition::kDerivedValue].As<double>(), 20.0);
}

TEST(SerializeMembersAndBase, Parse) {
  auto json_object = formats::json::FromString(
      R"json({"complication" : 10, "another_value" : 5, "derived_value" : 20.0})json");
  auto test_value = json_object.As<definition::DerivedType>();
  EXPECT_EQ(test_value.another_value, 5.0);
  EXPECT_EQ(test_value.complication.value, 10.0);
  EXPECT_EQ(test_value.derived_value, 20.0);
}

}  // namespace execution

}  // namespace test
