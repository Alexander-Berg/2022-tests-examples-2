#include <string>
#include <vector>

#include <userver/utest/utest.hpp>

#include <taxi_config/variables/BANK_CASHBACK_CALCULATOR_RULES.hpp>

#include <common/common.hpp>

namespace {
handlers::common::rules_config::Rule Rule(
    std::vector<std::string>&& required_tags,
    std::vector<std::string>&& blocking_tags) {
  handlers::common::rules_config::Rule result;
  result.required_tags = required_tags;
  result.blocking_tags = blocking_tags;
  return result;
}
}  // namespace

TEST(CommonTest, MatchesNoTags) {
  EXPECT_TRUE(handlers::common::DoesRuleMatchTags({}, {}));
  EXPECT_TRUE(handlers::common::DoesRuleMatchTags({}, {"a"}));
  EXPECT_TRUE(handlers::common::DoesRuleMatchTags(Rule({}, {}), {"a"}));
}

TEST(CommonTest, MatchesTags) {
  EXPECT_TRUE(handlers::common::DoesRuleMatchTags(Rule({"a"}, {}), {"a"}));
  EXPECT_TRUE(
      handlers::common::DoesRuleMatchTags(Rule({"a", "b"}, {}), {"a", "b"}));
  EXPECT_FALSE(
      handlers::common::DoesRuleMatchTags(Rule({"a", "b"}, {}), {"a"}));
}

TEST(CommonTest, MatchesStopTags) {
  EXPECT_TRUE(handlers::common::DoesRuleMatchTags(Rule({}, {"b"}), {"a"}));
  EXPECT_FALSE(handlers::common::DoesRuleMatchTags(Rule({}, {"a"}), {"a"}));
  EXPECT_FALSE(
      handlers::common::DoesRuleMatchTags(Rule({}, {"a", "b"}), {"a"}));
}
