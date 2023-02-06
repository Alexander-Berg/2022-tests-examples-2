#include "last_symbols_check.hpp"

#include <gtest/gtest.h>

TEST(LastSymbolsCheck, One) {
  utils::LastSymbolsCheck check;
  check.Apply({"hello", "world"});

  EXPECT_TRUE(check.Check("abc_hello"));
  EXPECT_TRUE(check.Check("abcworld"));
  EXPECT_FALSE(check.Check("abc_ello"));
  EXPECT_FALSE(check.Check("orls"));
}
