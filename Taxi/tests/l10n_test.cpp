#include "l10n/translations.hpp"

#include <gtest/gtest.h>
#include <utils/convert_to_template.hpp>

TEST(ConverToTemplate, One) {
  EXPECT_STREQ("Text", l10n::utils::ConvertToTemplate("Text").c_str());
  EXPECT_STREQ("{value}", l10n::utils::ConvertToTemplate("%(value)s").c_str());
  EXPECT_STREQ("{value:.0f} h",
               l10n::utils::ConvertToTemplate("%(value).0f h").c_str());
  EXPECT_STREQ("{from} - {to}",
               l10n::utils::ConvertToTemplate("%(from)s - %(to)s").c_str());
  EXPECT_STREQ("text1 {1} text2 {2}",
               l10n::utils::ConvertToTemplate("text1 %s text2 %d").c_str());
  EXPECT_STREQ("Text {{blabla}}",
               l10n::utils::ConvertToTemplate("Text {blabla}").c_str());
  EXPECT_STREQ("Text {12}",
               l10n::utils::ConvertToTemplate("Text {12}").c_str());
  EXPECT_STREQ("{{abc}} {0}",
               l10n::utils::ConvertToTemplate("{abc} {0}").c_str());
  EXPECT_STREQ("{1}{2}{3}", l10n::utils::ConvertToTemplate("%d%d%d").c_str());
  EXPECT_STREQ("{1}%d{2}", l10n::utils::ConvertToTemplate("%d%%d%d").c_str());
  EXPECT_STREQ("%d%d{1}", l10n::utils::ConvertToTemplate("%%d%%d%d").c_str());
}

TEST(ToLower, Full) {
  ASSERT_EQ("hello", l10n::ToLower("HELLO"));
  ASSERT_EQ("привет", l10n::ToLower("ПРИВЕТ"));
  ASSERT_EQ("բարեւ", l10n::ToLower("ԲԱՐԵՒ"));
  ASSERT_EQ("grüssen", l10n::ToLower("GRÜSSEN"));
}
