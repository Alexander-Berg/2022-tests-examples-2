#include <userver/utest/utest.hpp>

#include <eventus/filters/field_check_filter.hpp>

namespace {

using Event = eventus::pipeline::Event;
using FilterResult = eventus::filters::FilterResult;

eventus::filters::FilterTypePtr MakeFilter(
    const std::vector<eventus::common::OperationArgument>& args) {
  return std::make_shared<eventus::filters::FieldCheckFilter>(args);
}

}  // namespace

TEST(FiltersSuite, FieldCheckFilterTest) {
  auto key_exists =
      MakeFilter({{"key", "field_check"}, {"policy", "key_exists"}});
  auto key_not_exists =
      MakeFilter({{"key", "field_check"}, {"policy", "key_not_exists"}});

  auto is_null = MakeFilter({{"key", "field_check"}, {"policy", "is_null"}});
  auto is_not_null =
      MakeFilter({{"key", "field_check"}, {"policy", "is_not_null"}});

  {
    formats::json::ValueBuilder builder;
    builder["user_id"] = "wheat";

    Event event(builder.ExtractValue());

    ASSERT_EQ(FilterResult::kRejected, key_exists->Match(event).result);
    ASSERT_EQ(FilterResult::kAccepted, key_not_exists->Match(event).result);

    ASSERT_EQ(FilterResult::kAccepted, is_null->Match(event).result);
    ASSERT_EQ(FilterResult::kRejected, is_not_null->Match(event).result);
  }

  {
    formats::json::ValueBuilder builder;
    builder["field_check"] = "wheat";

    Event event(builder.ExtractValue());

    ASSERT_EQ(FilterResult::kAccepted, key_exists->Match(event).result);
    ASSERT_EQ(FilterResult::kRejected, key_not_exists->Match(event).result);

    ASSERT_EQ(FilterResult::kRejected, is_null->Match(event).result);
    ASSERT_EQ(FilterResult::kAccepted, is_not_null->Match(event).result);
  }

  {
    formats::json::ValueBuilder builder;
    builder["field_check"] =
        formats::json::ValueBuilder(formats::json::Type::kNull);

    Event event(builder.ExtractValue());

    ASSERT_EQ(FilterResult::kAccepted, key_exists->Match(event).result);
    ASSERT_EQ(FilterResult::kRejected, key_not_exists->Match(event).result);

    ASSERT_EQ(FilterResult::kAccepted, is_null->Match(event).result);
    ASSERT_EQ(FilterResult::kRejected, is_not_null->Match(event).result);
  }
}
