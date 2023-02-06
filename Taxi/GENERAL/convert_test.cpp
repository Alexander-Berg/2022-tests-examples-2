#include <chrono>

#include <gtest/gtest.h>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <yt-replica-reader/models/convert.hpp>

namespace {
formats::json::Value MakeDatetimeValue() {
  return formats::json::MakeObject(
      "datetime_key", formats::json::MakeObject(
                          "$v", "2021-02-24T13:58:35.470011", "$a",
                          formats::json::MakeObject("raw_type", "datetime")));
}
}  // namespace

TEST(YTConvert, YTDatetime) {
  auto yt_value = ytlib::Value{MakeDatetimeValue()};
  auto json1 = yt_value.As<formats::json::Value>();
  EXPECT_THROW(
      json1["datetime_key"].As<std::chrono::system_clock::time_point>(),
      std::runtime_error);
  auto json2 = yt_replica_reader::models::ConvertRawYson(yt_value);
  ASSERT_EQ(
      ::utils::datetime::Timestring(
          json2["datetime_key"].As<std::chrono::system_clock::time_point>()),
      "2021-02-24T13:58:35.470011+0000");
}

struct TestArgs {
  std::string input_json;
  std::string expected_json;
  yt_replica_reader::models::Aliases aliases;
};

class MigrationTest : public ::testing::TestWithParam<TestArgs> {};

TEST_P(MigrationTest, YTTest) {
  auto args = GetParam();
  auto yt_value = ytlib::Value{formats::json::FromString(args.input_json)};
  auto transformed = yt_replica_reader::models::ConvertRawYson(yt_value);
  transformed = yt_replica_reader::models::RenameJsonFields(
      std::move(transformed), args.aliases);
  auto expected = formats::json::FromString(args.expected_json);
  ASSERT_EQ(transformed.GetPath(), "/");
  ASSERT_EQ(transformed, expected) << "Input: " << args.input_json;
}

static const std::string kInputJson1 = R"~({
    "key_1": {
        "inner_1": {"subkey_key_1_1": "value1"},
        "inner_2": {"subkey_key_2_1": "value2"}
    },
    "key2": {"some_key":"some_value"}
})~";

INSTANTIATE_TEST_SUITE_P(

    YTConvertMigrations, MigrationTest,
    ::testing::Values(
        TestArgs{
            kInputJson1,
            kInputJson1,
            {},
        },
        TestArgs{
            kInputJson1,
            R"~({
                    "key_1_new": {
                        "inner_1": {"subkey_key_1_1": "value1"},
                        "inner_2": {"subkey_key_2_1": "value2"}
                    },
                    "key2": {"some_key":"some_value"}
                })~",
            {{"key_1", "key_1_new"}},
        },
        TestArgs{
            kInputJson1,
            R"~({
                    "key_1": {
                        "inner_1_new": {"subkey_key_1_1": "value1"},
                        "inner_2": {"subkey_key_2_1": "value2"}
                    },
                    "key2": {"some_key":"some_value"}
                })~",
            {{"key_1.inner_1", "inner_1_new"}},
        }));
