#include <userver/utest/utest.hpp>

#include <exceptions.hpp>
#include <models/common.hpp>
#include <utils/phone.hpp>

TEST(TestFromVtbPhone, success) {
  const auto& phone = maas::utils::phone::FromVtbPhone("79123456789");
  ASSERT_EQ(phone, maas::models::PhoneNumber("+79123456789"));
}

TEST(TestFromVtbPhone, wrongCountryCode) {
  try {
    maas::utils::phone::FromVtbPhone("39123456789");
    ASSERT_TRUE(false);  // Should be thrown exception
  } catch (const maas::PhoneFormatError&) {
    ASSERT_TRUE(true);
  }
}

TEST(TestToVtbPhone, success) {
  const auto& phone = maas::models::PhoneNumber("+79123456789");
  const auto& vtb_phone = maas::utils::phone::ToVtbPhone(phone);
  ASSERT_EQ(vtb_phone, "79123456789");
}

TEST(TestFromPersonalPhone, successFromCorrectPhone) {
  const auto& phone = maas::utils::phone::FromPersonalPhone("+79123456789");
  ASSERT_EQ(phone, maas::models::PhoneNumber("+79123456789"));
}

TEST(TestFromPersonalPhone, successFromTrashPhone) {
  const auto& phone =
      maas::utils::phone::FromPersonalPhone("+7 (912) 345-67-89");
  ASSERT_EQ(phone, maas::models::PhoneNumber("+79123456789"));
}

TEST(TestFromPersonalPhone, successFromTrashPhoneWithEight) {
  const auto& phone =
      maas::utils::phone::FromPersonalPhone("8 (912) 345-67-89");
  ASSERT_EQ(phone, maas::models::PhoneNumber("+79123456789"));
}

TEST(TestFromPersonalPhone, wrongLengthNumber) {
  try {
    maas::utils::phone::FromPersonalPhone("8 (495) 89");
    ASSERT_TRUE(false);  // Should be thrown exception
  } catch (const maas::PhoneFormatError&) {
    ASSERT_TRUE(true);
  }
}

TEST(TestFromPersonalPhone, wrongCountryCode) {
  try {
    maas::utils::phone::FromPersonalPhone("+3 (912) 345-67-89");
    ASSERT_TRUE(false);  // Should be thrown exception
  } catch (const maas::PhoneFormatError&) {
    ASSERT_TRUE(true);
  }
}

TEST(TestFromPersonalPhone, wrongLocalCode) {
  try {
    maas::utils::phone::FromPersonalPhone("4 (912) 345-67-89");
    ASSERT_TRUE(false);  // Should be thrown exception
  } catch (const maas::PhoneFormatError&) {
    ASSERT_TRUE(true);
  }
}
