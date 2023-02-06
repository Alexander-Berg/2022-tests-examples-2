#include <userver/utest/utest.hpp>

#include <billing-templates/billing_templates.hpp>

namespace billing_templates {

const auto jsonTemplate = formats::json::FromString(R"=(
{
  "entries": [
    {
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

const auto expectedEntries = formats::json::FromString(R"=(
 {
   "value_id": 125,
   "string_id": "125",
   "date_string":"2020-01-01T00:00:00+00:00",
   "dict_example": {
     "value": 111,
     "string": "RUB",
     "not_present_in_nested_dict":{}
   },
   "md5_example":"2063c1608d6e0baf80249c42e2be5804"
 })=");

TEST(TestGenerateEntries, EntryCorrectContext) {
  auto context = jsonCorrectContext["context"];
  auto generated_entries = GenerateEntries(jsonTemplate, context);
  auto entry = generated_entries[0];
  ASSERT_EQ(entry, expectedEntries);
}

TEST(TestGenerateEntries, EntryPresentValueException) {
  auto context = jsonExceptionContext["context"];
  EXPECT_THROW(GenerateEntries(jsonTemplate, context),
               fj::MemberMissingException);
}

}  // namespace billing_templates
