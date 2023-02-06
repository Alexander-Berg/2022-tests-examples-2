#include <gtest/gtest.h>

#include <fstream>

#include <cctz/civil_time.h>

#include <clients/billing_subventions.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include <utils/helpers/json.hpp>

namespace {

namespace bs = clients::billing_subventions;

const std::string kDirName = std::string(SOURCE_DIR) + "/tests/static/";

std::string ReadFile(const std::string& filename) {
  std::ifstream file(kDirName + filename);
  return std::string{std::istreambuf_iterator<char>(file),
                     std::istreambuf_iterator<char>()};
}

Json::Value ReadJson(const std::string& filename) {
  auto file = ReadFile(filename);
  Json::Value doc;
  if (!utils::helpers::TryParseJson(file, doc, {})) {
    throw utils::helpers::JsonMemberTypeError("Failed to parse json - " +
                                              filename);
  }
  return doc;
}

}  // namespace

TEST(TestClientBillingSubventions, CheckParseDailyGuarantee) {
  const auto& doc = ReadJson("daily_guarantee_rule.json");
  std::unique_ptr<bs::DailyGuaranteeSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_unique<bs::DailyGuaranteeSubvention>(doc, LogExtra()));

  ASSERT_EQ(rule->tariff_zones.size(), 1u);
  ASSERT_EQ(rule->tariff_zones[0], "moscow");
  ASSERT_EQ(rule->start_time.time_since_epoch().count(), 1525179600000000000);
  ASSERT_EQ(rule->end_time.time_since_epoch().count(), 1535806800000000000);
  ASSERT_EQ(rule->type, bs::subvention_rule_types::kDailyGuarantee);
  ASSERT_EQ(rule->acceptance_rate, 0.5);
  ASSERT_EQ(rule->completion_rate, 0.6);
  ASSERT_FALSE(rule->payment_type);

  ASSERT_EQ(rule->is_personal, false);
  ASSERT_EQ(rule->ticket_name, "TAXIRATE-111");
  ASSERT_EQ(rule->rule_id, "rule_id1");
  ASSERT_EQ(rule->drivers_count, 0u);
  ASSERT_EQ(rule->cursor, "2018-09-01T13:00:00.000000+00:00/rule_id1");
  ASSERT_EQ(rule->tags.size(), 1u);
  ASSERT_EQ(rule->tags[0], "cool_tag");
  ASSERT_EQ(rule->time_zone->id, "Asia/Yekaterinburg");
  ASSERT_EQ(rule->time_zone->offset, "+05:00");
  ASSERT_EQ(rule->tariff_classes.size(), 1u);
  ASSERT_EQ(rule->tariff_classes[0], "econom");
  ASSERT_EQ(rule->currency, "RUB");
  ASSERT_EQ(rule->visible_to_driver, true);
  ASSERT_EQ(*rule->days_span, 1);

  ASSERT_EQ(rule->trips_bounds.size(), 2u);
  ASSERT_EQ(rule->trips_bounds[0].lower_bound, 10);
  ASSERT_EQ(rule->trips_bounds[0].upper_bound, 14);
  ASSERT_EQ(rule->trips_bounds[0].bonus_amount, 100.0);
  ASSERT_EQ(rule->trips_bounds[1].lower_bound, 15);
  ASSERT_FALSE(rule->trips_bounds[1].upper_bound);
  ASSERT_EQ(rule->trips_bounds[1].bonus_amount, 250.0);

  ASSERT_EQ(rule->week_days,
            std::set<cctz::weekday>(
                {cctz::weekday::monday, cctz::weekday::tuesday,
                 cctz::weekday::wednesday, cctz::weekday::thursday,
                 cctz::weekday::friday, cctz::weekday::saturday,
                 cctz::weekday::sunday}));
  ASSERT_EQ(rule->hours, std::vector<int>({1, 2}));

  ASSERT_EQ(rule->daily_guarantee_tag, "cool_tag");
  ASSERT_TRUE(rule->agglomeration.empty());
}

TEST(TestClientBillingSubventions, CheckParseAgglomerationRule) {
  const auto& doc = ReadJson("daily_guarantee_agglomeration.json");
  std::unique_ptr<bs::DailyGuaranteeSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_unique<bs::DailyGuaranteeSubvention>(doc, LogExtra()));

  ASSERT_EQ(rule->tariff_zones.size(), 1u);
  ASSERT_EQ(rule->tariff_zones[0], "moscow");
  ASSERT_EQ(rule->start_time.time_since_epoch().count(), 1525179600000000000);
  ASSERT_EQ(rule->end_time.time_since_epoch().count(), 1535806800000000000);
  ASSERT_EQ(rule->type, bs::subvention_rule_types::kDailyGuarantee);
  ASSERT_EQ(rule->acceptance_rate, 0.5);
  ASSERT_EQ(rule->completion_rate, 0.6);
  ASSERT_FALSE(rule->payment_type);

  ASSERT_EQ(rule->is_personal, false);
  ASSERT_EQ(rule->ticket_name, "TAXIRATE-111");
  ASSERT_EQ(rule->rule_id, "rule_id2");
  ASSERT_EQ(rule->drivers_count, 0u);
  ASSERT_EQ(rule->cursor, "2018-09-01T13:00:00.000000+00:00/rule_id2");
  ASSERT_EQ(rule->tags.size(), 1u);
  ASSERT_EQ(rule->tags[0], "cool_tag");
  ASSERT_EQ(rule->time_zone->id, "Asia/Yekaterinburg");
  ASSERT_EQ(rule->time_zone->offset, "+05:00");
  ASSERT_EQ(rule->tariff_classes.size(), 1u);
  ASSERT_EQ(rule->tariff_classes[0], "econom");
  ASSERT_EQ(rule->currency, "RUB");
  ASSERT_EQ(rule->visible_to_driver, true);
  ASSERT_EQ(*rule->days_span, 1);

  ASSERT_EQ(rule->trips_bounds.size(), 2u);
  ASSERT_EQ(rule->trips_bounds[0].lower_bound, 10);
  ASSERT_EQ(rule->trips_bounds[0].upper_bound, 14);
  ASSERT_EQ(rule->trips_bounds[0].bonus_amount, 100.0);
  ASSERT_EQ(rule->trips_bounds[1].lower_bound, 15);
  ASSERT_FALSE(rule->trips_bounds[1].upper_bound);
  ASSERT_EQ(rule->trips_bounds[1].bonus_amount, 250.0);

  ASSERT_EQ(rule->week_days,
            std::set<cctz::weekday>(
                {cctz::weekday::monday, cctz::weekday::tuesday,
                 cctz::weekday::wednesday, cctz::weekday::thursday,
                 cctz::weekday::friday, cctz::weekday::saturday,
                 cctz::weekday::sunday}));
  ASSERT_EQ(rule->hours, std::vector<int>({1, 2}));

  ASSERT_EQ(rule->daily_guarantee_tag, "cool_tag");
  ASSERT_EQ(rule->agglomeration, "moscow+myt");
}

TEST(TestClientBillingSubventions, CheckParseInfos) {
  const auto& response = ReadFile("rules_info.json");
  clients::billing_subventions::SubventionInfos subvention_infos;

  ASSERT_NO_THROW(
      subvention_infos =
          clients::billing_subventions::ParseDailySubventionInfoResponse(
              response, {}));
  ASSERT_EQ(subvention_infos.size(), 1u);
  ASSERT_EQ(subvention_infos[0].rule_id, "rule_id1");
  ASSERT_EQ(*subvention_infos[0].orders_completed_count, 32u);
  ASSERT_EQ(subvention_infos[0].income.amount, 100.0);
  ASSERT_EQ(subvention_infos[0].income.currency, "RUB");
  ASSERT_EQ(subvention_infos[0].start_time.time_since_epoch().count(),
            1533254400000000000);
  ASSERT_EQ(subvention_infos[0].end_time.time_since_epoch().count(),
            1533340799000000000);
}

TEST(TestClientBillingSubventions, CheckParseInfosBooking) {
  const auto& response = ReadFile("rules_info_2.json");
  clients::billing_subventions::SubventionInfos subvention_infos;

  ASSERT_NO_THROW(
      subvention_infos =
          clients::billing_subventions::ParseDailySubventionInfoResponse(
              response, {}));
  ASSERT_EQ(subvention_infos.size(), 1u);
  ASSERT_EQ(subvention_infos[0].rule_id, "rule_id1");
  ASSERT_FALSE(subvention_infos[0].orders_completed_count);
  ASSERT_EQ(subvention_infos[0].income.amount, 100.0);
  ASSERT_EQ(subvention_infos[0].income.currency, "RUB");
  ASSERT_EQ(subvention_infos[0].start_time.time_since_epoch().count(),
            1533254400000000000);
  ASSERT_EQ(subvention_infos[0].end_time.time_since_epoch().count(),
            1533340799000000000);
}

TEST(TestClientBillingSubventions, CheckParseGeoBookingSubvention) {
  const auto& doc = ReadJson("geo_booking_rule.json");
  std::unique_ptr<bs::GeoBookingSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_unique<bs::GeoBookingSubvention>(doc, LogExtra()));

  ASSERT_EQ(rule->rule_id, "geo_booking_rule1");
  ASSERT_EQ(rule->tariff_zones, std::vector<std::string>({"moscow"}));
  ASSERT_EQ(rule->geoareas, std::vector<std::string>({"msk-big"}));
  ASSERT_TRUE(rule->driver_points);
  ASSERT_EQ(*rule->driver_points, 10.0);
  ASSERT_EQ(rule->start_time.time_since_epoch().count(), 1547154000000000000);
  ASSERT_EQ(rule->end_time.time_since_epoch().count(), 1559163600000000000);
  ASSERT_EQ(rule->week_days,
            std::set<cctz::weekday>(
                {cctz::weekday::monday, cctz::weekday::tuesday,
                 cctz::weekday::wednesday, cctz::weekday::thursday,
                 cctz::weekday::friday, cctz::weekday::saturday,
                 cctz::weekday::sunday}));
  ASSERT_EQ(rule->workshift.start,
            std::make_pair(static_cast<uint8_t>(10), static_cast<uint8_t>(0)));
  ASSERT_EQ(rule->workshift.end,
            std::make_pair(static_cast<uint8_t>(17), static_cast<uint8_t>(0)));
  ASSERT_EQ(rule->profile_payment_type_restrictions,
            bs::profile_payment_restriction_type::ONLINE);
}

TEST(TestClientBillingSubventions, GeoBookingSubventionWorkshiftTillZeros) {
  const auto& doc = ReadJson("geo_booking_rule_till_zeros.json");
  std::unique_ptr<bs::GeoBookingSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_unique<bs::GeoBookingSubvention>(doc, LogExtra()));

  ASSERT_EQ(rule->profile_payment_type_restrictions,
            bs::profile_payment_restriction_type::CASH);

  ASSERT_EQ(rule->workshift.start,
            std::make_pair(static_cast<uint8_t>(10), static_cast<uint8_t>(0)));
  ASSERT_EQ(rule->workshift.end,
            std::make_pair(static_cast<uint8_t>(24), static_cast<uint8_t>(0)));

  cctz::civil_minute from(2019, 2, 1, 0, 0);
  cctz::civil_minute to(2019, 2, 7, 0, 0);
  const auto& schedule = rule->GetSchedule(from, to, cctz::utc_time_zone());
  for (const auto& schedule_item : schedule) {
    ASSERT_TRUE(schedule_item.from < schedule_item.to);
  }
}

TEST(TestClientBillingSubventions, CheckParsedDates) {
  const auto& doc = ReadJson("billing_rule.json");
  std::unique_ptr<bs::GuaranteeSubvention> rule;
  ASSERT_NO_THROW(
      rule = std::make_unique<bs::GuaranteeSubvention>(doc, LogExtra()));

  ASSERT_EQ(rule->start_time.time_since_epoch().count(), 1525179600000000000);
  ASSERT_EQ(rule->end_time.time_since_epoch().count(),
            decltype(rule->end_time)::max().time_since_epoch().count());
}
