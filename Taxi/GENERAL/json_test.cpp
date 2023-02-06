#include <gtest/gtest.h>

#include <logging/log_extra.hpp>
#include <utils/helpers/json.hpp>

const std::string source =
    "{             "
    "  \"a\": 1,   "
    "  \"b\": {    "
    "    \"q\": 2, "
    "    \"w\": 3  "
    "  },          "
    "  \"c\": [    "
    "    1, 2      "
    "  ],          "
    "  \"d\": 4,   "
    "  \"e\": 5    "
    "}             ";

const std::string set =
    "{              "
    "  \"a\": 10,   "
    "  \"b\": {     "
    "    \"q\": 20  "
    "  },           "
    "  \"c\": [     "
    "    10         "
    "  ],           "
    "  \"f\": 20    "
    "}              ";

const std::string unset =
    "{              "
    "  \"d\": true, "
    "  \"g\": true  "
    "}              ";

const std::string expected =
    "{              "
    "  \"a\": 10,   "
    "  \"b\": {     "
    "    \"q\": 20  "
    "  },           "
    "  \"c\": [     "
    "    10         "
    "  ],           "
    "  \"e\": 5,    "
    "  \"f\": 20    "
    "}              ";

void Check(const Json::Value& jsource, const Json::Value& jset,
           const Json::Value& junset, const Json::Value& jexpected) {
  const auto jpatched = utils::helpers::ApplyJsonPatch(jsource, jset, junset);
  ASSERT_EQ(jexpected, jpatched) << utils::helpers::WriteJson(jexpected)
                                 << utils::helpers::WriteJson(jpatched);
}

TEST(Json, ApplyPatch) {
  const auto jsourse = utils::helpers::ParseJson(source, LogExtra{});
  const auto jset = utils::helpers::ParseJson(set, LogExtra{});
  const auto junset = utils::helpers::ParseJson(unset, LogExtra{});
  auto jexpected = utils::helpers::ParseJson(expected, LogExtra{});

  Check(jsourse, jset, junset, jexpected);
  jexpected["d"] = 4;
  Check(jsourse, jset, Json::Value{Json::objectValue}, jexpected);
  Check(Json::Value{Json::objectValue}, jset, Json::Value{Json::objectValue},
        jset);
  Check(Json::Value{Json::nullValue}, jset, Json::Value{Json::objectValue},
        jset);
  Check(Json::Value{Json::nullValue}, jset, Json::Value{Json::nullValue}, jset);
  Check(Json::Value{Json::nullValue}, Json::Value{Json::nullValue}, unset,
        Json::Value{Json::nullValue});
  Check(Json::Value{Json::nullValue}, Json::Value{Json::objectValue}, unset,
        Json::Value{Json::nullValue});
  Check(jsourse, Json::Value{Json::objectValue}, jsourse,
        Json::Value{Json::objectValue});
}
