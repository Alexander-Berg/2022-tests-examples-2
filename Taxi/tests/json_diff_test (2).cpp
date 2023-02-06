#include <userver/utest/utest.hpp>

#include <json-diff/json_diff_result.hpp>

namespace json_diff {

TEST(JsonDiff, Equals) {
  const auto& v1 = formats::json::FromString("{\"a\": 1}");
  const auto& v2 = formats::json::FromString("{\"a\": 1}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 0);
}

TEST(JsonDiff, DifferentValues) {
  const auto& v1 = formats::json::FromString("{\"a\": 2}");
  const auto& v2 = formats::json::FromString("{\"a\": 1}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 1);
  EXPECT_EQ(mismatches[0], "a");
}

TEST(JsonDiff, DifferentTypes) {
  const auto& v1 = formats::json::FromString("{\"a\": \"1\"}");
  const auto& v2 = formats::json::FromString("{\"a\": 1}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 1);
  EXPECT_EQ(mismatches[0], "a");
}

TEST(JsonDiff, DifferentKeys) {
  const auto& v1 = formats::json::FromString("{\"a\": 1}");
  const auto& v2 = formats::json::FromString("{\"b\": 1}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 2);
  EXPECT_EQ(mismatches[0], "a");
  EXPECT_EQ(mismatches[1], "b");
}

TEST(JsonDiff, DifferentStringValue) {
  const auto& v1 = formats::json::FromString("{\"a\": \"\"}");
  const auto& v2 = formats::json::FromString("{}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 1);
  EXPECT_EQ(mismatches[0], "a");
}

TEST(JsonDiff, DifferentStringValueSetting) {
  const auto& v1 = formats::json::FromString("{\"a\": \"\"}");
  const auto& v2 = formats::json::FromString("{}");
  const auto& mismatches = GetMismatches(v1, v2, {true});
  EXPECT_EQ(mismatches.size(), 0);
}

TEST(JsonDiff, Empty) {
  const auto& v1 = formats::json::FromString("{}");
  const auto& v2 = formats::json::FromString("{}");
  const auto& mismatches = GetMismatches(v1, v2);
  EXPECT_EQ(mismatches.size(), 0);
}

}  // namespace json_diff
