#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <common/mode.hpp>

class ShiftTime
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<std::string, uint32_t>> {};

TEST_P(ShiftTime, Test) {
  const auto& [shift_time, result] = GetParam();

  ASSERT_EQ(common::ParseShiftCloseTime(shift_time).offset, result);
}

INSTANTIATE_TEST_SUITE_P(
    ShiftTimeBase, ShiftTime,
    testing::Values(std::make_tuple("12:30:00+00:00", 30 * 60 + 12 * 3600),
                    std::make_tuple("12:30:00+03:00", 30 * 60 + 12 * 3600),
                    std::make_tuple("16:30:00+03:00", 30 * 60 + 16 * 3600)));

class ShiftRange
    : public testing::Test,
      public testing::WithParamInterface<
          std::tuple<std::string, std::string, std::string, std::string>> {};

TEST_P(ShiftRange, Test) {
  const auto& [now, shift_time, result_start, result_end] = GetParam();

  utils::datetime::MockNowSet(utils::datetime::Stringtime(now));

  const auto [start, end] = common::GetShiftRange(shift_time);

  ASSERT_EQ(result_start, utils::datetime::Timestring(start));
  ASSERT_EQ(result_end, utils::datetime::Timestring(end));
}

INSTANTIATE_TEST_SUITE_P(
    ShiftRangeBase, ShiftRange,
    testing::Values(
        std::make_tuple("2019-12-11T12:00:00+0300", "12:30:00+03:00",
                        "2019-12-10T09:30:00+0000", "2019-12-11T09:30:00+0000"),
        std::make_tuple("2019-12-11T12:30:00+0300", "12:30:00+03:00",
                        "2019-12-10T09:30:00+0000", "2019-12-11T09:30:00+0000"),
        std::make_tuple("2019-12-11T13:31:00+0300", "12:30:00+03:00",
                        "2019-12-11T09:30:00+0000",
                        "2019-12-12T09:30:00+0000")));
