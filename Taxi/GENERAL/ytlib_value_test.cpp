#include <gtest/gtest.h>
#include <userver/formats/json.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <ytlib/ytlib.hpp>

namespace {
formats::json::Value MakeJson() {
  return formats::json::MakeObject(
      "key",
      formats::json::MakeObject("$v", "string", "$a",
                                formats::json::MakeObject("foo", "bar")),
      "simple_key", "simple_string");
}

std::optional<formats::json::Value> YTAttrsProcessor(
    const formats::json::Value& value, const formats::json::Value& attrs) {
  if (!attrs["foo"].IsMissing()) {
    auto foo_value =
        value.As<std::string>() + "_" + attrs["foo"].As<std::string>();
    return formats::json::ValueBuilder(foo_value).ExtractValue();
  }
  return std::nullopt;
}

}  // namespace

TEST(YtlibValue, AsString) {
  auto yt_value = ytlib::Value{MakeJson()};
  ASSERT_EQ(yt_value["key"].As<std::string>(), "string");
}

TEST(YtlibValue, CheckMissing) {
  auto yt_value = ytlib::Value{MakeJson()};
  ASSERT_EQ(yt_value["missing_key"].As<std::optional<std::string>>(),
            std::nullopt);
}

TEST(YtlibValue, AsStringSimple) {
  auto yt_value = ytlib::Value{MakeJson()};
  ASSERT_EQ(yt_value["simple_key"].As<std::string>(), "simple_string");
}

TEST(YtlibValue, GetAttrs) {
  auto yt_value = ytlib::Value{MakeJson()};
  ytlib::Value attrs = yt_value["key"].GetAttributes();
  ASSERT_TRUE(attrs.IsObject());
  ASSERT_TRUE(attrs["empty"].IsMissing());
  ASSERT_EQ(attrs["foo"].As<std::string>(), "bar");
  ASSERT_TRUE(attrs.GetAttributes().IsNull());
}

TEST(YtlibValue, ToString) {
  auto yt_value = ytlib::Value{MakeJson()};
  ASSERT_EQ(ytlib::ToString(yt_value["key"]), "\"string\"");
  ASSERT_EQ(ytlib::ToString(yt_value),
            "{\"key\":\"string\",\"simple_key\":\"simple_string\"}");
  ASSERT_EQ(formats::json::ToString(yt_value.DebuggingGetRawJson()),
            "{\"key\":{\"$v\":\"string\",\"$a\":{\"foo\":\"bar\"}},\"simple_"
            "key\":\"simple_string\"}");
}

// YT Attributes
TEST(YtlibValue, AttrsProcessor) {
  auto yt_value = ytlib::Value{MakeJson()};
  auto json1 = yt_value.As<formats::json::Value>();
  ASSERT_EQ(json1["key"].As<std::string>(), "string");
  auto json2 = ytlib::transform::RecursiveVisit(yt_value, YTAttrsProcessor)
                   .As<formats::json::Value>();
  ASSERT_EQ(json2["key"].As<std::string>(), "string_bar");
}
