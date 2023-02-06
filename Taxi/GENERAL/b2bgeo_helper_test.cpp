#include <gtest/gtest.h>

#include "b2bgeo_helper.hpp"

namespace b2bgeo_helper {

class MakeDepotTimeWindowTests
    : public ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

TEST_P(MakeDepotTimeWindowTests, Base) {
  const auto dt = std::get<0>(GetParam());
  const auto expected = std::get<1>(GetParam());
  const auto pt = utils::datetime::Stringtime(dt);
  ASSERT_EQ(expected, internal::MakeDepotTimeWindow(pt));
}

INSTANTIATE_TEST_CASE_P(
    TestCases, MakeDepotTimeWindowTests,
    ::testing::Values(
        std::make_tuple("2022-06-01T10:10:10.000+03", "10:10:10-10:11:10"),
        std::make_tuple("2022-06-01T23:59:30.000+03", "23:59:30-1.00:00:30"),
        std::make_tuple("2022-06-01T00:00:00.000+03", "00:00:00-00:01:00"),
        std::make_tuple("2022-06-01T23:59:00.000+03", "23:59:00-1.00:00:00")));

}  // namespace b2bgeo_helper
