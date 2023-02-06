#include <optional>

#include <userver/utest/utest.hpp>

#include <common/utils/enriched_rule.hpp>
#include <models/subvention_rule.hpp>

TEST(EnrichedRuleTest, CreateTest) {
  ::billing_subventions_x::models::SubventionRule src;
  src.id = "TestId";
  src.group_id = "TestGroupId";
  src.bonus_type = "add";
  src.kind = std::nullopt;
  src.is_once = false;
  src.day_ride_count = ::billing_subventions_x::models::DayRideCount();
  auto dst = ::billing_subventions_x::utils::EnrichedRule::Create(src, true);
  EXPECT_EQ(dst.id, std::string("TestId"));
  EXPECT_EQ(dst.group_id, std::string("TestGroupId"));
  EXPECT_EQ(dst.bonus_type, std::string("add"));
  EXPECT_FALSE(dst.kind.has_value());
  EXPECT_EQ(dst.is_once, false);
  EXPECT_TRUE(dst.day_ride_count.IsOpen());
  EXPECT_EQ(dst.rule_type, ::handlers::RuleType::kOnTop);
  EXPECT_EQ(dst.is_personal, true);
}
