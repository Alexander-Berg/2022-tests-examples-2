#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include "formatter.hpp"

TEST(Formatter, HasFormatting) {
  formats::json::ValueBuilder no_formatting;
  no_formatting["param1"] = "No formatting";
  no_formatting["param2"]["subparam"] = "No formatting";
  no_formatting["param3"].PushBack("No formatting");
  EXPECT_FALSE(utils::HasFormatting(no_formatting.ExtractValue()));

  formats::json::ValueBuilder has_formatting_simple;
  has_formatting_simple["param1"] = "It {has} formatting";
  EXPECT_TRUE(utils::HasFormatting(has_formatting_simple.ExtractValue()));

  formats::json::ValueBuilder has_formatting_array;
  has_formatting_array["param1"].PushBack("It {has} formatting");
  EXPECT_TRUE(utils::HasFormatting(has_formatting_array.ExtractValue()));

  formats::json::ValueBuilder has_formatting_object;
  has_formatting_object["param1"]["subobj"] = "It {has} formatting";
  EXPECT_TRUE(utils::HasFormatting(has_formatting_object.ExtractValue()));
}

TEST(Formatter, StringOk) {
  EXPECT_EQ("Hello!", utils::Format("Hello!", {}));

  EXPECT_EQ("Hello, Vladimir!",
            utils::Format("Hello, {name}!", {{"name", "Vladimir"}}));

  EXPECT_EQ(
      "Hello, Vladimir! Here is your 100$",
      utils::Format("Hello, {name}! Here is your {value}{sign}",
                    {{"name", "Vladimir"}, {"value", "100"}, {"sign", "$"}}));

  EXPECT_EQ("at begin and at end",
            utils::Format("{begin} and {end}",
                          {{"begin", "at begin"}, {"end", "at end"}}));

  EXPECT_EQ(
      "Same param used twice param",
      utils::Format("Same {param} used twice {param}", {{"param", "param"}}));

  EXPECT_EQ("{external braces are escaped}",
            utils::Format("\\{{param}\\}",
                          {{"param", "external braces are escaped"}}));

  EXPECT_EQ("\\}{{}{}}{\\", utils::Format("\\\\}\\{\\{\\}\\{\\}\\}\\{\\", {}));
}

TEST(Formatter, StringErrors) {
  EXPECT_THROW(utils::Format("{missing closing brace", {}),
               utils::FormatterError);

  EXPECT_THROW(utils::Format("unexpected closing brace}", {}),
               utils::FormatterError);

  EXPECT_THROW(utils::Format("{unexpected opening brace{}", {}),
               utils::FormatterError);

  EXPECT_THROW(utils::Format("Parameter is {missing}", {}),
               utils::FormatterError);

  EXPECT_THROW(utils::Format("empty parameter name {}", {}),
               utils::FormatterError);

  EXPECT_THROW(utils::Format("{", {}), utils::FormatterError);

  EXPECT_THROW(utils::Format("}", {}), utils::FormatterError);
}

TEST(Formatter, JsonOk) {
  // Provided
  formats::json::ValueBuilder payload;
  payload["title"] = "Hello, {user}!";
  payload["text"] = "Here is your {value}{sign}";
  payload["empty_object"] = formats::common::Type::kObject;
  payload["empty_array"] = formats::common::Type::kArray;
  payload["null"] = formats::common::Type::kNull;
  payload["subobj"]["field1"] =
      "subobj->field1 with {parameter1} and {parameter2}";
  payload["subobj"]["field2"] = "subobj->field2 with null {nullparam}";
  payload["subobj"]["subobj"]["field"] = "\\{{escaped}\\}";
  payload["array"].PushBack("String {one}");
  payload["array"].PushBack("String {two}");

  std::unordered_map<std::string, std::string> payload_params;
  payload_params["user"] = "Vladimir";
  payload_params["value"] = "100";
  payload_params["sign"] = "$";
  payload_params["parameter1"] = "parameter1 value";
  payload_params["parameter2"] = "parameter2 value";
  payload_params["nullparam"] = "";
  payload_params["escaped"] = "99.999";
  payload_params["one"] = "TheOne";
  payload_params["two"] = "TheTwo";

  // Expected
  formats::json::ValueBuilder builder;
  builder["title"] = "Hello, Vladimir!";
  builder["text"] = "Here is your 100$";
  builder["empty_object"] = formats::common::Type::kObject;
  builder["empty_array"] = formats::common::Type::kArray;
  builder["null"] = formats::common::Type::kNull;
  builder["subobj"]["field1"] =
      "subobj->field1 with parameter1 value and parameter2 value";
  builder["subobj"]["field2"] = "subobj->field2 with null ";
  builder["subobj"]["subobj"]["field"] = "{99.999}";
  builder["array"].PushBack("String TheOne");
  builder["array"].PushBack("String TheTwo");

  const auto& expected = builder.ExtractValue();

  const auto& actual = utils::Format(payload.ExtractValue(), payload_params);
  ASSERT_EQ(expected, actual)
      << "Expect: " << formats::json::ToString(expected) << std::endl
      << "Actual: " << formats::json::ToString(actual);
}

TEST(Formatter, RemoveEscapedBraces) {
  formats::json::ValueBuilder payload;
  payload[""] = "";
  payload["string"] = "string";
  payload["{}"] = "{}";
  payload["{"] = "\\{";
  payload["{}"] = "\\{\\}";
  payload["{{{"] = "\\{\\{\\{";
  payload["\\\\\\"] = "\\\\\\";
  payload["\\\\{}"] = "\\\\\\{}";
  payload["{param}"] = "\\{param\\}";
  payload["{param}\\"] = "\\{param\\}\\";

  auto result = utils::RemoveEscapedBraces(payload.ExtractValue());

  for (auto it = result.begin(); it != result.end(); ++it) {
    ASSERT_EQ(it.GetName(), it->As<std::string>());
  }
}
