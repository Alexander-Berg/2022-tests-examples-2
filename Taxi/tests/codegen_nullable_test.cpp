#include <defs/api/openapi-30.hpp>
#include <defs/internal/sample-model.hpp>
#include <userver/formats/json/serialize.hpp>

#include <userver/utest/utest.hpp>

TEST(CodegenNullable, ParseNullString) {
  constexpr const char* kNullDoc = R"~({"nullable_string":null})~";
  const auto json = formats::json::FromString(kNullDoc);
  const auto obj = json.As<handlers::NullableField>();

  EXPECT_EQ(std::nullopt, obj.nullable_string);
}

TEST(CodegenNullable, ParseNonNullString) {
  constexpr const char* kNonNullDoc = R"~({"nullable_string":"string"})~";

  const auto json = formats::json::FromString(kNonNullDoc);
  const auto obj = json.As<handlers::NullableField>();

  ASSERT_TRUE(!!obj.nullable_string);
  EXPECT_EQ("string", *obj.nullable_string);
}

TEST(CodegenNullable, ParseNullStringEnum) {
  constexpr const char* kNullDoc = R"~({"nullable_str_enum":null})~";
  const auto json = formats::json::FromString(kNullDoc);
  const auto obj = json.As<handlers::NullableFieldStringEnum>();

  EXPECT_EQ(std::nullopt, obj.nullable_str_enum);
}

TEST(CodegenNullable, ParseNonNullStringEnum) {
  constexpr const char* kNonNullDoc = R"~({"nullable_str_enum":"aaa"})~";

  const auto json = formats::json::FromString(kNonNullDoc);
  const auto obj = json.As<handlers::NullableFieldStringEnum>();

  ASSERT_TRUE(!!obj.nullable_str_enum);
  EXPECT_EQ(handlers::NullableFieldStringEnumNullablestrenum::kAaa,
            *obj.nullable_str_enum);
}

TEST(CodegenNullable, ParseNonNullInteger) {
  constexpr const char* kNonNullDoc = R"~({"nullable_int":12})~";

  const auto json = formats::json::FromString(kNonNullDoc);
  const auto obj = json.As<handlers::NullableFieldInt>();

  ASSERT_TRUE(!!obj.nullable_int);
  EXPECT_EQ(12, *obj.nullable_int);
}

TEST(CodegenNullable, ParseNullArray) {
  constexpr const char* kNullDoc = R"~({"nullable_array": null})~";

  const auto json = formats::json::FromString(kNullDoc);
  const auto obj = json.As<handlers::NullableFieldArray>();

  ASSERT_TRUE(!obj.nullable_array);
}

TEST(CodegenNullable, ParseNonNullArray) {
  constexpr const char* kNonNullDoc = R"~({"nullable_array": [1,2,3]})~";

  const auto json = formats::json::FromString(kNonNullDoc);
  const auto obj = json.As<handlers::NullableFieldArray>();

  ASSERT_TRUE(!!obj.nullable_array);
  EXPECT_EQ((std::vector<int>{1, 2, 3}), *obj.nullable_array);
}

TEST(CodegenNullable, ParseNullObject) {
  constexpr const char* kNullDoc = R"~({"nullable_object": null})~";

  const auto json = formats::json::FromString(kNullDoc);
  const auto obj = json.As<handlers::NullableFieldObject>();

  ASSERT_TRUE(!obj.nullable_object);
}

TEST(CodegenNullable, ParseNonNullObject) {
  constexpr const char* kNonNullDoc = R"~({"nullable_object": {"value": 42}})~";

  const auto json = formats::json::FromString(kNonNullDoc);
  const auto obj = json.As<handlers::NullableFieldObject>();

  ASSERT_TRUE(!!obj.nullable_object);
  EXPECT_EQ(42, obj.nullable_object->value);
}

TEST(CodegenNullable, ParseInvalidType) {
  constexpr const char* kInvalidDoc = R"~({"nullable_string":42})~";

  const auto json = formats::json::FromString(kInvalidDoc);
  EXPECT_THROW(json.As<handlers::NullableField>(),
               formats::json::TypeMismatchException);
}

TEST(CodegenNullable, SerializeNull) {
  constexpr const char* kNullDoc = R"~({"nullable_string":null})~";
  handlers::NullableField obj;

  EXPECT_EQ(ToString(formats::json::ValueBuilder(obj).ExtractValue()),
            kNullDoc);
}

TEST(CodegenNullable, SerializeNonNullString) {
  constexpr const char* kNonNullDoc = R"~({"nullable_string":"string"})~";

  handlers::NullableField obj{std::string("string")};
  EXPECT_EQ(ToString(formats::json::ValueBuilder(obj).ExtractValue()),
            kNonNullDoc);
}

TEST(CodegenNullable, SerializeArrayNull) {
  constexpr const char* kNullDoc = R"~({"nullable_array":null})~";
  handlers::NullableFieldArray obj;

  EXPECT_EQ(ToString(formats::json::ValueBuilder(obj).ExtractValue()),
            kNullDoc);
}

TEST(CodegenNullable, SerializeArrayNonNull) {
  constexpr const char* kNonNullDoc = R"~({"nullable_array":[1,2,3]})~";

  handlers::NullableFieldArray obj{std::vector<int>{1, 2, 3}};
  EXPECT_EQ(ToString(formats::json::ValueBuilder(obj).ExtractValue()),
            kNonNullDoc);
}

TEST(CodegenNullable, ParseNullableWithRegexValid) {
  constexpr const char* kNonNullDoc = R"~({"nullable_field":"123"})~";
  const auto json = formats::json::FromString(kNonNullDoc);

  handlers::NullableWithRegexField nullable;
  EXPECT_NO_THROW(nullable = json.As<handlers::NullableWithRegexField>());
  ASSERT_FALSE(!nullable.nullable_field);
  EXPECT_EQ("123", *nullable.nullable_field);
}

TEST(CodegenNullable, ParseNullableWithRegexNull) {
  constexpr const char* kNullDoc = R"~({"nullable_field":null})~";
  const auto json = formats::json::FromString(kNullDoc);

  handlers::NullableWithRegexField nullable;
  EXPECT_NO_THROW(nullable = json.As<handlers::NullableWithRegexField>());
  EXPECT_TRUE(!nullable.nullable_field);
}

TEST(CodegenNullable, ParseNullableWithRegexNullMissing) {
  constexpr const char* kNullDoc = R"~({})~";
  const auto json = formats::json::FromString(kNullDoc);

  handlers::NullableWithRegexField nullable;
  EXPECT_NO_THROW(nullable = json.As<handlers::NullableWithRegexField>());
  EXPECT_TRUE(!nullable.nullable_field);
}

TEST(CodegenNullable, ParseNullableWithRegexInvalid) {
  constexpr const char* kNonNullDoc = R"~({"nullable_field":"abc"})~";
  const auto json = formats::json::FromString(kNonNullDoc);

  EXPECT_THROW(json.As<handlers::NullableWithRegexField>(),
               formats::json::Value::ParseException);
}

TEST(CodegenNullable, ParseNullableFieldOneOfValid) {
  constexpr const char* kDoc = R"~({"nullable_field":"abc"})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOf>();

  EXPECT_TRUE(obj.nullable_field.has_value());
  EXPECT_EQ(*obj.nullable_field, (std::variant<std::string, int>("abc")));
}

TEST(CodegenNullable, ParseNullableFieldOneOfMissing) {
  constexpr const char* kDoc = R"~({})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOf>();

  EXPECT_FALSE(obj.nullable_field.has_value());
}

TEST(CodegenNullable, ParseNullableFieldOneOfNull) {
  constexpr const char* kDoc = R"~({"nullable_field":null})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOf>();

  EXPECT_FALSE(obj.nullable_field.has_value());
}

TEST(CodegenNullable, ParseNullableFieldOneOfInvalid) {
  constexpr const char* kDoc = R"~({"nullable_field": {}})~";
  const auto json = formats::json::FromString(kDoc);

  EXPECT_THROW(json.As<handlers::NullableFieldOneOf>(),
               formats::json::Value::ParseException);
}

TEST(CodegenNullable, ParseNullableFieldOneOfDiscrValid) {
  constexpr const char* kDoc =
      R"~({"nullable_field": {"key": "obj1", "field1": "abc"}})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOfDiscr>();

  using VarT = std::variant<handlers::NullableFieldOneOfDiscr1,
                            handlers::NullableFieldOneOfDiscr2>;
  using VarWrapperT = handlers::NullableFieldOneOfDiscrNullablefield;

  const handlers::NullableFieldOneOfDiscr1 ethDiscr1{"obj1", "abc"};
  const VarT ethVar{ethDiscr1};
  const VarWrapperT ethVarWrapper{ethDiscr1};

  EXPECT_TRUE(obj.nullable_field.has_value());
  EXPECT_EQ(*obj.nullable_field, ethVarWrapper);
}

TEST(CodegenNullable, ParseNullableFieldOneOfDiscrMissing) {
  constexpr const char* kDoc = R"~({})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOfDiscr>();

  EXPECT_FALSE(obj.nullable_field.has_value());
}

TEST(CodegenNullable, ParseNullableFieldOneOfDiscrNull) {
  constexpr const char* kDoc = R"~({"nullable_field": null})~";
  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::NullableFieldOneOfDiscr>();

  EXPECT_FALSE(obj.nullable_field.has_value());
}

TEST(CodegenNullable, ParseNullableFieldOneOfDiscrInvalidEmpty) {
  constexpr const char* kDoc = R"~({"nullable_field": {}})~";
  const auto json = formats::json::FromString(kDoc);

  EXPECT_THROW(json.As<handlers::NullableFieldOneOfDiscr>(),
               formats::json::MemberMissingException);
}

TEST(CodegenNullable, ParseNullToDefault) {
  namespace ns = defs::internal::sample_model;

  auto json = formats::json::FromString(R"({"x": null})");

  EXPECT_EQ(json.As<ns::TreatNullAsDefault>(),
            ns::TreatNullAsDefault{"the default value"});
}
