#include "timestamp_mapper.hpp"

#include <iostream>
#include <string>
#include <vector>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <eventus/pipeline/event.hpp>

using eventus::common::OperationArgs;
using eventus::common::OperationArgument;
using eventus::common::OperationArgumentType;

TEST(Mappers, TimestampMapperStringsTest) {
  for (auto&& [arg_format, dt_format] :
       std::vector<std::pair<std::string, std::string>>{
           {"default", utils::datetime::kDefaultFormat},
           {"rfc3339", utils::datetime::kRfc3339Format},
           {"iso", utils::datetime::kIsoFormat},
           {"date", "%Y-%m-%d"},
           {"custom", "%Y%m%dT%H%M%S"},
           {"custom", "%s"},       // unixtime
           {"custom", "%s.%E3f"},  // unixtime with ms
           {"custom", "%s%E3f"},   // unixtime ms
       }) {
    const auto now = utils::datetime::Now();
    utils::datetime::MockNowSet(now);

    OperationArgs operation_args{std::vector<OperationArgument>{
        OperationArgument{"to", "utest_ts"},
        OperationArgument{"format", arg_format},
    }};
    if (arg_format == "custom") {
      operation_args.AppendBack(std::vector<OperationArgument>{
          {"custom", dt_format},
      });
    }
    auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

    eventus::mappers::Event event({});

    timestamp_mapper.Map(event);
    auto expected_value = utils::datetime::Timestring(
        now, utils::datetime::kDefaultTimezone, dt_format);

    const auto result = event.GetOpt<std::string>("utest_ts");
    LOG_INFO() << formats::json::ToString(event.GetData());
    ASSERT_TRUE(result.has_value());
    LOG_INFO() << expected_value << " ?? " << *result;
    ASSERT_EQ(*result, expected_value);
  }
}

TEST(Mappers, TimestampMapperSecondsTest) {
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"format", "seconds"},
  }};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  eventus::mappers::Event event({});

  timestamp_mapper.Map(event);
  const auto expected_value = static_cast<long>(
      std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch())
          .count());

  const auto result = event.GetOpt<long>("utest_ts");
  ASSERT_TRUE(result.has_value());
  LOG_INFO() << expected_value << " ?? " << *result;
  ASSERT_EQ(*result, expected_value);
}

TEST(Mappers, TimestampMapperSecondsWithMsTest) {
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"format", "seconds_with_ms"},
  }};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  eventus::mappers::Event event({});

  timestamp_mapper.Map(event);
  const auto expected_value =
      static_cast<double>(std::chrono::duration_cast<std::chrono::milliseconds>(
                              now.time_since_epoch())
                              .count()) /
      1000.0;

  const auto result = event.GetOpt<double>("utest_ts");
  ASSERT_TRUE(result.has_value());
  LOG_INFO() << expected_value << " ?? " << *result;
  ASSERT_EQ(*result, expected_value);
}

TEST(Mappers, TimestampMapperFromTest) {
  const auto now = utils::datetime::Now();

  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"from", "timestamp"},
      OperationArgument{"format", "seconds_with_ms"},
  }};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  const auto incoming_value = utils::datetime::Timestring(
      now, utils::datetime::kDefaultTimezone, utils::datetime::kRfc3339Format);
  formats::json::ValueBuilder builder(
      std::unordered_map<std::string, std::string>{
          {"timestamp", incoming_value}});
  eventus::mappers::Event event(builder.ExtractValue());

  timestamp_mapper.Map(event);
  const auto expected_value =
      static_cast<double>(std::chrono::duration_cast<std::chrono::milliseconds>(
                              now.time_since_epoch())
                              .count()) /
      1000.0;

  const auto result = event.GetOpt<double>("utest_ts");
  ASSERT_TRUE(result.has_value());
  LOG_INFO() << expected_value << " ?? " << *result;
  ASSERT_EQ(*result, expected_value);
}

TEST(Mappers, TimestampMapperInputWithoutTimezone) {
  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"from", "timestamp"},
      OperationArgument{"format", "default"},
  }};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  formats::json::ValueBuilder builder(
      std::unordered_map<std::string, std::string>{
          {"timestamp", "2019-07-31T18:47:36"}});

  eventus::mappers::Event event(builder.ExtractValue());

  timestamp_mapper.Map(event);
  const auto expected_value = "2019-07-31T18:47:36+0000";

  const auto result = event.GetOpt<std::string>("utest_ts");
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(*result, expected_value);
}

TEST(Mappers, TimestampMapperNotExitsPolicyNone) {
  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"from", "timestamp"},
      OperationArgument{"from_not_exists_policy", "none"},
      OperationArgument{"format", "default"}}};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  formats::json::ValueBuilder builder(
      std::unordered_map<std::string, std::string>{});

  eventus::mappers::Event event(builder.ExtractValue());

  timestamp_mapper.Map(event);

  const auto result = event.GetOpt<std::string>("utest_ts");
  ASSERT_TRUE(!result.has_value());
}

TEST(Mappers, TimestampMapperNotExitsPolicyEpoch) {
  OperationArgs operation_args{std::vector<OperationArgument>{
      OperationArgument{"to", "utest_ts"},
      OperationArgument{"from", "timestamp"},
      OperationArgument{"from_not_exists_policy", "epoch"},
      OperationArgument{"format", "seconds"}}};
  auto timestamp_mapper = eventus::mappers::TimestampMapper{operation_args};

  formats::json::ValueBuilder builder(
      std::unordered_map<std::string, std::string>{});

  eventus::mappers::Event event(builder.ExtractValue());

  timestamp_mapper.Map(event);

  const auto result = event.GetOpt<long>("utest_ts");
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(*result, 0);
}
