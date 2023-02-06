#include <userver/utest/parameter_names.hpp>
#include <userver/utest/utest.hpp>

#include <userver/formats/json/serialize.hpp>

#include <utils/json.hpp>

namespace utils::json {

struct BadFormatParams {
  std::string source;
  std::string test_name;
};

class ParseNdJsonBadFormat
    : public testing::Test,
      public testing::WithParamInterface<BadFormatParams> {};

const std::vector<BadFormatParams> bad_format_params{
    {
        "abacaba",
        "NotJson",
    },
    {
        "[}]",
        "WrongBracketsSequence",
    },
    {
        R"-({}{"a": 1})-",
        "NoNewlineSeparator",
    },
    {
        "{}\t{}",
        "TabInsteadOfNewline",
    },
};

TEST_P(ParseNdJsonBadFormat, ) {
  EXPECT_THROW(ParseNdJson(GetParam().source), ParseException);
}

INSTANTIATE_TEST_SUITE_P(, ParseNdJsonBadFormat,
                         testing::ValuesIn(bad_format_params),
                         ::utest::PrintTestName());

struct GoodFormatParams {
  std::string ndjson_source;
  std::string json_source;
  std::string test_name;
};

class ParseNdJsonGoodFormat
    : public testing::Test,
      public testing::WithParamInterface<GoodFormatParams> {};

const std::vector<GoodFormatParams> good_format_params{
    {
        "",
        "[]",
        "EmptyDoc",
    },
    {
        R"-({"a": 1, "b": "c"})-",
        R"-([{"a": 1, "b": "c"}])-",
        "SingleDoc",
    },
    {
        "{}\n{}\n{}",
        "[{}, {}, {}]",
        "MultipleDocsStrictFormat",
    },
    {
        R"-(
          {"a": 1, "b": "c"}
          {"a": 2, "b": "d"}
          {"a": 3, "b": "e"}
        )-",
        R"-([
          {"a": 1, "b": "c"},
          {"a": 2, "b": "d"},
          {"a": 3, "b": "e"}
        ])-",
        "MultipleDocsFreeFormat",
    },
    {
        R"-(
          {
            "a": 1,
            "b": [
              {
                "c": 1,
                "d": 2
              },
              {
                "c": 3,
                "d": 4
              }
            ]
          }
          {
            "a": 2,
            "b": [
              {
                "c": 5,
                "d": 6
              },
              {
                "c": 7,
                "d": 8
              }
            ]
          }
        )-",
        R"-([
          {
            "a": 1,
            "b": [
              {
                "c": 1,
                "d": 2
              },
              {
                "c": 3,
                "d": 4
              }
            ]
          },
          {
            "a": 2,
            "b": [
              {
                "c": 5,
                "d": 6
              },
              {
                "c": 7,
                "d": 8
              }
            ]
          }
        ])-",
        "MultipleDocsWithNestedDocs",
    },
};

TEST_P(ParseNdJsonGoodFormat, ) {
  const auto ndjson = ParseNdJson(GetParam().ndjson_source);
  const auto json = formats::json::FromString(GetParam().json_source);
  EXPECT_EQ(ndjson, json);
}

INSTANTIATE_TEST_SUITE_P(, ParseNdJsonGoodFormat,
                         testing::ValuesIn(good_format_params),
                         ::utest::PrintTestName());

}  // namespace utils::json
