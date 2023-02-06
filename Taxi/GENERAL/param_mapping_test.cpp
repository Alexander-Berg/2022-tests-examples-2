#include <gtest/gtest.h>

#include "param_mapping.hpp"

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace {

formats::json::ValueBuilder GetToBuilder() {
  formats::json::ValueBuilder doc;
  doc["a"]["b"]["c"]["d"] = "e";
  doc["a"]["0"]["1"] = 2;
  doc["b"] = std::vector<int>{1, 2, 3};
  doc["c"] = formats::json::Value();
  return doc;
}

formats::json::Value GetFromJson() { return GetToBuilder().ExtractValue(); }

}  // namespace

TEST(ParamMapping, SetNonexisting) {
  std::unordered_map<std::string, std::string> map = {
      {"x", ""},
  };
  const auto& from = GetFromJson();
  auto builder = GetToBuilder();
  utils::MapParams(builder, from, map, "/");
  auto result = builder.ExtractValue();
  ASSERT_EQ(result, from);
}

TEST(ParamMapping, SetExisting) {
  std::unordered_map<std::string, std::string> map = {
      {"a/b/c", "ab/c"},
      {"a/0/1", "ab/d"},
  };
  const auto& from = GetFromJson();
  auto builder = GetToBuilder();
  utils::MapParams(builder, from, map, "/");
  auto result = builder.ExtractValue();
  ASSERT_EQ(result["ab"]["c"], from["a"]["b"]["c"]);
  ASSERT_EQ(result["ab"]["d"], from["a"]["0"]["1"]);
}

TEST(ParamMapping, SetOnExisting) {
  std::unordered_map<std::string, std::string> map = {
      {"a", "b"},
  };
  const auto& from = GetFromJson();
  auto builder = GetToBuilder();
  utils::MapParams(builder, from, map, "/");
  auto result = builder.ExtractValue();
  ASSERT_EQ(result["b"], from["a"]);
}

TEST(ParamMapping, SetOnExistingNotObject) {
  std::unordered_map<std::string, std::string> map = {
      {"a", "b/n"},
  };
  const auto& from = GetFromJson();
  auto builder = GetToBuilder();
  utils::MapParams(builder, from, map, "/");
  auto result = builder.ExtractValue();
  ASSERT_THROW(result["b"]["n"], std::exception);
  ASSERT_EQ(result["b"], from["b"]);
}
