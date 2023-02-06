#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <access-control-info/utils/json.hpp>

namespace access_control_info {

TEST(AccessControlInfoJson, GetNestedTest) {
  formats::json::Value body = formats::json::FromString(R"=(
{
"simple_field": "string_value",
"simple_field2": 123,
"object": {
  "nested_field": "nested_string_value",
  "nested_field2": 456,
  "nested_object": {
    "subfield": "subfield_value"
  }
}
}
)=");

  {
    auto value =
        access_control_info::utils::json::GetNested("simple_field", body);
    EXPECT_EQ("string_value", value.As<std::string>());
  }
  {
    auto value =
        access_control_info::utils::json::GetNested("simple_field2", body);
    EXPECT_EQ(123, value.As<int>());
  }
  {
    auto value = access_control_info::utils::json::GetNested(
        "object.nested_field", body);
    EXPECT_EQ("nested_string_value", value.As<std::string>());
  }
  {
    auto value = access_control_info::utils::json::GetNested(
        "object.nested_field2", body);
    EXPECT_EQ(456, value.As<int>());
  }
  {
    auto value = access_control_info::utils::json::GetNested(
        "object.nested_object.subfield", body);
    EXPECT_EQ("subfield_value", value.As<std::string>());
  }
  {
    auto value = access_control_info::utils::json::GetNested(
        "nonexistent_firstlevel_field", body);
    EXPECT_TRUE(value.IsMissing());
  }
  {
    auto value = access_control_info::utils::json::GetNested(
        "nonexistent.subfield", body);
    EXPECT_TRUE(value.IsMissing());
  }
}

}  // namespace access_control_info
