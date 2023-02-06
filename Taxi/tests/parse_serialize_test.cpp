#include <models/rule.hpp>

#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

namespace {

const std::string kExpectedPriorityRule = R"(
{
  "single_rule": {
    "tag_name": "tag_name0",
    "priority_value": {
      "backend": 1,
      "display": 2
    },
    "override": {
      "and": [
        {"value": true},
        {"none_of": ["tag0", "tag1"]}
      ]
    }
  }
}
)";

const std::string kDeepPriorityRule = R"(
{
  "single_rule": {
    "tag_name": "tag_name0",
    "priority_value": {
      "backend": 1,
      "display": 2
    },
    "override": {
      "not": {
        "and": [
          {"none_of": ["tag0", "tag1"]},
          {"any_of": ["tag2", "tag3"]},
          {"not":
            {"all_of": ["tag4", "tag5"]}
          }
        ]
      }
    }
  }
}
)";

}  // namespace

TEST(ParseSerialize, PriorityRule) {
  // correct parse and serialize
  {
    const handlers::Condition kCondition{handlers::AndRule{
        {handlers::Value{true}, handlers::NoneOf{{"tag0", "tag1"}}}}};

    const handlers::TagRule kTagRule{"tag_name0", handlers::PriorityValue{1, 2},
                                     kCondition};

    const handlers::PriorityRule priority_rule{handlers::SingleRule{kTagRule}};

    const auto json = models::Serialize(priority_rule);
    ASSERT_EQ(json, formats::json::FromString(kExpectedPriorityRule));

    const auto rule = models::ParsePriorityRule(json);
    ASSERT_EQ(rule, priority_rule);
  }

  // parse failed: too deep condition
  {
    const auto json = formats::json::FromString(kDeepPriorityRule);
    ASSERT_THROW(models::ParsePriorityRule(json), std::exception);
  }
}
