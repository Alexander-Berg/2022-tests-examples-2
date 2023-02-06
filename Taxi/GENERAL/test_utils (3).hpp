#pragma once

#include <string>
#include <vector>

#include <userver/formats/json/serialize.hpp>

#include <eventus/pipeline/event.hpp>

namespace eventus::mappers::test_utils {

using eventus::common::OperationArgs;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

template <typename Mapper>
void MakeTest(std::string&& event_str, std::string&& expected,
              const OperationArgsV& mapper_args) {
  using namespace formats::json;

  auto expected_formatted = ToString(FromString(expected));

  auto mapper = Mapper(mapper_args);

  auto event = eventus::pipeline::Event(FromString(event_str));

  mapper.Map(event);
  std::string res_event_str = ToString(event.GetData());

  ASSERT_EQ(res_event_str, expected_formatted);
}

template <typename Mapper>
void MakeTestWithException(std::string&& event_str,
                           const OperationArgsV& mapper_args) {
  using namespace formats::json;

  auto event_str_formatted = ToString(FromString(event_str));

  auto mapper = Mapper(mapper_args);

  auto event = eventus::pipeline::Event(FromString(event_str));

  EXPECT_THROW(mapper.Map(event), std::exception);
  ASSERT_EQ(event_str_formatted, ToString(event.GetData()));
}

}  // namespace eventus::mappers::test_utils
