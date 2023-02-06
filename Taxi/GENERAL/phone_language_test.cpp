#include <gtest/gtest.h>

#include "phone_language.hpp"

namespace ucommunications {

TEST(PhoneLanguageTest, SimpleTest) {
  models::PhoneLanguage phone_language = {
      {"+7", "ru"},
      {"+7", "kk"},
      {"+376", "ad"},
      {"+1", "en"},
  };

  EXPECT_EQ("ru", models::FindLanguageByPhone("+79262223023", phone_language));
  EXPECT_EQ("kk", models::FindLanguageByPhone("+77262223023", phone_language));
  EXPECT_EQ("ad", models::FindLanguageByPhone("+37662223023", phone_language));
  EXPECT_EQ("en", models::FindLanguageByPhone("+17662223023", phone_language));
  EXPECT_EQ("en", models::FindLanguageByPhone("+39262223023", phone_language));
}

}  // namespace ucommunications
