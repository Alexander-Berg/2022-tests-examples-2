#include "elastic/batch_process.hpp"

#include <cstring>

#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/utils/mock_now.hpp>

#include "log_name_to_level.hpp"

namespace {

using pilorama::elastic::BasicStreamPolicyFactory;
using pilorama::elastic::BatchProcess;
using pilorama::elastic::LimitingStreamPolicyFactory;

std::string CanonicalJson(const std::string& s) {
  return ToString(formats::json::FromString(s));
}

struct data_t {
  const char* const name;
  const char* const from;
  const std::string json;
};

const std::string record_proplogue_empty_index =
    R"({"index":{"_index":"","_id":null,"_routing":null,"_type":"log"}})"
    "\n";

const std::string record_proplogue_common_index =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n";

const std::string record_proplogue_error_index =
    R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n";

inline std::string PrintToString(const data_t& d) { return d.name; }

struct data_with_error_t {
  const char* const name;
  const char* const from;
  const std::string json;
  const std::string json_error;
  const std::size_t input_bytes_skipped = 0;
};

inline std::string PrintToString(const data_with_error_t& d) { return d.name; }

struct data_partial_t {
  const char* const from;
  const std::string json;
  const size_t to_process;

  data_partial_t(const char* from, std::string json_in, int diff)
      : from(from),
        json(std::move(json_in)),
        to_process(std::strlen(from) + diff) {}
};

using TestData = std::initializer_list<data_t>;
using TestErrorData = std::initializer_list<data_with_error_t>;
using TestPartialData = std::initializer_list<data_partial_t>;

auto Newlines(const char* const data) {
  return std::count(data, data + std::strlen(data), '\n');
}

void TestBatchProcessErrorRecordCommon(const data_with_error_t& d) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.input_format = pilorama::InputFormats::kJson;
  f.LoadTimeZones();
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";
  f.input_format = pilorama::InputFormats::kJson;

  const auto batch =
      BatchProcess(f, output_config, d.from,
                   BasicStreamPolicyFactory(f, std::strlen(d.from)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_EQ(batch.stats.input_bytes_skipped, d.input_bytes_skipped);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.from));
  EXPECT_EQ(batch.error, d.json_error);
}

}  // namespace

////////////////////////////////////////////////////////////////////////////////

class JsonBatchProcessSingleLine : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessSingleLine,
    ::testing::ValuesIn(TestData{
        {"1_field", "{\"hello\":\"word\"}\n",
         record_proplogue_empty_index + CanonicalJson(R"({"hello":"word"})") +
             "\n"},

        {"2_fields", "{\"hello\":\"word\",\"foo\":\"bar\"}\n",
         record_proplogue_empty_index +
             CanonicalJson(R"({"hello":"word","foo":"bar"})") + "\n"},

        {"empty_record", "{}\n", ""},

        {"just_empty", "", ""},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonBatchProcessSingleLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.from,
                   BasicStreamPolicyFactory(f, std::strlen(d.from)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_EQ(batch.stats.input_records_processed,
            (batch.stats.input_bytes_processed ? 1 : 0));
  EXPECT_TRUE(batch.error.empty());
}

TEST_P(JsonBatchProcessSingleLine, ParsingLimiting) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{1024});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  const auto batch = BatchProcess(f, output_config, d.from,
                                  LimitingStreamPolicyFactory(limiter));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_EQ(batch.stats.input_records_processed,
            (batch.stats.input_bytes_processed ? 1 : 0));
  EXPECT_TRUE(batch.error.empty());
}

TEST_P(JsonBatchProcessSingleLine, ParsingLimitedTo1Byte) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{1});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  const auto batch = BatchProcess(f, output_config, d.from,
                                  LimitingStreamPolicyFactory(limiter));
  EXPECT_EQ(batch.full, "");
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_EQ(batch.stats.input_records_processed,
            (batch.stats.input_bytes_processed ? 1 : 0));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class JsonBatchProcessMultiLine : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessMultiLine,
    ::testing::ValuesIn(TestData{
        {"1_field_2_lines",
         "{\"hello\":\"word\"}\n"
         "{\"hello\":\"word\"}\n",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n"},

        {"3_empty_records",
         "{}\n"
         "{}\n"
         "{}\n",

         ""},

        {"1_field_2_lines_plus_empty_line",
         "{\"hello\":\"word\"}\n"
         "{}\n"
         "{\"hello\":\"word\"}\n",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n"},

        {"5_fields_5_lines",
         R"({"1":"11111","22222":"2","14":"4","55555":"55555"})"
         "\n"
         R"({"11":"1111","2222":"22","14":"4","55555":"55555"})"
         "\n"
         R"({"111":"111","222":"222","14":"4","55555":"55555"})"
         "\n"
         R"({"1111":"11","22":"2222","14":"4","55555":"55555"})"
         "\n"
         R"({"11111":"1","2":"22222","14":"4","55555":"55555"})"
         "\n",

         record_proplogue_empty_index +
             CanonicalJson(
                 R"({"1":"11111","22222":"2","14":"4","55555":"55555"})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(
                 R"({"11":"1111","2222":"22","14":"4","55555":"55555"})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(
                 R"({"111":"111","222":"222","14":"4","55555":"55555"})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(
                 R"({"1111":"11","22":"2222","14":"4","55555":"55555"})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(
                 R"({"11111":"1","2":"22222","14":"4","55555":"55555"})") +
             "\n"},

        {"5_fields_5_lines_integral",
         R"({"1":11111,"22222":2,"14":4,"55555":55555})"
         "\n"
         R"({"11":1111,"2222":22,"14":4,"55555":55555})"
         "\n"
         R"({"111":111,"222":222,"14":4,"55555":55555})"
         "\n"
         R"({"1111":11,"22":2222,"14":4,"55555":55555})"
         "\n"
         R"({"11111":1,"2":22222,"14":4,"55555":55555})"
         "\n",

         record_proplogue_empty_index +
             CanonicalJson(R"({"1":11111,"22222":2,"14":4,"55555":55555})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(R"({"11":1111,"2222":22,"14":4,"55555":55555})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(R"({"111":111,"222":222,"14":4,"55555":55555})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(R"({"1111":11,"22":2222,"14":4,"55555":55555})") +
             "\n" + record_proplogue_empty_index +
             CanonicalJson(R"({"11111":1,"2":22222,"14":4,"55555":55555})") +
             "\n"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonBatchProcessMultiLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.from,
                   BasicStreamPolicyFactory(f, std::strlen(d.from)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_EQ(
      batch.stats.input_records_processed + batch.stats.input_newlines_skipped,
      Newlines(d.from));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////
class JsonBatchProcessIncompleteMultiLine
    : public ::testing::TestWithParam<data_partial_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessIncompleteMultiLine,
    ::testing::ValuesIn(TestPartialData{
        /* 1 field, 2 lines and 5 empty line */
        {"\n"
         "\n"
         "{\"hello\":\"word\"}\n"
         "\n"
         "\n{\"hello\":\"word\"}\n"
         "\n"
         "\n",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n",
         -2},

        /* 1 field, 2 lines and 5 corrupted lines */
        {"I am broken beyond repair\n"
         "I\tam\tbroken\n"
         "{\"hello\":\"word\"}\n"
         "broken \t\t\n"
         "{\"hello\":\"word\"}\n"
         "\n"
         "\nI am broken ",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n",
         -14},
    }));

TEST_P(JsonBatchProcessIncompleteMultiLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.from,
                   BasicStreamPolicyFactory(f, std::strlen(d.from)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, d.to_process);
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class JsonBatchProcessRemovals : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessRemovals,
    ::testing::ValuesIn(TestData{
        {"empty_record", "{}\n", ""},

        {"single_field", "{\"hello\":\"word\"}\n", ""},

        {"multiline",
         "{\"hello\":\"word\"}\n{\"hello2\":\"word2\",\"_type\":\"log\"}\n",
         record_proplogue_empty_index + "{\"hello2\":\"word2\"}\n"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonBatchProcessRemovals, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.removals = {"hello", "_type"};
  f.input_format = pilorama::InputFormats::kJson;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.from,
                   BasicStreamPolicyFactory(f, std::strlen(d.from)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.from));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class JsonBatchProcessErrorRecord
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessErrorRecord,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
         "\n",

         record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})") +
             "\n",

         record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})") +
             "\n"},

        {"multiple_error_records",

         R"({"level":"CRITICAL","data":"keep me1","data2":"also keep"})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me2","data2":"also keep"})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n",

         record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me1","data2":"also keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","data2":"also keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})") +
             "\n",

         record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me1","data2":"also keep"})") +
             "\n" + record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","data2":"also keep"})") +
             "\n" + record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})") +
             "\n"},

        {"2_error_records_1_normal",

         R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
         "\n"
         R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me2","data2":"also keep2"})"
         "\n",

         record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","data2":"also keep2"})") +
             "\n",

         record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})") +
             "\n" + record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","data2":"also keep2"})") +
             "\n"},

    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonBatchProcessErrorRecord, Basic) {
  TestBatchProcessErrorRecordCommon(GetParam());
}

////////////////////////////////////////////////////////////////////////////////

class JsonBatchProcessFormCommandFromData
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, JsonBatchProcessFormCommandFromData,
    ::testing::ValuesIn(TestErrorData{
        {"2_error_records_1_normal",

         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
         "\n"
         R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
         "\n",

         record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})") +
             "\n",

         record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})") +
             "\n" + record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})") +
             "\n"},

        {"2_error_records_1_normal_2_broken",

         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
         "\n"
         R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
         "\n"
         R"({"level":"CRITICAL","BROKEN":"don not keep )"
         "\n"
         R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
         "\n"
         R"({"level":"CRITICAL","BROKEN2":"don not keep")"
         "\n",

         record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})") +
             "\n" + record_proplogue_common_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})") +
             "\n",

         record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})") +
             "\n" + record_proplogue_error_index +
             CanonicalJson(
                 R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})") +
             "\n",
         89},

    }),
    ::testing::PrintToStringParamName());

TEST_P(JsonBatchProcessFormCommandFromData, Basic) {
  TestBatchProcessErrorRecordCommon(GetParam());
}
