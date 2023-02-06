#include "driver_tags_condition_checker.hpp"

#include <variant>

#include <gtest/gtest.h>

using NoneOfRule = taxi_config::workshifts_subventions_rules::NoneOfRule;
using AllOfRule = taxi_config::workshifts_subventions_rules::AllOfRule;
using AnyOfRule = taxi_config::workshifts_subventions_rules::AnyOfRule;
using LogicalRule = taxi_config::workshifts_subventions_rules::LogicalRule;
using LogicalAndRule =
    taxi_config::workshifts_subventions_rules::LogicalAndRule;
using LogicalOrRule = taxi_config::workshifts_subventions_rules::LogicalOrRule;

using RulesVariant =
    std::variant<NoneOfRule, AllOfRule, AnyOfRule, LogicalRule>;

using Status = workers::impl::DriverTagsConditionStatus;

namespace {

const std::unordered_set<std::string> tag_set{"tag1", "tag2", "tag3", "tag4"};

const std::vector<std::string> tags{tag_set.begin(), tag_set.end()};

const std::string unknown_tag1 = "unknown1";
const std::string unknown_tag2 = "unknown2";

}  // namespace

TEST(DriverTagsConditionChecker, L1Rules) {
  const workers::impl::DriverTagsConditionChecker checker{tag_set};

  {
    RulesVariant rule{AllOfRule{{tags[1], tags[2], tags[3]}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{AllOfRule{{tags[1], tags[2], tags[3], unknown_tag1}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{AnyOfRule{{tags[0], tags[1], tags[2]}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{AnyOfRule{{unknown_tag1, unknown_tag2}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{NoneOfRule{{unknown_tag1}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{NoneOfRule{{tags[0]}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kDenied);
  }
}

TEST(DriverTagsConditionChecker, L2Rules) {
  const workers::impl::DriverTagsConditionChecker checker{tag_set};

  {
    RulesVariant rule{
        LogicalAndRule{{AllOfRule{{tags[0]}}, AllOfRule{{tags[1]}}}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{
        LogicalAndRule{{AllOfRule{{tags[0]}}, AllOfRule{{unknown_tag1}}}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kDenied);
  }

  {
    RulesVariant rule{LogicalOrRule{{AllOfRule{{tags[0]}}, AllOfRule{{tags[1]}},
                                     NoneOfRule{{unknown_tag1}}}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kAllowed);
  }

  {
    RulesVariant rule{
        LogicalOrRule{{AllOfRule{{unknown_tag1}}, AllOfRule{{unknown_tag2}}}}};
    ASSERT_EQ(std::visit(checker, rule).status, Status::kDenied);
  }
}
