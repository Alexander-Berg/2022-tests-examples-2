#include <gtest/gtest.h>

#include <string>

#include <utils/check_validity.hpp>

namespace tests {

TEST(NameValidationParametrized, Test) {
  ASSERT_FALSE(::geoareas::utils::IsNameValid(""));

  static const std::string russian_alphabet =
      "абвгдеёжеийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
  for (char ch : russian_alphabet) {
    ASSERT_FALSE(::geoareas::utils::IsNameValid({ch}));
  }

  static const std::string invalid_characters = "`=~!@#$%^&*()+[{]};:',<.>/?";
  for (char ch : invalid_characters) {
    ASSERT_FALSE(::geoareas::utils::IsNameValid({ch}));
  }

  static const std::string whitespace_characters = " \t\n";
  for (char ch : whitespace_characters) {
    ASSERT_FALSE(::geoareas::utils::IsNameValid({ch}));
  }

  static const std::vector<std::string> invalid_names = {
      "   ",
      " tomsk_iter5_pol2",
      "tomsk_iter5_ pol2",
      "tomsk_iter5_pol2 ",
      "\ntomsk_iter5_pol2",
      "tomsk_iter5_pol2\n",
      "\ttomsk_iter5_pol2",
      "tomsk_iter5_pol2\t",
      "воронеж_итер1_пул2",
      "8+800*555/35+35~12728"};
  for (const auto& name : invalid_names) {
    ASSERT_FALSE(::geoareas::utils::IsNameValid(name));
  }

  static const std::vector<std::string> valid_names = {
      "VaLiD_nAme", "8-800-555-35-35", "1_underscore-2-DASHES"};
  for (const auto& name : valid_names) {
    ASSERT_TRUE(::geoareas::utils::IsNameValid(name));
  }
}

}  // namespace tests
