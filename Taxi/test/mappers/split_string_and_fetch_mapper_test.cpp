#include <userver/utest/utest.hpp>

#include <eventus/mappers/split_string_and_fetch_mapper.hpp>

namespace {

static const std::string kUuidKey = "uuid";
static const std::string kClidUuidKey = "clid_uuid";

static const std::string kSplitStringAndFetchMapperName =
    "split_string_and_fetch";

}  // namespace

TEST(SplitStringAndFetchMapperSuite, MapperTest) {
  using OperationArgsV = std::vector<eventus::common::OperationArgument>;
  OperationArgsV mapper_args{
      {"to", kUuidKey},
      {"from", kClidUuidKey},
      {"separator", "_"},
      {"fetch_index", static_cast<double>(1)},
  };

  {  // destination key not exists
    auto mapper = eventus::mappers::SplitStringAndFetchMapper(mapper_args);
    formats::json::ValueBuilder builder;
    builder[kClidUuidKey] = "prefix_expectedvalue";
    eventus::mappers::Event event(builder.ExtractValue());
    EXPECT_NO_THROW(mapper.Map(event));
    ASSERT_TRUE(event.HasKey(kUuidKey));
    ASSERT_EQ(event.Get<std::string>(kUuidKey), std::string("expectedvalue"));
  }

  eventus::common::OperationArgs fixedcount_args{OperationArgsV{
      {"expect_count", static_cast<double>(2)},
  }};
  fixedcount_args.AppendBack(mapper_args);
  for (auto& invalid_value :
       std::vector<std::string>{"prefix_expectedvalue_huh", "prefix"}) {
    auto mapper = eventus::mappers::SplitStringAndFetchMapper(fixedcount_args);

    formats::json::ValueBuilder builder;
    builder[kClidUuidKey] = invalid_value;
    eventus::mappers::Event event(builder.ExtractValue());
    EXPECT_THROW(mapper.Map(event), std::exception);
    ASSERT_FALSE(event.HasKey(kUuidKey));
  }

  {  // no override flag
    auto mapper = eventus::mappers::SplitStringAndFetchMapper(mapper_args);
    formats::json::ValueBuilder builder;
    builder[kClidUuidKey] = "prefix_expectedvalue";
    builder[kUuidKey] = "valueisset";
    eventus::mappers::Event event(builder.ExtractValue());
    EXPECT_THROW(mapper.Map(event), std::exception);
    ASSERT_TRUE(event.HasKey(kUuidKey));
    ASSERT_EQ(event.Get<std::string>(kUuidKey), std::string("valueisset"));
  }

  eventus::common::OperationArgs override_args{OperationArgsV{
      {"override", "true"},
  }};
  override_args.AppendBack(mapper_args);
  {
    auto mapper = eventus::mappers::SplitStringAndFetchMapper(override_args);

    formats::json::ValueBuilder builder;
    builder[kClidUuidKey] = "prefix_expectedvalue";
    builder[kUuidKey] = "valueisset";
    eventus::mappers::Event event(builder.ExtractValue());
    EXPECT_NO_THROW(mapper.Map(event));
    ASSERT_TRUE(event.HasKey(kUuidKey));
    ASSERT_EQ(event.Get<std::string>(kUuidKey), std::string("expectedvalue"));
  }
}
