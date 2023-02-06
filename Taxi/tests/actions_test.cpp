#include <userver/utest/utest.hpp>

#include <billing-templates/billing_templates.hpp>

namespace billing_templates {

const auto jsonTemplateFilledVars = formats::json::FromString(R"=(
{
  "actions": [
    {
      "$func": "some_function_name",
      "$vars": {
        "value_id": {
          "$context": "value"
        },
        "string_id": {
          "$format": "{value}"
        },
        "not_present": {
          "$if_present": "wrong.field"
        },
        "date_string": {
          "$format": "{string}"
        },
        "dict_example": {
          "value": {
            "$context": "dict.value"
          },
          "string": {
            "$context": "dict.string"
          },
          "not_present_in_dict": {
            "$if_present": "wrong.field"
          },
          "not_present_in_nested_dict": {
            "not_present_value": {
              "$if_present": "wrong.field"
            }
          }
        },
        "md5_example": {
          "$md5": "value"
        }
      }
    },
    {
      "$func": "yet_another_function_name",
      "$vars": {}
    }
  ]
})=");

const auto jsonTemplateEmptyVars = formats::json::FromString(R"=(
{
  "actions": [
    {
      "$func": "yet_another_function_name",
      "$vars": {}
    }
  ]
})=");

const auto jsonTemplateFuncNameMissed = formats::json::FromString(R"=(
{
  "actions": [
    {
      "$vars": {}
    }
  ]
})=");

const auto jsonTemplateVarsMissed = formats::json::FromString(R"=(
{
  "actions": [
    {
      "$func": "yet_another_function_name"
    }
  ]
})=");

const auto jsonCorrectContext = formats::json::FromString(R"=(
{
  "context": {
    "value": 125,
    "string": "2020-01-01T00:00:00+00:00",
    "dict": {
      "value": 111,
      "string": "RUB"
    }
  }
})=");

const auto jsonExceptionContext = formats::json::FromString(R"=(
{
  "context": {
    "string": "2020-01-01T00:00:00+00:00",
    "dict": {
      "value": 111,
      "string": "RUB"
    }
  }
})=");

const auto jsonIncorrectContext = formats::json::FromString(R"=(
{
  "context": {
    "value": 225,
    "string": "2020-01-01T00:00:00+00:00",
    "dict": {
      "value": 111,
      "string": "EU"
    }
  }
})=");

const auto expectedActionFilledVars = formats::json::FromString(R"=(
 {
   "func": "some_function_name",
   "keywords": {
     "value_id": 125,
     "string_id": "125",
     "date_string":"2020-01-01T00:00:00+00:00",
     "dict_example": {
       "value": 111,
       "string": "RUB",
       "not_present_in_nested_dict":{}
     },
     "md5_example":"2063c1608d6e0baf80249c42e2be5804"
   }
 })=");

const auto expectedActionEmptyVars = formats::json::FromString(R"=(
 {
   "func": "yet_another_function_name",
   "keywords": {}
 })=");

TEST(TestGenerateActions, ActionCorrectContextFilledVars) {
  auto context = jsonCorrectContext["context"];
  auto generated_actions = GenerateActions(jsonTemplateFilledVars, context);
  auto action = generated_actions[0];
  ASSERT_EQ(action, expectedActionFilledVars);
}

TEST(TestGenerateActions, ActionCorrectContextEmptyVars) {
  auto context = jsonCorrectContext["context"];
  auto generated_actions = GenerateActions(jsonTemplateEmptyVars, context);
  auto action = generated_actions[0];
  ASSERT_EQ(action, expectedActionEmptyVars);
}

TEST(TestGenerateActions, ActionMissedFuncName) {
  auto context = jsonIncorrectContext["context"];
  EXPECT_THROW(GenerateActions(jsonTemplateFuncNameMissed, context),
               fj::MemberMissingException);
}

TEST(TestGenerateActions, ActionMissedVars) {
  auto context = jsonIncorrectContext["context"];
  EXPECT_THROW(GenerateActions(jsonTemplateVarsMissed, context),
               fj::MemberMissingException);
}

TEST(TestGenerateActions, ActionPresentValueException) {
  auto context = jsonExceptionContext["context"];
  EXPECT_THROW(GenerateActions(jsonTemplateFilledVars, context),
               fj::MemberMissingException);
}

}  // namespace billing_templates
