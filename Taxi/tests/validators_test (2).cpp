#include <gtest/gtest.h>

#include <utils/validators.hpp>

namespace pu = personal::utils;

TEST(ValidatorsTest, ValidPhones) {
  EXPECT_TRUE(pu::ValidatePhone("+71111111111"));
  EXPECT_TRUE(pu::ValidatePhone("+7"));
}

TEST(ValidatorsTest, InvalidPhones) {
  EXPECT_FALSE(pu::ValidatePhone(""));
  EXPECT_FALSE(pu::ValidatePhone("81111111111"));
  EXPECT_FALSE(pu::ValidatePhone("+711111111111111111"));
  EXPECT_FALSE(pu::ValidatePhone("++71111111111"));
  EXPECT_FALSE(pu::ValidatePhone("+"));
  EXPECT_FALSE(pu::ValidatePhone("+7111111+11"));
  EXPECT_FALSE(pu::ValidatePhone("+7111111a11"));
  EXPECT_FALSE(pu::ValidatePhone("    +711111111"));
  EXPECT_FALSE(pu::ValidatePhone("+711    111111"));
  EXPECT_FALSE(pu::ValidatePhone("+711111111    "));
}

TEST(ValidatorsTest, ValidEmails) {
  EXPECT_TRUE(pu::ValidateEmail("email@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email123@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email.123@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email123email@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email-value@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email_value+sub@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email@yandex.team.ru"));
  EXPECT_TRUE(pu::ValidateEmail(".....@yandex.team.ru"));
  EXPECT_TRUE(pu::ValidateEmail("@yandex.ru"));
  EXPECT_TRUE(pu::ValidateEmail("email@"));
  EXPECT_TRUE(pu::ValidateEmail("@"));
}

TEST(ValidatorsTest, InvalidEmails) {
  EXPECT_FALSE(pu::ValidateEmail(""));
  EXPECT_FALSE(pu::ValidateEmail("email"));
  EXPECT_FALSE(pu::ValidateEmail("email@yandex@yandex.ru"));
  EXPECT_FALSE(pu::ValidateEmail("email@@yandex.ru"));
  EXPECT_FALSE(pu::ValidateEmail("@@yandex.ru"));
  EXPECT_FALSE(pu::ValidateEmail("email@@"));
  EXPECT_FALSE(pu::ValidateEmail("@email@"));
}

TEST(ValidatorsTest, ValidNumbers) {
  EXPECT_TRUE(pu::ValidateNumber("1111111111"));
  EXPECT_TRUE(pu::ValidateNumber("0"));
}

TEST(ValidatorsTest, InvalidNumbers) {
  EXPECT_FALSE(pu::ValidateNumber(""));
  EXPECT_FALSE(pu::ValidateNumber("inn"));
  EXPECT_FALSE(pu::ValidateNumber("инн"));
  EXPECT_FALSE(pu::ValidateNumber("123q"));
}

TEST(ValidatorsTest, ValidTelegramLogins) {
  EXPECT_TRUE(pu::ValidateTelegramLogin("TeleGram_Login_123"));
  EXPECT_TRUE(pu::ValidateTelegramLogin("telegram_login_123"));
  EXPECT_TRUE(pu::ValidateTelegramLogin("1111111111"));
}

TEST(ValidatorsTest, InvalidTelegramLogins) {
  EXPECT_FALSE(pu::ValidateTelegramLogin(""));
  EXPECT_FALSE(pu::ValidateTelegramLogin("1234"));
  EXPECT_FALSE(pu::ValidateTelegramLogin("логин"));
  EXPECT_FALSE(pu::ValidateTelegramLogin("telegram login"));
  EXPECT_FALSE(pu::ValidateTelegramLogin("telegram-login"));
  EXPECT_FALSE(pu::ValidateTelegramLogin(" telegram_login"));
  EXPECT_FALSE(pu::ValidateTelegramLogin("telegram_login "));
}
