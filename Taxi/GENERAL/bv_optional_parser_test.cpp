#include <gtest/gtest.h>

#include <pricing-functions/helpers/adapted_io.hpp>
#include <pricing-functions/helpers/bv_optional_parse.hpp>
#include <pricing-functions/lang/internal/backend_variables_io.hpp>
#include <userver/formats/json.hpp>
#include <userver/formats/json/serialize_duration.hpp>

namespace {

std::string to_json(const lang::variables::BackendVariables& bv) {
  return formats::json::ToString(
      Serialize(bv, formats::serialize::To<formats::json::Value>()));
}

}  // namespace

TEST(BvOptionalParserTest, ParseEmpty) {
  auto doc = formats::json::FromString("{}");
  const auto parsed_bv = formats::parse::ParseBackendVariablesOptional(doc);
  const lang::variables::BackendVariables default_bv{};
  EXPECT_EQ(to_json(parsed_bv), to_json(default_bv));
}

TEST(BvOptionalParserTest, ParseUnorderedMapFromConfig) {
  auto doc = formats::json::FromString(R"json({
  "editable_requirements": {
    "luggage_count": {
      "max_value": 3,
      "min_value": 0
    },
    "third_passenger": {
      "max_value": 1,
      "min_value": 0
    }
  }
})json");

  const auto parsed_bv = formats::parse::ParseBackendVariablesOptional(doc);
  lang::variables::BackendVariables bv{};
  bv.editable_requirements = lang::variables::EditableRequirements{
      {"luggage_count", {0, 0, 3}}, {"third_passenger", {0, 0, 1}}};
  EXPECT_EQ(to_json(parsed_bv), to_json(bv));
}

TEST(BvOptionalParserTest, ParseOptionalEnum) {
  auto doc = formats::json::FromString(R"json(
{
  "forced_skip_label": "without_surge"
}
)json");

  const auto parsed_bv = formats::parse::ParseBackendVariablesOptional(doc);
  lang::variables::BackendVariables bv{};
  bv.forced_skip_label = lang::variables::ForcedSkipLabel::kWithoutSurge;
  EXPECT_EQ(to_json(parsed_bv), to_json(bv));
}
