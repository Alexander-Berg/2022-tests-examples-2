#include <defs/definitions.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

TEST(CodegenOptional, Empty) {
  constexpr const char* kDoc = "{}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::Optional>();

  EXPECT_EQ(std::nullopt, obj.int_);
  EXPECT_EQ(std::nullopt, obj.string);
  EXPECT_EQ(std::nullopt, obj.double_);
  EXPECT_EQ(std::nullopt, obj.variant);
  EXPECT_EQ(std::nullopt, obj.object);
  EXPECT_EQ(std::nullopt, obj.array);

  const auto obj2 =
      formats::json::ValueBuilder(obj).ExtractValue().As<handlers::Optional>();
  EXPECT_EQ(obj2, obj);
}

TEST(CodegenOptional, Null) {
  constexpr const char* kDoc = R"(
    {
      "int": null,
      "string": null,
      "double": null,
      "object": null,
      "variant": null,
      "array": null
    }
  )";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::Optional>();

  EXPECT_EQ(std::nullopt, obj.int_);
  EXPECT_EQ(std::nullopt, obj.string);
  EXPECT_EQ(std::nullopt, obj.double_);
  EXPECT_EQ(std::nullopt, obj.variant);
  EXPECT_EQ(std::nullopt, obj.object);
  EXPECT_EQ(std::nullopt, obj.array);

  const auto obj2 =
      formats::json::ValueBuilder(obj).ExtractValue().As<handlers::Optional>();

  EXPECT_EQ(obj2, obj);
}

TEST(CodegenOptional, Full) {
  constexpr const char* kDoc =
      "{\"int\": 3, \"string\": \"abc\", "
      "\"object\": {\"f\": 5}, \"variant\": 7, "
      "\"array\": [5, 4, 3]}";

  const auto json = formats::json::FromString(kDoc);
  const auto obj = json.As<handlers::Optional>();

  EXPECT_EQ(3, obj.int_);
  EXPECT_EQ(std::string("abc"), obj.string);
  EXPECT_EQ(handlers::OptionalObject{5}, obj.object);
  ASSERT_TRUE(obj.variant);
  EXPECT_EQ((std::variant<int, std::string>(7)), *obj.variant);
  EXPECT_EQ((std::vector<int>{5, 4, 3}), obj.array);

  const auto obj2 =
      formats::json::ValueBuilder(obj).ExtractValue().As<handlers::Optional>();
  EXPECT_EQ(obj2, obj);
}

TEST(CodegenOptional, ArrayTrivialValidation) {
  constexpr const char* kDoc = "{\"array\": [0]}";

  const auto json = formats::json::FromString(kDoc);
  EXPECT_THROW(json.As<handlers::Optional>(),
               formats::json::Value::ParseException);
}

TEST(CodegenOptional, MissingStruct) {
  constexpr const char* kDoc = "{\"array\": []}";

  const auto json = formats::json::FromString(kDoc);
  EXPECT_THROW(json.As<handlers::ContainerWithRequired>(),
               formats::json::Exception);
}

TEST(CodegenOptional, MissingArray) {
  constexpr const char* kDoc = "{\"struct\": {}}";

  const auto json = formats::json::FromString(kDoc);
  EXPECT_THROW(json.As<handlers::ContainerWithRequired>(),
               formats::json::Exception);
}

TEST(CodegenOptional, AllRequiredExist) {
  constexpr const char* kDoc = "{\"struct\": {}, \"array\": []}";

  const auto json = formats::json::FromString(kDoc);
  EXPECT_NO_THROW(json.As<handlers::ContainerWithRequired>());
}
