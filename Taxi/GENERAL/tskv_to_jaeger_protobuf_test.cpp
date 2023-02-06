#include <fmt/compile.h>
#include <fmt/format.h>
#include <gtest/gtest.h>
#include <jaeger/proto/model.grpc.pb.h>
#include <userver/utils/encoding/hex.hpp>

#include "tskv_to_jaeger_protobuf.hpp"

constexpr std::string_view kTskvLog =
    "tskv"
    "\ttimestamp=2020-04-27T15:08:58.551723"
    "\ttimezone=+03:00\tlevel=INFO"
    "\tmodule=LogOpenTracing ( "
    "userver/core/src/tracing/span_opentracing.cpp:87 )"
    "\ttask_id=7F3806C2D140"
    "\tservice_name=some_serive"
    "\tcoro_id=7F39BF746E18thread_id=0x00007F3826326700"
    "\ttext=\ttrace_id=04464e25b316aecc093e04d4e9eae57b"
    "\tparent_id=c5438739a6159d79"
    "\tspan_id=6d00674cadea6e1f\tstart_time=1587989338546529"
    "\tstart_time_millis=1587989338546"
    "\tduration=5179\toperation_name=pg_query"
    "\ttags=[{\"value\":\"postgres\",\"type\":\"string\",\"key\":\"db.type\"},"
    "{\"value\":\"myt-5ft9u7puo9l3rddo.db.yandex.net:6432\",\"type\":"
    "\"string\",\"key\":\"peer.address\"},"
    "{\"value\":\"\\nSELECT parks.contracts.\\\\\"ID\\\\\" FROM "
    "parks.contracts\", \"type\":\"string\",\"key\":\"db.statement\"}]\n";

TEST(TskvJaegerProtobuf, TraceId) {
  pilorama::FilterConfig f;
  f.put_message = false;
  f.drop_empty_fields = true;
  f.transform_date = false;

  std::string span_proto_bytes;

  pilorama::jaeger_collector::converter::TskvToJaegerProtobuf converter{
      f, kTskvLog};
  converter.WriteSingleRecord(span_proto_bytes);
  EXPECT_FALSE(converter.IsAtLeastErrorRecord());

  ::jaeger::api_v2::Span span;
  span.ParseFromString(span_proto_bytes);
  ASSERT_EQ(span.operation_name(), "pg_query");
}
