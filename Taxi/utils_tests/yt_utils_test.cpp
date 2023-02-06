#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <utils/yt_utils.hpp>

namespace eats_products::tests {

struct ModificationTimeTestParams {
  std::chrono::system_clock::time_point now;
  std::string modification_time;
  std::chrono::hours expiration_period;
  bool expected_result;
};

struct CheckModificationTimeTest
    : public ::testing::TestWithParam<ModificationTimeTestParams> {};

const std::vector<ModificationTimeTestParams> kModificationTimeTestParams{
    // Все ОК.
    {::utils::datetime::Stringtime("2022-01-02T10:00:00", "UTC",
                                   "%Y-%m-%dT%H:%M:%S"),
     "2022-01-01T10:00:00.000001Z", std::chrono::hours(48), true},
    // Таблица просрочилась.
    {::utils::datetime::Stringtime("2022-01-02T10:00:00", "UTC",
                                   "%Y-%m-%dT%H:%M:%S"),
     "2022-01-01T10:00:00.000001Z", std::chrono::hours(10), false},
    // Время модификации больше текущего времени.
    {::utils::datetime::Stringtime("2022-01-01T10:00:00", "UTC",
                                   "%Y-%m-%dT%H:%M:%S"),
     "2022-01-02T10:00:00.000001Z", std::chrono::hours(48), false},
    // Время модификации в некорректном формате
    {::utils::datetime::Stringtime("2022-01-02T10:00:00", "UTC",
                                   "%Y-%m-%dT%H:%M:%S"),
     "2022:01:01T10:00:00.000001Z", std::chrono::hours(48), false}};

TEST_P(CheckModificationTimeTest, CheckModificationTimeTest) {
  ::utils::datetime::MockNowSet(GetParam().now);
  const auto result = utils::yt::CheckModificationTime(
      "Test", GetParam().modification_time, GetParam().expiration_period);

  ASSERT_EQ(result, GetParam().expected_result);
}

INSTANTIATE_TEST_SUITE_P(YtUtils, CheckModificationTimeTest,
                         testing::ValuesIn(kModificationTimeTestParams));

}  // namespace eats_products::tests
