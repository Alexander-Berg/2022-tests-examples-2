#include <userver/utest/utest.hpp>

#include <sharding/condition.hpp>
#include <sharding/rule.hpp>

#include <memory>

namespace processing::sharding {

TEST(ShardingRule, HappyPath) {
  using StringSet = std::unordered_set<std::string>;
  Condition::List conditions;
  conditions.push_back(
      std::make_unique<conditions::ByValues>("scope", StringSet{"foo"}));
  conditions.push_back(
      std::make_unique<conditions::ByValues>("queue", StringSet{"bar"}));
  Rule rule(std::move(conditions), nullptr, nullptr, "", 0);

  EXPECT_TRUE(rule.DoesMatch({{"scope", "foo"}, {"queue", "bar"}}, {}));
  EXPECT_FALSE(rule.DoesMatch({{"scope", "foo"}, {"queue", "nop"}}, {}));
  EXPECT_FALSE(rule.DoesMatch({{"scope", "baz"}}, {}));
  EXPECT_THROW(rule.DoesMatch({}, {}), std::runtime_error);

  {
    ValueCoverage expect{{"scope", {"foo"}}, {"queue", {"bar"}}};
    EXPECT_EQ(rule.GetCoverage(), expect);
  }
}

}  // namespace processing::sharding
