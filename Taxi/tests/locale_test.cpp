#include <gtest/gtest.h>

#include <locale.hpp>

TEST(LocaleTest, FromAcceptLanguage) {
  const std::vector<std::string>& locales_supported = {"ru", "en", "hy", "ka"};
  const std::unordered_map<std::string, std::string>& locales_mapping = {
      {"be", "ru"}};

  EXPECT_EQ("ru", http::language::ParseLocale("r", locales_supported,
                                              locales_mapping));
  EXPECT_EQ("ru", http::language::ParseLocale("ru", locales_supported,
                                              locales_mapping));
  EXPECT_EQ("en", http::language::ParseLocale("en, fi", locales_supported,
                                              locales_mapping));
  EXPECT_EQ("en",
            http::language::ParseLocale("en-us; q=0.8, en; q=0.6",
                                        locales_supported, locales_mapping));
  EXPECT_EQ("ru", http::language::ParseLocale("be", locales_supported,
                                              locales_mapping));
  EXPECT_EQ("en", http::language::ParseLocale("az", locales_supported,
                                              locales_mapping));
}
