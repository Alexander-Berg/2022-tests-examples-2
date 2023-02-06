#include <cstring>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/hostinfo/blocking/get_hostname.hpp>
#include <userver/utils/mock_now.hpp>

#include "elastic/batch_process.hpp"
#include "log_name_to_level.hpp"
#include "utils/read_conductor_group.hpp"

namespace {

using pilorama::elastic::BasicStreamPolicyFactory;
using pilorama::elastic::BatchProcess;
using pilorama::elastic::LimitingStreamPolicyFactory;

struct data_t {
  const char* const name;
  const char* const tskv;
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
  const char* const tskv;
  const std::string json;
  const std::string json_error;
};

inline std::string PrintToString(const data_with_error_t& d) { return d.name; }

struct data_partial_t {
  const char* const tskv;
  const std::string json;
  const size_t to_process;

  data_partial_t(const char* tskv_in, std::string json_in, int diff)
      : tskv(tskv_in),
        json(std::move(json_in)),
        to_process(std::strlen(tskv_in) + diff) {}
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
  f.LoadTimeZones();
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";

  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_EQ(batch.stats.input_bytes_skipped, 0);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.tskv));
  EXPECT_EQ(batch.error, d.json_error);
}

std::string GetJaegerSpans() {
  std::string service_name = pilorama::ReadConductorGroup();
  if (!service_name.empty()) {
    service_name = R"=(,"serviceName":")=" + service_name + '"';
  }
  auto host = hostinfo::blocking::GetRealHostName();
  std::string jaeger_span =
      R"=({"index":{"_index":"jaeger-span-2020-02-25",)="
      R"=("_id":null,"_routing":null,"_type":"log"}}
{"traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"f388096a7c974eb2","operationName":"pg_query",)="
      R"=("duration":11,"startTime":1581064128321122,)="
      R"=("startTimeMillis":1581064128321,)="
      R"=("references":[{"refType":"CHILD_OF",)="
      R"=("traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"2a69bcf3c91e4807"}],"process":{)="
      R"=("tags":[],"tag":{"hostname":")=" +
      host + R"=("})=" + service_name +
      R"=(},"flags":1}
{"index":{"_index":"jaeger-span-2020-02-25",)="
      R"=("_id":null,"_routing":null,)="
      R"=("_type":"log"}}
{"traceID":"104ccb34595c42e2bae7869fda4df088",)="
      R"=("spanID":"5406d45733d243bc","operationName":"some_task",)="
      R"=("duration":15,"startTime":1581064128321140,)="
      R"=("startTimeMillis":1581064128321,"references":[{)="
      R"=("refType":"CHILD_OF","traceID":"104ccb34595c42e2bae7869fda4df088",)="
      R"=("spanID":"e9d805fa30174462"}],)="
      R"=("process":{"tags":[],)="
      R"=("tag":{"hostname":")=" +
      host + R"=("})=" + service_name +
      R"=(},"flags":1}
)=";
  return jaeger_span;
}

std::string GetJaegerServices() {
  std::string service_name = pilorama::ReadConductorGroup();
  if (!service_name.empty()) {
    service_name = R"=(,"serviceName":")=" + service_name + '"';
  }
  std::string jaeger_service =
      R"=({"index":{"_index":"jaeger=service-2020-02-25",)="
      R"=("_id":null,"_routing":null,"_type":"log"}}
{"operationName":"pg_query")=" +
      service_name +
      R"=(}
{"index":{"_index":"jaeger=service-2020-02-25","_id":null,)="
      R"=("_routing":null,"_type":"log"}}
{"operationName":"some_task")=" +
      service_name +
      R"=(}
)=";
  return jaeger_service;
}

}  // namespace

////////////////////////////////////////////////////////////////////////////////

class BatchProcessSingleLine : public ::testing::TestWithParam<data_t> {};

// This test is close to the TskvJsonConverterSingleLine, but note the '\n' and
// record_proplogues.
INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessSingleLine,
    ::testing::ValuesIn(TestData{
        {"1_field", "tskv\thello=word\n",
         record_proplogue_empty_index + R"({"hello":"word"})"
                                        "\n"},

        {"2_fields", "tskv\thello=word\tfoo=bar\n",
         record_proplogue_empty_index + R"({"hello":"word","foo":"bar"})"
                                        "\n"},

        {"2_field_and_eq_sign", "tskv\thello\\=there=word\tfoo\\=there=bar\n",
         record_proplogue_empty_index +
             R"({"hello=there":"word","foo=there":"bar"})"
             "\n"},

        {"2_fields_and_many_eq_signs",
         "tskv\t\\=hello=word\t\\=foo\\=\\=there\\==bar\n",
         record_proplogue_empty_index +
             R"({"=hello":"word","=foo==there=":"bar"})"
             "\n"},

        {"2_fields_and_many_tabs",
         "tskv\thello=\\t\\tw\\t\\to\\tr\\td\\t\\t\tfoo\\=there=\\tbar\n",
         record_proplogue_empty_index +
             R"({"hello":"\\t\\tw\\t\\to\\tr\\td\\t\\t","foo=there":"\\tbar"})"
             "\n"},

        {"2_fields_and_many_newlines",
         "tskv\thello=\\n\\nw\\n\\no\\nr\\nd\\n\\n\tfoo\\=there=\\nbar\n",
         record_proplogue_empty_index +
             R"({"hello":"\\n\\nw\\n\\no\\nr\\nd\\n\\n","foo=there":"\\nbar"})"
             "\n"},

        {"3_fields_with_empty_key_values", "tskv\t=word\tfoo=\t=\n",
         record_proplogue_empty_index + R"({"":"word","foo":"","":""})"
                                        "\n"},

        {"3_fields_with_empty_key_values_and_eq_signs",
         "tskv\t\\===\tfoo==\t==\n",
         record_proplogue_empty_index + R"({"=":"=","foo":"=","":"="})"
                                        "\n"},

        {"key_no_equals", "tskv\tkey\n",
         record_proplogue_empty_index + R"({"key":""})"
                                        "\n"},

        {"empty_record", "tskv\t\n", ""},

        {"just_empty", "", ""},
    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessSingleLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_records_processed,
            (batch.stats.input_bytes_processed ? 1 : 0));
  EXPECT_TRUE(batch.error.empty());
}

TEST_P(BatchProcessSingleLine, ParsingLimiting) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  auto d = GetParam();
  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{1024});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  const auto batch = BatchProcess(f, output_config, d.tskv,
                                  LimitingStreamPolicyFactory(limiter));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(
      batch.stats.input_records_processed + batch.stats.input_newlines_skipped,
      Newlines(d.tskv));
  EXPECT_TRUE(batch.error.empty());
}

TEST_P(BatchProcessSingleLine, ParsingLimitedTo1Byte) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  auto d = GetParam();
  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{1});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  const auto batch = BatchProcess(f, output_config, d.tskv,
                                  LimitingStreamPolicyFactory(limiter));
  EXPECT_EQ(batch.full, "");
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(
      batch.stats.input_records_processed + batch.stats.input_newlines_skipped,
      Newlines(d.tskv));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessMultiLine : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessMultiLine,
    ::testing::ValuesIn(TestData{
        {"1_field_2_lines",
         "tskv\thello=word\n"
         "tskv\thello=word\n",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n"},

        {"3_empty_records",
         "tskv\t\n"
         "tskv\t\n"
         "tskv\t\n",

         ""},

        {"1_field_2_lines_plus_empty_line",
         "tskv\thello=word\n"
         "\n"
         "tskv\thello=word\n",

         record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"hello":"word"})"
             "\n"},

        {"5_fields_5_lines",
         "tskv\t1=11111\t22222=2\t33333=3\t14=4\t55555=55555\n"
         "tskv\t11=1111\t2222=22\t3333=33\t14=4\t55555=55555\n"
         "tskv\t111=111\t222=222\t333=333\t14=4\t55555=55555\n"
         "tskv\t1111=11\t22=2222\t33=3333\t14=4\t55555=55555\n"
         "tskv\t11111=1\t2=22222\t3=33333\t14=4\t55555=55555\n",

         record_proplogue_empty_index +
             R"({"1":"11111","22222":"2","33333":"3","14":"4","55555":"55555"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"11":"1111","2222":"22","3333":"33","14":"4","55555":"55555"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"111":"111","222":"222","333":"333","14":"4","55555":"55555"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"1111":"11","22":"2222","33":"3333","14":"4","55555":"55555"})"
             "\n" +
             record_proplogue_empty_index +
             R"({"11111":"1","2":"22222","3":"33333","14":"4","55555":"55555"})"
             "\n"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessMultiLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(
      batch.stats.input_records_processed + batch.stats.input_newlines_skipped,
      Newlines(d.tskv));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessIncompleteMultiLine
    : public ::testing::TestWithParam<data_partial_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessIncompleteMultiLine,
    ::testing::ValuesIn(TestPartialData{
        /* 1 field, 2 lines and 5 empty line */
        {"\n"
         "\n"
         "tskv\thello=word\n"
         "\n"
         "\ntskv\thello=word\n"
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
         "tskv\thello=word\n"
         "broken \t\t\n"
         "tskv\thello=word\n"
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

TEST_P(BatchProcessIncompleteMultiLine, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, d.to_process);
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessSingleLineMessage : public ::testing::TestWithParam<data_t> {
};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessSingleLineMessage,
    ::testing::ValuesIn(TestData{
        {"1_field", "tskv\thello=word\n",
         record_proplogue_empty_index +
             R"({"hello":"word","message":"tskv\thello=word"})"
             "\n"},

        {"prod_data",
         "tskv\ttimestamp=2018-07-25 17:04:11,890542\tmodule=operator() ( "
         "common/src/threads/thread_pool_monitor.cpp:96 "
         ")\tlevel=INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_"
         "http_"
         "pool\texecution_delay_time=0.016813\t_type=log\ttext=\t\n",

         record_proplogue_empty_index +
             R"ololo({"@timestamp":"2018-07-25T14:04:11.890542Z","module":)ololo"
             R"ololo("operator() ( common/src/threads/thread_pool_monitor.cpp)ololo"
             R"ololo(:96 )","level":"INFO","thread":"7f247cd45700","link":"No)ololo"
             R"ololo(ne","pool_name":"clients_http_pool","execution_delay_tim)ololo"
             R"ololo(e":"0.016813","_type":"log","text":"","message":"tskv\tt)ololo"
             R"ololo(imestamp=2018-07-25 17:04:11,890542\tmodule=operator() ()ololo"
             R"ololo( common/src/threads/thread_pool_monitor.cpp:96 )\tlevel=)ololo"
             R"ololo(INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_)ololo"
             R"ololo(http_pool\texecution_delay_time=0.016813\t_type=log\ttex)ololo"
             R"ololo(t=\t"})ololo"
             "\n"}}),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessSingleLineMessage, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = true;
  f.transform_date = true;
  f.drop_empty_fields = false;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_EQ(batch.stats.input_bytes_skipped, 0);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.tskv));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessRemovals : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessRemovals,
    ::testing::ValuesIn(TestData{
        {"empty_record", "tskv\t\n", ""},

        {"single_field", "tskv\thello=word\n", ""},

        {"multiline", "tskv\thello=word\ntskv\thello2=word2\t_type=log\n",
         record_proplogue_empty_index + "{\"hello2\":\"word2\"}\n"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessRemovals, Parsing) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = false;
  f.removals = {"hello", "_type"};

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessErrorRecord
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessErrorRecord,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also keep\n",

         record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n"},

        {"multiple_error_records",

         "tskv\tlevel=CRITICAL\tdata=keep me1\tdata2=also keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me2\tdata2=also keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me3\tdata2=also keep\n",

         record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me1","data2":"also keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me2","data2":"also keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me1","data2":"also keep"})"
             "\n" +
             record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me2","data2":"also keep"})"
             "\n" +
             record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
             "\n"},

        {"2_error_records_1_normal",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also keep\n"
         "tskv\tlevel=INFO\tdata=do not keep me\tdata2=also do not keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me2\tdata2=also keep2\n",

         record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me2","data2":"also keep2"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n" +
             record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me2","data2":"also keep2"})"
             "\n"},

        {"2_normal_record_1_error",

         "tskv\tlevel=WARNING\tdata=do not keep me1\tdata2=also do not keep\n"
         "tskv\tlevel=INFO\tdata=do not keep me2\tdata2=also do not keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also keep\n",

         record_proplogue_common_index +
             R"({"level":"WARNING","data":"do not keep me1","data2":"also do not keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"INFO","data":"do not keep me2","data2":"also do not keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep"})"
             "\n"}

    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessErrorRecord, Basic) {
  TestBatchProcessErrorRecordCommon(GetParam());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessFormCommandFromData
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessFormCommandFromData,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also "
         "keep\ttype=my_log_type\n",

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n"},

        {"multiple_error_records",

         "tskv\tlevel=CRITICAL\ttype=my_log_type2\tdata=keep me1\tdata2=also "
         "keep\n"
         "tskv\tlevel=CRITICAL\t_type=my_log_type!\tdata=keep me2\tdata2=also "
         "keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me3\tdata2=also keep\n",

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type2"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type!"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type2"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type!"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"log"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n"},

        {"2_error_records_1_normal",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also keep\ttype=log\n"
         "tskv\tlevel=INFO\tdata=do not keep me\tdata2=also do not keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me2\t_type=log\tdata2=also keep2\n",

         record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
             "\n" +
             record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
             "\n"},

    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessFormCommandFromData, Basic) {
  TestBatchProcessErrorRecordCommon(GetParam());
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessFormCommandForElastic7
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessFormCommandForElastic7,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also "
         "keep\ttype=my_log_type\n",

         R"({"index":{"_index":"COMMON_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n"},

        {"multiple_error_records",

         "tskv\tlevel=CRITICAL\ttype=my_log_type2\tdata=keep me1\tdata2=also "
         "keep\n"
         "tskv\tlevel=CRITICAL\t_type=my_log_type!\tdata=keep me2\tdata2=also "
         "keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me3\tdata2=also keep\n",

         R"({"index":{"_index":"COMMON_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n"},

    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessFormCommandForElastic7, Basic) {
  pilorama::OutputConfig output_config{};
  output_config.elastic_version = pilorama::ElasticVersion::Version7;
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_EQ(batch.stats.input_bytes_skipped, 0);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.tskv));
  EXPECT_EQ(batch.error, d.json_error);
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessSkipRecords
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessSkipRecords,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         "tskv\tlevel=DEBUG\tdata=dont keep me\tdata2=also "
         "don't keep\ttype=my_log_type\n"
         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also "
         "keep\ttype=my_log_type\n"
         "tskv\tlevel=DEBUG\tdata=dont keep me2\tdata2=also "
         "don't keep2\ttype=my_log_type\n",

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"my_log_type"})"
         "\n"},

        {"multiple_error_records",

         "tskv\tlevel=CRITICAL\ttype=my_log_type2\tdata=keep me1\tdata2=also "
         "keep\n"
         "tskv\tlevel=DEBUG\tdata=dont keep me\tdata2=also "
         "don't keep\ttype=my_log_type\n"
         "tskv\tlevel=CRITICAL\t_type=my_log_type!\tdata=keep me2\tdata2=also "
         "keep\n"
         "tskv\tlevel=TRACE\tdata=dont keep me2\tdata2=also "
         "don't keep2\ttype=my_log_type\n"
         "tskv\tlevel=CRITICAL\tdata=keep me3\tdata2=also keep\n",

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type2"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"my_log_type!"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n",

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type2"}})"
         "\n"
         R"({"level":"CRITICAL","type":"my_log_type2","data":"keep me1","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"my_log_type!"}})"
         "\n"
         R"({"level":"CRITICAL","_type":"my_log_type!","data":"keep me2","data2":"also keep"})"
         "\n"

         R"({"index":{"_index":"ERROR_INDEX","_id":null,"_routing":null,"_type":"log"}})"
         "\n"
         R"({"level":"CRITICAL","data":"keep me3","data2":"also keep"})"
         "\n"},

        {"2_error_records_1_normal",

         "tskv\tlevel=CRITICAL\tdata=keep me\tdata2=also keep\ttype=log\n"
         "tskv\tlevel=DEBUG\tdata=dont keep me\tdata2=also "
         "don't keep\ttype=my_log_type\n"
         "tskv\tlevel=TRACE\tdata=dont keep me2\tdata2=also "
         "don't keep2\ttype=my_log_type\n"
         "tskv\tlevel=INFO\tdata=do not keep me\tdata2=also do not keep\n"
         "tskv\tlevel=CRITICAL\tdata=keep me2\t_type=log\tdata2=also keep2\n",

         record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"INFO","data":"do not keep me","data2":"also do not keep"})"
             "\n" +
             record_proplogue_common_index +
             R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
             "\n",

         record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me","data2":"also keep","type":"log"})"
             "\n" +
             record_proplogue_error_index +
             R"({"level":"CRITICAL","data":"keep me2","_type":"log","data2":"also keep2"})"
             "\n"},

    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessSkipRecords, Basic) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  f.minimal_log_level = pilorama::LogLevel::kInfo;
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";

  auto d = GetParam();
  const auto batch =
      BatchProcess(f, output_config, d.tskv,
                   BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_NE(batch.stats.input_bytes_skipped, 0);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.tskv));
  EXPECT_EQ(batch.error, d.json_error);
}

////////////////////////////////////////////////////////////////////////////////

class BatchProcessFormCommandWithTimestamp
    : public ::testing::TestWithParam<data_with_error_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, BatchProcessFormCommandWithTimestamp,
    ::testing::ValuesIn(TestErrorData{
        {"single_record",

         "tskv\tlevel=CRITICAL\ttimestamp=2018-07-25 "
         "17:04:11,490542\tdata2=also "
         "keep\ttype=my_log_type\n",

         R"({"index":{"_index":"pilorama-yandex-taxi-2018.07.25.14","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","@timestamp":"2018-07-25T14:04:11.490542Z","data2":"also keep","type":"my_log_type"})"
         "\n",

         R"({"index":{"_index":"pilorama-errors-yandex-taxi-2018.07.25","_id":null,"_routing":null,"_type":"my_log_type"}})"
         "\n"
         R"({"level":"CRITICAL","@timestamp":"2018-07-25T14:04:11.490542Z","data2":"also keep","type":"my_log_type"})"
         "\n"},

    }),
    ::testing::PrintToStringParamName());

TEST_P(BatchProcessFormCommandWithTimestamp, Basic) {
  pilorama::OutputConfig c{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.transform_date = true;
  f.drop_empty_fields = true;
  f.timezone = "Europe/Moscow";
  f.LoadTimeZones();
  c.index = "pilorama-yandex-taxi-%Y.%m.%d.%H";
  c.error_index = "pilorama-errors-yandex-taxi-%Y.%m.%d";

  auto d = GetParam();
  const auto batch = BatchProcess(
      f, c, d.tskv, BasicStreamPolicyFactory(f, std::strlen(d.tskv)));
  EXPECT_EQ(batch.full, d.json);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(d.tskv));
  EXPECT_EQ(batch.stats.input_newlines_skipped, 0);
  EXPECT_EQ(batch.stats.input_bytes_skipped, 0);
  EXPECT_EQ(batch.stats.input_records_processed, Newlines(d.tskv));
  EXPECT_EQ(batch.error, d.json_error);
}

////////////////////////////////////////////////////////////////////////////////

TEST(BatchProcessValidate, Skips) {
  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = false;

  constexpr char data[] =
      "1\ntskv\tk=v\n"
      "23\ntskv\tk=v\n";

  constexpr char result[] =
      R"({"index":{"_index":"","_id":null,"_routing":null,"_type":"log"}})"
      "\n{\"k\":\"v\"}\n"
      R"({"index":{"_index":"","_id":null,"_routing":null,"_type":"log"}})"
      "\n{\"k\":\"v\"}\n";

  const auto batch = BatchProcess(
      f, output_config, data, BasicStreamPolicyFactory(f, std::strlen(data)));
  EXPECT_EQ(batch.full, result);
  EXPECT_EQ(batch.stats.input_bytes_processed, std::strlen(data));
  EXPECT_EQ(batch.stats.input_records_processed, 2);
  EXPECT_EQ(batch.stats.input_bytes_skipped, 5);
  EXPECT_EQ(batch.stats.input_newlines_skipped, 2);
  EXPECT_TRUE(batch.error.empty());
}

////////////////////////////////////////////////////////////////////////////////

TEST(BatchProcessJaeger, Multiline) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  output_config.index = "jaeger-span-2020-02-25";
  output_config.jaeger_service_index = "jaeger=service-2020-02-25";

  pilorama::FilterConfig f;
  f.put_message = false;
  f.additions.append("\"flags\":1");
  f.removals = {"timestamp", "timezone",        "module",         "level",
                "delay",     "stopwatch_units", "start_timestamp"};
  f.renames = {{"trace_id", "traceID"},
               {"span_id", "spanID"},
               {"start_time", "startTime"},
               {"start_time_millis", "startTimeMillis"},
               {"operation_name", "operationName"}};
  f.drop_empty_fields = true;
  f.transform_date = false;
  f.input_format = pilorama::InputFormats::kTskvJaegerSpan;
  constexpr char data[] =
      "tskv"
      "\ttrace_id=ed6a3545c9ac4651a6b3f9b3281b5e88"
      "\tspan_id=f388096a7c974eb2"
      "\tparent_id=2a69bcf3c91e4807"
      "\toperation_name=pg_query"
      "\tduration=11"
      "\tstart_time=1581064128321122"
      "\tstart_time_millis=1581064128321\n"
      "tskv"
      "\ttrace_id=104ccb34595c42e2bae7869fda4df088"
      "\tspan_id=5406d45733d243bc"
      "\tparent_id=e9d805fa30174462"
      "\toperation_name=some_task"
      "\tduration=15"
      "\tstart_time=1581064128321140"
      "\tstart_time_millis=1581064128321\n";

  auto jaeger_span = GetJaegerSpans();
  auto jaeger_service = GetJaegerServices();

  {
    const auto batch = BatchProcess(
        f, output_config, data, BasicStreamPolicyFactory(f, std::strlen(data)));
    EXPECT_TRUE(batch.error.empty());
    EXPECT_FALSE(batch.full.empty());
    EXPECT_FALSE(batch.jaeger_index.empty());

    EXPECT_EQ(batch.full, jaeger_span);
    EXPECT_EQ(batch.jaeger_index, jaeger_service);
  }

  {
    pilorama::StreamLimiter limiter;
    limiter.SetMaxOutputSize(utils::BytesPerSecond{1024});
    limiter.DrainOutputLimit();
    utils::datetime::MockSleep(std::chrono::seconds{1});
    const auto batch = BatchProcess(f, output_config, data,
                                    LimitingStreamPolicyFactory(limiter));
    EXPECT_TRUE(batch.error.empty());
    EXPECT_FALSE(batch.full.empty());
    EXPECT_FALSE(batch.jaeger_index.empty());

    EXPECT_EQ(batch.jaeger_index, jaeger_service);
  }

  {
    pilorama::StreamLimiter limiter;
    limiter.SetMaxOutputSize(utils::BytesPerSecond{1});
    limiter.DrainOutputLimit();
    utils::datetime::MockSleep(std::chrono::seconds{1});
    const auto batch = BatchProcess(f, output_config, data,
                                    LimitingStreamPolicyFactory(limiter));
    EXPECT_TRUE(batch.error.empty());
    EXPECT_TRUE(batch.full.empty());
    EXPECT_FALSE(batch.jaeger_index.empty());

    EXPECT_EQ(batch.jaeger_index, jaeger_service);
  }
}
