#include <stq/helpers/calc_missed_time.hpp>

#include <userver/utest/utest.hpp>

#include <clients/eats-shifts/definitions.hpp>

#include <userver/decimal64/decimal64.hpp>

namespace stq::helpers {

namespace {

// Shortcuts:

using TimePoint = std::chrono::system_clock::time_point;
using MissedTime = decimal64::Decimal<4>;

using EsShiftStatus = clients::eats_shifts::DataShiftStatus;
using EsShiftType = clients::eats_shifts::ShiftType;

using EsShifts = std::vector<EsShift>;

// Helpers:

const TimePoint kMidnight = ::utils::datetime::Stringtime(
    "2021-12-06T00:00:00+0300", utils::datetime::kDefaultDriverTimezone,
    utils::datetime::kDefaultFormat);

TimePoint MkTimepoint(const std::string& daytime_str) {
  return (kMidnight +
          std::chrono::seconds{::utils::datetime::ParseDayTime(daytime_str)});
}

template <EsShiftType shift_type>
EsShift MkShift(const std::string& shift_id, const EsShiftStatus& status,
                const std::optional<std::string>& planned_start_str,
                const std::optional<std::string>& planned_end_str,
                const std::optional<std::string>& actual_start_str,
                const std::optional<std::string>& actual_end_str) {
  EsShift shift{};

  shift.shift_id = shift_id;
  shift.status = status;
  shift.type = shift_type;

  if (planned_start_str.has_value()) {
    shift.planned_to_start_at = MkTimepoint(planned_start_str.value());
  }
  if (planned_end_str.has_value()) {
    shift.planned_to_close_at = MkTimepoint(planned_end_str.value());
  }
  if (actual_start_str.has_value()) {
    shift.started_at = MkTimepoint(actual_start_str.value());
  }
  if (actual_end_str.has_value()) {
    shift.closes_at = MkTimepoint(actual_end_str.value());
  }

  return shift;
}

EsShift MkPlannedShift(
    const std::string& shift_id, const EsShiftStatus& status,
    const std::string& planned_start_str, const std::string& planned_end_str,
    const std::optional<std::string>& actual_start_str = std::nullopt,
    const std::optional<std::string>& actual_end_str = std::nullopt) {
  return MkShift<EsShiftType::kPlanned>(shift_id, status, planned_start_str,
                                        planned_end_str, actual_start_str,
                                        actual_end_str);
}

EsShift MkUnplannedShift(
    const std::string& shift_id, const EsShiftStatus& status,
    const std::optional<std::string>& actual_start_str = std::nullopt,
    const std::optional<std::string>& actual_end_str = std::nullopt) {
  return MkShift<EsShiftType::kPlanned>(shift_id, status, std::nullopt,
                                        std::nullopt, actual_start_str,
                                        actual_end_str);
}

}  // namespace

// One shift tests:

TEST(CalcMissedTime, OneShiftClosed) {
  EsShift cl_shift = MkPlannedShift("0000", EsShiftStatus::kClosed, "10:15",
                                    "12:15", "10:20", "12:20");

  MissedTime mt_calc = CalcMissedTime(cl_shift, EsShifts{});
  ASSERT_EQ(mt_calc, MissedTime{5});
}

TEST(CalcMissedTime, OneShiftNotStarted) {
  EsShift ns_shift =
      MkPlannedShift("1000", EsShiftStatus::kNotStarted, "10:15", "12:15");

  MissedTime mt_calc = CalcMissedTime(ns_shift, EsShifts{});
  ASSERT_EQ(mt_calc, MissedTime{120});
}

// Shift stack tests:

TEST(CalcMissedTime, StackShiftsClosed) {
  EsShift n0_shift =
      MkPlannedShift("2000", EsShiftStatus::kNotStarted, "10:15", "12:15");
  EsShift n1_shift =
      MkPlannedShift("2001", EsShiftStatus::kNotStarted, "10:30", "12:15");
  EsShift cl_shift = MkPlannedShift("2002", EsShiftStatus::kClosed, "10:45",
                                    "12:15", "10:50", "12:15");

  EsShifts n0_intersections{n1_shift, cl_shift};
  EsShifts n1_intersections{n0_shift, cl_shift};
  EsShifts cl_intersections{n0_shift, n1_shift};
  MissedTime n0_mt_calc = CalcMissedTime(n0_shift, n0_intersections);
  MissedTime n1_mt_calc = CalcMissedTime(n1_shift, n1_intersections);
  MissedTime cl_mt_calc = CalcMissedTime(cl_shift, cl_intersections);

  ASSERT_EQ(n0_mt_calc + n1_mt_calc + cl_mt_calc, MissedTime{35});

  ASSERT_EQ(n0_mt_calc, MissedTime{35});
  ASSERT_EQ(n1_mt_calc, MissedTime{0});
  ASSERT_EQ(cl_mt_calc, MissedTime{0});
}

TEST(CalcMissedTime, StackShiftsNotStarted) {
  EsShift n0_shift =
      MkPlannedShift("3000", EsShiftStatus::kNotStarted, "10:15", "12:15");
  EsShift n1_shift =
      MkPlannedShift("3001", EsShiftStatus::kNotStarted, "10:30", "12:15");
  EsShift n2_shift =
      MkPlannedShift("3002", EsShiftStatus::kNotStarted, "10:45", "12:15");

  EsShifts n0_intersections{n1_shift, n2_shift};
  EsShifts n1_intersections{n0_shift, n2_shift};
  EsShifts n2_intersections{n0_shift, n1_shift};
  MissedTime n0_mt_calc = CalcMissedTime(n0_shift, n0_intersections);
  MissedTime n1_mt_calc = CalcMissedTime(n1_shift, n1_intersections);
  MissedTime n2_mt_calc = CalcMissedTime(n2_shift, n2_intersections);

  ASSERT_EQ(n0_mt_calc + n1_mt_calc + n2_mt_calc, MissedTime{120});

  ASSERT_EQ(n0_mt_calc, MissedTime{120});
  ASSERT_EQ(n1_mt_calc, MissedTime{0});
  ASSERT_EQ(n2_mt_calc, MissedTime{0});
}

// Shift chain tests:

TEST(CalcMissedTime, ChainedShiftsClosed) {
  EsShift c0_shift = MkPlannedShift("4000", EsShiftStatus::kClosed, "10:15",
                                    "12:15", "10:15", "12:25");
  EsShift c1_shift = MkPlannedShift("4001", EsShiftStatus::kClosed, "12:15",
                                    "14:15", "12:25", "14:15");

  MissedTime c0_mt_calc = CalcMissedTime(c0_shift, EsShifts{c1_shift});
  MissedTime c1_mt_calc = CalcMissedTime(c1_shift, EsShifts{c0_shift});

  ASSERT_EQ(c0_mt_calc + c1_mt_calc, MissedTime{0});
}

// Planned x unplanned tests:

TEST(CalcMissedTime, PlannedXUnplannedClosed) {
  EsShift p_shift = MkPlannedShift("5000", EsShiftStatus::kClosed, "10:15",
                                   "12:15", "10:15", "12:05");
  EsShift u_shift =
      MkUnplannedShift("5001", EsShiftStatus::kClosed, "12:05", "14:00");

  MissedTime p_mt_calc = CalcMissedTime(p_shift, EsShifts{u_shift});

  ASSERT_EQ(p_mt_calc, MissedTime{0});
}

TEST(CalcMissedTime, PlannedXUnplannedInProgress) {
  EsShift p_shift = MkPlannedShift("6000", EsShiftStatus::kClosed, "10:15",
                                   "12:15", "10:15", "12:05");
  EsShift u_shift =
      MkUnplannedShift("6001", EsShiftStatus::kInProgress, "12:05");

  MissedTime p_mt_calc = CalcMissedTime(p_shift, EsShifts{u_shift});

  // Yes, this may look unfair - the shift is in progress and those 10 min,
  // probably, have already been worked by now.
  // But it is not a critical error: when unplanned shift is closed, a
  // recalculation will be invoked, which will correct this mistake and upsert
  // missed time to 0 for a planned shift.
  ASSERT_EQ(p_mt_calc, MissedTime{10});
}

// Impossible border case tests:

TEST(CalcMissedTime, SimultaniousShiftsNotStarted) {
  // I assume, this case is not real, but it is better to check such border
  // conditions like this
  EsShift n0_shift =
      MkPlannedShift("7000", EsShiftStatus::kNotStarted, "10:15", "12:00");
  EsShift n1_shift =
      MkPlannedShift("7001", EsShiftStatus::kNotStarted, "10:15", "12:15");

  MissedTime n0_mt_calc = CalcMissedTime(n0_shift, EsShifts{n1_shift});
  MissedTime n1_mt_calc = CalcMissedTime(n1_shift, EsShifts{n0_shift});

  ASSERT_EQ(n0_mt_calc + n1_mt_calc, MissedTime{120});
}

TEST(CalcMissedTime, PlannedXPlannedInProgress) {
  // This case also looks like impossible, but a border one, that shall be
  // checked
  EsShift pc_shift = MkPlannedShift("8000", EsShiftStatus::kClosed, "10:15",
                                    "12:15", "10:15", "12:05");
  EsShift pp_shift = MkPlannedShift("8001", EsShiftStatus::kInProgress, "12:15",
                                    "14:15", "12:05");

  MissedTime pc_mt_calc = CalcMissedTime(pc_shift, EsShifts{pp_shift});

  ASSERT_EQ(pc_mt_calc, MissedTime{0});
}

}  // namespace stq::helpers
