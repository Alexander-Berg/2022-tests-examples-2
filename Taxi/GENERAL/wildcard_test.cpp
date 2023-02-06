#include <gtest/gtest.h>

#include "wildcard.hpp"

using utils::wildcard::IsSatisfy;
using utils::wildcard::PreparePattern;

TEST(PreparePattern, Empty) { ASSERT_EQ(PreparePattern("").str(), ""); }

TEST(PreparePattern, JustString) {
  std::string test_string;
  test_string = "arbitrary_string";
  ASSERT_EQ(PreparePattern(test_string).str(), test_string);
  test_string = "path/with/slashes";
  ASSERT_EQ(PreparePattern(test_string).str(), test_string);
  test_string = "string with spaces";
  ASSERT_EQ(PreparePattern(test_string).str(), test_string);
}

TEST(PreparePattern, SpecialSymbols) {
  ASSERT_EQ(PreparePattern("[a-z]*").str(), "\\[a-z\\]\\*");
}

TEST(PreparePattern, Wildcard) {
  ASSERT_EQ(PreparePattern("%").str(), ".*");
  ASSERT_EQ(PreparePattern("%/%").str(), ".*/.*");
  ASSERT_EQ(PreparePattern("%\\%").str(), ".*\\\\.*");
  ASSERT_EQ(PreparePattern("some%pattern").str(), "some.*pattern");
}

TEST(IsSatisfy, Empty) {
  ASSERT_TRUE(IsSatisfy("", PreparePattern("")));
  ASSERT_TRUE(IsSatisfy("", PreparePattern("%")));
  ASSERT_FALSE(IsSatisfy("some", PreparePattern("")));
}

TEST(IsSatisfy, JustString) {
  ASSERT_TRUE(IsSatisfy("a", PreparePattern("a")));
  ASSERT_FALSE(IsSatisfy("aa", PreparePattern("a")));
  ASSERT_FALSE(IsSatisfy("a", PreparePattern("aa")));

  ASSERT_TRUE(IsSatisfy("[a-z]*", PreparePattern("[a-z]*")));
  ASSERT_FALSE(IsSatisfy("abcz", PreparePattern("[a-z]*")));
}

TEST(IsSatisfy, Wildcard) {
  ASSERT_TRUE(IsSatisfy("arbitrary string", PreparePattern("%")));

  ASSERT_TRUE(IsSatisfy("prefix", PreparePattern("prefix%")));
  ASSERT_TRUE(IsSatisfy("prefixxx", PreparePattern("prefix%")));
  ASSERT_FALSE(IsSatisfy("preffix", PreparePattern("prefix%")));
  ASSERT_FALSE(IsSatisfy("pprefix", PreparePattern("prefix%")));

  ASSERT_TRUE(IsSatisfy("postfix", PreparePattern("%postfix")));
  ASSERT_FALSE(IsSatisfy("postfixxx", PreparePattern("%postfix")));
  ASSERT_TRUE(IsSatisfy("pppostfix", PreparePattern("%postfix")));

  ASSERT_TRUE(IsSatisfy("insde", PreparePattern("ins%de")));
  ASSERT_TRUE(IsSatisfy("inside", PreparePattern("ins%de")));
  ASSERT_TRUE(IsSatisfy("insxxxde", PreparePattern("ins%de")));
  ASSERT_FALSE(IsSatisfy("insider", PreparePattern("ins%de")));

  ASSERT_TRUE(IsSatisfy("taximeter_driver_id/dbid0/uuid0",
                        PreparePattern("taximeter_driver_id/%")));
  ASSERT_TRUE(IsSatisfy("taximeter_driver_id/dbid0/uuid0",
                        PreparePattern("taximeter_driver_id/%/%")));
  ASSERT_FALSE(IsSatisfy("taximeter_driver_id/dbid0_uuid0",
                         PreparePattern("taximeter_driver_id/%/%")));
}
