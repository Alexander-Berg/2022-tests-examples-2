#include <common/utils/generator.hpp>

#include <gtest/gtest.h>
#include <algorithm>

namespace utils::generator {

namespace {

bool AlphabetContainsChar(const std::string& alphabet, char c) {
  return std::find(begin(alphabet), end(alphabet), c) != end(alphabet);
}

}  // namespace

TEST(CheckGenerate, CheckCodeLen) {
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

TEST(CheckGenerate, CheckSeedReproducible) {
  const std::string alphabet = "abc";
  const int seed = 42;
  const int len = 8;

  EXPECT_EQ(GenerateRandomStr(len, alphabet, seed),
            GenerateRandomStr(len, alphabet, seed));
}

TEST(CheckGenerate, CheckCodeCharsFromAlphabet) {
  const std::string alphabet = "abc";
  const int seed = 42;
  const int len = 8;

  const auto& code = GenerateRandomStr(len, alphabet, seed);
  EXPECT_TRUE(std::all_of(begin(code), end(code), [&](char c) {
    return AlphabetContainsChar(alphabet, c);
  }));
}

TEST(CheckGenerate, CheckExceptionEmptyAlphabet) {
  const std::string alphabet = "";
  const int len = 8;

  EXPECT_THROW(GenerateRandomStr(len, alphabet), std::invalid_argument);
}

TEST(CheckGenerate, CheckExceptionNegativeLength) {
  const std::string alphabet = "";
  const int len = -1;

  EXPECT_THROW(GenerateRandomStr(len, alphabet), std::domain_error);
}

TEST(CheckGenerateUniqueCodes, CheckNumCodes) {
  const std::string alphabet = "abcaaaaaaaa";
  const int num_codes = 5;
  const int code_length = 3;

  const auto generated_codes =
      GenerateUniqueInviteCodes(num_codes, code_length, alphabet);
  EXPECT_EQ(generated_codes.size(), num_codes);
}

TEST(CheckGenerateUniqueCodes, CheckExceptionNegativeNumCodes) {
  const std::string alphabet = "abc";
  const int num_codes = -1;
  const int code_length = 3;

  EXPECT_THROW(GenerateUniqueInviteCodes(num_codes, code_length, alphabet),
               std::domain_error);
}

TEST(CheckGenerateUniqueCodes, CheckExceptionTooManyCodes) {
  const std::string alphabet = "abc";
  const int num_codes = 42;
  const int code_length = 2;

  EXPECT_THROW(GenerateUniqueInviteCodes(num_codes, code_length, alphabet),
               std::domain_error);
}

}  // namespace utils::generator
