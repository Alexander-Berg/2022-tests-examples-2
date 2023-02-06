#include <cctz/civil_time.h>
#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/curfew_config.hpp>

#include "utils/jsonfixtures.hpp"

namespace config {

bool operator==(const DayTime& left, const DayTime& right) {
  return left.hours == right.hours && left.minutes == right.minutes;
}

}  // namespace config

TEST(TestCurfewConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& curfew_config = config.Get<config::CurfewConfig>();

  ASSERT_EQ(curfew_config.curfew_rules.size(), 0u);
}

TEST(TestCurfewConfig, StandardParsingConfig) {
  const auto& curfew_rules_bson =
      JSONFixtures::GetFixtureBSON("curfew_config.json");
  config::DocsMap docs_map;
  docs_map.Insert("CURFEW_RULES", curfew_rules_bson);
  config::CurfewConfig curfew_config(docs_map);

  const auto& curfew_rules = curfew_config.curfew_rules;

  ASSERT_EQ(curfew_rules.size(), 2U);

  const auto& rule1 = curfew_rules[0];
  ASSERT_EQ(rule1.enabled, true);
  ASSERT_STREQ(rule1.message_key.c_str(), "some_tanker_key");
  ASSERT_FALSE(rule1.short_message_key);

  ASSERT_FALSE(rule1.countries);
  ASSERT_EQ(rule1.zones, std::set<std::string>{"bishkek"});
  ASSERT_FALSE(rule1.tariffs);

  const auto& intervals = rule1.intervals;
  ASSERT_EQ(intervals.size(), 2U);

  ASSERT_EQ(intervals[0].time_from, (config::DayTime{20, 0}));
  ASSERT_EQ(intervals[0].time_to, (config::DayTime{7, 0}));
  ASSERT_EQ(
      intervals[0].weekdays,
      (std::set<cctz::weekday>{cctz::weekday::monday, cctz::weekday::tuesday,
                               cctz::weekday::wednesday}));
  ASSERT_EQ(intervals[0].message_key, boost::none);

  ASSERT_EQ(intervals[1].time_from, (config::DayTime{9, 0}));
  ASSERT_EQ(intervals[1].time_to, (config::DayTime{12, 0}));
  ASSERT_EQ(intervals[1].weekdays, boost::none);
  ASSERT_STREQ(intervals[1].message_key->c_str(), "some_overriding_key");

  const auto& rule2 = curfew_rules[1];
  ASSERT_STREQ(rule2.message_key.c_str(), "some_tanker_key2");
  ASSERT_STREQ(rule2.short_message_key->c_str(), "some_short_message_key");
  ASSERT_EQ(rule2.countries, std::set<std::string>{"kgz"});
  ASSERT_FALSE(rule2.zones);
  ASSERT_EQ(rule2.tariffs, std::set<std::string>{"econom"});

  ASSERT_EQ(rule2.intervals.size(), 1U);
  // test on duplicates
  ASSERT_EQ(rule2.intervals[0].weekdays,
            (std::set<cctz::weekday>{cctz::weekday::wednesday}));
  ASSERT_EQ(rule2.intervals[0].message_key, boost::none);
}
