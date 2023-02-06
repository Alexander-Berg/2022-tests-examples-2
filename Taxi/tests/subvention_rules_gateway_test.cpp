#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <clients/billing_subventions/client_mock_base.hpp>

#include <gateways/subvention_rules/details/billing_subventions_gateway.hpp>
#include <gateways/subvention_rules/details/mappers.hpp>

namespace {

namespace details = billing_time_events::gateways::subvention_rules::details;
namespace models = billing_time_events::models;
namespace mappers =
    billing_time_events::gateways::subvention_rules::details::mappers;
namespace subventions = ::clients::billing_subventions;
namespace select_rules = ::subventions::v1_rules_select::post;
namespace types = billing_time_events::types;

using Seconds = std::chrono::seconds;
using Hours = std::chrono::hours;

template <typename C1, typename C2>
bool IsEqual(C1 c1, C2 c2) {
  if (c1.size() != c2.size()) return false;
  for (const auto& el : c1) {
    if (auto it = std::find(std::begin(c2), std::end(c2), el);
        it == std::end(c2)) {
      return false;
    }
  }
  return true;
}

class MockSubventionsClient : public subventions::ClientMockBase {
 public:
  MOCK_METHOD(subventions::v1_rules_select::post::Response, V1RulesSelect,
              (const subventions::v1_rules_select::post::Request&,
               const subventions::CommandControl& command_control),
              (const, override));
};

class SubventionRuleGatewayTest : public ::testing::Test {
  void SetUp() override {
    rule_schema_.subvention_rule_id = "_id/6";
    rule_schema_.group_id = "group_id/28";
    rule_schema_.profile_tariff_classes.push_back("econom");
    rule_schema_.profile_payment_type_restrictions =
        subventions::ProfilePaymentTypeRestrictions::kAny;
    rule_schema_.commission_rate_if_fraud = "0.2";
    rule_schema_.currency = "USD";
    rule_schema_.rates.push_back(
        {subventions::RateValueWeekday::kSun, "23:59", "6"});
    rule_schema_.geoareas = std::vector<std::string>{"msk"};
    rule_schema_.tariff_classes = std::vector<std::string>{"comfort"};
    rule_schema_.tags = std::vector<std::string>{"tag1"};
    rule_schema_.time_zone.id = "Australia/Sydney";
    rule_schema_.time_zone.offset = "+10:00";
    rule_schema_.tariff_zones.push_back("Moscow");
    rule_schema_.start = utils::datetime::GuessStringtime(
        "2020-05-10T20:00:00.000000+00:00", "UTC");
    rule_schema_.end = utils::datetime::GuessStringtime(
        "2020-05-11T20:00:00.000000+00:00", "UTC");

    boundaries_ =
        types::TimeRange{utils::datetime::GuessStringtime(
                             "2020-05-11T20:00:00.000000+00:00", "UTC"),
                         utils::datetime::GuessStringtime(
                             "2020-05-11T21:00:00.000000+00:00", "UTC")};
  }

 protected:
  subventions::DriverFixRule rule_schema_{};
  types::TimeRange boundaries_;
};

}  // namespace

TEST_F(SubventionRuleGatewayTest, MapDriverFixRule) {
  auto rule =
      mappers::MapToDriverFixRule(subventions::Rule{std::move(rule_schema_)});

  EXPECT_EQ(rule.rule_id, "_id/6");
  // EXPECT_EQ(rule.group_id, "group_id/28");
  EXPECT_EQ(rule.group_id, "_id/6");
  EXPECT_EQ(rule.geoarea, "msk");
  EXPECT_TRUE(IsEqual(rule.tariff_classes, std::vector<std::string>{"econom"}));

  EXPECT_EQ(*rule.tag, "tag1");
  EXPECT_EQ(rule.validity.lower(),
            utils::datetime::GuessStringtime("2020-05-10T20:00:00.000000+00:00",
                                             "UTC"));
  EXPECT_EQ(rule.validity.upper(),
            utils::datetime::GuessStringtime("2020-05-11T20:00:00.000000+00:00",
                                             "UTC"));
  EXPECT_EQ(rule.timezone_id, "Australia/Sydney");
  EXPECT_EQ(rule.currency, "USD");
  EXPECT_EQ(rule.zone_name, "Moscow");
}

TEST_F(SubventionRuleGatewayTest, BillingSubventionsGateway) {
  MockSubventionsClient client{};
  details::BillingSubventionsGateway gateway{client, 2};

  subventions::Rule subv_rule{rule_schema_};
  EXPECT_CALL(client, V1RulesSelect(testing::_, testing::_))
      // request by id
      .WillOnce(testing::Return(select_rules::Response200{
          subventions::SelectRulesPostResponse{{subv_rule}}}))
      // request by key: first page
      .WillOnce(testing::Return(subventions::v1_rules_select::post::Response200{
          subventions::SelectRulesPostResponse{{subv_rule, subv_rule}}}))
      // request by key: second page
      .WillOnce(testing::Return(subventions::v1_rules_select::post::Response200{
          subventions::SelectRulesPostResponse{{subv_rule}}}));

  gateway.GetDriverFixRules("_id/6", boundaries_);
}
