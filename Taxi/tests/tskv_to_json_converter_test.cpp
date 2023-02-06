#include "tskv_to_json_converter.hpp"

#include "log_name_to_level.hpp"

#include <gtest/gtest.h>
#include <cstring>

namespace {

struct data_t {
  const char* const name;
  const char* const tskv;
  const char* const json;
};
inline std::string PrintToString(const data_t& d) { return d.name; }

struct data_escaping_t {
  const char* const name;
  const char* const tskv;
  const char* const json;
  const char* const json_escaping_bypassed;
};
inline std::string PrintToString(const data_escaping_t& d) { return d.name; }

struct data_partial_t {
  const char* const tskv;
  const char* const json;
  const size_t to_process;

  data_partial_t(const char* tskv_in, const char* json_in, int diff)
      : tskv(tskv_in), json(json_in), to_process(std::strlen(tskv_in) + diff) {}
};

struct data_skips_t {
  const char* const tskv;
  const size_t skipped_bytes;
  const size_t skipped_newlines;
};

using TestData = std::initializer_list<data_t>;
using TestDataEscaping = std::initializer_list<data_escaping_t>;
using TestPartialData = std::initializer_list<data_partial_t>;
using TestSkipsData = std::initializer_list<data_skips_t>;
}  // namespace

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterSingleLine : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterSingleLine,
    ::testing::ValuesIn(TestData{
        {"1_field", "tskv\thello=word\n", R"({"hello":"word"})"},

        {"2_fields", "tskv\thello=word\tfoo=bar\n",
         R"({"hello":"word","foo":"bar"})"},

        {"2_field_and_eq_sign", "tskv\thello\\=there=word\tfoo\\=there=bar\n",
         R"({"hello=there":"word","foo=there":"bar"})"},

        {"2_fields_and_many_eq_signs",
         "tskv\t\\=hello=word\t\\=foo\\=\\=there\\==bar\n",
         R"({"=hello":"word","=foo==there=":"bar"})"},

        {"2_fields_and_many_tabs",
         "tskv\thello=\\t\\tw\\t\\to\\tr\\td\\t\\t\tfoo\\=there=\\tbar\n",
         R"({"hello":"\\t\\tw\\t\\to\\tr\\td\\t\\t","foo=there":"\\tbar"})"},

        {"2_fields_and_many_newlines",
         "tskv\thello=\\n\\nw\\n\\no\\nr\\nd\\n\\n\tfoo\\=there=\\nbar\n",
         R"({"hello":"\\n\\nw\\n\\no\\nr\\nd\\n\\n","foo=there":"\\nbar"})"},

        {"3_fields_with_empty_key_values", "tskv\t=word\tfoo=\t=\n",
         R"({"":"word","foo":"","":""})"},

        {"3_fields_with_empty_key_values_and_eq_signs",
         "tskv\t\\===\tfoo==\t==\n", R"({"=":"=","foo":"=","":"="})"},

        {"key_no_equals", "tskv\tkey\n", R"({"key":""})"},

        {"empty_record", "tskv\t\n", ""},

        {"just_empty", "", ""},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterSingleLine, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterIncompleteSingleLine
    : public ::testing::TestWithParam<data_partial_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterIncompleteSingleLine,
    ::testing::ValuesIn(TestPartialData{
        {"tskv\th=w", "", -8},
        {"t", "", -1},
        {"t\n", "", -2},
        {"tskv\n", "", -5},
        {"\n", "", -1},
        {"\ntskv", "", -5},
        {"\ntskv\t", "", -6},
        {"\ntskv\tk", "", -7},
        {"\ntskv\tk=", "", -8},
        {"\ntskv\tk=v", "", -9},
        {"\ntskv\tke=v", "", -10},
        {"\ntskv\tkey=v", "", -11},
    }));

TEST_P(TskvJsonConverterIncompleteSingleLine, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  {
    f.put_message = false;
    std::string result;

    pilorama::TskvToJsonConverter converter{f, d.tskv};
    const size_t bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result, d.json);
    EXPECT_EQ(bytes_processed, d.to_process);
  }
  {
    f.put_message = true;
    std::string result;

    pilorama::TskvToJsonConverter converter{f, d.tskv};
    const size_t bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result, d.json);
    EXPECT_EQ(bytes_processed, d.to_process);
  }
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterBrokenStartLine
    : public ::testing::TestWithParam<data_skips_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterBrokenStartLine,
    ::testing::ValuesIn(TestSkipsData{
        {"\ntskv\tk=v\n", 1, 1},
        {"q\ntskv\tk=v\n", 2, 1},
        {"q\n\ntskv\tk=v\n", 3, 2},
        {"q123\ntskv\tk=v\n", 5, 1},
        {"1\n2\n3\ntskv\tk=v\n", 6, 3},
    }));

TEST_P(TskvJsonConverterBrokenStartLine, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  f.put_message = false;
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, R"({"k":"v"})");
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(converter.BytesSkipped(), d.skipped_bytes);
  EXPECT_EQ(converter.NewlinesSkipped(), d.skipped_newlines);
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterEscapeSingleLine
    : public ::testing::TestWithParam<data_escaping_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterEscapeSingleLine,
    ::testing::ValuesIn(TestDataEscaping{
        {"quotes", "tskv\t\"k\"=\"v\"\t\"=\"\n",
         R"({"\"k\"":"\"v\"","\"":"\""})", R"({"\"k\"":"\"v\"","\"":"\""})"},

        {"already_escaped_quotes", "tskv\t\\\"k\\\"=\\\"v\\\"\t\\\"=\\\"\n",
         R"({"\\\"k\\\"":"\\\"v\\\"","\\\"":"\\\""})",
         R"({"\"k\"":"\"v\"","\"":"\""})"},

        {"slashes1", "tskv\t\\k=\\v\\\t\\\\=\\\n",
         R"({"\\k":"\\v\\","\\\\":"\\"})", R"({"\\k":"\\v\\","\\":"\\"})"},

        {"already_escaped_slashes1", "tskv\t\\\\k=\\\\v\\\\\t=\\\\\n",
         R"({"\\\\k":"\\\\v\\\\","":"\\\\"})", R"({"\\k":"\\v\\","":"\\"})"},

        {"already_escaped_slashes2", "tskv\t\\\\k\\\\=\\\\v\\\\\t\\\\=\\\\\n",
         R"({"\\\\k\\\\":"\\\\v\\\\","\\\\":"\\\\"})",
         R"({"\\k\\":"\\v\\","\\":"\\"})"},

        {"carrige_returns", "tskv\t\rk\r=\rv\r\t\r=\r\n",
         R"({"\rk\r":"\rv\r","\r":"\r"})", R"({"\rk\r":"\rv\r","\r":"\r"})"},

        {"control_sym_0x01", "tskv\t\1k\1=\1v\1\t\1=\1\n",
         R"({"\u0001k\u0001":"\u0001v\u0001","\u0001":"\u0001"})",
         R"({"\u0001k\u0001":"\u0001v\u0001","\u0001":"\u0001"})"},

        {"already_escaped_control_sym", "tskv\t\\rk\\r=\\nv\\n\t\\n=\\b\n",
         R"({"\\rk\\r":"\\nv\\n","\\n":"\\b"})",
         R"({"\rk\r":"\nv\n","\n":"\b"})"},

        {"control_sym_0x1f", "tskv\t\x1fk\x1f=\x1fv\x1f\t\x1f=\x1f\n",
         R"({"\u001fk\u001f":"\u001fv\u001f","\u001f":"\u001f"})",
         R"({"\u001fk\u001f":"\u001fv\u001f","\u001f":"\u001f"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterEscapeSingleLine, EsacapeAll) {
  pilorama::FilterConfig f;
  f.transform_date = false;

  auto d = GetParam();
  f.put_message = false;
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

TEST_P(TskvJsonConverterEscapeSingleLine, SimpleEscapeBypassing) {
  pilorama::FilterConfig f;
  f.transform_date = false;
  f.escaping = utils::JsonRecordWriter::Escaping::SimpleEscapeBypass;

  auto d = GetParam();
  f.put_message = false;
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json_escaping_bypassed);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterTimestamp : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterTimestamp,
    ::testing::ValuesIn(TestData{
        {"time_simple", "tskv\ttimestamp=2018-07-25 17:04:11,490542\n",
         R"({"@timestamp":"2018-07-25T14:04:11.490542Z"})"},

        {"time_standard", "tskv\ttimestamp=2018-07-25T17:04:11.490542\n",
         R"({"@timestamp":"2018-07-25T14:04:11.490542Z"})"},

        {"time_no_ms", "tskv\ttimestamp=2018-07-25 17:04:11,\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_standard_no_ms", "tskv\ttimestamp=2018-07-25T17:04:11.\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_no_ms_and_coma", "tskv\ttimestamp=2018-07-25 17:04:11\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_standard_no_ms_and_coma",
         "tskv\ttimestamp=2018-07-25T17:04:11\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},

        {"time_epoch", "tskv\ttimestamp=1532527451\n",
         R"({"@timestamp":"2018-07-25T14:04:11.000000Z"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterTimestamp, Parsing) {
  pilorama::FilterConfig f;

  auto d = GetParam();
  f.put_message = false;
  f.transform_date = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  f.time_formats.push_back("%s");  // unix epoch
  static const auto utc_tz = cctz::utc_time_zone();

  std::chrono::system_clock::time_point tp{};
  const auto success =
      cctz::parse("%FT%T.000Z", "2018-07-25T14:04:11.000Z", utc_tz, &tp);
  ASSERT_TRUE(success);
  ASSERT_EQ(cctz::format("%FT%T.000Z", tp, utc_tz), "2018-07-25T14:04:11.000Z");

  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(
      std::chrono::duration_cast<std::chrono::seconds>(
          converter.RecordTime().time_since_epoch()),
      std::chrono::duration_cast<std::chrono::seconds>(tp.time_since_epoch()));
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterTimestampBroken
    : public ::testing::TestWithParam<const char*> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterTimestampBroken,
    ::testing::ValuesIn(std::initializer_list<const char*>{
        "tskv\ttimestamp=2018!-07-25 17:04:11\n",
        "tskv\ttimestamp=2018-07-25 18:04:61\n",
        "tskv\ttimestamp=Monday\n",
    }));

TEST_P(TskvJsonConverterTimestampBroken, BeyondRepiar) {
  pilorama::FilterConfig f;

  f.put_message = false;
  f.transform_date = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  std::string result;
  const char* bad_date = GetParam();

  pilorama::TskvToJsonConverter converter{f, bad_date};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_TRUE(result.find("T") != std::string::npos);
  EXPECT_TRUE(result.find("Z") != std::string::npos);
  EXPECT_TRUE(result.find("-") != std::string::npos);
  EXPECT_TRUE(result.find(":") != std::string::npos);
  EXPECT_TRUE(result.find("@timestamp") != std::string::npos);
  EXPECT_EQ(bytes_processed, std::strlen(bad_date));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterSingleLineMessage
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterSingleLineMessage,
    ::testing::ValuesIn(TestData{
        {"1_field", "tskv\thello=word\n",
         R"({"hello":"word","message":"tskv\thello=word"})"},

        {"prod_data",
         "tskv\ttimestamp=2018-07-25 17:04:11,890542\tmodule=operator() ( "
         "common/src/threads/thread_pool_monitor.cpp:96 "
         ")\tlevel=INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_"
         "http_"
         "pool\texecution_delay_time=0.016813\t_type=log\ttext=\t\n",

         R"ololo({"@timestamp":"2018-07-25T14:04:11.890542Z","module":)ololo"
         R"ololo("operator() ( common/src/threads/thread_pool_monitor.cpp)ololo"
         R"ololo(:96 )","level":"INFO","thread":"7f247cd45700","link":"No)ololo"
         R"ololo(ne","pool_name":"clients_http_pool","execution_delay_tim)ololo"
         R"ololo(e":"0.016813","_type":"log","text":"","message":"tskv\tt)ololo"
         R"ololo(imestamp=2018-07-25 17:04:11,890542\tmodule=operator() ()ololo"
         R"ololo( common/src/threads/thread_pool_monitor.cpp:96 )\tlevel=)ololo"
         R"ololo(INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_)ololo"
         R"ololo(http_pool\texecution_delay_time=0.016813\t_type=log\ttex)ololo"
         R"ololo(t=\t"})ololo"}}),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterSingleLineMessage, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.transform_date = true;
  f.drop_empty_fields = false;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterSingleLineEmpties
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterSingleLineEmpties,
    ::testing::ValuesIn(TestData{
        {"1_empty_field", "tskv\thello=\n", ""},
        {"2_empty_fields", "tskv\thello=\tthere=is\tword=\n",
         "{\"there\":\"is\"}"},

        {"many_empty_fields", "tskv\tt=\tmodule=\tlevel=\t\n", ""},

        {"prod_data",
         "tskv\ttimestamp=2018-07-25 17:04:11,890542\tmodule=operator() ( "
         "common/src/threads/thread_pool_monitor.cpp:96 "
         ")\tlevel=INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_"
         "http_"
         "pool\texecution_delay_time=0.016813\t_type=log\ttext=\t\n",

         R"ololo({"@timestamp":"2018-07-25T14:04:11.890542Z","module":)ololo"
         R"ololo("operator() ( common/src/threads/thread_pool_monitor.cpp)ololo"
         R"ololo(:96 )","level":"INFO","thread":"7f247cd45700","link":"No)ololo"
         R"ololo(ne","pool_name":"clients_http_pool","execution_delay_tim)ololo"
         R"ololo(e":"0.016813","_type":"log"})ololo"}}),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterSingleLineEmpties, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterAdditions : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterAdditions,
    ::testing::ValuesIn(TestData{
        {"empty_record", "tskv\t\n", "{\"addition\":\"bla\"}"},
        {"single_field", "tskv\thello=word\n",
         R"({"hello":"word","addition":"bla"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterAdditions, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.additions = R"("addition":"bla")";

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterAdditionsAndMessage
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterAdditionsAndMessage,
    ::testing::ValuesIn(TestData{
        {"empty_record", "tskv\t\n",
         R"({"addition":"bla","message":"tskv\t"})"},

        {"single_field", "tskv\thello=word\n",
         R"({"hello":"word","addition":"bla","message":"tskv\thello=word"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterAdditionsAndMessage, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.transform_date = false;
  f.additions = R"("addition":"bla")";

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterRenames : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterRenames,
    ::testing::ValuesIn(TestData{
        {"empty_record", "tskv\t\n", ""},

        {"single_field", "tskv\thello=word\n", "{\"hell\":\"word\"}"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterRenames, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.renames = {
      {"hello", "hell"},
      {"_type", "plan"},
  };

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

class TskvJsonConverterRemovals : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterRemovals,
    ::testing::ValuesIn(TestData{
        {"empty_record", "tskv\t\n", ""},

        {"single_field", "tskv\thello=word\n", ""},

        {"multiple_fields", "tskv\thello=word\tthe=test\n",
         R"({"the":"test"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterRemovals, Parsing) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.removals = {"hello", "_type"};

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

////////////////////////////////////////////////////////////////////////////////

TEST(TskvJsonConverterMessageRecord, MessageFlag) {
  pilorama::FilterConfig f;
  f.put_message = true;
  f.start_message_from_tskv = false;

  const char message[] = "Hello\ntskv\tkey=value\n";

  std::string result;
  {
    pilorama::TskvToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(result, R"({"key":"value","message":"Hello\ntskv\tkey=value"})");
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }
  f.start_message_from_tskv = true;
  result.clear();

  pilorama::TskvToJsonConverter converter{f, message};
  const size_t bytes_processed2 = converter.WriteSingleRecord(result);
  EXPECT_EQ(result, R"({"key":"value","message":"tskv\tkey=value"})");
  EXPECT_EQ(bytes_processed2, sizeof(message) - 1);
}

////////////////////////////////////////////////////////////////////////////////

TEST(TskvJsonConverterRecordInfo, Type) {
  pilorama::FilterConfig f;
  f.put_message = true;

  std::string result;
  const char message[] = "Hello\ntskv\tkey=value\t_type=testing_log\n";
  pilorama::TskvToJsonConverter converter{f, message};
  const auto bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(converter.RecordType(), "testing_log");
  EXPECT_EQ(
      result,
      R"({"key":"value","_type":"testing_log","message":"tskv\tkey=value\t_type=testing_log"})");
  EXPECT_EQ(bytes_processed, sizeof(message) - 1);
}

TEST(TskvJsonConverterRecordInfo, ErrorRecord) {
  pilorama::FilterConfig f;

  std::string result;
  const char message[] = "Hello\ntskv\tlevel=ERROR\t_type=testing_error_log\n";
  pilorama::TskvToJsonConverter converter{f, message};
  const auto bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_TRUE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(converter.RecordType(), "testing_error_log");
  EXPECT_EQ(result, R"({"level":"ERROR","_type":"testing_error_log"})");
  EXPECT_EQ(bytes_processed, sizeof(message) - 1);
}

TEST(TskvJsonConverterRecordInfo, RecordFiltering) {
  pilorama::FilterConfig f;
  f.minimal_log_level = pilorama::LogLevel::kError;
  const char message[] =
      "Hello\ntskv\tlevel=WARNING\t_type=testing_error_log\n";

  {
    std::string result;
    pilorama::TskvToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_TRUE(converter.ShouldIgnoreRecord());
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }

  f.minimal_log_level = pilorama::LogLevel::kWarning;
  {
    std::string result;
    pilorama::TskvToJsonConverter converter{f, message};
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_FALSE(converter.ShouldIgnoreRecord());
    EXPECT_EQ(bytes_processed, sizeof(message) - 1);
  }
}

TEST(TskvJsonConverterRecordInfo, ConverterReuse) {
  pilorama::FilterConfig f;

  const char message[] =
      "tskv\tlevel=ERROR\t_type=testing_error_log\n"
      "tskv\tlevel=INFO\t_type=testing_non_error_log\n"
      "tskv\tlevel=INFO\ttype=testing_another_non_error_log\n"
      "tskv\tlevel=ERROR\t\n";

  pilorama::TskvToJsonConverter converter{f, message};

  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_TRUE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_error_log");
    EXPECT_EQ(result, R"({"level":"ERROR","_type":"testing_error_log"})");
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_non_error_log");
    EXPECT_EQ(result, R"({"level":"INFO","_type":"testing_non_error_log"})");
  }
  {
    std::string result;
    const auto bytes_processed = converter.WriteSingleRecord(result);
    EXPECT_NE(bytes_processed, 0);
    EXPECT_FALSE(converter.IsAtLeastErrorRecord());
    EXPECT_EQ(converter.RecordType(), "testing_another_non_error_log");
    EXPECT_EQ(result,
              R"({"level":"INFO","type":"testing_another_non_error_log"})");
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

class TskvJsonConverterDefaults : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvJsonConverterDefaults,
    ::testing::ValuesIn(TestData{
        {"should_add", "tskv\thello=word\n",
         R"({"hello":"word","type":"log"})"},

        {"should_not_add", "tskv\thello=word\ttype=doc\n",
         R"({"hello":"word","type":"doc"})"},

        {"renamed_should_not_add", "tskv\thello=word\t_type=doc2\n",
         R"({"hello":"word","type":"doc2"})"},

        {"empty_should_add", "tskv\ttype=\thello=word\n",
         R"({"hello":"word","type":"log"})"},

        {"empty_renamed_should_add", "tskv\thello=word\t_type=\n",
         R"({"hello":"word","type":"log"})"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvJsonConverterDefaults, Base) {
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

  pilorama::TskvToJsonConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}
