#include "json_stable_collect.hpp"

#include <iomanip>
#include <optional>
#include <sstream>
#include <string>

#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>

namespace json_hash::details::stable_collect {

namespace {

class PrintCollector {
 public:
  void PutField(std::string&& name) {
    stream << "\"" << std::move(name) << "\":";
  }
  void PutElementsSeparator() { stream << ","; }
  void PutObjectStart() { stream << "{"; }
  void PutObjectEnd() { stream << "}"; }
  void PutArrayStart() { stream << "["; }
  void PutArrayEnd() { stream << "]"; }

  void PutValue(std::uint64_t v) { stream << v; }
  void PutValue(std::int64_t v) { stream << v; }
  void PutValue(double v) { stream << std::fixed << std::setprecision(1) << v; }
  void PutValue(bool v) { stream << std::boolalpha << v; }
  void PutValue(std::string&& v) { stream << "\"" << std::move(v) << "\""; }
  void PutNullValue() { stream << "null"; }
  void FinishCollect() { result = stream.str(); }
  std::string Result() const { return result; }

 private:
  std::stringstream stream{};
  std::string result;
};

std::string Print(const std::string& json_str, bool skip_null = false) {
  const auto json = formats::json::FromString(json_str);
  auto collector = PrintCollector{};
  StableCollect(json, collector, skip_null);
  return collector.Result();
}

TEST(JsonStableCollect, TrivialCases) {
  EXPECT_EQ(Print("{}"), "{}");
  EXPECT_EQ(Print("[]"), "[]");
  EXPECT_EQ(Print("null"), "null");
  EXPECT_EQ(Print(R"({"field": "string"})"), R"({"field":"string"})");
  EXPECT_EQ(Print(R"({"field": [3, 2, 1]})"), R"({"field":[3,2,1]})");
  EXPECT_EQ(Print(R"({"field": 1, "build": 1.2, "dield": true})"),
            R"({"build":1.2,"dield":true,"field":1})");
}

TEST(JsonStableCollect, DoubleVsInt) {
  EXPECT_EQ(Print(R"({"field": 1.0})"), R"({"field":1})");
  EXPECT_EQ(Print(R"({"field": -2.0})"), R"({"field":-2})");
}

TEST(JsonStableCollect, NoneTrivialCase) {
  const auto str_json = std::string(R"(
        {
            "aa": {},
            "c": "str",
            "bb": {
                "ddd": ["x"],
                "dd": [1, 2, 3],
                "dddd": -12,
                "d": [
                    {
                        "s": 1.4,
                        "m": 2,
                        "z": {
                            "lul": null,
                            "pop": []
                        }
                    },
                    {
                        "a2": -2.4,
                        "a1": {
                            "bo": true,
                            "bo2": false
                        },
                        "a3": ""
                    }
                ]
            }
        }
    )");
  const auto expected_str = std::string{
      "{"
      R"("aa":{},)"
      R"("bb":{)"
      R"("d":[)"
      R"({"m":2,"s":1.4,"z":{"lul":null,"pop":[]}})"
      ","
      R"({"a1":{"bo":true,"bo2":false},"a2":-2.4,"a3":""})"
      "],"
      R"("dd":[1,2,3],"ddd":["x"],"dddd":-12},)"
      R"("c":"str")"
      "}"};
  EXPECT_EQ(Print(str_json), expected_str);
}

TEST(JsonStableCollect, SkipNullFields) {
  const auto print = [](std::string s) { return Print(std::move(s), true); };
  EXPECT_EQ(print("null"), "null");
  EXPECT_EQ(print(R"({"field": "string"})"), R"({"field":"string"})");
  EXPECT_EQ(print(R"({"field": null})"), R"({})");
  EXPECT_EQ(print(R"({"a": null, "b": 1})"), R"({"b":1})");
  EXPECT_EQ(print(R"({"b": null, "a": 1})"), R"({"a":1})");
  const auto str_json = std::string(R"(
        {
            "aa": {},
            "cc": null,
            "bbb": {
                "dddd": 12,
                "ddd": [1, null, 3],
                "ddddd": null
            }
        }
    )");
  const auto expected_str =
      std::string{R"({"aa":{},"bbb":{"ddd":[1,null,3],"dddd":12}})"};
  EXPECT_EQ(print(str_json), expected_str);
}

}  // namespace

}  // namespace json_hash::details::stable_collect
