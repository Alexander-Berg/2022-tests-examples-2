#include <models/visitors/condition.hpp>

#include <variant>

#include <gtest/gtest.h>

using NoneOfRule = models::NoneOfRule;
using AllOfRule = models::AllOfRule;
using AnyOfRule = models::AnyOfRule;
using LogicalRule = models::LogicalRule;
using LogicalAndRule = models::LogicalAndRule;
using LogicalOrRule = models::LogicalOrRule;

using RulesVariant =
    std::variant<NoneOfRule, AllOfRule, AnyOfRule, LogicalRule>;

using Status = models::ConditionStatus;

namespace {

const models::TagsSet tag_set{models::TagName{"tag1"}, models::TagName{"tag2"},
                              models::TagName{"tag3"}, models::TagName{"tag4"}};

const std::vector<std::string> tags{tag_set.begin(), tag_set.end()};

const std::string unknown_tag1 = "unknown1";
const std::string unknown_tag2 = "unknown2";

}  // namespace

TEST(DriverModeRuleCondition, L1Rules) {
  const models::ConditionVisitor visitor{tag_set};

  {
    RulesVariant rule{AllOfRule{{tags[1], tags[2], tags[3]}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{AllOfRule{{tags[1], tags[2], tags[3], unknown_tag1}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{AnyOfRule{{tags[0], tags[1], tags[2]}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{AnyOfRule{{unknown_tag1, unknown_tag2}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{NoneOfRule{{unknown_tag1}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{NoneOfRule{{tags[0]}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kDenied);
  }
}

TEST(DriverModeRuleCondition, L2Rules) {
  const models::ConditionVisitor visitor{tag_set};

  {
    RulesVariant rule{
        LogicalAndRule{{AllOfRule{{tags[0]}}, AllOfRule{{tags[1]}}}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{
        LogicalAndRule{{AllOfRule{{tags[0]}}, AllOfRule{{unknown_tag1}}}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{LogicalOrRule{{AllOfRule{{tags[0]}}, AllOfRule{{tags[1]}},
                                     NoneOfRule{{unknown_tag1}}}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{
        LogicalOrRule{{AllOfRule{{unknown_tag1}}, AllOfRule{{unknown_tag2}}}}};
    ASSERT_EQ(std::visit(visitor, rule).status, Status::kDenied);
  }
}
