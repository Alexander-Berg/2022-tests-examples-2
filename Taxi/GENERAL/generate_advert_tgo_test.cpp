#include "generate_advert_tgo.hpp"

#include <gtest/gtest.h>
namespace {
namespace utils = eats_restapp_marketing::utils;

struct GenerateAdvertTgoSuccessTest
    : ::testing::TestWithParam<
          std::tuple<std::string, std::string, std::string>> {};

struct GenerateAdvertTgoExceptionTest
    : ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

INSTANTIATE_TEST_SUITE_P(
    results, GenerateAdvertTgoSuccessTest,
    ::testing::Values(
        std::make_tuple("{name}", "Ресторан", "Ресторан"),
        std::make_tuple("Ресторан {name}", "Ресторан", "Ресторан Ресторан"),
        std::make_tuple("Закажите в ресторане {name} еду", "Ресторан",
                        "Закажите в ресторане Ресторан еду"),
        std::make_tuple("", "Ресторан", ""),
        std::make_tuple("name", "Ресторан", "name")));

INSTANTIATE_TEST_SUITE_P(results, GenerateAdvertTgoExceptionTest,
                         ::testing::Values(std::make_tuple("name}", "Ресторан"),
                                           std::make_tuple("{name", "Ресторан"),
                                           std::make_tuple("{place}",
                                                           "Ресторан")));

TEST_P(GenerateAdvertTgoSuccessTest, shouldReturnExpectedString) {
  const auto [tmpl, name, expected] = GetParam();
  ASSERT_EQ(utils::GenerateAdvert(tmpl, name), expected);
}

TEST_P(GenerateAdvertTgoExceptionTest, shouldCallThrow) {
  const auto [tmpl, name] = GetParam();
  ASSERT_THROW(utils::GenerateAdvert(tmpl, name), utils::GenerateAdvertError);
}

}  // namespace
