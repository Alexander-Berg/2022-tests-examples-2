#include <userver/utest/utest.hpp>

#include <boost/regex.hpp>

#include "utils/generators.hpp"

namespace {

using namespace eats_partners::utils::generators;

struct PasswordGeneratorTest : ::testing::TestWithParam<size_t> {};

INSTANTIATE_TEST_SUITE_P(results, PasswordGeneratorTest,
                         ::testing::Values(0, 1, 6, 25, 100, 1000));

TEST_P(PasswordGeneratorTest, generate_password) {
  const auto length = GetParam();
  auto password = Password(length);
  ASSERT_EQ(password.size(), length);
  if (length > 0) {
    boost::regex pass_template("[a-zA-Z0-9]+");
    ASSERT_TRUE(boost::regex_match(password.GetUnderlying(), pass_template));
  }
}

}  // namespace
