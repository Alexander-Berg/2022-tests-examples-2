#include <helpers/json_merge.hpp>
#include <userver/utest/utest.hpp>

namespace eats_restapp_communications::helpers {

struct JsonMergeParams {
  std::string origin;
  std::string patch;
  std::string expected_result;
};

struct JsonMergeTest : public ::testing::TestWithParam<JsonMergeParams> {};

const std::vector<JsonMergeParams> kJsonMergeParamsData{
    {"{}", "{}", "{}"},
    {R"({"key": "value"})", "{}", R"({"key": "value"})"},
    {"{}", R"({"key": "value"})", R"({"key": "value"})"},
    {R"({"key": "value"})", R"({"other": "value"})",
     R"({"key": "value", "other": "value"})"},
    {R"({"key": "value"})", R"({"key": "other"})", R"({"key": "other"})"},
    {R"({"key": "value"})", R"({"key": ["other"]})", R"({"key": ["other"]})"},
    {R"({"key": ["value"]})", R"({"key": "other"})", R"({"key": "other"})"},
    {R"({"key": ["value"]})", R"({"key": ["other"]})",
     R"({"key": ["value", "other"]})"},
    {R"({"key": "value"})", R"({"key": {"other": "value"}})",
     R"({"key": {"other": "value"}})"},
    {R"({"key": {"some": "value"}})", R"({"key": "other"})",
     R"({"key": "other"})"},
    {R"({"key": {"some": "value"}})", R"({"key": ["other"]})",
     R"({"key": ["other"]})"},
    {R"({"key": ["value"]})", R"({"key": {"other": "value"}})",
     R"({"key": {"other": "value"}})"},
    {R"({"key": {"some": "value"}})", R"({"key": {"some": "other"}})",
     R"({"key": {"some": "other"}})"},
    {R"({"key": {"some": "value"}})", R"({"key": {"other": "value"}})",
     R"({"key": {"some": "value", "other": "value"}})"},
    {R"({"key": {"some": ["value"]}})", R"({"key": {"some": "other"}})",
     R"({"key": {"some": "other"}})"},
    {R"({"key": {"some": "value"}})", R"({"key": {"some": ["other"]}})",
     R"({"key": {"some": ["other"]}})"},
    {R"({"key": {"some": ["value"]}})", R"({"key": {"some": ["other"]}})",
     R"({"key": {"some": ["value", "other"]}})"},
};

INSTANTIATE_TEST_SUITE_P(JsonMergeParams, JsonMergeTest,
                         ::testing::ValuesIn(kJsonMergeParamsData));

TEST_P(JsonMergeTest, should_merge_jsons) {
  auto param = GetParam();
  ::formats::json::ValueBuilder origin(
      ::formats::json::FromString(param.origin));
  auto patch = ::formats::json::FromString(param.patch);
  JsonMerge(origin, patch);
  ASSERT_EQ(origin.ExtractValue(),
            ::formats::json::FromString(param.expected_result));
}

}  // namespace eats_restapp_communications::helpers
