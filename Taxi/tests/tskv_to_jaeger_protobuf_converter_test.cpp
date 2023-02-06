#include <google/protobuf/util/message_differencer.h>
#include <gtest/gtest.h>

#include <jaeger/proto/model.pb.h>
#include <jaeger_collector/converter/tskv_to_jaeger_protobuf.hpp>
#include <log_name_to_level.hpp>

namespace {

constexpr std::string_view tskv_jaeger_span_with_query =
    "tskv"
    "\ttimestamp=2020-04-27T15:08:58.551723"
    "\ttimezone=+03:00\tlevel=INFO"
    "\tmodule=LogOpenTracing ( "
    "userver/core/src/tracing/span_opentracing.cpp:87 )"
    "\ttask_id=7F3806C2D140"
    "\tservice_name=some_service"
    "\tcoro_id=7F39BF746E18thread_id=0x00007F3826326700"
    "\ttext=\ttrace_id=6d00674cadea6e1c"
    "\tparent_id=c5438739a6159d79"
    "\tspan_id=6d00674cadea6e1f\tstart_time=1587989338546529"
    "\tstart_time_millis=1587989338546"
    "\tduration=5179\toperation_name=pg_query"
    "\ttags=[{\"value\":\"postgres\",\"type\":\"string\",\"key\":\"db.type\"},"
    "{\"value\":\"myt-5ft9u7puo9l3rddo.db.yandex.net:6432\",\"type\":"
    "\"string\",\"key\":\"peer.address\"},"
    "{\"value\":\"\\nSELECT parks.contracts.\\\\\"ID\\\\\" FROM "
    "parks.contracts\", \"type\":\"string\",\"key\":\"db.statement\"}]\n";

}  // namespace

////////////////////////////////////////////////////////////////////////////////

TEST(TskvJaegerProtobuf, Default) {
  pilorama::FilterConfig f;

  pilorama::jaeger_collector::converter::TskvToJaegerProtobuf converter{
      f, tskv_jaeger_span_with_query};

  std::string result;
  converter.WriteSingleRecord(result);

  jaeger::api_v2::Span result_span;
  result_span.ParseFromString(result);
  EXPECT_FALSE(converter.ShouldIgnoreRecord());
  EXPECT_EQ(result_span.operation_name(), "pg_query");
}
