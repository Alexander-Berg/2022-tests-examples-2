#include <userver/utest/utest.hpp>

#include <eventus/mappers/bool_to_int_mapper.hpp>
#include <eventus/mappers/test_utils.hpp>
#include <string>
#include <vector>

using namespace eventus::mappers::test_utils;

TEST(BoolToIntMapper, True) {
  const std::vector<eventus::common::OperationArgument> fetch_keys_args{
      {"dst", "field"}, {"src", "field"}};
  std::string event_str = R"(
    {
      "field": true
    }
  )";
  std::string expected = R"(
    {
      "field": 1
    }
  )";
  MakeTest<eventus::mappers::BoolToIntMapper>(
      std::move(event_str), std::move(expected), fetch_keys_args);
}

TEST(BoolToIntMapper, False) {
  const std::vector<eventus::common::OperationArgument> fetch_keys_args{
      {"dst", "field2"}, {"src", "field1"}};
  std::string event_str = R"(
    {
      "field1": false
    }
  )";
  std::string expected = R"(
    {
      "field1": false,
      "field2": 0
    }
  )";
  MakeTest<eventus::mappers::BoolToIntMapper>(
      std::move(event_str), std::move(expected), fetch_keys_args);
}
