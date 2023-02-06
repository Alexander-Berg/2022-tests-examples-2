#include "bool_equal_filter.hpp"

#include <userver/utest/utest.hpp>

#include <string>
#include <vector>

namespace {

using OperationArgs = eventus::common::OperationArgs;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

void MakeTest(std::string expected_param_value, bool value,
              bool expected_result) {
  using namespace formats::json;
  using namespace std::string_literals;

  const OperationArgsV args{{"key", "value"},
                            {"expected", expected_param_value}};

  std::string event_str = "{\"value\":" + (value ? "true"s : "false"s) + "}";

  auto filter = eventus::filters::BoolEqualFilter(OperationArgs(args));

  auto event = eventus::filters::Event(FromString(event_str));

  auto result = filter.Match(event);

  ASSERT_EQ(result.result == eventus::filters::FilterResult::kAccepted,
            expected_result);
}

}  // namespace

TEST(BoolEqualFilter, Good) {
  MakeTest("true", true, true);
  MakeTest("true", false, false);
  MakeTest("false", true, false);
  MakeTest("false", false, true);
  MakeTest("True", true, true);
  MakeTest("TRUE", true, true);
  MakeTest("FALSE", false, true);
  MakeTest("False", false, true);
}

TEST(BoolEqualFilter, IncorrectExpectedParam) {
  const OperationArgsV args{{"key", "value"}, {"expected", "treu"}};
  EXPECT_THROW(eventus::filters::BoolEqualFilter(OperationArgs(args)),
               std::exception);
}
