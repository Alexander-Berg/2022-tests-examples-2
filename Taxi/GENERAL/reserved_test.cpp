#include <utils/reserved.hpp>

#include <array>

#include <userver/utest/utest.hpp>

namespace {

namespace utils = geobus::utils;

struct TestReserved : public ::testing::TestWithParam<size_t> {};

TEST_P(TestReserved, VectorOfInt) {
  const auto capacity = GetParam();

  const std::vector<int> int_vector(utils::Reserved{capacity});
  ASSERT_EQ(int_vector.capacity(), capacity);
}

TEST_P(TestReserved, VectorOfStrings) {
  const auto capacity = GetParam();

  const std::vector<std::string> str_vector(utils::Reserved{capacity});
  ASSERT_EQ(str_vector.capacity(), capacity);
}

auto MakeTestData() {
  return std::array{0ul, 1ul, 2ul, 5ul, 10ul, 100ul, 666ul, 1000ul, 10000ul};
}

INSTANTIATE_TEST_SUITE_P(TestReserved, TestReserved,
                         ::testing::ValuesIn(MakeTestData()));

}  // namespace
