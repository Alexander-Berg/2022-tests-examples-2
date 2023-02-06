#include <gtest/gtest.h>

#include <utility>

#include <utils/internation_phone_cleaner.hpp>

static models::Country GetCountry(std::string name, std::string currency_code,
                                  uint32_t vat, uint32_t phone_min_length,
                                  uint32_t phone_max_length,
                                  std::string phone_code,
                                  std::string national_access_code) {
  models::Country result{};

  result.name = std::move(name);
  result.currency_code = std::move(currency_code);
  result.vat = vat;
  result.phone_min_length = phone_min_length;
  result.phone_max_length = phone_max_length;
  result.phone_code = std::move(phone_code);
  result.national_access_code = std::move(national_access_code);

  return result;
}

TEST(TestCleanInternationalPhones, CleanInternationalPhone) {
  models::CountryMap m;
  m["rus"] = GetCountry({}, "_", 0, 11, 11, "7", "8");
  m["ukr"] = GetCountry({}, "_", 0, 12, 12, "380", "0");

  EXPECT_EQ(utils::CleanInternationalPhone("", "rus", m), "");
  EXPECT_EQ(
      utils::CleanInternationalPhone(" +7(900)888 77 66 ", "some_country", m),
      "+79008887766");
  EXPECT_EQ(utils::CleanInternationalPhone("79008887766", "rus", m),
            "+79008887766");
  EXPECT_EQ(utils::CleanInternationalPhone("8(900)888-77-66", "rus", m),
            "+79008887766");
  EXPECT_EQ(utils::CleanInternationalPhone("+380937740000", "rus", m),
            "+380937740000");
  EXPECT_EQ(utils::CleanInternationalPhone("0937740000", "ukr", m),
            "+380937740000");
}
