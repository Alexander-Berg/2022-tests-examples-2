#include <gtest/gtest.h>

#include <models/common_types.hpp>
#include <utils/normalizations.hpp>

namespace {
const bool kValidationOn = true;
const bool kValidationOff = false;
}  // namespace

namespace pm = personal::models;

const personal::utils::NormalizationPreferences phone_normalization_disabled = {
    false, "rus"};

const personal::utils::NormalizationPreferences phone_normalization_enabled = {
    true, "rus"};

const personal::utils::NormalizationPreferences
    phone_normalization_unknown_country = {true, "brz"};

TEST(CommonTypesTest, ValidPhoneWithoutNormalization) {
  handlers::CommonType input;
  input.phone = "+71111111111";
  auto output =
      pm::ParseCommonType(input, kValidationOn, phone_normalization_disabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "+71111111111");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidPhoneWithoutNormalization) {
  handlers::CommonType input;
  input.phone = "+7-111-1111111";
  auto output =
      pm::ParseCommonType(input, kValidationOn, phone_normalization_disabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "+7-111-1111111");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, InvalidPhoneWithoutValidationAndNormalization) {
  handlers::CommonType input;
  input.phone = "+7-111-1111111";
  auto output =
      pm::ParseCommonType(input, kValidationOff, phone_normalization_disabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "+7-111-1111111");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, NormalizePhone) {
  handlers::CommonType input;
  input.phone = "+7-111-1111111";
  auto output =
      pm::ParseCommonType(input, kValidationOn, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "+71111111111");
  EXPECT_TRUE(output.normalized);
  EXPECT_EQ(output.normalized->phone, "+71111111111");
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, NormalizePhoneUnknownCountry) {
  handlers::CommonType input;
  input.phone = "8-111-1111111";
  auto output = pm::ParseCommonType(input, kValidationOff,
                                    phone_normalization_unknown_country);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "81111111111");
  EXPECT_TRUE(output.normalized);
  EXPECT_EQ(output.normalized->phone, "81111111111");
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, NormalizePhoneWithNationalAccessCode) {
  handlers::CommonType input;
  input.phone = "8-111-1111111";
  auto output =
      pm::ParseCommonType(input, kValidationOn, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kPhone);
  EXPECT_EQ(output.value, "+71111111111");
  EXPECT_TRUE(output.normalized);
  EXPECT_EQ(output.normalized->phone, "+71111111111");
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidEmail) {
  handlers::CommonType input;
  input.email = "test@test.ru";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kEmail);
  EXPECT_EQ(output.value, "test@test.ru");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidEmail) {
  handlers::CommonType input;
  input.email = "test-test.ru";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kEmail);
  EXPECT_EQ(output.value, "test-test.ru");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, InvalidEmailWithoutValidation) {
  handlers::CommonType input;
  input.email = "test-test.ru";
  auto output = pm::ParseCommonType(input, false, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kEmail);
  EXPECT_EQ(output.value, "test-test.ru");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidNormalDriverLicense) {
  handlers::CommonType input;
  input.driver_license = "123ABC";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kDriverLicense);
  EXPECT_EQ(output.value, "123ABC");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidUnNormalDriverLicense) {
  handlers::CommonType input;
  input.driver_license = "123-  aBС";  // Russian C
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kDriverLicense);
  EXPECT_EQ(output.value, "123-ABC");
  EXPECT_TRUE(output.normalized);
  EXPECT_EQ(output.normalized->driver_license, "123-ABC");
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidYandexLogin) {
  handlers::CommonType input;
  input.yandex_login = "yandex-login-111";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kYandexLogin);
  EXPECT_EQ(output.value, "yandex-login-111");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidTin) {
  handlers::CommonType input;
  input.tin = "000000000003";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTin);
  EXPECT_EQ(output.value, "000000000003");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidTin) {
  handlers::CommonType input;
  input.tin = "00000000-0003";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTin);
  EXPECT_EQ(output.value, "00000000-0003");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, ValidIdentification) {
  handlers::CommonType input;
  input.identification = "0000111111";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kIdentification);
  EXPECT_EQ(output.value, "0000111111");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidTelegramLogin) {
  handlers::CommonType input;
  input.telegram_login = "1234_Kolya";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTelegramLogin);
  EXPECT_EQ(output.value, "1234_Kolya");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidTelegramLogin) {
  handlers::CommonType input;
  input.telegram_login = "@1234";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTelegramLogin);
  EXPECT_EQ(output.value, "@1234");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, ValidTelegramId) {
  handlers::CommonType input;
  input.telegram_id = "1234";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTelegramId);
  EXPECT_EQ(output.value, "1234");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidTelegramId) {
  handlers::CommonType input;
  input.telegram_id = "12-34";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kTelegramId);
  EXPECT_EQ(output.value, "12-34");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, ValidDeptransId) {
  handlers::CommonType input;
  input.deptrans_id = "1234";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kDeptransId);
  EXPECT_EQ(output.value, "1234");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidDeptransId) {
  handlers::CommonType input;
  input.deptrans_id = "12-34";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kDeptransId);
  EXPECT_EQ(output.value, "12-34");
  EXPECT_FALSE(output.normalized);
  EXPECT_FALSE(output.error.empty());
}

TEST(CommonTypesTest, ValidFullNameForeNameOnly) {
  handlers::CommonType input;
  auto& full_name = input.full_name.emplace();
  full_name.forename = "Иван";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kFullName);
  EXPECT_EQ(output.value, "{\"f\":\"Иван\"}");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidFullNameSurname) {
  handlers::CommonType input;
  auto& full_name = input.full_name.emplace();
  full_name.forename = "Иван";
  full_name.surname = "Сидоров";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kFullName);
  EXPECT_EQ(output.value, "{\"f\":\"Иван\",\"s\":\"Сидоров\"}");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, ValidFullName) {
  handlers::CommonType input;
  auto& full_name = input.full_name.emplace();
  full_name.forename = "Иван";
  full_name.surname = "Сидоров";
  full_name.patronymic = "Петрович";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kFullName);
  EXPECT_EQ(output.value,
            "{\"f\":\"Иван\",\"p\":\"Петрович\",\"s\":\"Сидоров\"}");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, InvalidFullName) {
  handlers::CommonType input;
  auto& full_name = input.full_name.emplace();
  full_name.surname = "Сидоров";
  full_name.patronymic = "Петрович";
  auto output = pm::ParseCommonType(input, true, phone_normalization_enabled);
  EXPECT_EQ(*output.type, handlers::CommonTypeEnum::kFullName);
  EXPECT_EQ(output.value, "{\"f\":\"\",\"p\":\"Петрович\",\"s\":\"Сидоров\"}");
  EXPECT_FALSE(output.normalized);
  EXPECT_TRUE(output.error.empty());
}

TEST(CommonTypesTest, UnknownType) {
  handlers::CommonType input;
  auto output = pm::ParseCommonType(input, true, phone_normalization_disabled);
  EXPECT_FALSE(output.type.has_value());
  EXPECT_EQ(output.value, "");
  EXPECT_FALSE(output.normalized);
  EXPECT_EQ(output.error, "Unknown value type");
}

TEST(CommonTypesTest, MultiType) {
  auto check = [](const handlers::CommonType& input) {
    auto output =
        pm::ParseCommonType(input, false, phone_normalization_disabled);
    EXPECT_FALSE(output.type.has_value());
    EXPECT_EQ(output.value, "");
    EXPECT_FALSE(output.normalized);
    EXPECT_EQ(output.error, "Multi types in one item");
  };
  {
    handlers::CommonType input;
    input.phone = "+71111111111";
    input.email = "test@test.ru";
    check(input);
  }
  {
    handlers::CommonType input;
    input.phone = "+71111111111";
    auto& full_name = input.full_name.emplace();
    full_name.forename = "Иван";
    check(input);
  }
}

TEST(CommonTypesTest, StoredValuePhone) {
  auto output = pm::StoredValueToCommonType("123456789",
                                            handlers::CommonTypeEnum::kPhone);
  handlers::CommonType sample;
  sample.phone = "123456789";
  EXPECT_EQ(output, sample);
}

TEST(CommonTypesTest, StoredValueEmail) {
  auto output = pm::StoredValueToCommonType("test@test.ru",
                                            handlers::CommonTypeEnum::kEmail);
  handlers::CommonType sample;
  sample.email = "test@test.ru";
  EXPECT_EQ(output, sample);
}

TEST(CommonTypesTest, StoredValueFullNameForenameOnly) {
  auto output = pm::StoredValueToCommonType(
      "{\"f\":\"Иван\"}", handlers::CommonTypeEnum::kFullName);
  handlers::CommonType sample;
  sample.full_name.emplace().forename = "Иван";
  EXPECT_EQ(output, sample);
}

TEST(CommonTypesTest, StoredValueFullNameForenameSurnameOnly) {
  auto output = pm::StoredValueToCommonType(
      "{\"f\":\"Иван\",\"s\":\"Иванов\"}", handlers::CommonTypeEnum::kFullName);
  handlers::CommonType sample;
  sample.full_name.emplace();
  sample.full_name->forename = "Иван";
  sample.full_name->surname = "Иванов";
  EXPECT_EQ(output, sample);
}

TEST(CommonTypesTest, StoredValueFullName) {
  auto output = pm::StoredValueToCommonType(
      "{\"f\":\"Иван\",\"s\":\"Иванов\",\"p\":\"Иванович\"}",
      handlers::CommonTypeEnum::kFullName);
  handlers::CommonType sample;
  sample.full_name.emplace();
  sample.full_name->forename = "Иван";
  sample.full_name->surname = "Иванов";
  sample.full_name->patronymic = "Иванович";
  EXPECT_EQ(output, sample);
}

TEST(CommonTypesTest, StoredValueFullNameInvalid) {
  EXPECT_THROW(pm::StoredValueToCommonType("{\"bad_field\":\"Иван\"}",
                                           handlers::CommonTypeEnum::kFullName),
               formats::json::MemberMissingException);
}
