#include "json_to_json_converter.hpp"

#include "log_name_to_level.hpp"

#include <gtest/gtest.h>
#include <cstring>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace {

struct data_t {
  const char* const name;
  const char* const json_from;
  const std::string json_converted;
};

inline std::string PrintToString(const data_t& d) { return d.name; }

struct data_partial_t {
  const char* const json_in;
  const size_t to_process;

  data_partial_t(const char* json_in, int diff)
      : json_in(json_in), to_process(std::strlen(json_in) + diff) {}
};
using TestPartialData = std::initializer_list<data_partial_t>;

struct data_skips_t {
  const char* const json;
  const size_t skipped_bytes;
  const size_t skipped_newlines;
};

using TestSkipsData = std::initializer_list<data_skips_t>;

using TestData = std::initializer_list<data_t>;
}  // namespace

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterSingleLine : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterSingleLine,
    ::testing::ValuesIn(TestData{
        {"1_field", "{\"hello\":\"word\"}\n",
         ToString(formats::json::FromString(R"({"hello":"word"})"))},

        {"1_field_key_escaped", "{\"he\\\"llo\":\"word\"}\n",
         ToString(formats::json::FromString(R"({"he\"llo":"word"})"))},

        {"1_field_value_escaped", "{\"hello\":\"wo\\\"rd\"}\n",
         ToString(formats::json::FromString(R"({"hello":"wo\"rd"})"))},

        {"2_fields", "{\"hello\":\"word\",\"foo\":\"bar\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","foo":"bar"})"))},

        {"2_fields_integral", "{\"hello\":1,\"foo\":2}\n",
         ToString(formats::json::FromString(R"({"hello":1,"foo":2})"))},

        {"2_fields_array", "{\"hello\":[1, 2, 3, 4],\"foo\":[2, 3]}\n",
         ToString(formats::json::FromString(
             R"({"hello":[1, 2, 3, 4],"foo":[2, 3]})"))},

        {"nested_objects",
         R"({"hello":"word","foo":{"bar":"buz"}})"
         "\n",
         ToString(formats::json::FromString(
             R"({"hello":"word","foo":{"bar":"buz"}})"))},

        {"2_fields_with_empty_values", "{\"hello\":\"\",\"foo\":\"\"}\n",
         ToString(formats::json::FromString(R"({"hello":"","foo":""})"))},

        {"empty_record", "{}\n", ""},

        {"just_empty", "", ""},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterSingleLine, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////
class JsonJsonConverterIncompleteSingleLine
    : public ::testing::TestWithParam<data_partial_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterIncompleteSingleLine,
    ::testing::ValuesIn(TestPartialData{
        {"tskv\th=w", -8},
        {"t", -1},
        {"t\n", -2},
        {"tskv\n", -5},
        {"\n", -1},
        {"\ntskv", -5},
        {"\ntskv\t", -6},
        {"\ntskv\tk", -7},
        {"\ntskv\tk=", -8},
        {"\ntskv\tk=v", -9},
        {"\ntskv\tke=v", -10},
        {"\ntskv\tkey=v", -11},
    }));

TEST_P(JsonJsonConverterIncompleteSingleLine, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  {
    f.put_message = false;
    std::string result;

    pilorama::JsonToJsonConverter converter{f, d.json_in};
    const size_t bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result, "");
    EXPECT_EQ(bytes_processed, d.to_process);
  }
  {
    f.put_message = true;
    std::string result;

    pilorama::JsonToJsonConverter converter{f, d.json_in};
    const size_t bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result, "");
    EXPECT_EQ(bytes_processed, d.to_process);
  }
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterBrokenStartLine
    : public ::testing::TestWithParam<data_skips_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterBrokenStartLine,
    ::testing::ValuesIn(TestSkipsData{
        {"\n{\"k\":\"v\"}\n", 1, 1},
        {"q\n{\"k\":\"v\"}\n", 2, 1},
        {"q\n\n{\"k\":\"v\"}\n", 3, 2},
        {"q123\n{\"k\":\"v\"}\n", 5, 1},
        {"1\n2\n3\n{\"k\":\"v\"}\n", 6, 3},
    }));

TEST_P(JsonJsonConverterBrokenStartLine, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  f.put_message = false;
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, R"({"k":"v"})");
  EXPECT_EQ(bytes_processed, std::strlen(d.json));
  EXPECT_EQ(converter.BytesSkipped(), d.skipped_bytes);
  EXPECT_EQ(converter.NewlinesSkipped(), d.skipped_newlines);
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterTimestamp : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterTimestamp,
    ::testing::ValuesIn(TestData{
        {"time_simple", "{\"timestamp\":\"2018-07-25 17:04:11,490542\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.490542Z"})"},

        {"time_standard", "{\"timestamp\":\"2018-07-25T17:04:11.490542\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.490542Z"})"},

        {"time_no_ms", "{\"timestamp\":\"2018-07-25 17:04:11,\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_standard_no_ms", "{\"timestamp\":\"2018-07-25T17:04:11.\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_no_ms_and_coma", "{\"timestamp\":\"2018-07-25 17:04:11\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_standard_no_ms_and_coma",
         "{\"timestamp\":\"2018-07-25T17:04:11\"}\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterTimestamp, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  f.put_message = false;
  f.transform_date = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  static const auto utc_tz = cctz::utc_time_zone();

  std::chrono::system_clock::time_point tp{};
  const auto success =
      cctz::parse("%FT%T.000Z", "2018-07-25T14:04:11.000Z", utc_tz, &tp);
  ASSERT_TRUE(success);
  ASSERT_EQ(cctz::format("%FT%T.000Z", tp, utc_tz), "2018-07-25T14:04:11.000Z");

  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(
      std::chrono::duration_cast<std::chrono::seconds>(
          converter.RecordTime().time_since_epoch()),
      std::chrono::duration_cast<std::chrono::seconds>(tp.time_since_epoch()));
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterSingleLineMessage
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterSingleLineMessage,
    ::testing::ValuesIn(TestData{
        {"1_field", "{\"hello\":\"word\"}\n",
         R"({"hello":"word","message":"{\"hello\":\"word\"}"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterSingleLineMessage, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.transform_date = true;
  f.drop_empty_fields = false;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterSingleLineEmpties
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterSingleLineEmpties,
    ::testing::ValuesIn(TestData{
        {"1_empty_field", "{\"hello\":\"\"}\n", ""},
        {"2_empty_fields", "{\"hello\":\"\",\"world\":\"\",\"there\":\"is\"}\n",
         "{\"there\":\"is\"}"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterSingleLineEmpties, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterAdditions : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterAdditions,
    ::testing::ValuesIn(TestData{
        {"empty_record", "{}\n", "{\"addition\":\"bla\"}"},
        {"single_field", "{\"hello\":\"word\"}\n",
         R"({"hello":"word","addition":"bla"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterAdditions, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.additions = R"("addition":"bla")";

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterAdditionsAndMessage
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterAdditionsAndMessage,
    ::testing::ValuesIn(TestData{
        {"empty_record", "{}\n", R"({"addition":"bla","message":"{}"})"},

        {"single_field", "{\"hello\":\"word\"}\n",
         R"({"hello":"word","addition":"bla","message":"{\"hello\":\"word\"}"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterAdditionsAndMessage, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.transform_date = false;
  f.additions = R"("addition":"bla")";

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterRenames : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterRenames,
    ::testing::ValuesIn(TestData{
        {"empty_record", "{}\n", ""},

        {"single_field", "{\"hello\":\"word\"}\n", "{\"hell\":\"word\"}"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterRenames, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.renames = {
      {"hello", "hell"},
      {"_type", "plan"},
  };

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterRemovals : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterRemovals,
    ::testing::ValuesIn(TestData{
        {"empty_record", "{}\n", ""},

        {"single_field", "{\"hello\":\"word\"}\n", ""},

        {"multiple_fields", "{\"hello\":\"word\",\"the\":\"test\"}\n",
         R"({"the":"test"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterRemovals, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.removals = {"hello", "_type"};

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}

////////////////////////////////////////////////////////////////////////////////

TEST(JsonJsonConverterMessageRecord, MessageFlag) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.start_message_from_tskv = false;

  const char message[] = "Hello\n{\"key\":\"value\"}\n";

  std::string result;
  {
    pilorama::JsonToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result,
              R"({"key":"value","message":"Hello\n{\"key\":\"value\"}"})");
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }
  f.start_message_from_tskv = true;
  result.clear();

  pilorama::JsonToJsonConverter converter{f, message};
  const size_t bytes_processed2 = converter.WriteSingleRecord(result);
  EXPECT_EQ(result, R"({"key":"value","message":"{\"key\":\"value\"}"})");
  EXPECT_EQ(bytes_processed2, sizeof(message) - 1);
}

////////////////////////////////////////////////////////////////////////////////

TEST(JsonJsonConverterRecordInfo, Type) {
  pilorama::FilterConfig f;
  f.put_message = true;

  std::string result;
  const char message[] =
      "Hello\n{\"key\":\"value\",\"_type\":\"testing_log\"}\n";
  pilorama::JsonToJsonConverter converter{f, message};
  const auto bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(converter.RecordType(), "testing_log");
  EXPECT_EQ(
      result,
      ToString(formats::json::FromString(
          R"({"key":"value","_type":"testing_log","message":"{\"key\":\"value\",\"_type\":\"testing_log\"}"})")));
  EXPECT_EQ(bytes_processed, sizeof(message) - 1);
}

TEST(JsonJsonConverterRecordInfo, ErrorRecord) {
  pilorama::FilterConfig f;

  std::string result;
  const char message[] =
      "Hello\n{\"level\":\"ERROR\",\"_type\":\"testing_error_log\"}\n";
  pilorama::JsonToJsonConverter converter{f, message};
  const auto bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_TRUE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(converter.RecordType(), "testing_error_log");
  EXPECT_EQ(formats::json::FromString(result),
            formats::json::FromString(
                R"({"_type":"testing_error_log","level":"ERROR"})"));
  EXPECT_EQ(bytes_processed, sizeof(message) - 1);
}

TEST(JsonJsonConverterRecordInfo, RecordFiltering) {
  pilorama::FilterConfig f;
  f.minimal_log_level = pilorama::LogLevel::kError;
  const char message[] =
      "Hello\n{\"level\":\"WARNING\",\"_type\":\"testing_error_log\"}\n";

  {
    std::string result;
    pilorama::JsonToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_TRUE(converter.ShouldIgnoreRecord());
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }

  f.minimal_log_level = pilorama::LogLevel::kWarning;
  {
    std::string result;
    pilorama::JsonToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.ShouldIgnoreRecord());
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }
}

TEST(JsonJsonConverterRecordInfo, ConverterReuse) {
  pilorama::FilterConfig f;

  const char message[] =
      "{\"level\":\"ERROR\",\"_type\":\"testing_error_log\"}\n"
      "{\"level\":\"INFO\",\"_type\":\"testing_non_error_log\"}\n"
      "{\"level\":\"INFO\",\"_type\":\"testing_another_non_error_log\"}\n"
      "{\"level\":\"ERROR\"}\n";

  pilorama::JsonToJsonConverter converter{f, message};

  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_TRUE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_error_log");
    EXPECT_EQ(ToString(formats::json::FromString(result)),
              ToString(formats::json::FromString(
                  R"({"level":"ERROR","_type":"testing_error_log"})")));
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_non_error_log");
    EXPECT_EQ(ToString(formats::json::FromString(result)),
              ToString(formats::json::FromString(
                  R"({"level":"INFO","_type":"testing_non_error_log"})")));
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_another_non_error_log");
    EXPECT_EQ(
        ToString(formats::json::FromString(result)),
        ToString(formats::json::FromString(
            R"({"level":"INFO","_type":"testing_another_non_error_log"})")));
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_TRUE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "");
    EXPECT_EQ(result, R"({"level":"ERROR"})");
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_EQ(bytes_processed, 0);
    EXPECT_EQ(converter.RecordType(), "");
  }
}

////////////////////////////////////////////////////////////////////////////////

class JsonJsonConverterDefaults : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonJsonConverterDefaults,
    ::testing::ValuesIn(TestData{
        {"should_add", "{\"hello\":\"word\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","type":"log"})"))},

        {"should_not_add", "{\"hello\":\"word\",\"type\":\"doc\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","type":"doc"})"))},

        {"renamed_should_not_add", "{\"hello\":\"word\",\"_type\":\"doc2\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","type":"doc2"})"))},

        {"empty_should_add", "{\"hello\":\"word\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","type":"log"})"))},

        {"empty_renamed_should_add", "{\"hello\":\"word\",\"_type\":\"\"}\n",
         ToString(
             formats::json::FromString(R"({"hello":"word","type":"log"})"))},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonJsonConverterDefaults, Base) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.renames = {
      {"_type", "type"},
  };
  f.drop_empty_fields = true;
  f.defaults = {
      {"type", "log"},
  };

  auto d = GetParam();
  std::string result;

  pilorama::JsonToJsonConverter converter{f, d.json_from};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(ToString(formats::json::FromString(result)), d.json_converted);
  EXPECT_EQ(bytes_processed, std::strlen(d.json_from));
}
