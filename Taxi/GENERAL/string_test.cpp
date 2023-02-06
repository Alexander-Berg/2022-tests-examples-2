#include "string.hpp"

#include <gtest/gtest.h>

namespace eats_cart::utils {

namespace {

struct ReplaceSpacesTestCase {
  std::string input, expected;
};

void TestReplaceSpaces(const ReplaceSpacesTestCase& tc) {
  EXPECT_EQ(tc.expected, ReplaceSpacesWithNonBreaking(tc.input));
}

}  // namespace

TEST(ReplaceSpacesWithNonBreaking, EmptyInput) {
  ReplaceSpacesTestCase tc{
      "",  // input
      ""   // expected
  };
  TestReplaceSpaces(tc);
}

TEST(ReplaceSpacesWithNonBreaking, OnlySpaces) {
  ReplaceSpacesTestCase tc{
      "  ",           // input
      "\u00a0\u00a0"  // expected
  };
  TestReplaceSpaces(tc);
}

TEST(ReplaceSpacesWithNonBreaking, OneSpace) {
  ReplaceSpacesTestCase tc{
      "prefix suffix",      // input
      "prefix\u00a0suffix"  // expected
  };
  TestReplaceSpaces(tc);
}

TEST(ReplaceSpacesWithNonBreaking, MultipleSpaces) {
  std::vector<ReplaceSpacesTestCase> cases{
      {
          // 1
          " one two three",                // input
          "\u00a0one\u00a0two\u00a0three"  // expected
      },
      {
          // 2
          " one two three ",                     // input
          "\u00a0one\u00a0two\u00a0three\u00a0"  // expected
      },
      {
          // 2
          "one two three four",                // input
          "one\u00a0two\u00a0three\u00a0four"  // expected
      }};
  for (const auto& tc : cases) {
    TestReplaceSpaces(tc);
  }
}

TEST(ReplaceSpacesWithNonBreaking, NothingToReplace) {
  std::vector<ReplaceSpacesTestCase> cases{{
                                               // 1
                                               "abacaba",  // input
                                               "abacaba"   // expected
                                           },
                                           {
                                               // 2
                                               "prefix\u00a0suffix",  // input
                                               "prefix\u00a0suffix"  // expected
                                           },
                                           {
                                               // 2
                                               "\u00a0\u00a0",  // input
                                               "\u00a0\u00a0"   // expected
                                           }};
  for (const auto& tc : cases) {
    TestReplaceSpaces(tc);
  }
}

}  // namespace eats_cart::utils
