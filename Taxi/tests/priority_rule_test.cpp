#include <models/priorities/find_matching_ttl.hpp>

#include <variant>

#include <gtest/gtest.h>

#include "common.hpp"

using handlers::AllOf;
using handlers::AndRule;
using handlers::AnyOf;
using handlers::NoneOf;
using handlers::OrRule;
using handlers::PriorityRule;

using RulesVariant = std::variant<NoneOf, AllOf, AnyOf, AndRule, OrRule>;

namespace {

const auto kExpireEarly =
    utils::datetime::Stringtime("2018-07-09T13:56:07.000+0000");
const auto kExpireNotThatEarly =
    utils::datetime::Stringtime("2019-07-09T13:56:07.000+0000");
const auto kExpireNotSoon =
    utils::datetime::Stringtime("2020-07-09T13:56:07.000+0000");
const auto kNeverExpire = kValidInfinity;

const std::vector<std::string> tag{"early_expire", "nte_expire",
                                   "not_soon_expire", "never_expire"};

models::DriverInfo InitDriverInfo() {
  models::DriverInfo driver_info;
  driver_info.tags_info[tag[0]] = models::TagInfo{kExpireEarly, {}};
  driver_info.tags_info[tag[1]] = models::TagInfo{kExpireNotThatEarly, {}};
  driver_info.tags_info[tag[2]] = models::TagInfo{kExpireNotSoon, {}};
  driver_info.tags_info[tag[3]] = models::TagInfo{kNeverExpire, {}};
  return driver_info;
}

}  // namespace

TEST(PriorityRule, L1Rules) {
  const auto driver_info = InitDriverInfo();
  const models::priorities::FindMatchingTtl visitor{driver_info};

  {
    RulesVariant rule{AllOf{{tag[1], tag[2], tag[3]}}};
    const auto result = std::visit(visitor, rule);
    ASSERT_EQ(*result, kExpireNotThatEarly);
  }

  {
    RulesVariant rule{AllOf{{tag[1], tag[2], tag[3], "non_existing"}}};
    ASSERT_FALSE(std::visit(visitor, rule));
  }

  {
    RulesVariant rule{AnyOf{{tag[0], tag[1], tag[2]}}};
    const auto result = std::visit(visitor, rule);
    ASSERT_EQ(*result, kExpireNotSoon);
  }

  {
    RulesVariant rule{AnyOf{{"non1", "non2"}}};
    ASSERT_FALSE(std::visit(visitor, rule));
  }

  {
    RulesVariant rule{NoneOf{{"non_existing_tag"}}};
    const auto result = std::visit(visitor, rule);
    ASSERT_EQ(*result, kNeverExpire);
  }

  {
    RulesVariant rule{NoneOf{{tag[0]}}};
    ASSERT_FALSE(std::visit(visitor, rule));
  }
}

TEST(PriorityRule, L2Rules) {
  const auto driver_info = InitDriverInfo();
  const models::priorities::FindMatchingTtl visitor{driver_info};

  {
    RulesVariant rule = AndRule{{AllOf{{tag[0]}}, AllOf{{tag[1]}}}};
    const auto result = std::visit(visitor, rule);
    ASSERT_EQ(*result, kExpireEarly);
  }

  {
    RulesVariant rule = AndRule{{AllOf{{tag[0]}}, AllOf{{"non_existing"}}}};
    ASSERT_FALSE(std::visit(visitor, rule));
  }

  {
    RulesVariant rule{
        OrRule{{AllOf{{tag[0]}}, AllOf{{tag[1]}}, NoneOf{{"non_existing"}}}}};
    const auto result = std::visit(visitor, rule);
    ASSERT_EQ(*result, kNeverExpire);
  }

  {
    RulesVariant rule{OrRule{{AllOf{{"non_existing"}}, AllOf{{"abacaba"}}}}};
    ASSERT_FALSE(std::visit(visitor, rule));
  }
}
