#pragma once

#include <grocery-shared/datetime/timetable.hpp>

#include <set>
#include <string_view>

#include <cctz/time_zone.h>
#include <userver/utest/utest.hpp>

#include <grocery-shared/datetime/datetime.hpp>

namespace grocery_shared::datetime {

using Day = TimeOfDayInterval::DayType;

namespace test {

const std::string kMoscowTimezone = "Europe/Moscow";          // UTC +03:00
const std::string kReykjavikTimezone = "Atlantic/Reykjavik";  // UTC +00:00
const std::string kAustraliaEucla = "Australia/Eucla";        // UTC +08:45

inline void Append(std::vector<TimeOfDayInterval>& timetable, Day day,
                   std::string_view from, std::string_view to) {
  TimeOfDayInterval interval;
  interval.day_type = day;
  interval.range.open_from = TimeOfDayInterval::Time{from};
  interval.range.open_to = TimeOfDayInterval::Time{to};
  timetable.push_back(std::move(interval));
}

inline cctz::weekday GetWeekDay(
    std::chrono::system_clock::time_point time_point,
    const std::string& timezone) {
  cctz::civil_second seconds =
      cctz::convert(time_point, LoadCachedTimeZone(timezone));
  return cctz::get_weekday(cctz::civil_day(seconds));
}

inline std::chrono::system_clock::time_point GetTimePoint(
    cctz::civil_minute time, const std::string& timezone) {
  return cctz::convert(cctz::civil_second(time), LoadCachedTimeZone(timezone));
}

inline std::chrono::system_clock::time_point GetTimePoint(
    cctz::civil_second time, const std::string& timezone) {
  return cctz::convert(cctz::civil_second(time), LoadCachedTimeZone(timezone));
}

inline std::chrono::system_clock::time_point GetMomentInUTC(int year, int month,
                                                            int day, int hh,
                                                            int mm,
                                                            int sec = 0) {
  auto civil_time_utc = cctz::civil_second(year, month, day, hh, mm, sec);
  auto std_time_utc = GetTimePoint(civil_time_utc, kReykjavikTimezone);
  return std_time_utc;
}

inline Timetable ConstructTimetable(
    const std::vector<std::tuple<Day, std::string_view, std::string_view>>&
        data) {
  std::vector<TimeOfDayInterval> intervals;
  for (const auto& [type, from, to] : data) {
    Append(intervals, type, from, to);
  }

  return Timetable{std::move(intervals)};
}

inline TimeOfDayInterval ConstructInterval(const Day& day,
                                           std::string_view from,
                                           std::string_view to) {
  TimeOfDayInterval interval;
  interval.day_type = day;
  interval.range.open_from = TimeOfDayInterval::Time{from};
  interval.range.open_to = TimeOfDayInterval::Time{to};
  return interval;
}

}  // namespace test
}  // namespace grocery_shared::datetime
