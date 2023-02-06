#include <grocery-shared/datetime/timetable.hpp>

#include <set>
#include <string_view>

#include <cctz/time_zone.h>
#include <userver/utest/utest.hpp>

#include <grocery-shared/datetime/datetime.hpp>
#include "common.hpp"

namespace grocery_shared::datetime {

namespace {
std::chrono::system_clock::time_point GetDayInMoscow(cctz::weekday weekday,
                                                     int hh_in_moscow_tz,
                                                     int mm) {
  auto time_point = test::GetMomentInUTC(
      2020, 5, 11 + static_cast<int>(weekday), hh_in_moscow_tz - 3, mm);
  EXPECT_EQ(test::GetWeekDay(time_point, test::kMoscowTimezone), weekday);
  return time_point;
}

void TestAvailableTill(
    const Timetable& timetable, std::chrono::system_clock::time_point now,
    const std::string& timezone,
    std::optional<std::chrono::system_clock::time_point> answer) {
  const auto to = timetable.GetAvailableTill(now, timezone);
  if (answer.has_value()) {
    EXPECT_TRUE(to.has_value());
    EXPECT_TRUE(to == answer);
  } else {
    EXPECT_TRUE(to == std::nullopt);
  }
}

void TestAvailableSince(
    const Timetable& timetable, std::chrono::system_clock::time_point now,
    const std::string& timezone,
    std::optional<std::chrono::system_clock::time_point> answer) {
  const auto to = timetable.GetAvailableSince(now, timezone);
  if (answer.has_value()) {
    EXPECT_TRUE(to.has_value());
    EXPECT_TRUE(to == answer);
  } else {
    EXPECT_TRUE(to == std::nullopt);
  }
}

}  // namespace

TEST(Timetable, Moscow_Friday) {
  auto time_moscow_08_59 = test::GetMomentInUTC(2020, 5, 15, 05, 59);
  auto time_moscow_09_00 = test::GetMomentInUTC(2020, 5, 15, 06, 00);
  auto time_moscow_13_00 = test::GetMomentInUTC(2020, 5, 15, 10, 00);
  auto time_moscow_19_00 = test::GetMomentInUTC(2020, 5, 15, 16, 00);
  auto time_moscow_22_59 = test::GetMomentInUTC(2020, 5, 15, 19, 59);
  auto time_moscow_23_01 = test::GetMomentInUTC(2020, 5, 15, 20, 01);
  auto time_moscow_00_00 = test::GetMomentInUTC(2020, 5, 14, 21, 00);

  EXPECT_EQ(test::GetWeekDay(time_moscow_13_00, test::kMoscowTimezone),
            cctz::weekday::friday);
  EXPECT_EQ(test::GetWeekDay(time_moscow_00_00, test::kMoscowTimezone),
            cctz::weekday::friday);

  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "23:00"}});

  EXPECT_FALSE(timetable.IsAvailable(time_moscow_08_59, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_09_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_13_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_19_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_22_59, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_23_01, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_00_00, test::kMoscowTimezone));
}

TEST(Timetable, Moscow_Friday_Wednesday) {
  auto time_moscow_fr_12_00 = test::GetMomentInUTC(2020, 5, 15, 9, 00);
  auto time_moscow_wed_12_00 = test::GetMomentInUTC(2020, 5, 13, 9, 00);
  auto time_moscow_wed_15_00 = test::GetMomentInUTC(2020, 5, 13, 12, 00);
  auto time_moscow_wed_20_29 = test::GetMomentInUTC(2020, 5, 13, 17, 29);
  auto time_moscow_wed_20_30 = test::GetMomentInUTC(2020, 5, 13, 17, 30);
  auto time_moscow_wed_20_31 = test::GetMomentInUTC(2020, 5, 13, 17, 31);

  EXPECT_EQ(test::GetWeekDay(time_moscow_fr_12_00, test::kMoscowTimezone),
            cctz::weekday::friday);
  EXPECT_EQ(test::GetWeekDay(time_moscow_wed_12_00, test::kMoscowTimezone),
            cctz::weekday::wednesday);

  const auto timetable =
      test::ConstructTimetable({{Day::kFriday, "09:00", "23:00"},  // split line
                                {Day::kWednesday, "14:00", "20:30"}});

  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_fr_12_00, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_wed_12_00, test::kMoscowTimezone));
  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_wed_15_00, test::kMoscowTimezone));
  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_wed_20_29, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_wed_20_30, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_wed_20_31, test::kMoscowTimezone));
}

TEST(Timetable, Moscow_Workday_Weekend) {
  auto time_moscow_sa_12_00 = test::GetMomentInUTC(2020, 5, 16, 9, 00);
  auto time_moscow_sa_15_00 = test::GetMomentInUTC(2020, 5, 16, 12, 00);

  auto time_moscow_sun_12_00 = test::GetMomentInUTC(2020, 5, 17, 9, 00);
  auto time_moscow_sun_15_00 = test::GetMomentInUTC(2020, 5, 17, 12, 00);

  auto time_moscow_wed_12_00 = test::GetMomentInUTC(2020, 5, 13, 9, 00);
  auto time_moscow_wed_16_00 = test::GetMomentInUTC(2020, 5, 13, 13, 00);

  EXPECT_EQ(test::GetWeekDay(time_moscow_wed_12_00, test::kMoscowTimezone),
            cctz::weekday::wednesday);
  EXPECT_EQ(test::GetWeekDay(time_moscow_sa_12_00, test::kMoscowTimezone),
            cctz::weekday::saturday);
  EXPECT_EQ(test::GetWeekDay(time_moscow_sun_12_00, test::kMoscowTimezone),
            cctz::weekday::sunday);

  const auto timetable = test::ConstructTimetable(
      {{Day::kWeekend, "10:00", "13:00"},  // split line
       {Day::kWorkday, "14:00", "18:00"}});

  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_sa_12_00, test::kMoscowTimezone));
  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_sun_12_00, test::kMoscowTimezone));

  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_sa_15_00, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_sun_15_00, test::kMoscowTimezone));

  EXPECT_FALSE(
      timetable.IsAvailable(time_moscow_wed_12_00, test::kMoscowTimezone));
  EXPECT_TRUE(
      timetable.IsAvailable(time_moscow_wed_16_00, test::kMoscowTimezone));
}

TEST(Timetable, Work_24h) {
  std::vector<std::string_view> times;
  times.push_back("00:00");
  times.push_back("24:00");

  for (const auto& from : times) {
    for (const auto& to : times) {
      const auto timetable =
          test::ConstructTimetable({{Day::kEveryday, from, to}});

      std::set<cctz::weekday> visited_weekdays;
      int base_day = 11;   // May 11, 2020  - it is Monday
      int base_hour = 21;  // 24 - 3, where -3 it Moscow timezone
      for (int day = 0; day < 7; ++day) {
        for (int hour = 0; hour < 24; ++hour) {
          auto time_moscow = test::GetMomentInUTC(2020, 5, base_day + day,
                                                  base_hour + hour, 00);

          visited_weekdays.insert(
              test::GetWeekDay(time_moscow, test::kMoscowTimezone));
          EXPECT_TRUE(
              timetable.IsAvailable(time_moscow, test::kMoscowTimezone));
        }
      }

      // Visit all weekday during for(...)
      EXPECT_EQ(visited_weekdays.size(), 7);
    }
  }
}

TEST(Timetable, Until_24h) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "10:00", "24:00"}});

  auto time_moscow_15_00 = test::GetMomentInUTC(2020, 5, 13, 12, 00);
  auto time_moscow_20_00 = test::GetMomentInUTC(2020, 5, 13, 17, 00);
  auto time_moscow_23_59 = test::GetMomentInUTC(2020, 5, 13, 20, 59);
  auto time_moscow_24_00 = test::GetMomentInUTC(2020, 5, 13, 21, 00);
  auto time_moscow_00_01 = test::GetMomentInUTC(2020, 5, 13, 21, 01);
  auto time_moscow_06_00 = test::GetMomentInUTC(2020, 5, 13, 03, 00);

  EXPECT_TRUE(timetable.IsAvailable(time_moscow_15_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_20_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_23_59, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_24_00, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_00_01, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_06_00, test::kMoscowTimezone));
}

TEST(Timetable, From_24h) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "24:00", "10:00"}});

  auto time_moscow_00_00 = test::GetMomentInUTC(2020, 5, 13, 21, 00);
  auto time_moscow_05_00 = test::GetMomentInUTC(2020, 5, 13, 02, 00);
  auto time_moscow_09_59 = test::GetMomentInUTC(2020, 5, 13, 06, 59);
  auto time_moscow_10_00 = test::GetMomentInUTC(2020, 5, 13, 07, 00);
  auto time_moscow_10_01 = test::GetMomentInUTC(2020, 5, 13, 07, 01);
  auto time_moscow_15_00 = test::GetMomentInUTC(2020, 5, 13, 12, 00);

  EXPECT_TRUE(timetable.IsAvailable(time_moscow_00_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_05_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_09_59, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_10_00, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_10_01, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_15_00, test::kMoscowTimezone));
}

TEST(Timetable, Right_Less_Than_Left) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "12:00", "06:00"}});

  auto time_moscow_12_00 = test::GetMomentInUTC(2020, 5, 13, 9, 00);
  auto time_moscow_15_00 = test::GetMomentInUTC(2020, 5, 13, 12, 00);
  auto time_moscow_23_00 = test::GetMomentInUTC(2020, 5, 13, 20, 00);
  auto time_moscow_24_00 = test::GetMomentInUTC(2020, 5, 13, 21, 00);
  auto time_moscow_05_00 = test::GetMomentInUTC(2020, 5, 13, 02, 00);
  auto time_moscow_06_00 = test::GetMomentInUTC(2020, 5, 13, 03, 00);
  auto time_moscow_06_01 = test::GetMomentInUTC(2020, 5, 13, 03, 01);
  auto time_moscow_10_00 = test::GetMomentInUTC(2020, 5, 13, 07, 00);

  EXPECT_TRUE(timetable.IsAvailable(time_moscow_12_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_15_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_23_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_24_00, test::kMoscowTimezone));
  EXPECT_TRUE(timetable.IsAvailable(time_moscow_05_00, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_06_00, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_06_01, test::kMoscowTimezone));
  EXPECT_FALSE(timetable.IsAvailable(time_moscow_10_00, test::kMoscowTimezone));
}

TEST(Timetable, AustraliaTimezone) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "08:00", "23:00"}});

  // 22:15 + 08:45 == 07:00 + day, where 08:45 - |kAustraliaEucla| timezone.
  auto time_australia_07_00 = test::GetMomentInUTC(2020, 5, 10, 22, 15);
  auto time_australia_08_00 = test::GetMomentInUTC(2020, 5, 10, 23, 15);
  auto time_australia_20_00 = test::GetMomentInUTC(2020, 5, 11, 11, 15);
  auto time_australia_23_30 = test::GetMomentInUTC(2020, 5, 11, 14, 45);

  EXPECT_EQ(test::GetWeekDay(time_australia_07_00, test::kAustraliaEucla),
            cctz::weekday::monday);

  EXPECT_FALSE(
      timetable.IsAvailable(time_australia_07_00, test::kAustraliaEucla));
  EXPECT_TRUE(
      timetable.IsAvailable(time_australia_08_00, test::kAustraliaEucla));
  EXPECT_TRUE(
      timetable.IsAvailable(time_australia_20_00, test::kAustraliaEucla));
  EXPECT_FALSE(
      timetable.IsAvailable(time_australia_23_30, test::kAustraliaEucla));
}

TEST(Timetable, Overlapping) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "20:00", "23:00"},
                                {Day::kEveryday, "12:00", "23:00"},
                                {Day::kWorkday, "16:00", "23:00"}});

  auto monday_moscow_17_00 = test::GetMomentInUTC(2020, 5, 11, 14, 00);
  EXPECT_EQ(test::GetWeekDay(monday_moscow_17_00, test::kMoscowTimezone),
            cctz::weekday::monday);
  // Available by kWorkday and kEveryday rule but kMonday has higher priority.
  EXPECT_FALSE(
      timetable.IsAvailable(monday_moscow_17_00, test::kMoscowTimezone));

  auto tuesday_moscow_14_00 = test::GetMomentInUTC(2020, 5, 12, 11, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_14_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);
  // Available by kEveryday but kWorkday has higher priority.
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_14_00, test::kMoscowTimezone));

  auto sunday_moscow_14_00 = test::GetMomentInUTC(2020, 5, 17, 11, 00);
  EXPECT_EQ(test::GetWeekDay(sunday_moscow_14_00, test::kMoscowTimezone),
            cctz::weekday::sunday);
  // Just available by kEveryday.
  EXPECT_TRUE(
      timetable.IsAvailable(sunday_moscow_14_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingWithPrevious) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "20:00", "10:00"},  // split
                                {Day::kTuesday, "12:00", "23:00"},
                                {Day::kWednesday, "12:00", "23:00"}});

  auto tuesday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 12, 06, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);
  auto wednesday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 13, 06, 00);
  EXPECT_EQ(test::GetWeekDay(wednesday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::wednesday);

  // Not available by kTuesday, but available by kMonday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_09_00, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(wednesday_moscow_09_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingWithEveryday) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "20:00", "10:00"},  // split
                                {Day::kTuesday, "12:00", "23:00"}});

  auto tuesday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 12, 06, 00);
  auto tuesday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 12, 12, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);

  auto wednesday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 13, 06, 00);
  auto wednesday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 13, 12, 00);
  EXPECT_EQ(test::GetWeekDay(wednesday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::wednesday);

  // Not available by kTuesday, but available by kEveryday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_09_00, test::kMoscowTimezone));
  // By kTuesday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_15_00, test::kMoscowTimezone));

  // By kEveryday
  EXPECT_TRUE(
      timetable.IsAvailable(wednesday_moscow_09_00, test::kMoscowTimezone));
  // Nu rule for wednesday
  EXPECT_FALSE(
      timetable.IsAvailable(wednesday_moscow_15_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingWithWeekend) {
  const auto timetable =
      test::ConstructTimetable({{Day::kWeekend, "20:00", "10:00"},  // split
                                {Day::kMonday, "12:00", "23:00"}});

  auto monday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 11, 06, 00);
  auto monday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 11, 12, 00);
  EXPECT_EQ(test::GetWeekDay(monday_moscow_15_00, test::kMoscowTimezone),
            cctz::weekday::monday);

  auto tuesday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 12, 06, 00);
  auto tuesday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 12, 12, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);

  // By weekend
  EXPECT_TRUE(
      timetable.IsAvailable(monday_moscow_09_00, test::kMoscowTimezone));
  // By kMonday
  EXPECT_TRUE(
      timetable.IsAvailable(monday_moscow_15_00, test::kMoscowTimezone));
  // No rule for tuesday
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_09_00, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_15_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingWithWorkdays) {
  const auto timetable =
      test::ConstructTimetable({{Day::kWorkday, "20:00", "10:00"},  // split
                                {Day::kSaturday, "12:00", "23:00"},
                                {Day::kSunday, "12:00", "23:00"}});

  auto saturday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 16, 06, 00);
  auto saturday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 16, 12, 00);
  EXPECT_EQ(test::GetWeekDay(saturday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::saturday);

  auto sunday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 17, 06, 00);
  auto sunday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 17, 12, 00);
  EXPECT_EQ(test::GetWeekDay(sunday_moscow_15_00, test::kMoscowTimezone),
            cctz::weekday::sunday);

  // By kWorkday
  EXPECT_TRUE(
      timetable.IsAvailable(saturday_moscow_09_00, test::kMoscowTimezone));
  // By kSaturday
  EXPECT_TRUE(
      timetable.IsAvailable(saturday_moscow_15_00, test::kMoscowTimezone));
  // No such rule for sunday
  EXPECT_FALSE(
      timetable.IsAvailable(sunday_moscow_09_00, test::kMoscowTimezone));
  // By kSunday
  EXPECT_TRUE(
      timetable.IsAvailable(sunday_moscow_15_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingWorkdaysAndWeekends) {
  const auto timetable =
      test::ConstructTimetable({{Day::kWorkday, "20:00", "10:00"},  // split
                                {Day::kWeekend, "12:00", "05:00"}});

  auto monday_moscow_04_00 = test::GetMomentInUTC(2020, 5, 11, 01, 00);
  auto monday_moscow_07_00 = test::GetMomentInUTC(2020, 5, 11, 04, 00);
  auto monday_moscow_21_00 = test::GetMomentInUTC(2020, 5, 11, 18, 00);
  EXPECT_EQ(test::GetWeekDay(monday_moscow_04_00, test::kMoscowTimezone),
            cctz::weekday::monday);

  auto saturday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 16, 06, 00);
  auto saturday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 16, 12, 00);
  EXPECT_EQ(test::GetWeekDay(saturday_moscow_09_00, test::kMoscowTimezone),
            cctz::weekday::saturday);

  auto sunday_moscow_09_00 = test::GetMomentInUTC(2020, 5, 17, 06, 00);
  auto sunday_moscow_15_00 = test::GetMomentInUTC(2020, 5, 17, 12, 00);
  EXPECT_EQ(test::GetWeekDay(sunday_moscow_15_00, test::kMoscowTimezone),
            cctz::weekday::sunday);

  // By kWorkday
  EXPECT_TRUE(
      timetable.IsAvailable(saturday_moscow_09_00, test::kMoscowTimezone));
  // By kWeekend
  EXPECT_TRUE(
      timetable.IsAvailable(saturday_moscow_15_00, test::kMoscowTimezone));

  // No such rule for sunday
  EXPECT_FALSE(
      timetable.IsAvailable(sunday_moscow_09_00, test::kMoscowTimezone));
  // By kWeekend
  EXPECT_TRUE(
      timetable.IsAvailable(sunday_moscow_15_00, test::kMoscowTimezone));

  // By kWeekend
  EXPECT_TRUE(
      timetable.IsAvailable(monday_moscow_04_00, test::kMoscowTimezone));
  // kWeekend ends at 05:00
  EXPECT_FALSE(
      timetable.IsAvailable(monday_moscow_07_00, test::kMoscowTimezone));
  // By kWorkday
  EXPECT_TRUE(
      timetable.IsAvailable(monday_moscow_21_00, test::kMoscowTimezone));
}

TEST(Timetable, NotOverlappingLogicallyNotAvailable) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "20:00", "10:00"},  // split
                                {Day::kMonday, "12:00", "20:00"},
                                {Day::kTuesday, "12:00", "20:00"}});

  auto tuesday_moscow_04_00 = test::GetMomentInUTC(2020, 5, 12, 01, 00);
  auto tuesday_moscow_08_00 = test::GetMomentInUTC(2020, 5, 12, 05, 00);
  auto tuesday_moscow_13_00 = test::GetMomentInUTC(2020, 5, 12, 10, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_04_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);

  auto friday_moscow_04_00 = test::GetMomentInUTC(2020, 5, 15, 01, 00);
  auto friday_moscow_08_00 = test::GetMomentInUTC(2020, 5, 15, 05, 00);
  auto friday_moscow_13_00 = test::GetMomentInUTC(2020, 5, 15, 10, 00);
  EXPECT_EQ(test::GetWeekDay(friday_moscow_04_00, test::kMoscowTimezone),
            cctz::weekday::friday);

  // By kMonday
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_04_00, test::kMoscowTimezone));
  // By kMonday
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_08_00, test::kMoscowTimezone));
  // By kTuesday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_13_00, test::kMoscowTimezone));

  // By kEveryday
  EXPECT_TRUE(
      timetable.IsAvailable(friday_moscow_04_00, test::kMoscowTimezone));
  EXPECT_TRUE(
      timetable.IsAvailable(friday_moscow_08_00, test::kMoscowTimezone));
  EXPECT_FALSE(
      timetable.IsAvailable(friday_moscow_13_00, test::kMoscowTimezone));
}

TEST(Timetable, OverlappingPriority) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "20:00", "10:00"},  // split
                                {Day::kMonday, "20:00", "05:00"},
                                {Day::kTuesday, "12:00", "20:00"}});

  auto tuesday_moscow_04_00 = test::GetMomentInUTC(2020, 5, 12, 01, 00);
  auto tuesday_moscow_08_00 = test::GetMomentInUTC(2020, 5, 12, 05, 00);
  auto tuesday_moscow_13_00 = test::GetMomentInUTC(2020, 5, 12, 10, 00);
  EXPECT_EQ(test::GetWeekDay(tuesday_moscow_04_00, test::kMoscowTimezone),
            cctz::weekday::tuesday);

  // By kMonday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_04_00, test::kMoscowTimezone));
  // By kMonday
  EXPECT_FALSE(
      timetable.IsAvailable(tuesday_moscow_08_00, test::kMoscowTimezone));
  // By kTuesday
  EXPECT_TRUE(
      timetable.IsAvailable(tuesday_moscow_13_00, test::kMoscowTimezone));
}

TEST(Timetable_AvailableTill, Basic) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "20:00"}});

  auto tuesday_moscow_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  auto tuesday_moscow_21_00 = GetDayInMoscow(cctz::weekday::tuesday, 21, 00);

  auto end_for_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 20, 00);
  TestAvailableTill(timetable, tuesday_moscow_13_00, test::kMoscowTimezone,
                    end_for_13_00);
  TestAvailableTill(timetable, tuesday_moscow_21_00, test::kMoscowTimezone,
                    std::nullopt);
}

TEST(Timetable_AvailableTill, Till_00_00) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "07:00", "00:00"}});

  auto tuesday_moscow_16_00 = GetDayInMoscow(cctz::weekday::tuesday, 16, 00);

  auto end_for_16_00 = GetDayInMoscow(cctz::weekday::wednesday, 00, 00);
  TestAvailableTill(timetable, tuesday_moscow_16_00, test::kMoscowTimezone,
                    end_for_16_00);
}

TEST(Timetable_AvailableTill, RoundMinutes) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "07:00", "00:00"}});

  auto now_seconds = cctz::civil_second(2020, 5, 12, 10, 30, 13 /* ss */);
  auto now_std =
      cctz::convert(now_seconds, LoadCachedTimeZone(test::kMoscowTimezone));
  EXPECT_EQ(test::GetWeekDay(now_std, test::kMoscowTimezone),
            cctz::weekday::tuesday);

  auto end_for_16_00 = GetDayInMoscow(cctz::weekday::wednesday, 00, 00);
  TestAvailableTill(timetable, now_std, test::kMoscowTimezone, end_for_16_00);
}

TEST(Timetable_AvailableTill, BasicPriority) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "20:00"},
                                {Day::kMonday, "09:00", "15:00"},
                                {Day::kWeekend, "09:00", "23:00"}});

  auto monday_moscow_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);
  auto tuesday_moscow_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  auto sunday_moscow_13_00 = GetDayInMoscow(cctz::weekday::sunday, 13, 00);

  auto end_for_monday = GetDayInMoscow(cctz::weekday::monday, 15, 00);
  TestAvailableTill(timetable, monday_moscow_13_00, test::kMoscowTimezone,
                    end_for_monday);

  auto end_for_tuesday = GetDayInMoscow(cctz::weekday::tuesday, 20, 00);
  TestAvailableTill(timetable, tuesday_moscow_13_00, test::kMoscowTimezone,
                    end_for_tuesday);

  auto end_for_sunday = GetDayInMoscow(cctz::weekday::sunday, 23, 00);
  TestAvailableTill(timetable, sunday_moscow_13_00, test::kMoscowTimezone,
                    end_for_sunday);
}

TEST(Timetable_AvailableTill, Overlapping) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "09:00", "06:00"},
                                {Day::kTuesday, "06:00", "15:00"},
                                {Day::kWednesday, "10:00", "20:00"}});

  auto monday_moscow_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);
  auto tuesday_moscow_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  auto wednesday_moscow_13_00 =
      GetDayInMoscow(cctz::weekday::wednesday, 13, 00);

  // monday, 13:00 + 24h
  auto end_for_monday = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  TestAvailableTill(timetable, monday_moscow_13_00, test::kMoscowTimezone,
                    end_for_monday);

  auto end_for_tuesday = GetDayInMoscow(cctz::weekday::tuesday, 15, 00);
  TestAvailableTill(timetable, tuesday_moscow_13_00, test::kMoscowTimezone,
                    end_for_tuesday);

  auto end_for_wednesday = GetDayInMoscow(cctz::weekday::wednesday, 20, 00);
  TestAvailableTill(timetable, wednesday_moscow_13_00, test::kMoscowTimezone,
                    end_for_wednesday);
}

TEST(Timetable_AvailableTill, Overlapping_24Hours) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "00:00", "24:00"},  // split
                                {Day::kFriday, "10:00", "21:00"}});

  auto monday_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);
  auto friday_13_00 = GetDayInMoscow(cctz::weekday::friday, 13, 00);

  // monday 13:00 + 24h
  auto end_for_monday = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  TestAvailableTill(timetable, monday_13_00, test::kMoscowTimezone,
                    end_for_monday);

  auto end_for_friday = GetDayInMoscow(cctz::weekday::friday, 21, 00);
  TestAvailableTill(timetable, friday_13_00, test::kMoscowTimezone,
                    end_for_friday);
}

TEST(Timetable_AvailableTill, Overlapping_24Hours_EveryDay) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "00:00", "24:00"}});

  auto monday_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);

  // monday 13:00 + 24h
  auto end_for_monday = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  TestAvailableTill(timetable, monday_13_00, test::kMoscowTimezone,
                    end_for_monday);
}

TEST(Timetable_AvailableTill, SeveralIntervalsInOneDay) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "10:00", "15:00"},  // split
                                {Day::kMonday, "15:30", "21:00"}});

  auto monday_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);
  auto monday_15_15 = GetDayInMoscow(cctz::weekday::monday, 15, 15);
  auto monday_16_00 = GetDayInMoscow(cctz::weekday::monday, 16, 00);

  auto end_for_13_00 = GetDayInMoscow(cctz::weekday::monday, 15, 00);
  TestAvailableTill(timetable, monday_13_00, test::kMoscowTimezone,
                    end_for_13_00);

  TestAvailableTill(timetable, monday_15_15, test::kMoscowTimezone,
                    std::nullopt);

  auto end_for_16_00 = GetDayInMoscow(cctz::weekday::monday, 21, 00);
  TestAvailableTill(timetable, monday_16_00, test::kMoscowTimezone,
                    end_for_16_00);
}

TEST(Timetable_AvailableTill, PriorityPartyHard) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "10:00", "00:00"},
                                {Day::kWorkday, "00:00", "05:00"},
                                {Day::kTuesday, "00:00", "06:00"},
                                {Day::kTuesday, "13:00", "20:00"},
                                {Day::kWeekend, "20:00", "10:00"}});

  auto monday_13_00 = GetDayInMoscow(cctz::weekday::monday, 13, 00);
  auto tuesday_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 13, 00);
  auto friday_00_30 = GetDayInMoscow(cctz::weekday::friday, 00, 30);
  auto sunday_20_00 = GetDayInMoscow(cctz::weekday::sunday, 20, 00);

  auto end_for_monday = GetDayInMoscow(cctz::weekday::tuesday, 06, 00);
  TestAvailableTill(timetable, monday_13_00, test::kMoscowTimezone,
                    end_for_monday);

  auto end_for_tuesday_13_00 = GetDayInMoscow(cctz::weekday::tuesday, 20, 00);
  TestAvailableTill(timetable, tuesday_13_00, test::kMoscowTimezone,
                    end_for_tuesday_13_00);

  auto end_for_friday = GetDayInMoscow(cctz::weekday::friday, 05, 00);
  TestAvailableTill(timetable, friday_00_30, test::kMoscowTimezone,
                    end_for_friday);

  // Monday, 20:00 (sunday 20:00 + 24h).
  auto end_for_sunday = test::GetMomentInUTC(2020, 5, 18, 17, 00);
  EXPECT_EQ(test::GetWeekDay(end_for_sunday, test::kMoscowTimezone),
            cctz::weekday::monday);
  TestAvailableTill(timetable, sunday_20_00, test::kMoscowTimezone,
                    end_for_sunday);
}

TEST(Timetable_AvailableSince, Basic) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "10:00", "23:00"}});

  auto monday_06_00 = GetDayInMoscow(cctz::weekday::monday, 06, 00);
  auto monday_23_30 = GetDayInMoscow(cctz::weekday::monday, 23, 30);

  auto start_for_monday_06_00 = GetDayInMoscow(cctz::weekday::monday, 10, 00);
  TestAvailableSince(timetable, monday_06_00, test::kMoscowTimezone,
                     start_for_monday_06_00);

  auto start_for_monday_23_30 = GetDayInMoscow(cctz::weekday::tuesday, 10, 00);
  TestAvailableSince(timetable, monday_23_30, test::kMoscowTimezone,
                     start_for_monday_23_30);
}

TEST(Timetable_AvailableSince, BasicPriority) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "09:00", "20:00"},
                                {Day::kMonday, "10:00", "15:00"},
                                {Day::kWeekend, "13:00", "23:00"}});

  auto monday_07_00 = GetDayInMoscow(cctz::weekday::monday, 07, 00);
  auto monday_16_00 = GetDayInMoscow(cctz::weekday::monday, 16, 00);
  auto tuesday_07_00 = GetDayInMoscow(cctz::weekday::tuesday, 07, 00);
  auto friday_21_00 = GetDayInMoscow(cctz::weekday::friday, 21, 00);
  auto sunday_10_00 = GetDayInMoscow(cctz::weekday::sunday, 10, 00);

  auto start_for_monday_07_00 = GetDayInMoscow(cctz::weekday::monday, 10, 00);
  TestAvailableSince(timetable, monday_07_00, test::kMoscowTimezone,
                     start_for_monday_07_00);

  auto start_for_monday_16_00 = GetDayInMoscow(cctz::weekday::tuesday, 9, 00);
  TestAvailableSince(timetable, monday_16_00, test::kMoscowTimezone,
                     start_for_monday_16_00);

  auto start_for_tuesday = GetDayInMoscow(cctz::weekday::tuesday, 9, 00);
  TestAvailableSince(timetable, tuesday_07_00, test::kMoscowTimezone,
                     start_for_tuesday);

  auto start_for_friday = GetDayInMoscow(cctz::weekday::saturday, 13, 00);
  TestAvailableSince(timetable, friday_21_00, test::kMoscowTimezone,
                     start_for_friday);

  auto start_for_sunday = GetDayInMoscow(cctz::weekday::sunday, 13, 00);
  TestAvailableSince(timetable, sunday_10_00, test::kMoscowTimezone,
                     start_for_sunday);
}

TEST(Timetable_AvailableSince, Test_24Hours) {
  const auto timetable =
      test::ConstructTimetable({{Day::kEveryday, "00:00", "24:00"},  // split
                                {Day::kFriday, "10:00", "21:00"}});

  auto friday_07_00 = GetDayInMoscow(cctz::weekday::friday, 07, 00);
  auto friday_20_00 = GetDayInMoscow(cctz::weekday::friday, 20, 00);
  auto friday_21_30 = GetDayInMoscow(cctz::weekday::friday, 21, 30);

  auto start_for_07_00 = GetDayInMoscow(cctz::weekday::friday, 10, 00);
  TestAvailableSince(timetable, friday_07_00, test::kMoscowTimezone,
                     start_for_07_00);

  TestAvailableSince(timetable, friday_20_00, test::kMoscowTimezone,
                     std::nullopt);

  auto start_for_21_30 = GetDayInMoscow(cctz::weekday::saturday, 00, 00);
  TestAvailableSince(timetable, friday_21_30, test::kMoscowTimezone,
                     start_for_21_30);
}

TEST(Timetable_AvailableSince, Holes) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "10:00", "20:00"},  // split
                                {Day::kFriday, "09:00", "21:00"}});

  auto monday_07_00 = GetDayInMoscow(cctz::weekday::monday, 07, 00);
  auto monday_20_30 = GetDayInMoscow(cctz::weekday::monday, 20, 30);
  auto friday_07_00 = GetDayInMoscow(cctz::weekday::friday, 07, 00);
  auto friday_21_30 = GetDayInMoscow(cctz::weekday::friday, 21, 30);

  auto start_for_monday_07_00 = GetDayInMoscow(cctz::weekday::monday, 10, 00);
  TestAvailableSince(timetable, monday_07_00, test::kMoscowTimezone,
                     start_for_monday_07_00);

  auto start_for_monday_20_30 = GetDayInMoscow(cctz::weekday::friday, 9, 00);
  TestAvailableSince(timetable, monday_20_30, test::kMoscowTimezone,
                     start_for_monday_20_30);

  auto start_for_friday_07_00 = GetDayInMoscow(cctz::weekday::friday, 9, 00);
  TestAvailableSince(timetable, friday_07_00, test::kMoscowTimezone,
                     start_for_friday_07_00);

  // Monday, 10:00 next week.
  auto start_for_friday_21_30 = test::GetMomentInUTC(2020, 5, 18, 07, 00);
  EXPECT_EQ(test::GetWeekDay(start_for_friday_21_30, test::kMoscowTimezone),
            cctz::weekday::monday);
  TestAvailableSince(timetable, friday_21_30, test::kMoscowTimezone,
                     start_for_friday_21_30);
}

TEST(Timetable_AvailableSince, SeveralIntervalsInOneDay) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "10:00", "15:00"},  // split
                                {Day::kMonday, "15:30", "21:00"}});

  auto monday_07_00 = GetDayInMoscow(cctz::weekday::monday, 07, 00);
  auto monday_15_15 = GetDayInMoscow(cctz::weekday::monday, 15, 15);
  auto monday_21_30 = GetDayInMoscow(cctz::weekday::monday, 21, 30);

  auto start_for_07_00 = GetDayInMoscow(cctz::weekday::monday, 10, 00);
  TestAvailableSince(timetable, monday_07_00, test::kMoscowTimezone,
                     start_for_07_00);

  auto start_for_15_15 = GetDayInMoscow(cctz::weekday::monday, 15, 30);
  TestAvailableSince(timetable, monday_15_15, test::kMoscowTimezone,
                     start_for_15_15);

  // Monday, 10:00 next week.
  auto start_for_21_30 = test::GetMomentInUTC(2020, 5, 18, 07, 00);
  TestAvailableSince(timetable, monday_21_30, test::kMoscowTimezone,
                     start_for_21_30);
}

TEST(Timetable_AvailableSince, PriorityPartyHard) {
  const auto timetable =
      test::ConstructTimetable({{Day::kMonday, "13:00", "05:00"},
                                {Day::kWorkday, "10:00", "21:00"},
                                {Day::kEveryday, "14:00", "15:00"},
                                {Day::kWeekend, "09:00", "19:00"}});

  auto tuesday_07_00 = GetDayInMoscow(cctz::weekday::tuesday, 07, 00);
  auto start_for_tuesday_07_00 = GetDayInMoscow(cctz::weekday::tuesday, 10, 00);
  TestAvailableSince(timetable, tuesday_07_00, test::kMoscowTimezone,
                     start_for_tuesday_07_00);

  auto tuesday_21_30 = GetDayInMoscow(cctz::weekday::tuesday, 21, 30);
  auto start_for_tuesday_21_30 =
      GetDayInMoscow(cctz::weekday::wednesday, 10, 00);
  TestAvailableSince(timetable, tuesday_21_30, test::kMoscowTimezone,
                     start_for_tuesday_21_30);

  auto friday_21_30 = GetDayInMoscow(cctz::weekday::friday, 21, 30);
  auto start_for_friday_21_30 = GetDayInMoscow(cctz::weekday::saturday, 9, 00);
  TestAvailableSince(timetable, friday_21_30, test::kMoscowTimezone,
                     start_for_friday_21_30);

  auto saturday_20_00 = GetDayInMoscow(cctz::weekday::saturday, 20, 00);
  auto start_for_saturday_20_00 = GetDayInMoscow(cctz::weekday::sunday, 9, 00);
  TestAvailableSince(timetable, saturday_20_00, test::kMoscowTimezone,
                     start_for_saturday_20_00);

  auto sunday_20_00 = GetDayInMoscow(cctz::weekday::sunday, 20, 00);
  // Monday, 13:00 next week.
  auto start_for_sunday_20_00 = test::GetMomentInUTC(2020, 5, 18, 10, 00);
  TestAvailableSince(timetable, sunday_20_00, test::kMoscowTimezone,
                     start_for_sunday_20_00);
}

TEST(TimeOfDayInterval_IntersectsWith, Sunday_Monday) {
  TimeOfDayInterval first, second;

  // Weekend -> Monday
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Sunday -> Monday
  first = test::ConstructInterval(Day::kSunday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend -> Workday
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWorkday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // kSunday -> Workday
  first = test::ConstructInterval(Day::kSunday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWorkday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday -> Monday
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday -> Workday
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWorkday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // No intersection
  // Weekend -> Monday
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Weekend -> Tuesday
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "08:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Sunday -> Monday
  first = test::ConstructInterval(Day::kSunday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Sunday -> Tuesday
  first = test::ConstructInterval(Day::kSunday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "08:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Weekend -> Workday
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWorkday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Everyday -> Monday
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Saturday -> Monday
  first = test::ConstructInterval(Day::kSaturday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kMonday, "08:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));
}

TEST(TimeOfDayInterval_IntersectsWith, Friday_Saturday) {
  TimeOfDayInterval first, second;

  // Friday -> Saturday
  first = test::ConstructInterval(Day::kFriday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSaturday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday -> Saturday
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSaturday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday -> Saturday
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSaturday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Friday -> Weekend
  first = test::ConstructInterval(Day::kFriday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday -> Weekend
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday -> Weekend
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // No intersection
  // Friday -> Saturday
  first = test::ConstructInterval(Day::kFriday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSaturday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Friday -> Sunday
  first = test::ConstructInterval(Day::kFriday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSunday, "08:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Workday -> Saturday
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSaturday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Workday -> Sunday
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kSunday, "08:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Friday -> Weekend
  first = test::ConstructInterval(Day::kFriday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Everyday -> Weekend
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));
}

TEST(TimeOfDayInterval_IntersectsWith, SameType) {
  const auto check_same_type = [](Day day_type) {
    TimeOfDayInterval first, second;

    // Same interval
    first = test::ConstructInterval(day_type, "10:00", "18:00");
    second = test::ConstructInterval(day_type, "10:00", "18:00");
    EXPECT_TRUE(first.IntersectsWith(second));
    EXPECT_TRUE(second.IntersectsWith(first));

    // Simple intersection
    first = test::ConstructInterval(day_type, "10:00", "18:00");
    second = test::ConstructInterval(day_type, "12:00", "20:00");
    EXPECT_TRUE(first.IntersectsWith(second));
    EXPECT_TRUE(second.IntersectsWith(first));

    // Simple intersection with next day overlap
    first = test::ConstructInterval(day_type, "10:00", "20:00");
    second = test::ConstructInterval(day_type, "18:00", "08:00");
    EXPECT_TRUE(first.IntersectsWith(second));
    EXPECT_TRUE(second.IntersectsWith(first));

    // Inside
    first = test::ConstructInterval(day_type, "10:00", "20:00");
    second = test::ConstructInterval(day_type, "12:00", "18:00");
    EXPECT_TRUE(first.IntersectsWith(second));
    EXPECT_TRUE(second.IntersectsWith(first));

    // Inside with next day overlap
    first = test::ConstructInterval(day_type, "21:00", "08:00");
    second = test::ConstructInterval(day_type, "22:00", "23:00");
    EXPECT_TRUE(first.IntersectsWith(second));
    EXPECT_TRUE(second.IntersectsWith(first));

    // Simple no intersection
    first = test::ConstructInterval(day_type, "10:00", "18:00");
    second = test::ConstructInterval(day_type, "18:00", "20:00");
    EXPECT_FALSE(first.IntersectsWith(second));
    EXPECT_FALSE(second.IntersectsWith(first));

    // Overlap no intersection
    first = test::ConstructInterval(day_type, "20:00", "10:00");
    second = test::ConstructInterval(day_type, "10:00", "20:00");
    EXPECT_FALSE(first.IntersectsWith(second));
    EXPECT_FALSE(second.IntersectsWith(first));
  };
  check_same_type(Day::kMonday);
  check_same_type(Day::kTuesday);
  check_same_type(Day::kWednesday);
  check_same_type(Day::kThursday);
  check_same_type(Day::kFriday);
  check_same_type(Day::kSunday);
  check_same_type(Day::kSaturday);
  check_same_type(Day::kWorkday);
  check_same_type(Day::kWeekend);
  check_same_type(Day::kEveryday);
}

TEST(TimeOfDayInterval_IntersectsWith, Misc) {
  TimeOfDayInterval first, second;

  // Monday-tuesday overlap
  first = test::ConstructInterval(Day::kMonday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Monday-tuesday full overlap
  first = test::ConstructInterval(Day::kMonday, "20:00", "14:00");
  second = test::ConstructInterval(Day::kTuesday, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday-tuesday overlap
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday simple
  first = test::ConstructInterval(Day::kTuesday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWorkday, "12:00", "20:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday workday overlap
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWorkday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Workday workday full overlap
  first = test::ConstructInterval(Day::kWorkday, "20:00", "14:00");
  second = test::ConstructInterval(Day::kWorkday, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend simple
  first = test::ConstructInterval(Day::kSunday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWeekend, "12:00", "20:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend-sunday overlap
  first = test::ConstructInterval(Day::kSunday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWeekend, "22:00", "11:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend-sunday full overlap
  first = test::ConstructInterval(Day::kWeekend, "20:00", "14:00");
  second = test::ConstructInterval(Day::kSunday, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend Weekend overlap
  first = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  second = test::ConstructInterval(Day::kWeekend, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Weekend Weekend full overlap
  first = test::ConstructInterval(Day::kWeekend, "20:00", "14:00");
  second = test::ConstructInterval(Day::kWeekend, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday simple
  first = test::ConstructInterval(Day::kEveryday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWednesday, "12:00", "20:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Wednesday-everyday overlap
  first = test::ConstructInterval(Day::kWednesday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kEveryday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Wednesday-everyday full overlap
  first = test::ConstructInterval(Day::kWednesday, "20:00", "14:00");
  second = test::ConstructInterval(Day::kEveryday, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday Everyday overlap
  first = test::ConstructInterval(Day::kEveryday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kEveryday, "08:00", "18:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));

  // Everyday Everyday full overlap
  first = test::ConstructInterval(Day::kEveryday, "20:00", "14:00");
  second = test::ConstructInterval(Day::kEveryday, "08:00", "14:00");
  EXPECT_TRUE(first.IntersectsWith(second));
  EXPECT_TRUE(second.IntersectsWith(first));
}

TEST(TimeOfDayInterval_IntersectsWith, NoIntersection) {
  TimeOfDayInterval first, second;

  // Monday-tuesday overlap
  first = test::ConstructInterval(Day::kMonday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kMonday, "18:00", "12:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Monday-tuesday simple
  first = test::ConstructInterval(Day::kMonday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Workday simple
  first = test::ConstructInterval(Day::kWorkday, "20:00", "10:00");
  second = test::ConstructInterval(Day::kTuesday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Workday-monday overlap
  first = test::ConstructInterval(Day::kWorkday, "20:00", "12:00");
  second = test::ConstructInterval(Day::kMonday, "10:00", "18:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Tuesday-workday simple
  first = test::ConstructInterval(Day::kTuesday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWorkday, "18:00", "20:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Weekend simple
  first = test::ConstructInterval(Day::kSunday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWeekend, "18:00", "20:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Saturday-Weekend overlap
  first = test::ConstructInterval(Day::kSaturday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWeekend, "18:00", "12:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Sunday-Weekend overlap
  first = test::ConstructInterval(Day::kSunday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWeekend, "20:00", "10:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Everyday simple
  first = test::ConstructInterval(Day::kEveryday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWednesday, "18:00", "20:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));

  // Wednesday-everyday overlap
  first = test::ConstructInterval(Day::kEveryday, "10:00", "18:00");
  second = test::ConstructInterval(Day::kWednesday, "20:00", "10:00");
  EXPECT_FALSE(first.IntersectsWith(second));
  EXPECT_FALSE(second.IntersectsWith(first));
}

TEST(Timetable_IntersectsWith, Misc) {
  const auto test_timetable =
      test::ConstructTimetable({{Day::kMonday, "10:00", "00:00"},
                                {Day::kTuesday, "00:00", "06:00"},
                                {Day::kTuesday, "13:00", "20:00"},
                                {Day::kSaturday, "20:00", "10:00"}});

  // Monday
  auto other_timetable =
      test::ConstructTimetable({{Day::kMonday, "12:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kMonday, "00:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));

  // Weekday
  other_timetable = test::ConstructTimetable({{Day::kTuesday, "5:00", "9:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "6:00", "13:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "10:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));

  // Saturday
  other_timetable =
      test::ConstructTimetable({{Day::kSaturday, "18:00", "20:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSaturday, "20:00", "24:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));

  // Sunday
  other_timetable = test::ConstructTimetable({{Day::kSunday, "9:00", "14:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "10:00", "24:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));

  // Workday
  other_timetable = test::ConstructTimetable({{Day::kWorkday, "5:00", "9:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "6:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "10:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));

  // Everyday
  other_timetable =
      test::ConstructTimetable({{Day::kEveryday, "5:00", "9:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kEveryday, "6:00", "10:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kEveryday, "10:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));

  // Weekend
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "9:00", "14:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "10:00", "20:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
}

TEST(Timetable_IntersectsWith, Everyday) {
  const auto test_timetable = test::ConstructTimetable(
      {{Day::kEveryday, "10:00", "18:00"}, {Day::kEveryday, "22:00", "05:00"}});
  auto other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "10:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "00:00", "06:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "10:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "10:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
}

TEST(Timetable_IntersectsWith, Workday) {
  const auto test_timetable = test::ConstructTimetable(
      {{Day::kWorkday, "10:00", "18:00"}, {Day::kWorkday, "22:00", "05:00"}});
  auto other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "10:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSaturday, "00:00", "06:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "10:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "04:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "00:00", "06:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSaturday, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
}

TEST(Timetable_IntersectsWith, Weekend) {
  const auto test_timetable = test::ConstructTimetable(
      {{Day::kWeekend, "10:00", "18:00"}, {Day::kWeekend, "22:00", "05:00"}});
  auto other_timetable =
      test::ConstructTimetable({{Day::kMonday, "04:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "00:00", "06:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "04:00", "18:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "10:00", "15:00"}});
  EXPECT_TRUE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kMonday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kTuesday, "04:00", "18:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kSunday, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWorkday, "05:00", "10:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
  other_timetable =
      test::ConstructTimetable({{Day::kWeekend, "18:00", "22:00"}});
  EXPECT_FALSE(test_timetable.IntersectsWith(other_timetable));
}

}  // namespace grocery_shared::datetime
