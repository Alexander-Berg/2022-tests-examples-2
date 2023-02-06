#include <gtest/gtest.h>

#include <utils/json.hpp>
#include <utils/time_suffixes.hpp>
#include <utils/translation_mock.hpp>
#include <utils/units.hpp>

void checks(const std::string& ans_time_to_string,
            const std::chrono::seconds& ans_get_time_time_seconds,
            const std::chrono::seconds& time, const std::string& locale,
            const l10n::Translations& translations, bool round_minutes) {
  EXPECT_EQ(ans_time_to_string, common::units::TimeToString(
                                    time, locale, translations, round_minutes));
  common::units::TimeInterval ansGetTime = {ans_time_to_string,
                                            ans_get_time_time_seconds};
  EXPECT_EQ(ansGetTime,
            common::units::GetTime(time, locale, translations, round_minutes));
}

TEST(Units, TimeToStingAndGetTime) {
  MockTranslations tr(true);

  checks("1 min", 1_min, 5_sec, "en", tr, false);
  checks("2 min", 2_min, 61_sec, "en", tr, false);
  checks("25 min", 25_min, 25_min, "en", tr, false);
  checks("37 min", 37_min, 37_min, "en", tr, false);
  checks("55 min", 55_min, 55_min, "en", tr, false);
  checks("56 min", 56_min, 56_min, "en", tr, false);
  checks("1 h", 1_hour, 59_min + 50_sec, "en", tr, false);
  checks("1 h 4 min", 1_hour + 4_min, 1_hour + 4_min, "en", tr, false);
  checks("1 h 5 min", 1_hour + 5_min, 1_hour + 5_min, "en", tr, false);
  checks("23 h 50 min", 23_hour + 50_min, 23_hour + 50_min, "en", tr, false);
  checks("23 h 51 min", 23_hour + 51_min, 23_hour + 51_min, "en", tr, false);
  checks("23 h 59 min", 23_hour + 59_min, 23_hour + 59_min, "en", tr, false);
  checks("1 d", 1_day, 23_hour + 59_min + 1_sec, "en", tr, false);
  checks("1 d 16 h", 1_day + 16_hour, 1_day + 16_hour, "en", tr, false);
  checks("2 d 23 h", 2_day + 23_hour, 2_day + 23_hour, "en", tr, false);
  checks("3 d", 3_day, 2_day + 23_hour + 1_sec, "en", tr, false);
  checks("8 d", 8_day, 7_day + 3_hour, "en", tr, false);

  checks("1 min", 1_min, 5_sec, "en", tr, true);
  checks("2 min", 2_min, 61_sec, "en", tr, true);
  checks("25 min", 25_min, 25_min, "en", tr, true);
  checks("40 min", 40_min, 37_min, "en", tr, true);
  checks("55 min", 55_min, 55_min, "en", tr, true);
  checks("1 h", 1_hour, 56_min, "en", tr, true);
  checks("1 h 10 min", 1_hour + 10_min, 1_hour + 4_min, "en", tr, true);
  checks("1 h 10 min", 1_hour + 10_min, 1_hour + 5_min, "en", tr, true);
  checks("23 h 50 min", 23_hour + 50_min, 23_hour + 50_min, "en", tr, true);
  checks("1 d", 1_day, 23_hour + 51_min, "en", tr, true);
  checks("1 d 16 h", 1_day + 16_hour, 1_day + 16_hour, "en", tr, true);
  checks("2 d 23 h", 2_day + 23_hour, 2_day + 23_hour, "en", tr, true);
  checks("3 d", 3_day, 2_day + 23_hour + 1_sec, "en", tr, true);
  checks("8 d", 8_day, 7_day + 3_hour, "en", tr, true);
}

TEST(Units, DistanceToString) {
  namespace units = common::units;

  MockTranslations tr(true);

  EXPECT_EQ("10 m", units::DistanceToString(0, "en", tr));
  EXPECT_EQ("10 m", units::DistanceToString(5, "en", tr));
  EXPECT_EQ("100 m", units::DistanceToString(99, "en", tr));
  EXPECT_EQ("700 m", units::DistanceToString(634, "en", tr));
  EXPECT_EQ("1.3 km", units::DistanceToString(1234, "en", tr));
  EXPECT_EQ("2 km", units::DistanceToString(1999, "en", tr));
  EXPECT_EQ("13 km", units::DistanceToString(12345, "en", tr));
}
