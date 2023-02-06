#include <gtest/gtest.h>

#include <utils/string.hpp>

namespace eats_full_text_search::utils::string::tests {

struct TestCase {
  std::string name;
  std::string text;
  std::string expected;
};

class SanitizeSearchTextTest : public ::testing::TestWithParam<TestCase> {};

TEST_P(SanitizeSearchTextTest, SanitizeSearchText) {
  auto params = GetParam();
  const auto result = SanitizeSearchText(std::move(params.text));
  ASSERT_EQ(result, params.expected);
}

INSTANTIATE_TEST_SUITE_P(
    /**/, SanitizeSearchTextTest,
    ::testing::Values(
        TestCase{
            "empty",  // name
            "",       // text
            "",       // expected
        },
        TestCase{
            "no_spec_sym",        // name
            "Салфетки бумажные",  // text
            "Салфетки бумажные",  // expected
        },
        TestCase{
            "remove_spec_sym",                 // name
            "Салфетки бумажные \u0000\u0000",  // text
            "Салфетки бумажные ",              // expected
        }),
    [](const auto& v) { return v.param.name; });

}  // namespace eats_full_text_search::utils::string::tests
