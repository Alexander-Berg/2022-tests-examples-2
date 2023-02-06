#include "string_array_filter.hpp"

#include <userver/utest/utest.hpp>

#include <eventus/operations/details/test_helpers.hpp>

namespace {

const auto kTags = "tags";
const auto kUserId = "user_id";
const auto kCardSystem = "card_system";

using namespace eventus::operations::details::test_helpers;

using FilterResult = eventus::filters::FilterResult;
using OperationArg = eventus::common::OperationArgument;

struct BasicTestParam {
  OperationArgsV args;
  eventus::filters::FilterResult expected_result;
};

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<BasicTestParam>& data) {
  return PrintOperationArgs(data.param.args);
}

}  // namespace

class StringArrayFilterBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, StringArrayFilterBasicSuite,
    ::testing::Values(
        // indexed args
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_all"},
             {"match_with", StringV{"life", "is"}}},
            FilterResult::kAccepted,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_all"},
             {"match_with", StringV{"life", "is", "bad"}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_none"},
             {"match_with", StringV{"is", "torture"}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_none"},
             {"match_with", StringV{"fine"}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_none"},
             {"match_with", StringV{"good"}}},
            FilterResult::kAccepted,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kUserId},
             {"policy", "contains_any"},
             {"match_with", StringV{}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kCardSystem},
             {"policy", "contains_any"},
             {"match_with", StringV{}}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{"it's", "my", "life"}}},
            FilterResult::kAccepted,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{"it's", "my", "car!"}}},
            FilterResult::kRejected,
        },
        // assosiative args
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{"i"}},
             {"compare_policy", "contains"}},
            FilterResult::kAccepted,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{"i"}},
             {"compare_policy", "exact"}},
            FilterResult::kRejected,
        },
        BasicTestParam{
            {{"src", kTags},
             {"policy", "contains_any"},
             {"match_with", StringV{"ine"}},
             {"compare_policy", "contains"}},
            FilterResult::kAccepted,
        }),
    PrintOperationArgsParam);

UTEST_P(StringArrayFilterBasicSuite, BasicTest) {
  auto param = GetParam();
  eventus::filters::Event event({});
  event.Set(kTags, StringV{"life", "is", "fine"});
  event.Set(kUserId, "death");

  eventus::filters::StringArrayFilter filter(param.args);
  auto check_res = filter.Match(event);
  ASSERT_EQ(check_res.result, param.expected_result);
}
