#include <gtest/gtest.h>

#include "helpers/sort_shifts_helper.hpp"

using CourierShift = eats_performer_shifts::providers::shift_info_readers::
    utils::shift_structs::CourierShift;
using ShiftStatusDeprecated = eats_performer_shifts::providers::
    shift_info_readers::utils::shift_structs::ShiftStatusDeprecated;
using CourierShiftState = eats_performer_shifts::providers::shift_info_readers::
    utils::shift_structs::CourierShiftState;
using TimePointTz = storages::postgres::TimePointTz;
using eats_performer_shifts::helpers::SortShifts;

CourierShift BuildCourierShift(
    ShiftStatusDeprecated status,
    const std::optional<CourierShiftState>& state = std::nullopt,
    const std::optional<TimePointTz>& finished_at = std::nullopt,
    const std::optional<TimePointTz>& starts_at = std::nullopt,
    const std::optional<TimePointTz>& ends_at = std::nullopt) {
  CourierShift courier_shift;
  courier_shift.status.status = status;
  courier_shift.state = state;
  if (starts_at) {
    courier_shift.starts_at = *starts_at;
  }
  if (ends_at) {
    courier_shift.ends_at = *ends_at;
  }
  if (finished_at) {
    courier_shift.state = CourierShiftState();
    courier_shift.state->finished_at = finished_at;
  }

  return courier_shift;
}

// TimePointTzFromString
TimePointTz TFS(const std::string& time_str) {
  return TimePointTz(utils::datetime::Stringtime(time_str));
}

bool operator==(const CourierShift& lhs, const CourierShift& rhs) {
  if (lhs.state && rhs.state) {
    return lhs.status.status == rhs.status.status && lhs.state->finished_at &&
           rhs.state->finished_at && lhs.starts_at == rhs.starts_at &&
           lhs.ends_at == rhs.ends_at;
  } else if (!lhs.state && !rhs.state) {
    return lhs.status.status == rhs.status.status &&
           lhs.starts_at == rhs.starts_at && lhs.ends_at == rhs.ends_at;
  }
  return false;
}

bool Compare(const std::vector<CourierShift>& lhs,
             const std::vector<CourierShift>& rhs) {
  if (lhs.size() != rhs.size()) {
    return false;
  }
  for (std::size_t i = 0; i < lhs.size(); ++i) {
    if (!(lhs[i] == rhs[i])) {
      return false;
    }
  }
  return true;
}

TEST(SortShiftsHelper, Check_StatusSort_InProgressAndPlannedStatuses) {
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress)};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_StatusSort_InProgressAndNoCourier) {
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress)};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_StatusSort_PlannedAndComeLateWithState) {
  auto state = CourierShiftState();
  state.finished_at.emplace(
      utils::datetime::Stringtime("2021-08-06T07:00:00+0000"));
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kComeLate, state),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned)};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kComeLate, state),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_StatusSort_PlannedAndComeLateWithoutState) {
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kComeLate)};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned),
      BuildCourierShift(ShiftStatusDeprecated::kComeLate),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_EqualStartsAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_NotEqualStartsAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T05:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T05:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kPlanned, std::nullopt,
                        std::nullopt, TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_EqualFinishedAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_NotEqualFinishedAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T05:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T05:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_EqualEndsAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}

TEST(SortShiftsHelper, Check_TimeSort_NotEqualEndsAt) {
  TFS("2021-08-06T07:00:00+0000");
  std::vector<CourierShift> un_sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T05:00:00+0000"))};
  std::vector<CourierShift> sorted{
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T07:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kInProgress, std::nullopt,
                        std::nullopt, std::nullopt,
                        TFS("2021-08-06T05:00:00+0000")),
      BuildCourierShift(ShiftStatusDeprecated::kNoCourier)};

  EXPECT_TRUE(Compare(sorted, SortShifts(un_sorted)));
}
