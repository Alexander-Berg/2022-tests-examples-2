#include <chrono>

#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>

#include <models/wms_shifts.hpp>

using grocery_checkins::models::ShiftStatus;
using grocery_checkins::models::wms::Shift;
using grocery_checkins::models::wms::ShiftPtr;
using grocery_checkins::models::wms::ShiftsMap;

using CourierId = grocery_checkins::models::CourierId;

using optional_timepoint = std::optional<std::chrono::system_clock::time_point>;
using namespace std::chrono_literals;

struct ParametrizedShiftsMapTestParams {
  ShiftStatus status;
  std::string test_name;
};

class ParametrizedShiftsMapTest
    : public testing::TestWithParam<ParametrizedShiftsMapTestParams> {};

const std::vector<ParametrizedShiftsMapTestParams>
    kParametrizedShiftsMapTestParams = {
        {ShiftStatus::kInProgress, "in_progress"},
        {ShiftStatus::kPaused, "paused"},
        {ShiftStatus::kClosed, "closed"},
        {ShiftStatus::kWaiting, "waiting"}};

TEST_P(ParametrizedShiftsMapTest, AddNewShiftToEmptyMap) {
  const auto& param = GetParam();
  const utest::PrintTestName test_name_printer;
  const testing::TestParamInfo<ParametrizedShiftsMapTestParams> param_info(
      param, /* index */ 0);
  EXPECT_EQ(test_name_printer(param_info), param.test_name);

  auto status = param.status;
  ShiftsMap empty_map{};

  CourierId c_id1{"c1"};
  ::grocery_shared::LegacyDepotId dp_id1{""};

  Shift sh1{c_id1,
            "sh1",
            dp_id1,
            optional_timepoint(),
            optional_timepoint(),
            status,
            optional_timepoint(),
            optional_timepoint(),
            optional_timepoint()};

  empty_map.TryAddShift(std::make_shared<Shift>(sh1));
  auto current_shift = empty_map.GetCurrentShift();
  auto waiting_shift = empty_map.GetWaitingShift();
  auto data_ = empty_map.GetData();

  switch (status) {
    case grocery_checkins::models::ShiftStatus::kInProgress:
    case grocery_checkins::models::ShiftStatus::kPaused:
    case grocery_checkins::models::ShiftStatus::kClosed: {
      ASSERT_TRUE(data_.size() == 1);
      ASSERT_NE(current_shift, nullptr);
      ASSERT_EQ(sh1, *current_shift);
      ASSERT_EQ(waiting_shift, nullptr);
      break;
    }
    case grocery_checkins::models::ShiftStatus::kWaiting: {
      ASSERT_TRUE(data_.size() == 1);
      ASSERT_EQ(current_shift, nullptr);
      ASSERT_NE(waiting_shift, nullptr);
      ASSERT_EQ(sh1, *waiting_shift);
      break;
    }
  }
}

UTEST(ShiftsMapTest, AddNewCurrentShiftToMap) {
  auto now = ::utils::datetime::Now();
  ShiftsMap shift_map;

  CourierId c_id1{"c1"};
  ::grocery_shared::LegacyDepotId dp_id1{""};

  Shift sh1{c_id1,
            "sh1",
            dp_id1,
            now - 1h,
            optional_timepoint(),
            ShiftStatus::kInProgress,
            optional_timepoint(),
            optional_timepoint(),
            optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh1));

  Shift sh2{c_id1,
            "sh1",
            dp_id1,
            now - 1h,
            optional_timepoint(),
            ShiftStatus::kInProgress,
            now - 50min,
            now - 30min,
            optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh2));
  auto current_shift = shift_map.GetCurrentShift();

  ASSERT_NE(current_shift, nullptr);
  ASSERT_EQ(*current_shift, sh2);

  Shift sh3{c_id1,       "sh1",       dp_id1,
            now - 1h,    now - 10min, ShiftStatus::kClosed,
            now - 50min, now - 30min, optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh3));
  current_shift = shift_map.GetCurrentShift();

  ASSERT_NE(current_shift, nullptr);
  ASSERT_EQ(*current_shift, sh3);
}

UTEST(ShiftsMapTest, AddNewWaitingShiftToMap) {
  auto now = ::utils::datetime::Now();
  ShiftsMap shift_map;

  CourierId c_id1{"c1"};
  ::grocery_shared::LegacyDepotId dp_id1{""};

  Shift sh1{c_id1,
            "sh1",
            dp_id1,
            now + 1h,
            optional_timepoint(),
            ShiftStatus::kWaiting,
            optional_timepoint(),
            optional_timepoint(),
            optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh1));

  Shift sh2{c_id1,
            "sh1",
            dp_id1,
            now + 2h,
            optional_timepoint(),
            ShiftStatus::kWaiting,
            optional_timepoint(),
            optional_timepoint(),
            optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh2));
  auto waiting_shift = shift_map.GetWaitingShift();

  ASSERT_NE(waiting_shift, nullptr);
  ASSERT_EQ(*waiting_shift, sh1);

  Shift sh3{c_id1,
            "sh1",
            dp_id1,
            now + 30min,
            optional_timepoint(),
            ShiftStatus::kWaiting,
            optional_timepoint(),
            optional_timepoint(),
            optional_timepoint()};

  shift_map.TryAddShift(std::make_shared<Shift>(sh3));
  waiting_shift = shift_map.GetWaitingShift();

  ASSERT_NE(waiting_shift, nullptr);
  ASSERT_EQ(*waiting_shift, sh3);
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, ParametrizedShiftsMapTest,
                         testing::ValuesIn(kParametrizedShiftsMapTestParams),
                         utest::PrintTestName());
