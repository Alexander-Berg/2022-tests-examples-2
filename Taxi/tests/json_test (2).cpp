#include <algorithm>

#include <gtest/gtest.h>

#include <userver/formats/json.hpp>

#include <sensitive-data-masking/json.hpp>

namespace sensitive_data_masking {

namespace {

const std::vector<JsonPath> kDefaultPaths = {{"phone"}};

std::string CorrectJsonWithoutSpaces(const std::string& source) {
  return formats::json::ToString(
      formats::json::FromString(R"({"root":)" + source + "}"));
}

void MaskAndCheck(const std::string& source, const std::string& expected,
                  const std::vector<JsonPath>& paths = kDefaultPaths) {
  const auto& source_json = formats::json::FromString(source);
  const auto& result = MaskJsonPaths(source_json, paths);

  EXPECT_EQ(CorrectJsonWithoutSpaces(result),
            CorrectJsonWithoutSpaces(expected));
}

void RemoveAndCheck(const std::string& source, const std::string& expected,
                    const std::vector<JsonPath>& paths = kDefaultPaths) {
  const auto& source_json = formats::json::FromString(source);
  const auto& result = RemoveJsonPaths(source_json, paths);

  EXPECT_EQ(CorrectJsonWithoutSpaces(result),
            CorrectJsonWithoutSpaces(expected));
}

}  // namespace

TEST(TestCorrectJsonWithoutspaces, CheckSimple) {
  const auto& input = R"({
    "array": [
      1,
      2,
      3
    ],
    "object": {
      "key": "value"
    },
    "string": "string",
    "number": 42,
    "null": null
  })";
  const auto& expected =
      R"({"root":{"array":[1,2,3],"object":{"key":"value"},"string":"string",)"
      R"("number":42,"null":null}})";

  EXPECT_EQ(CorrectJsonWithoutSpaces(input), expected);
}

TEST(TestMaskingJson, CheckEmptyObject) {
  MaskAndCheck("{}", "{}");
  MaskAndCheck("{}", "{}", {});
}

TEST(TestMaskingJson, CheckEmptyArray) {
  MaskAndCheck("[]", "[]");
  MaskAndCheck("[]", "[]", {});
}

TEST(TestMaskingJson, CheckRootObject) {
  const auto& json = R"({"phone": "+70001234567"})";
  // empty path corresponds to the root object
  MaskAndCheck(json, R"("{...}")", {{}});
}

TEST(TestMaskingJson, CheckRootArray) {
  const auto& json = R"(["+70001234567"])";
  // empty path corresponds to the root object which can be an array
  MaskAndCheck(json, R"("[...]")", {{}});
}

TEST(TestMaskingJson, CheckMissingField) {
  const auto& json = R"({"phone": "+70001234567"})";
  const auto& expected = json;
  MaskAndCheck(json, expected, {{"phone_number"}});
}

TEST(TestMaskingJson, CheckScalarField) {
  const auto& inputs = {
      R"({"phone": "+70001234567"})",
      R"({"phone": 12345})",
      R"({"phone": null})",
  };

  for (const auto& input : inputs) {
    MaskAndCheck(input, R"({"phone": "..."})");
  }
}

TEST(TestMaskingJson, CheckObjectField) {
  const auto& input = R"({"phone": {"a": 1}})";
  MaskAndCheck(input, R"({"phone": "{...}"})");
}

TEST(TestMaskingJson, CheckArrayField) {
  const auto& input = R"({"phone": [1, 2, 3]})";
  MaskAndCheck(input, R"({"phone": "[...]"})");
}

TEST(TestMaskingJson, CheckFieldAsValue) {
  const auto& json = R"({
    "column": "phone",
    "phone": "+70001234567"
  })";
  const auto& expected = R"({
    "column": "phone",
    "phone": "..."
  })";
  MaskAndCheck(json, expected);
}

TEST(TestMaskingJson, CheckRootAndNestedField) {
  const auto& json = R"({
    "user": {"phone": "+70001234567"},
    "phone": "+70007654321"
  })";
  const auto& root_field_expected = R"({
    "user": {"phone": "+70001234567"},
    "phone": "..."
  })";
  const auto& nested_field_expected = R"({
    "user": {"phone": "..."},
    "phone": "+70007654321"
  })";
  const auto& both_fields_expected = R"({
    "user": {"phone": "..."},
    "phone": "..."
  })";

  MaskAndCheck(json, root_field_expected, {{"phone"}});
  MaskAndCheck(json, nested_field_expected, {{"user", "phone"}});
  MaskAndCheck(json, both_fields_expected, {{"user", "phone"}, {"phone"}});
}

TEST(TestMaskingJson, CheckNestedPath) {
  const auto& json = R"({
    "user": {"phone": "+70001234567"}
  })";
  const auto& expected = R"({
    "user": "{...}"
  })";

  MaskAndCheck(json, expected, {{"user", "phone"}, {"user"}});
  MaskAndCheck(json, expected, {{"user"}, {"user", "phone"}});
}

TEST(TestMaskingJson, CheckInjectionDotNotation) {
  const auto& json = R"({
    "user": {"phone": "+70001234567"},
    "user.phone": "+70007654321"
  })";
  const auto& nested_field_expected = R"({
    "user": {"phone": "..."},
    "user.phone": "+70007654321"
  })";
  const auto& dot_field_expected = R"({
    "user": {"phone": "+70001234567"},
    "user.phone": "..."
  })";

  MaskAndCheck(json, nested_field_expected, {{"user", "phone"}});
  MaskAndCheck(json, dot_field_expected, {{"user.phone"}});
}

TEST(TestMaskingJson, CheckArrayFields) {
  const auto& json = R"([
    {"user": "alice", "phone": "+70001234567"},
    {"user": "bob", "phone": "+70007654321"}
  ])";
  const auto& expected_json = R"([
    {"user": "alice", "phone": "..."},
    {"user": "bob", "phone": "..."}
  ])";

  MaskAndCheck(json, expected_json);
}

TEST(TestMaskingJson, CheckComposite) {
  const auto& json = R"({
    "user": {
      "phones": [
        {
          "type": "android",
          "number": "+70001234567"
        },
        {
          "type": "iphone",
          "number": "+70007654321"
        }
      ],
      "number": 11
    },
    "main_phone": "+70001234567",
    "number": 42
  })";
  const auto& expected_json = R"({
    "user": {
      "phones": [
        {
          "type": "android",
          "number": "..."
        },
        {
          "type": "iphone",
          "number": "..."
        }
      ],
      "number": 11
    },
    "main_phone": "...",
    "number": 42
  })";

  MaskAndCheck(json, expected_json,
               {{"user", "phones", "number"}, {"main_phone"}});
}

TEST(TestPurgingJson, CheckRootAndNestedField) {
  const auto& json = R"({
    "user": {"phone": "+70001234567"},
    "phone": "+70007654321"
  })";
  const auto& root_field_expected = R"({
    "user": {"phone": "+70001234567"}
  })";
  const auto& nested_field_expected = R"({
    "user": {},
    "phone": "+70007654321"
  })";
  const auto& both_fields_expected = R"({
    "user": {}
  })";

  RemoveAndCheck(json, root_field_expected, {{"phone"}});
  RemoveAndCheck(json, nested_field_expected, {{"user", "phone"}});
  RemoveAndCheck(json, both_fields_expected, {{"user", "phone"}, {"phone"}});
}

TEST(TestPurgingJson, CheckEmpty) {
  const auto& json = R"({
    "user": {"phone": "+70001234567"}
  })";
  const auto& empty_expected = R"({})";

  RemoveAndCheck(json, empty_expected, {{"user"}});
}

TEST(TestPurgingJson, CheckArray) {
  const auto& json = R"({
    "user": {"items": [{"a": 1, "b": 2}]}
  })";
  const auto& json_multiple = R"({
    "user": {"items": [{"a": 1, "b": 2}, {"a": 2, "b": 3, "c": 4}]}
  })";
  const auto& expected = R"({
    "user": {"items": [{"b": 2}]}
  })";
  const auto& expected_multiple = R"({
    "user": {"items": [{"b": 2}, {"b": 3, "c": 4}]}
  })";

  RemoveAndCheck(json, expected, {{"user", "items", "a"}});
  RemoveAndCheck(json_multiple, expected_multiple, {{"user", "items", "a"}});
}

}  // namespace sensitive_data_masking
