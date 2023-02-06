#include <gtest/gtest.h>

#include <matching/match.hpp>

TEST(match, substitute_token) {
  EXPECT_EQ("{0}", matching::SubstituteToken({"zero"}, "{0}"));
  EXPECT_EQ("{1}", matching::SubstituteToken({}, "{1}"));
  EXPECT_EQ("one{2}", matching::SubstituteToken({"one"}, "{1}{2}"));
  EXPECT_EQ("onetwo", matching::SubstituteToken({"one", "two"}, "{1}{2}"));
  EXPECT_EQ("one::one", matching::SubstituteToken({"one"}, "{1}::{1}"));
  EXPECT_EQ("xx-one-yy",
            matching::SubstituteToken({"one", "two"}, "xx-{1}-yy"));
}
