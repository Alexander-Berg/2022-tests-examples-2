#include <utils/promocode_generate.hpp>

#include <gtest/gtest.h>
#include <algorithm>

namespace utils::promocode {

namespace {

bool AlphabetContainsChar(const std::string& alphabet, char c) {
  return std::find(begin(alphabet), end(alphabet), c) != end(alphabet);
}

}  // namespace

TEST(CheckReferralGenerate, CheckCodeLen) {
  const std::string alphabet = "abc";
  const int seed = 42;

  {
    const auto& code = GenerateRandomStr(0, alphabet, seed);
    EXPECT_EQ(code.size(), 0);
  }
  {
    const auto& code = GenerateRandomStr(8, alphabet, seed);
    EXPECT_EQ(code.size(), 8);
  }
}

TEST(CheckReferralGenerate, CheckSeedReproducible) {
  const std::string alphabet = "abc";
  const int seed = 42;
  const size_t len = 8;

  EXPECT_EQ(GenerateRandomStr(len, alphabet, seed),
            GenerateRandomStr(len, alphabet, seed));
}

TEST(CheckReferralGenerate, CheckCodeCharsFromAlphabet) {
  const std::string alphabet = "abc";
  const int seed = 42;
  const size_t len = 8;

  const auto& code = GenerateRandomStr(len, alphabet, seed);
  EXPECT_TRUE(std::all_of(begin(code), end(code), [&](char c) {
    return AlphabetContainsChar(alphabet, c);
  }));
}

TEST(CheckReferralGenerate, CheckExceptionEmptyAlphabet) {
  const std::string alphabet = "";
  const size_t len = 8;

  EXPECT_THROW(GenerateRandomStr(len, alphabet), std::runtime_error);
}

}  // namespace utils::promocode
