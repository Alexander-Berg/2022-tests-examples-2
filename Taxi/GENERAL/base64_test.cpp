#include "base64.hpp"

#include <gtest/gtest.h>

#include <tuple>

namespace {

class TestBase64Basic
    : public ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

TEST_P(TestBase64Basic, Encode) {
  GTEST_ASSERT_EQ(utils::base64::Encode(std::get<0>(GetParam())),
                  std::get<1>(GetParam()));
}

TEST_P(TestBase64Basic, Decode) {
  GTEST_ASSERT_EQ(utils::base64::Decode(std::get<1>(GetParam())),
                  std::get<0>(GetParam()));
}

TEST_P(TestBase64Basic, EncodeStream) {
  std::stringstream input(std::get<0>(GetParam()));
  std::ostringstream output;

  utils::base64::Encode(input, output);
  GTEST_ASSERT_EQ(output.str(), std::get<1>(GetParam()));
}

TEST_P(TestBase64Basic, DecodeStream) {
  std::stringstream input(std::get<1>(GetParam()));
  std::ostringstream output;

  utils::base64::Decode(input, output);
  GTEST_ASSERT_EQ(output.str(), std::get<0>(GetParam()));
}

INSTANTIATE_TEST_CASE_P(
    Base64Pairs, TestBase64Basic,
    ::testing::Values(
        std::make_tuple("foo", "Zm9v"), std::make_tuple("foob", "Zm9vYg=="),
        std::make_tuple("fooba", "Zm9vYmE="),
        std::make_tuple("foobar", "Zm9vYmFy"),
        std::make_tuple(std::string({'\x00', '\x01', '\x02'}), "AAEC"),
        std::make_tuple(
            "These all are whitespace characters: \n\t\r\v\f",
            "VGhlc2UgYWxsIGFyZSB3aGl0ZXNwYWNlIGNoYXJhY3RlcnM6IAoJDQsM"),
        std::make_tuple(
            "This long text should not be split into lines when encoded"
            " at least with boost base64 implementation",
            "VGhpcyBsb25nIHRleHQgc2hvdWxkIG5vdCBiZSBzcGxpdCBpbnRvIGxpbm"
            "VzIHdoZW4gZW5jb2RlZCBhdCBsZWFzdCB3aXRoIGJvb3N0IGJhc2U2NCBp"
            "bXBsZW1lbnRhdGlvbg==")), );

class TestBase64Cleanup
    : public ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

TEST_P(TestBase64Cleanup, Decode) {
  GTEST_ASSERT_EQ(utils::base64::Decode(std::get<1>(GetParam())),
                  std::get<0>(GetParam()));
}

TEST_P(TestBase64Cleanup, DecodeStream) {
  std::stringstream input(std::get<1>(GetParam()));
  std::ostringstream output;

  utils::base64::Decode(input, output);
  GTEST_ASSERT_EQ(output.str(), std::get<0>(GetParam()));
}

INSTANTIATE_TEST_CASE_P(Base64PairsCleanup, TestBase64Cleanup,
                        ::testing::Values(std::make_tuple("foo", "Zm9v="),
                                          std::make_tuple("foo", "Zm9v=="),
                                          std::make_tuple("foo", "Zm9v=="),
                                          std::make_tuple("foo", "Z m9v"),
                                          std::make_tuple("foo", "Z\tm9v"),
                                          std::make_tuple("foo", "Z\nm9v"),
                                          std::make_tuple("foo", "Zm9v  ")), );

class TestBase64DecodeFailure : public ::testing::TestWithParam<std::string> {};

TEST_P(TestBase64DecodeFailure, Decode) {
  ASSERT_THROW(utils::base64::Decode(GetParam()), utils::base64::DecodeError);
}

TEST_P(TestBase64DecodeFailure, DecodeStream) {
  std::stringstream input(GetParam());
  std::ostringstream output;

  ASSERT_THROW(utils::base64::Decode(input, output),
               utils::base64::DecodeError);
}

INSTANTIATE_TEST_CASE_P(Base64Failures, TestBase64DecodeFailure,
                        ::testing::Values("Zm9v$", "!@#$"), );
}  // namespace
