#include <gtest/gtest.h>

#include <iostream>
#include <userver/formats/json.hpp>

#include <utils/exceptions.hpp>

namespace names {
const std::string kNameEmpty = "";
const std::string kNameNone = "none";
const std::string kNameString = "string_val";
const std::string kNameStringEmpty = "string_empty";
const std::string kNameStringLong = "string_long";
const std::string kNameInt = "int_val";
const std::string kNameReal = "real_val";
const std::string kNameBool = "bool_val";
const std::string kNameArray = "array_val";
const std::string kNameObject = "object_val";

const std::string kValString = "string";
const std::string kValStringLong = "long string";
const std::string kValNone = "none";
const std::string kValEmpty = "";
}  // namespace names

namespace dnexc = utils::exceptions;

TEST(DeviceNotifyJson, Empty) {
  std::string str_value;
  formats::json::Value nil;

  EXPECT_THROW(str_value = nil[names::kNameNone].As<std::string>(),
               formats::json::MemberMissingException);
  EXPECT_THROW(str_value = nil[names::kNameEmpty].As<std::string>(),
               formats::json::MemberMissingException);

  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  builder[names::kNameString] = names::kValString;
  const auto data = builder.ExtractValue();

  EXPECT_THROW(str_value = data[names::kNameNone].As<std::string>(),
               formats::json::MemberMissingException);
  EXPECT_THROW(str_value = data[names::kNameEmpty].As<std::string>(),
               formats::json::MemberMissingException);
}

TEST(DeviceNotifyJson, WrongType) {
  std::string str_value;
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  formats::json::ValueBuilder array(formats::json::Type::kArray);
  formats::json::ValueBuilder object(formats::json::Type::kObject);
  builder[names::kNameInt] = 500;
  builder[names::kNameReal] = 3.14;
  builder[names::kNameBool] = true;
  builder[names::kNameArray] = array.ExtractValue();
  builder[names::kNameObject] = object.ExtractValue();
  builder[names::kNameString] = names::kValString;
  const auto data = builder.ExtractValue();

  EXPECT_THROW(str_value = data[names::kNameInt].As<std::string>(),
               formats::json::TypeMismatchException);
  EXPECT_THROW(str_value = data[names::kNameReal].As<std::string>(),
               formats::json::TypeMismatchException);
  EXPECT_THROW(str_value = data[names::kNameBool].As<std::string>(),
               formats::json::TypeMismatchException);
  EXPECT_THROW(str_value = data[names::kNameArray].As<std::string>(),
               formats::json::TypeMismatchException);
  EXPECT_THROW(str_value = data[names::kNameObject].As<std::string>(),
               formats::json::TypeMismatchException);
  EXPECT_NO_THROW(str_value = data[names::kNameString].As<std::string>());
}

TEST(DeviceNotifyJson, Strings) {
  std::string str_value;
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  builder[names::kNameString] = names::kValString;
  builder[names::kNameStringLong] = names::kValStringLong;
  builder[names::kNameStringEmpty] = names::kValEmpty;
  const auto data = builder.ExtractValue();

  EXPECT_THROW(str_value = data[names::kNameNone].As<std::string>(),
               formats::json::MemberMissingException);
  EXPECT_NO_THROW(str_value = data[names::kNameStringEmpty].As<std::string>());
  EXPECT_NO_THROW(str_value = data[names::kNameStringEmpty].As<std::string>());
  EXPECT_NO_THROW(str_value = data[names::kNameString].As<std::string>());
  EXPECT_NO_THROW(str_value = data[names::kNameStringLong].As<std::string>());
  EXPECT_NO_THROW(str_value = data[names::kNameString].As<std::string>());

  EXPECT_NO_THROW(str_value = data[names::kNameString].As<std::string>());
  EXPECT_EQ(str_value, names::kValString);
  EXPECT_NO_THROW(str_value = data[names::kNameStringLong].As<std::string>());
  EXPECT_EQ(str_value, names::kValStringLong);
  EXPECT_NO_THROW(str_value = data[names::kNameStringEmpty].As<std::string>());
  EXPECT_EQ(str_value, names::kValEmpty);

  EXPECT_NO_THROW(str_value = data[names::kNameString].As<std::string>());
  EXPECT_EQ(str_value, names::kValString);
  EXPECT_NO_THROW(str_value = data[names::kNameStringEmpty].As<std::string>());
  EXPECT_EQ(str_value, names::kValEmpty);
}

TEST(DeviceNotifyJson, Arrays) {
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  {
    builder[names::kNameString] = names::kValString;
    builder[names::kNameNone] =
        formats::json::ValueBuilder(formats::json::Type::kArray).ExtractValue();
    formats::json::ValueBuilder array(formats::json::Type::kArray);
    array.PushBack(names::kValEmpty);
    builder[names::kNameArray] = array.ExtractValue();
  }
  const auto data = builder.ExtractValue();

  {
    formats::json::Value absent_name;
    EXPECT_NO_THROW(absent_name = data[names::kNameReal]);
    EXPECT_FALSE(absent_name.IsNull());
    EXPECT_TRUE(absent_name.IsMissing());
    EXPECT_THROW(for ([[maybe_unused]] const auto& item
                      : absent_name){},
                 formats::json::MemberMissingException);
  }
  {
    formats::json::Value not_an_array;
    EXPECT_NO_THROW(not_an_array = data[names::kNameString]);
    EXPECT_FALSE(not_an_array.IsNull());
    EXPECT_TRUE(not_an_array.IsString());
    EXPECT_THROW(for ([[maybe_unused]] const auto& item
                      : not_an_array){},
                 formats::json::TypeMismatchException);
  }
  {
    formats::json::Value array_items;
    EXPECT_NO_THROW(array_items = data[names::kNameArray]);
    EXPECT_FALSE(array_items.IsNull());
    EXPECT_TRUE(array_items.IsArray());
    EXPECT_NO_THROW(for ([[maybe_unused]] const auto& item : array_items){});
  }
  {
    std::string str_value;
    EXPECT_THROW(str_value = data[names::kNameArray].As<std::string>(),
                 formats::json::TypeMismatchException);
  }
  {
    size_t fetched = 0;
    formats::json::Value empty_array;
    EXPECT_NO_THROW(empty_array = data[names::kNameNone]);
    EXPECT_NO_THROW(for ([[maybe_unused]] const auto& i
                         : empty_array) { ++fetched; });
    EXPECT_EQ(fetched, 0);
  }
  {
    size_t fetched = 0;
    formats::json::Value array_items;
    EXPECT_NO_THROW(array_items = data[names::kNameArray]);
    EXPECT_NO_THROW(for ([[maybe_unused]] const auto& i
                         : array_items) { ++fetched; });
    EXPECT_EQ(fetched, 1);
  }
}

class DeviceNotifyJsonArrayTest
    : public ::testing::TestWithParam<std::vector<std::string>> {};

TEST_P(DeviceNotifyJsonArrayTest, Values) {
  const std::vector<std::string>& values = GetParam();
  formats::json::ValueBuilder builder(formats::json::Type::kObject);
  formats::json::ValueBuilder array(formats::json::Type::kArray);
  for (const std::string& value : values) {
    array.PushBack(value);
  }
  builder[names::kNameArray] = array.ExtractValue();
  const auto data = builder.ExtractValue();

  std::vector<std::string> result;
  formats::json::Value json_items;
  EXPECT_NO_THROW(json_items = data[names::kNameArray]);
  EXPECT_NO_THROW(
      for (const auto& s
           : json_items) { result.push_back(s.As<std::string>()); });
  ASSERT_EQ(values.size(), result.size());
  for (size_t i = 0; i < values.size(); ++i) {
    EXPECT_EQ(values[i], result[i]);
  }
}

INSTANTIATE_TEST_SUITE_P(
    /* empty */, DeviceNotifyJsonArrayTest,
    ::testing::Values(std::vector<std::string>{},
                      std::vector<std::string>{names::kValEmpty},
                      std::vector<std::string>{names::kValString,
                                               names::kValEmpty,
                                               names::kValStringLong}));
