#include <json-hash/json_crypto_hash.hpp>

#include <gtest/gtest.h>

#include <userver/crypto/hash.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

namespace json_hash {

namespace {

void CompareSha1(std::string json_str, std::string exp_str) {
  const auto json = formats::json::FromString(json_str);
  using CryptoEncode = crypto::hash::OutputEncoding;
  using JsonHashEncode = json_hash::OutputEncoding;
  const auto exp_sha1_hex = crypto::hash::Sha1(exp_str, CryptoEncode::kHex);
  const auto sha1_hex = json_hash::Sha1(json, JsonHashEncode::kHex);
  ASSERT_EQ(exp_sha1_hex, sha1_hex);
  const auto exp_sha1_b64 = crypto::hash::Sha1(exp_str, CryptoEncode::kBase64);
  const auto sha1_b64 = json_hash::Sha1(json, JsonHashEncode::kBase64);
  ASSERT_EQ(exp_sha1_b64, sha1_b64);
  const auto exp_sha1_bin = crypto::hash::Sha1(exp_str, CryptoEncode::kBinary);
  const auto sha1_bin = json_hash::Sha1(json, JsonHashEncode::kBinary);
  ASSERT_EQ(exp_sha1_bin, sha1_bin);
}

TEST(JsonHashSha1, TrivialCases) {
  EXPECT_NO_FATAL_FAILURE(CompareSha1("{}", "{}"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1("[]", "[]"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1("null", "null"));
  EXPECT_NO_FATAL_FAILURE(
      CompareSha1(R"({"field": "string"})", R"({"field":"string"})"));
  EXPECT_NO_FATAL_FAILURE(
      CompareSha1(R"({"field": [3, 2, 1]})", R"({"field":[3,2,1]})"));
  EXPECT_NO_FATAL_FAILURE(
      CompareSha1(R"({"field": 1, "build": 1.2, "dield": true})",
                  R"({"build":1.2,"dield":true,"field":1})"));
}

TEST(JsonHashSha1, NoneTrivialCase) {
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
                            "lul": "txt",
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
      R"({"m":2,"s":1.4,"z":{"lul":"txt","pop":[]}})"
      ","
      R"({"a1":{"bo":true,"bo2":false},"a2":-2.4,"a3":""})"
      "],"
      R"("dd":[1,2,3],"ddd":["x"],"dddd":-12},)"
      R"("c":"str")"
      "}"};
  EXPECT_NO_FATAL_FAILURE(CompareSha1(str_json, expected_str));
}

TEST(JsonHashSha1, IgnoringNullFields) {
  EXPECT_NO_FATAL_FAILURE(CompareSha1("null", "null"));
  EXPECT_NO_FATAL_FAILURE(
      CompareSha1(R"({"field": "string"})", R"({"field":"string"})"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1(R"({"field": null})", R"({})"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1(R"({"a": null, "b": 1})", R"({"b":1})"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1(R"({"b": null, "a": 1})", R"({"a":1})"));
  const auto str_json = std::string(R"(
        {
            "aa": {},
            "cc": null,
            "bbb": {
                "dd": 12,
                "d": [1, null, 3],
                "ddd": null
            }
        }
    )");
  const auto expected_str =
      std::string{R"({"aa":{},"bbb":{"d":[1,null,3],"dd":12}})"};
  EXPECT_NO_FATAL_FAILURE(CompareSha1(str_json, expected_str));
}

TEST(JsonHashSha1, DoubleVsInt) {
  EXPECT_NO_FATAL_FAILURE(CompareSha1(R"({"field": 1.0})", R"({"field":1})"));
  EXPECT_NO_FATAL_FAILURE(CompareSha1(R"({"field": -2.0})", R"({"field":-2})"));
}

}  // namespace

}  // namespace json_hash
