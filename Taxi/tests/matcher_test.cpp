#include <memory>
#include <set>
#include <string>
#include <unordered_set>
#include <variant>
#include <vector>

#include <gtest/gtest.h>

#include <set-rules-matcher/matcher.hpp>

namespace {

struct NoneOfRule {
  NoneOfRule(std::initializer_list<std::string> vars) : none_of(vars) {}
  std::unordered_set<std::string> none_of;
};

struct AllOfRule {
  AllOfRule(std::initializer_list<std::string> vars) : all_of(vars) {}
  std::unordered_set<std::string> all_of;
};

struct AnyOfRule {
  AnyOfRule(std::initializer_list<std::string> vars) : any_of(vars) {}
  std::set<std::string> any_of;
};

struct SubsetOfRule {
  SubsetOfRule(std::initializer_list<std::string> vars) : subset_of(vars) {}
  std::set<std::string> subset_of;
};

using SingleLevelRule = std::variant<NoneOfRule,     //
                                     AllOfRule,      //
                                     AnyOfRule,      //
                                     SubsetOfRule>;  //

struct NotRule {
  NotRule(SingleLevelRule rule) : not_(std::move(rule)) {}
  SingleLevelRule not_;
};

struct AndRule {
  AndRule(std::vector<SingleLevelRule> rules) : and_(std::move(rules)) {}
  std::vector<SingleLevelRule> and_;
};

struct OrRule {
  OrRule(std::vector<SingleLevelRule> rules) : or_(std::move(rules)) {}
  std::vector<SingleLevelRule> or_;
};

using Rule = std::variant<NoneOfRule,    //
                          AllOfRule,     //
                          AnyOfRule,     //
                          SubsetOfRule,  //
                          NotRule,       //
                          AndRule,       //
                          OrRule>;       //

struct RuleWithValue {
  RuleWithValue(Rule r, int v) : rule(std::move(r)), value(v) {}
  Rule rule;
  int value;
};

struct CustomNotRule {
  CustomNotRule(SingleLevelRule rule) : nested(std::move(rule)) {}
  SingleLevelRule nested;
};

struct CustomAndRule {
  CustomAndRule(std::vector<SingleLevelRule> rules)
      : nested(std::move(rules)) {}
  std::vector<SingleLevelRule> nested;
};

struct CustomOrRule {
  CustomOrRule(std::vector<SingleLevelRule> rules) : nested(std::move(rules)) {}
  std::vector<SingleLevelRule> nested;
};

using CustomRule = std::variant<NoneOfRule,     //
                                AllOfRule,      //
                                AnyOfRule,      //
                                SubsetOfRule,   //
                                CustomNotRule,  //
                                CustomAndRule,  //
                                CustomOrRule>;  //

template <class T, class R>
void AddRule(std::vector<R>& rules,
             std::initializer_list<std::string> rule_vals) {
  rules.push_back(T(rule_vals));
}

template <class T, class R>
void AddRule(std::vector<R>& rules,
             std::vector<SingleLevelRule>&& nested_rules) {
  rules.push_back(T(std::move(nested_rules)));
}

}  // namespace

namespace set_rules_matcher {

TEST(TestMatcher, TestMatchValuePositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<RuleWithValue> rules_with_values;
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"x", "y"});  // false
    AddRule<AnyOfRule>(nested_rules, {"z"});       // false

    rules_with_values.emplace_back(OrRule(std::move(nested_rules)),  // false
                                   0);
  }
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"a", "b"});  // true
    AddRule<AnyOfRule>(nested_rules, {"x"});       // false

    rules_with_values.emplace_back(OrRule(std::move(nested_rules)),  // true
                                   1);
  }

  auto val_ptr = MatchValue(
      rules_with_values.begin(),                                      //
      rules_with_values.end(),                                        //
      vals,                                                           //
      [](const RuleWithValue& r) -> const Rule& { return r.rule; },   //
      [](const RuleWithValue& r) -> const int& { return r.value; });  //
  ASSERT_NE(val_ptr, nullptr);
  ASSERT_EQ(*val_ptr, 1);
}

TEST(TestMatcher, TestMatchValueNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<RuleWithValue> rules_with_values;
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"x", "y"});  // false
    AddRule<AnyOfRule>(nested_rules, {"z"});       // false

    rules_with_values.emplace_back(OrRule(std::move(nested_rules)),  // false
                                   0);
  }

  auto val_ptr = MatchValue(rules_with_values.begin(),  //
                            rules_with_values.end(),    //
                            vals);                      //
  ASSERT_EQ(val_ptr, nullptr);
}

TEST(TestMatcher, TestNoneOfPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<NoneOfRule>(rules, {"x", "y"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestNoneOfNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<NoneOfRule>(rules, {"a", "x"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestNoneOfNegativeLongRule) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<NoneOfRule>(rules, {"a", "x", "y", "z"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestAnyOfPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<AnyOfRule>(rules, {"a", "x"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestAnyOfNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<AnyOfRule>(rules, {"x", "y"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestAnyOfNegativeLongRule) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<AnyOfRule>(rules, {"x", "y", "z", "w"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestAllOfPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<AllOfRule>(rules, {"a", "b"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestAllOfNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<AllOfRule>(rules, {"a", "x"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestSubsetOfPositive) {
  std::unordered_set<std::string> vals{"a", "b"};

  std::vector<Rule> rules{};
  AddRule<SubsetOfRule>(rules, {"a", "b", "c"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestSubsetOfNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  AddRule<SubsetOfRule>(rules, {"a", "b"});

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestNotPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules;
  rules.push_back(NotRule(AnyOfRule({"x", "y"})));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestCustomNotPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<CustomRule> rules;
  rules.push_back(CustomNotRule(AnyOfRule({"x", "y"})));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestNotNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules;
  rules.push_back(NotRule(AnyOfRule({"a", "b"})));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestAndPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"c"});

  std::vector<Rule> rules{};
  AddRule<AndRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestCustomAndPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"c"});

  std::vector<CustomRule> rules{};
  AddRule<CustomAndRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestAndNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"x"});

  std::vector<Rule> rules{};
  AddRule<AndRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestOrPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"x"});

  std::vector<Rule> rules{};
  AddRule<OrRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestCustomOrPositive) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"x"});

  std::vector<CustomRule> rules{};
  AddRule<CustomOrRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

TEST(TestMatcher, TestOrNegative) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"x", "y"});
  AddRule<AnyOfRule>(nested_rules, {"z"});

  std::vector<Rule> rules{};
  AddRule<OrRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cend());
}

TEST(TestMatcher, TestMultipleRules) {
  std::unordered_set<std::string> vals{"a", "b", "c"};

  std::vector<Rule> rules{};
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"x", "y"});  // false
    AddRule<AnyOfRule>(nested_rules, {"z"});       // false

    AddRule<OrRule>(rules, std::move(nested_rules));  // false
  }
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"a", "b"});  // true
    AddRule<AnyOfRule>(nested_rules, {"x"});       // false

    AddRule<AndRule>(rules, std::move(nested_rules));  // false
  }
  {
    std::vector<SingleLevelRule> nested_rules{};
    AddRule<AnyOfRule>(nested_rules, {"x", "y"});  // false
    AddRule<AnyOfRule>(nested_rules, {"a"});       // true

    AddRule<OrRule>(rules, std::move(nested_rules));  // true
  }
  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, std::next(rules.cbegin(), 2));
}

TEST(TestMatcher, TestIterableValues) {
  std::vector<std::string> vals{"a", "b", "c"};

  std::vector<SingleLevelRule> nested_rules{};
  AddRule<AnyOfRule>(nested_rules, {"a", "b"});
  AddRule<AnyOfRule>(nested_rules, {"c"});

  std::vector<Rule> rules{};
  AddRule<AndRule>(rules, std::move(nested_rules));

  auto it = MatchRule(rules.begin(), rules.end(), vals);
  ASSERT_EQ(it, rules.cbegin());
}

}  // namespace set_rules_matcher
