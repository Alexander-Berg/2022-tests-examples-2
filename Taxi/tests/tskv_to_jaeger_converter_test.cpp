#include <fmt/format.h>
#include <gtest/gtest.h>

#include <cstring>

#include <userver/formats/json/serialize.hpp>
#include <userver/hostinfo/blocking/get_hostname.hpp>

#include "log_name_to_level.hpp"
#include "tskv_to_jaeger_span_converter.hpp"
#include "utils/read_conductor_group.hpp"

namespace {

struct data_t {
  const char* const name;
  const char* const tskv;
  const char* const json;
  const char* const jaeger_service;
};
inline std::string PrintToString(const data_t& d) { return d.name; }

struct data_escaping_t {
  const char* const name;
  const char* const tskv;
  const char* const json;
  const char* const json_escaping_bypassed;
};
// inline std::string PrintToString(const data_escaping_t& d) { return d.name; }

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

const std::string tskv_jaeger_span_with_query =
    "tskv"
    "\ttimestamp=2020-04-27T15:08:58.551723"
    "\ttimezone=+03:00\tlevel=INFO"
    "\tmodule=LogOpenTracing ( "
    "userver/core/src/tracing/span_opentracing.cpp:87 )"
    "\ttask_id=7F3806C2D140"
    "\tcoro_id=7F39BF746E18thread_id=0x00007F3826326700"
    "\ttext=\ttrace_id=57e4ad231fa14b858b914db04ac5f24c"
    "\tparent_id=c5438739a6159d79"
    "\tspan_id=6d00674cadea6e1f\tstart_time=1587989338546529"
    "\tstart_time_millis=1587989338546"
    "\tduration=5179\toperation_name=pg_query"
    "\ttags=[{\"value\":\"postgres\",\"type\":\"string\",\"key\":\"db.type\"},"
    "{\"value\":\"myt-5ft9u7puo9l3rddo.db.yandex.net:6432\",\"type\":"
    "\"string\",\"key\":\"peer.address\"},"
    "{\"value\":\"\\nSELECT parks.contracts.\\\\\"ID\\\\\" FROM "
    "parks.contracts\", \"type\":\"string\",\"key\":\"db.statement\"}]\n";

const char* GetJaegerSpanTestData() {
  static const std::string kTestData =
      R"=({"traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"3c4283d0afc94d41b89f71373871cb53",)="
      R"=("operationName":"Distlock db operations",)="
      R"=("duration":11,)="
      R"=("startTime":1581064128321122,)="
      R"=("startTimeMillis":1581064128321,)="
      R"=("tags":[{"key":"key","value":"value","type":"type"}],)="
      R"=("references":[{)="
      R"=("refType":"CHILD_OF",)="
      R"=("traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"7668a0239eb641a69bf83980116e3423")="
      R"=(}],)="
      R"=("process":{"tags":[],"tag":{"hostname":")=" +
      hostinfo::blocking::GetRealHostName() +
      R"=("},"serviceName":"test_service"},"flags":1)="
      R"=(})=";
  return kTestData.data();
}

const char* GetJaegerSpanTestDataWithServiceName() {
  static const std::string kTestData =
      R"=({"traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"3c4283d0afc94d41b89f71373871cb53",)="
      R"=("operationName":"Distlock db operations",)="
      R"=("duration":11,)="
      R"=("startTime":1581064128321122,)="
      R"=("startTimeMillis":1581064128321,)="
      R"=("tags":[{"key":"key","value":"value","type":"type"}],)="
      R"=("references":[{)="
      R"=("refType":"CHILD_OF",)="
      R"=("traceID":"ed6a3545c9ac4651a6b3f9b3281b5e88",)="
      R"=("spanID":"7668a0239eb641a69bf83980116e3423")="
      R"=(}],)="
      R"=("process":{"tags":[],"tag":{"hostname":")=" +
      hostinfo::blocking::GetRealHostName() +
      R"=("},"serviceName":"from_span"},"flags":1)="
      R"=(})=";
  return kTestData.data();
}

const char* GetJaegerServiceTestData(
    const std::string& service_name = "test_service") {
  static const std::string kTestData =
      R"=({"operationName":"Distlock db operations",)="
      R"=("serviceName":")=" +
      service_name + R"=("})=";
  return kTestData.data();
}
}  // namespace

////////////////////////////////////////////////////////////////////////////////

class TskvToJaegerConverterSingleLine
    : public ::testing::TestWithParam<data_t> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, TskvToJaegerConverterSingleLine,
    ::testing::ValuesIn(TestData{
        {"default",
         "tskv"
         "\ttrace_id=ed6a3545c9ac4651a6b3f9b3281b5e88"
         "\tspan_id=3c4283d0afc94d41b89f71373871cb53"
         "\tparent_id=7668a0239eb641a69bf83980116e3423"
         "\toperation_name=Distlock db operations"
         "\tduration=11"
         "\tstart_time=1581064128321122"
         "\tstart_time_millis=1581064128321"
         "\tservice_name=test_service"
         "\ttags=[{\"key\":\"key\",\"value\":\"value\",\"type\":\"type\"}]\n",
         GetJaegerSpanTestData(), GetJaegerServiceTestData()},
        {"service_name_from_span",
         "tskv"
         "\ttrace_id=ed6a3545c9ac4651a6b3f9b3281b5e88"
         "\tspan_id=3c4283d0afc94d41b89f71373871cb53"
         "\tparent_id=7668a0239eb641a69bf83980116e3423"
         "\tservice_name=from_span"
         "\toperation_name=Distlock db operations"
         "\tduration=11\tservice_name=from_span"
         "\tstart_time=1581064128321122"
         "\tstart_time_millis=1581064128321"
         "\ttags=[{\"key\":\"key\",\"value\":\"value\",\"type\":\"type\"}]\n",
         GetJaegerSpanTestDataWithServiceName(),
         GetJaegerServiceTestData("from_span")},
    }),
    ::testing::PrintToStringParamName());

TEST_P(TskvToJaegerConverterSingleLine, Parsing) {
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

  auto d = GetParam();
  std::string result;

  pilorama::TskvToJaegerSpanConverter converter{f, d.tskv};
  const size_t bytes_processed = converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  EXPECT_EQ(result, d.json);
  EXPECT_EQ(bytes_processed, std::strlen(d.tskv));
}

TEST(TskvJaegerSqlQuery, SqlQuery) {
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

  std::string result;

  pilorama::TskvToJaegerSpanConverter converter{f, tskv_jaeger_span_with_query};
  converter.WriteSingleRecord(result);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());
  formats::json::Value es_json;
  try {
    es_json = formats::json::FromString(result);
  } catch (const std::exception& exception) {
    FAIL() << exception.what();
  }
  auto tags = es_json["tags"];
  ASSERT_TRUE(tags.IsArray());
  ASSERT_EQ(tags.GetSize(), 3);
  ASSERT_EQ(tags[2]["key"].As<std::string>(), "db.statement");
}
