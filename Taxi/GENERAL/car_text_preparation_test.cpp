#include <gtest/gtest.h>

#include <models/useful_constants.hpp>
#include <models/validation_error.hpp>
#include <utils/car_text_preparation.hpp>

TEST(CarTextPreparation, PrepareVIN) {
  using utils::car::PrepareVIN;

  EXPECT_EQ(std::string{"ABC123"}, PrepareVIN("abc123"));
  EXPECT_EQ(std::string{"ABCDEFGHJKLMNPRS"}, PrepareVIN("abcdefghjklmnprs"));
  EXPECT_EQ(std::string{"ABCDEFGHJKLMNPRST"}, PrepareVIN("abcdefghjklmnprst"));
  EXPECT_EQ(std::string{"UVWXYZ01234567899"}, PrepareVIN("uvwxyz01234567899"));
  EXPECT_EQ(std::string{"UVWXYZ01234567899X"},
            PrepareVIN("uvwxyz01234567899x"));
  EXPECT_EQ(std::string{"ABCEHKM0PTXY12345"},
            PrepareVIN(u8"авсенкмортху12345"));
  EXPECT_EQ(std::string{"ABC"}, PrepareVIN("  AB   C "));
  EXPECT_EQ(std::string{"ABCDEFGHJKLMNP12"}, PrepareVIN("ABCDEFGHJKLMNP 12"));
  EXPECT_EQ(std::string{"ABCDEFGH1JKL12345"}, PrepareVIN("abcdefghijkl12345"));
  EXPECT_EQ(std::string{"ABCDEFGHJKLMN0123"}, PrepareVIN("abcdefghjklmno123"));
  EXPECT_EQ(std::string{"Q.БГДЯ10"}, PrepareVIN("q.бгдяio"));
  EXPECT_EQ(std::string{u8"ЯЯЯЯЯЯЯ"}, PrepareVIN(u8"Яяяяяяя"));
}

TEST(CarTextPreparation, ValidateVIN) {
  using utils::car::ValidateVIN;

  // incorrect length
  EXPECT_THROW(ValidateVIN("Q1234567812345678"), models::ValidationError);
  EXPECT_THROW(ValidateVIN(u8"Яяяяяяя"), models::ValidationError);
  EXPECT_THROW(ValidateVIN("ABC123"), models::ValidationError);
  EXPECT_THROW(ValidateVIN("ABCDEFGHJKLMNP1234"), models::ValidationError);

  // contains invalid symbol
  EXPECT_THROW(ValidateVIN("ABCDEFGHJKLMNPQ12"), models::ValidationError);
  EXPECT_THROW(ValidateVIN("ABCDEFGHJKLMNP.12"), models::ValidationError);
  EXPECT_THROW(ValidateVIN(u8"ABCDEFGHJKLMNPб12"), models::ValidationError);
  EXPECT_THROW(ValidateVIN(u8"ABCDEFGHJKLMNPг12"), models::ValidationError);
  EXPECT_THROW(ValidateVIN(u8"ABCDEFGHJKLMNPд12"), models::ValidationError);
  EXPECT_THROW(ValidateVIN(u8"Яяяяяяяяяяяяяяяяя"), models::ValidationError);

  // correct
  EXPECT_NO_THROW(ValidateVIN("ABCDEFG0123456789"));
}

TEST(CarTextPreparation, PrepareNumber) {
  using useful_constants::kRussiaCountryId;
  using utils::car::PrepareNumber;
  EXPECT_EQ(u8"АВСЕНКМОРТХУ", PrepareNumber("ABCEHKMOPTXY", kRussiaCountryId));
  EXPECT_EQ(u8"У123У", PrepareNumber("Y123Y", kRussiaCountryId));
  EXPECT_EQ(u8"У123У", PrepareNumber(u8"Y123У", kRussiaCountryId));
  EXPECT_EQ(u8"1У2У3", PrepareNumber(u8"1У2Y3", kRussiaCountryId));
  EXPECT_EQ(u8"НВАА123124", PrepareNumber("hbAA123124", kRussiaCountryId));
  EXPECT_EQ(u8"НВАА123124", PrepareNumber(u8"hbаа123124", kRussiaCountryId));
  EXPECT_EQ(u8"АМНКРАА", PrepareNumber(u8"амнкрaa", kRussiaCountryId));
}
