#include <gtest/gtest.h>

#include "random_string_generator.hpp"

using utils::GenerateRandomString;

const std::string kAbc = "abcdefghijklmnopqrstuvwxyz";

TEST(RandomStringGenerator, EmptyString) {
  ASSERT_EQ("", GenerateRandomString("a", 0));
  ASSERT_EQ("", GenerateRandomString("a", 0, 0));
}

TEST(RandomStringGenerator, SimpleAbcExactLength) {
  ASSERT_EQ("aaaaaaa", utils::GenerateRandomString("a", 7));
  ASSERT_EQ("aaaaaaa", utils::GenerateRandomString("a", 7, 7));
}

TEST(RandomStringGenerator, ComplexAbcExactLength) {
  std::string astring = utils::GenerateRandomString(kAbc, 13);
  ASSERT_EQ(13u, astring.length());
  for (const char c : astring) {
    ASSERT_TRUE(kAbc.find(c) != std::string::npos);
  }
}

TEST(RandomStringGenerator, ComplexAbc) {
  std::string astring = utils::GenerateRandomString(kAbc, 9, 20);
  ASSERT_LE(9u, astring.length());
  ASSERT_GE(20u, astring.length());
  for (const char c : astring) {
    ASSERT_TRUE(kAbc.find(c) != std::string::npos);
  }
}
