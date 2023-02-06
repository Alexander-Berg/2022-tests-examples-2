#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

#include "json_filter.hpp"

using eats_layout_constructor::utils::json::FilterJSON;
using formats::json::FromString;

TEST(FilterJSON, NothingFiltered) {
  for (const auto json_str :
       {"{}", "[]", R"({"i": 1})", R"([1])", R"(["a"])", R"([1, "a"])"}) {
    const auto json = FromString(json_str);
    ASSERT_EQ(FilterJSON(json, {}), json);
    ASSERT_EQ(FilterJSON(json, {"a", "b"}), json);
  }
}

TEST(FilterJSON, SimpleJSON) {
  ASSERT_EQ(FilterJSON(FromString(R"({"a": 1})"), {"a"}), FromString("{}"));
  ASSERT_EQ(
      FilterJSON(FromString(R"({"a": 1, "b": {"i": 1}, "c": []})"), {"b"}),
      FromString(R"({"a": 1, "c": []})"));
  ASSERT_EQ(FilterJSON(FromString(R"({"i": {"a": 1}})"), {"a"}),
            FromString(R"({"i": {}})"));
  ASSERT_EQ(FilterJSON(FromString(R"([1, "a", {"a": 3, "b": 33}, 4])"), {"a"}),
            FromString(R"([1, "a", {"b": 33}, 4])"));
  ASSERT_EQ(
      FilterJSON(FromString(R"([1, "a", {"a": 3, "b": 33}, 4])"), {"a", "b"}),
      FromString(R"([1, "a", {}, 4])"));
}

TEST(FilterJSON, ComplexJSON) {
  const auto src_json = FromString(R"(
  {
    "i": 1,
    "arr": [1, 2, {"bad": [11, 12]}, 3],
    "bad": 1234,
    "obj1": {"obj1_1": 1, "ugly": {"x": 2}},
    "obj2": {"obj2_1": ["bad", {"bad": [], "i": 2}]}
  }
  )");
  const auto filtered_json = FromString(R"(
  {
    "i": 1,
    "arr": [1, 2, {}, 3],
    "obj1": {"obj1_1": 1},
    "obj2": {"obj2_1": ["bad", {"i": 2}]}
  }
  )");
  ASSERT_EQ(FilterJSON(src_json, {"bad", "ugly"}), filtered_json);
}
