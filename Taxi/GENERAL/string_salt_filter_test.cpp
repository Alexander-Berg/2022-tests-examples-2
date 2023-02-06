#include "string_salt_filter.hpp"

#include <vector>

#include <userver/utest/utest.hpp>

namespace utils::rule {

namespace {

const auto kUserId = "user_id";

}  // namespace

using Event = eventus::filters::Event;

using eventus::common::OperationArgs;
using eventus::common::OperationArgument;
using OperationArgsV = std::vector<eventus::common::OperationArgumentType>;
using eventus::filters::StringSaltFilter;
using FilterResult = eventus::filters::FilterResult;

UTEST(RuleMatcher, StringSaltFilter) {
  formats::json::ValueBuilder builder;
  builder[kUserId] = "wheat";
  builder["key_to_int"] = 5318008;

  Event event(builder.ExtractValue());

  {
    StringSaltFilter pepper_0_to_50(
        std::vector<OperationArgument>{{"src", kUserId},
                                       {"salt", "pepper"},
                                       {"hash_from", static_cast<double>(0)},
                                       {"hash_to", static_cast<double>(50)}});
    auto check_res = pepper_0_to_50.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kRejected);
  }
  {
    StringSaltFilter pepper_50_to_100(
        std::vector<OperationArgument>{{"src", kUserId},
                                       {"salt", "pepper"},
                                       {"hash_from", static_cast<double>(50)},
                                       {"hash_to", static_cast<double>(100)}});
    auto check_res = pepper_50_to_100.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kAccepted);
  }
  {
    StringSaltFilter cinnamon_0_to_100(
        std::vector<OperationArgument>{{"src", kUserId},
                                       {"salt", "cinnamon"},
                                       {"hash_from", static_cast<double>(0)},
                                       {"hash_to", static_cast<double>(100)}});
    auto check_res = cinnamon_0_to_100.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kAccepted);
  }
  {
    StringSaltFilter never(
        std::vector<OperationArgument>{{"src", kUserId},
                                       {"salt", "never"},
                                       {"hash_from", static_cast<double>(82)},
                                       {"hash_to", static_cast<double>(82)}});
    auto check_res = never.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kRejected);
  }
  {
    StringSaltFilter legendary_key(
        std::vector<OperationArgument>{{"src", "thelegend27"},
                                       {"salt", ""},
                                       {"hash_from", static_cast<double>(0)},
                                       {"hash_to", static_cast<double>(100)}});
    auto check_res = legendary_key.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kRejected);
  }
  {
    StringSaltFilter key_to_int(
        std::vector<OperationArgument>{{"src", "key_to_int"},
                                       {"salt", ""},
                                       {"hash_from", static_cast<double>(0)},
                                       {"hash_to", static_cast<double>(100)}});
    auto check_res = key_to_int.Match(event);
    ASSERT_EQ(check_res.result, FilterResult::kRejected);
  }
}

}  // namespace utils::rule
