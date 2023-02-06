#include "string_equal_filter.hpp"

#include <vector>

#include <userver/utest/utest.hpp>

namespace utils::rule {

namespace {

const auto kEventKey = "event_key";

}

using Event = eventus::filters::Event;

using eventus::common::OperationArgs;
using eventus::common::OperationArgument;
using OperationArgsV = std::vector<eventus::common::OperationArgumentType>;
using eventus::filters::StringEqualFilter;
using FilterResult = eventus::filters::FilterResult;

UTEST(StringEqualFilter, RuleMatcher) {
  std::string raw_result = "cucumber";
  StringEqualFilter filter(std::vector<OperationArgument>{
      {"src", kEventKey}, {"match_with", raw_result}});

  {
    formats::json::ValueBuilder builder;
    builder[kEventKey] = raw_result;
    Event event(builder.ExtractValue());

    auto check_res = filter.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kAccepted);
  }
  {
    formats::json::ValueBuilder builder;
    builder[kEventKey] = "tomato";
    Event event(builder.ExtractValue());

    auto check_res = filter.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kRejected);
  }
}

}  // namespace utils::rule
