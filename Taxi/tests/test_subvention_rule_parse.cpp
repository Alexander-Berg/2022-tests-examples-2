#include <userver/utest/utest.hpp>

#include <userver/formats/bson.hpp>
#include <userver/formats/json.hpp>

#include <common/pack/bson/subvention_rule.hpp>
#include <common/utils/types.hpp>

#include "builders.hpp"

namespace {

using ValueBuilder = formats::bson::ValueBuilder;
using Value = formats::bson::Value;
using Type = formats::common::Type;
using Strings = billing_subventions_x::types::Strings;
using Integers = billing_subventions_x::types::Integers;
using Budget = billing_subventions_x::models::Budget;
using Rates = billing_subventions_x::models::Rates;
using Workshift = billing_subventions_x::models::Workshift;

namespace fb = ::formats::bson;

Value makeDailyGuaranteeRule() {
  const auto kDoc = formats::bson::MakeDoc(
      "acceptance_rate", 0.5,      //
      "branding_type", "sticker",  //
      "class",
      formats::bson::MakeArray("econom", "business", "uberx", "uberstart"),  //
      "completion_rate", 0.9,                                                //
      "currency", "RUB",                                                     //
      "day_beginning_offset_in_seconds", 0,                                  //
      "dayofweek", formats::bson::MakeArray(1, 3, 5),                        //
      "dayridecount_days", 1,                                                //
      "dayridecount",
      formats::bson::MakeArray(formats::bson::MakeArray(23, 23)),  //
      "display_in_taximeter", true,                                //
      "end", ATimePoint("2018-08-26T21:00:00Z"),                   //
      "geoareas", formats::bson::MakeArray("zone_a", "zone_b"),    //
      "group_id", "voronezh_subvention_rules",                     //
      "group_member_id", "num_orders/23/week_days/1,2,3,4,5,6,7",  //
      "has_fake_counterpart", false,                               //
      "hour", formats::bson::MakeArray(),                          //
      "_id", "5b7bf9644f007eaf850c775a",                           //
      "is_bonus", true,                                            //
      "is_fake", false,                                            //
      "is_net", false,                                             //
      "is_once", true,                                             //
      "is_test", false,                                            //
      "kind", "daily_guarantee",                                   //
      "log", formats::bson::MakeArray(),                           //
      "paymenttype", "card",                                       //
      "region", "Воронеж",                                         //
      "start", ATimePoint("2018-08-19T21:00:00Z"),                 //
      "sub_commission", true,                                      //
      "sum", static_cast<double>(4508),                            //
      "tags", formats::bson::MakeArray("mytag"),                   //
      "tariffzone", formats::bson::MakeArray("voronezh"),          //
      "time_zone", "Europe/Moscow",                                //
      "type", "guarantee",                                         //
      "updated", ATimePoint("2018-08-21T11:37:08Z"),               //
      "budget",
      fb::MakeDoc(                                    //
          "id", "some_id",                            //
          "daily", "123",                             //
          "weekly", "456",                            //
          "rolling", true,                            //
          "threshold", 100,                           //
          "tickets", fb::MakeArray("tkt1", "tkt2"),   //
          "approvers", fb::MakeArray("appA", "appB")  //
          ),                                          //
      "rates",
      fb::MakeArray(fb::MakeDoc(                    //
                        "rate_per_minute", "6.67",  //
                        "start_hour", 0,            //
                        "start_minute", 0,          //
                        "week_day", 1),             //
                    fb::MakeDoc(                    //
                        "rate_per_minute", "8.34",  //
                        "start_hour", 6,            //
                        "start_minute", 0,          //
                        "week_day", 3),             //
                    fb::MakeDoc(                    //
                        "rate_per_minute", "6.67",  //
                        "start_hour", 9,            //
                        "start_minute", 0,          //
                        "week_day", 7)              //
                    ),                              //
      "workshift",
      fb::MakeDoc(              //
          "duration", "15:00",  //
          "start", "07:00")     //
  );                            //
  return kDoc;
}

Value makeRuleWithOmittedParts() {
  const auto kDoc = formats::bson::MakeDoc(
      "acceptance_rate", 0.5,  //
      // "branding_type"
      "class", formats::bson::MakeArray(),          //
      "completion_rate", 0.9, "currency",           //
      "RUB", "day_beginning_offset_in_seconds", 0,  //
      "dayofweek", formats::bson::MakeArray(),      //
      // "dayridecount_days"
      // "dayridecount"
      // "display_in_taximeter"
      // driver_points
      "end", ATimePoint("2018-08-26T21:00:00Z"),  //
      // "geoareas"
      "group_id", "voronezh_subvention_rules",  //
      // "group_member_id"
      "has_fake_counterpart", false,       //
      "hour", formats::bson::MakeArray(),  //
      "_id", "5b7bf9644f007eaf850c775a",   //
      "is_bonus", true,                    //
      "is_fake", false,                    //
      // "is_net"
      "is_once", true,  //
      // "is_test"
      // "kind"
      "log", formats::bson::MakeArray(),  //
      // "paymenttype"
      "region", "Воронеж", "start", ATimePoint("2018-08-19T21:00:00Z"),  //
      // "status"
      "sub_commission", true,            //
      "sum", static_cast<double>(4508),  //
      // "tags"
      "tariffzone", formats::bson::MakeArray("voronezh"),  //
      // "time_zone"
      "type", "guarantee",                             //
      "updated", ATimePoint("2018-08-21T11:37:08Z"));  //
  return kDoc;
}

Value makeRuleWithNulls() {
  const auto kDoc = formats::bson::MakeDoc(
      "acceptance_rate", 0.5,                              //
      "branding_type", nullptr,                            //
      "class", formats::bson::MakeArray(),                 //
      "completion_rate", 0.9,                              //
      "currency", "RUB",                                   //
      "day_beginning_offset_in_seconds", 0,                //
      "dayofweek", formats::bson::MakeArray(),             //
      "end", ATimePoint("2018-08-26T21:00:00Z"),           //
      "group_id", "voronezh_subvention_rules",             //
      "has_fake_counterpart", false,                       //
      "hour", formats::bson::MakeArray(),                  //
      "_id", "5b7bf9644f007eaf850c775a",                   //
      "is_bonus", true,                                    //
      "is_fake", false,                                    //
      "is_once", true,                                     //
      "log", formats::bson::MakeArray(),                   //
      "paymenttype", nullptr,                              //
      "region", "Воронеж",                                 //
      "start", ATimePoint("2018-08-19T21:00:00Z"),         //
      "sub_commission", true,                              //
      "sum", static_cast<double>(4508),                    //
      "tariffzone", formats::bson::MakeArray("voronezh"),  //
      "type", "guarantee",                                 //
      "updated", ATimePoint("2018-08-21T11:37:08Z"));      //
  return kDoc;
}

}  // anonymous namespace

TEST(SubventionRuleParse, makeBson) {
  EXPECT_NO_FATAL_FAILURE((void)makeDailyGuaranteeRule());
}

TEST(SubventionRuleParse, compareStrings) {
  auto a = Strings{"a", "b", "c"};
  EXPECT_EQ(a.size(), 3);
  EXPECT_EQ(a[0], std::string("a"));
  EXPECT_EQ(a[1], std::string("b"));
  EXPECT_EQ(a[2], std::string("c"));
  EXPECT_EQ(a, (Strings{"a", "b", "c"}));
}

TEST(SubventionRuleParse, budgetMakeStruct) {
  auto budget = Budget{std::string("some_id"),
                       std::optional<std::string>("123"),
                       std::optional<std::string>("456"),
                       std::optional<bool>(true),
                       std::optional<int>(100),
                       std::optional<Strings>({"tkt1", "tkt2"}),
                       std::optional<Strings>({"appA", "appB"})};
  EXPECT_EQ(budget.id, std::string("some_id"));
  EXPECT_TRUE(budget.daily.has_value());
  EXPECT_EQ(budget.daily, std::optional<std::string>("123"));
  EXPECT_TRUE(budget.weekly.has_value());
  EXPECT_EQ(budget.weekly, std::optional<std::string>("456"));
  EXPECT_TRUE(budget.rolling.has_value());
  EXPECT_EQ(budget.rolling, std::optional<bool>(true));
  EXPECT_TRUE(budget.threshold.has_value());
  EXPECT_EQ(budget.threshold, std::optional<int>(100));
  EXPECT_TRUE(budget.tickets.has_value());
  EXPECT_EQ(budget.tickets, std::optional<Strings>({"tkt1", "tkt2"}));
  EXPECT_TRUE(budget.approvers.has_value());
  EXPECT_EQ(budget.approvers, std::optional<Strings>({"appA", "appB"}));
}

TEST(SubventionRuleParse, budgetCompareStruct) {
  auto a = Budget{std::string("some_id"),
                  std::optional<std::string>("123"),
                  std::optional<std::string>("456"),
                  std::optional<bool>(true),
                  std::optional<int>(100),
                  std::optional<Strings>({"tkt1", "tkt2"}),
                  std::optional<Strings>({"appA", "appB"})};
  auto b = Budget{std::string("some_id"),
                  std::optional<std::string>("123"),
                  std::optional<std::string>("456"),
                  std::optional<bool>(true),
                  std::optional<int>(100),
                  std::optional<Strings>({"tkt1", "tkt2"}),
                  std::optional<Strings>({"appA", "appB"})};
  EXPECT_EQ(a, b);
}

TEST(SubventionRuleParse, budgetFromDoc) {
  auto doc = fb::MakeDoc(                         //
      "id", "some_id",                            //
      "daily", "123",                             //
      "weekly", "456",                            //
      "rolling", true,                            //
      "threshold", 100,                           //
      "tickets", fb::MakeArray("tkt1", "tkt2"),   //
      "approvers", fb::MakeArray("appA", "appB")  //
  );

  auto budget = doc.As<Budget>();
  EXPECT_EQ(
      budget,
      (Budget{std::string("some_id"), std::optional<std::string>("123"),
              std::optional<std::string>("456"), std::optional<bool>(true),
              std::optional<int>(100), std::optional<Strings>({"tkt1", "tkt2"}),
              std::optional<Strings>({"appA", "appB"})}));
}

TEST(SubventionRuleParse, ratesEntryFromDoc) {
  auto doc = fb::MakeDoc("rate_per_minute", "12.34", "start_hour", 5,
                         "start_minute", 6, "week_day", 7);
  auto entry = doc.As<Rates::Entry>();
  EXPECT_EQ(entry, (Rates::Entry{"12.34", 5, 6, 7}));
}

TEST(SubventionRuleParse, ratesFromDoc) {
  auto doc = fb::MakeArray(fb::MakeDoc("rate_per_minute", "12.34", "start_hour",
                                       5, "start_minute", 6, "week_day", 7),
                           fb::MakeDoc("rate_per_minute", "89.01", "start_hour",
                                       2, "start_minute", 3, "week_day", 4));

  auto entry = doc.As<Rates>();
  EXPECT_EQ(entry, (Rates{{Rates::Entry{"12.34", 5, 6, 7},
                           Rates::Entry{"89.01", 2, 3, 4}}}));
}

TEST(SubventionRuleParse, workshiftDoc) {
  auto doc = fb::MakeDoc("duration", "23:45", "start", "00:15");

  auto entry = doc.As<Workshift>();
  EXPECT_EQ(entry, (Workshift{"23:45", "00:15"}));
}

void ExpectTimePointsEqual(TimePoint actual, TimePoint expected) {
  EXPECT_EQ(actual, expected) << TimePointsNotEqual(actual, expected);
}

TEST(SubventionRuleParse, parseSynteticRule) {
  const auto kDoc = makeDailyGuaranteeRule();
  const auto rule = kDoc.As<billing_subventions_x::models::SubventionRule>();
  EXPECT_EQ(rule.id, std::string("5b7bf9644f007eaf850c775a"));
  EXPECT_EQ(rule.group_id, std::string("voronezh_subvention_rules"));
  EXPECT_EQ(rule.group_member_id,
            std::string("num_orders/23/week_days/1,2,3,4,5,6,7"));
  EXPECT_TRUE(rule.branding_type);
  EXPECT_EQ(rule.branding_type, std::optional<std::string>("sticker"));
  EXPECT_EQ(rule.tariff_class,
            (Strings{"econom", "business", "uberx", "uberstart"}));
  EXPECT_EQ(rule.currency, std::string("RUB"));
  EXPECT_EQ(rule.day_of_week, (Integers{1, 3, 5}));
  EXPECT_FALSE(rule.day_ride_count.IsOpen());
  EXPECT_FALSE(rule.day_ride_count.IsHalfOpen());
  EXPECT_EQ(rule.day_ride_count.lower, 23);
  EXPECT_EQ(rule.day_ride_count.upper, 23);
  EXPECT_EQ(rule.day_ride_count_days, 1);
  EXPECT_EQ(rule.display_in_taximeter, true);
  EXPECT_FALSE(rule.driver_points);
  EXPECT_TRUE(rule.geo_areas);
  EXPECT_EQ(rule.geo_areas, std::optional<Strings>({"zone_a", "zone_b"}));
  ExpectTimePointsEqual(rule.end, ATimePoint("2018-08-26T21:00:00Z"));
  EXPECT_TRUE(rule.hour.empty());
  EXPECT_EQ(rule.is_bonus, true);
  EXPECT_EQ(rule.is_net, false);
  EXPECT_EQ(rule.is_once, true);
  EXPECT_EQ(rule.is_test, false);
  EXPECT_EQ(rule.kind, std::string("daily_guarantee"));
  EXPECT_TRUE(rule.payment_type);
  EXPECT_EQ(rule.payment_type, std::string("card"));
  ExpectTimePointsEqual(rule.start, ATimePoint("2018-08-19T21:00:00Z"));
  EXPECT_EQ(rule.status, "approved");
  EXPECT_EQ(rule.sub_commission, true);
  EXPECT_EQ(rule.sum, static_cast<double>(4508));
  EXPECT_TRUE(rule.tags);
  EXPECT_EQ(rule.tags, std::optional<Strings>({"mytag"}));
  EXPECT_EQ(rule.zone_name, std::string("voronezh"));
  EXPECT_EQ(rule.time_zone, std::optional<std::string>("Europe/Moscow"));
  EXPECT_EQ(rule.bonus_type, std::string("guarantee"));
  ExpectTimePointsEqual(rule.updated, ATimePoint("2018-08-21T11:37:08Z"));
  EXPECT_EQ(rule.day_beginning_offset_in_seconds, 0);
  EXPECT_TRUE(rule.budget.has_value());
  EXPECT_EQ(
      rule.budget,
      std::optional<Budget>(
          {std::string("some_id"), std::optional<std::string>("123"),
           std::optional<std::string>("456"), std::optional<bool>(true),
           std::optional<int>(100), std::optional<Strings>({"tkt1", "tkt2"}),
           std::optional<Strings>({"appA", "appB"})}));
  EXPECT_TRUE(rule.rates.has_value());
  EXPECT_EQ(rule.rates,
            std::optional<Rates>(
                {{{"6.67", 0, 0, 1}, {"8.34", 6, 0, 3}, {"6.67", 9, 0, 7}}}));
  EXPECT_TRUE(rule.workshift.has_value());
  EXPECT_EQ(rule.workshift, std::optional<Workshift>({"15:00", "07:00"}));
}

TEST(SubventionRuleParse, checkOmitted) {
  const auto kDoc = makeRuleWithOmittedParts();
  const auto rule = kDoc.As<billing_subventions_x::models::SubventionRule>();
  EXPECT_FALSE(rule.branding_type);
  EXPECT_FALSE(rule.day_ride_count_days);
  EXPECT_TRUE(rule.day_ride_count.IsOpen());
  EXPECT_TRUE(rule.display_in_taximeter);  // default value: true
  EXPECT_FALSE(rule.driver_points);
  EXPECT_FALSE(rule.geo_areas);
  EXPECT_FALSE(rule.group_member_id);
  EXPECT_FALSE(rule.kind);
  EXPECT_FALSE(rule.payment_type);
  EXPECT_EQ(rule.status, std::string("approved"));
  EXPECT_FALSE(rule.tags);
  EXPECT_FALSE(rule.time_zone);
  EXPECT_FALSE(rule.budget);
  EXPECT_FALSE(rule.rates);
  EXPECT_FALSE(rule.workshift);
}

TEST(SubventionRuleParse, checkNulls) {
  const auto kDoc = makeRuleWithNulls();
  const auto rule = kDoc.As<billing_subventions_x::models::SubventionRule>();
  EXPECT_FALSE(rule.branding_type);
  EXPECT_FALSE(rule.payment_type);
}
