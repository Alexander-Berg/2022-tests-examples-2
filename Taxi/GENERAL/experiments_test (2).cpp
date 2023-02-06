#include "experiments.hpp"

#include <gtest/gtest.h>
#include <string>

#include <ua_parser/application.hpp>

namespace eats_communications::utils {

TEST(ParseApplicationVersion, InvalidNoThrow) {
  ASSERT_NO_THROW({
    const std::string version = "invalid version here";
    auto actual = impl::ParseApplicationVersion(version);
    const auto expected = ua_parser::ApplicationVersion(0, 0, 0);
    ASSERT_EQ(actual, expected);
  });
}

TEST(ParseApplicationVersion, SpacesNoThrow) {
  ASSERT_NO_THROW({
    const std::string version = " ";
    const auto actual = impl::ParseApplicationVersion(version);
    const auto expected = ua_parser::ApplicationVersion(0, 0, 0);
    ASSERT_EQ(actual, expected);
  });
}

TEST(ParseApplicationVersion, EmptyNoThrow) {
  ASSERT_NO_THROW({
    const std::string version = "";
    const auto actual = impl::ParseApplicationVersion(version);
    const auto expected = ua_parser::ApplicationVersion(0, 0, 0);
    ASSERT_EQ(actual, expected);
  });
}

TEST(ParseApplicationVersion, InvalidSuffixNoThrow) {
  ASSERT_NO_THROW({
    const std::string version = "1.2.3-test";
    const auto actual = impl::ParseApplicationVersion(version);
    const auto expected = ua_parser::ApplicationVersion(0, 0, 0);
    ASSERT_EQ(actual, expected);
  });
}

TEST(ParseApplicationVersion, OK) {
  ASSERT_NO_THROW({
    const std::string version = "1.2.3";
    const auto actual = impl::ParseApplicationVersion(version);
    const auto expected = ua_parser::ApplicationVersion(1, 2, 3);
    ASSERT_EQ(actual, expected);
  });
}

}  // namespace eats_communications::utils
