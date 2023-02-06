#include "markcode.hpp"
#include <gtest/gtest.h>

TEST(CompiledMarkCodeTests, ParseCompiledMarkCode) {
  EXPECT_EQ(gs1::ParseCompiledMarkCode("\n 44 4D 00 00 00 00 003741\t "),
            "444D00000000003741");
  EXPECT_EQ(gs1::ParseCompiledMarkCode("444d00000000003741"),
            "444D00000000003741");
}
