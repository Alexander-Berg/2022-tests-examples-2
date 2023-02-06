#include <gtest/gtest.h>

#include <logging/log_extra.hpp>
#include <utils/helpers/obfuscation.hpp>

const std::string kPhoneField = "phone";

auto obfuscator = utils::helpers::obfuscation::ObfuscateJsonFieldInPlace;

void ObfuscateAndCheck(std::string& json, const std::string& expected_json,
                       const std::string& field_name = kPhoneField) {
  LogExtra log_extra;
  obfuscator(json, field_name, log_extra);
  EXPECT_EQ(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckEmpty) {
  std::string json = R"({})";
  const auto expected_json = json;

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckMissingField) {
  std::string json = R"({"phone": "+70001234567"})";
  const std::string expected_json = json;

  ObfuscateAndCheck(json, expected_json, "phone_number");
}

TEST(TestObfuscatePhoneNumbers, CheckNonStringField) {
  std::string json = R"({"phone": 1234567})";
  const std::string expected_json = json;

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckExistingField) {
  std::string json = R"({"phone": "+70001234567"})";
  const std::string expected_json = R"({"phone": "............"})";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckFieldAsValue) {
  std::string json = R"({
    "column": "phone", "phone": "+70001234567"
  })";
  const std::string expected_json = R"({
    "column": "phone", "phone": "............"
  })";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckNestedField) {
  std::string json = R"({"user": {"phone": "+70001234567"}})";
  const std::string expected_json = R"({"user": {"phone": "............"}})";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckMultipleEntries) {
  std::string json = R"({
    "user": {"phone": "+70001234567"},
    "phone": "+70001234567"
  })";
  const std::string expected_json = R"({
    "user": {"phone": "............"},
    "phone": "............"
  })";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckOtherFieldsUntouched) {
  std::string json = R"({
    "id": "0000", "phone": "+70001234567", "yandex_uid": "0123456789"
  })";
  const std::string expected_json = R"({
    "id": "0000", "phone": "............", "yandex_uid": "0123456789"
  })";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckEscapedQuotes) {
  std::string json = R"({"phone": "+7\"abacaba\"1234567"})";
  const std::string expected_json = R"({"phone": "...................."})";

  ObfuscateAndCheck(json, expected_json);
}

TEST(TestObfuscatePhoneNumbers, CheckNonDigits) {
  std::string json = R"({"phone": "+7 (000) 123-45-67"})";
  const std::string expected_json = R"({"phone": ".................."})";

  ObfuscateAndCheck(json, expected_json);
}
