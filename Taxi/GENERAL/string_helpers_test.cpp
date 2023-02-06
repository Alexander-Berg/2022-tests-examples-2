#include <gtest/gtest.h>

#include "string_helpers.hpp"

namespace u = fleet_parks::utils;

TEST(TrimWhitespaceSymbolsTest, TrimWhitespaceSymbols) {
  std::string s1{"a         b "};
  u::TrimWhitespaceSymbols(s1);
  ASSERT_EQ("a  b ", s1);

  std::string s2{"привет           это тесты  "};
  u::TrimWhitespaceSymbols(s2);
  ASSERT_EQ("привет  это тесты  ", s2);

  std::string s3{"a\n\nb\n\n\n\n                c\t\t\t\td"};
  u::TrimWhitespaceSymbols(s3);
  ASSERT_EQ("a\n\nb\n\n  c\t\t\t\td", s3);

  std::string s4{"я ч  с \n\n\n\nм  ц  к п\n \nэ"};
  u::TrimWhitespaceSymbols(s4);
  ASSERT_EQ("я ч  с \n\nм  ц  к п\n \nэ", s4);

  std::string s5{"я \n\r\n\r\n\r\n\r\n\r @"};
  u::TrimWhitespaceSymbols(s5);
  ASSERT_EQ("я \n\r\n\r @", s5);
}
