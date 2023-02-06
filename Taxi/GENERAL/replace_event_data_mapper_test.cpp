#include "replace_event_data_mapper.hpp"

#include <userver/utest/utest.hpp>

#include <optional>
#include <variant>

#include <test/common.hpp>

namespace {

using namespace test::common;
using eventus::mappers::ReplaceEventDataMapper;

using ExpectedType = std::variant<std::string, std::exception>;

struct BasicTestParam {
  OperationArgsV args;
  std::string input_event;
  ExpectedType expected;
  std::optional<std::string> testname_prefix{};
};

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<BasicTestParam>& param) {
  return param.param.testname_prefix.value_or("") +
         test::common::PrintOperationArgs(param.param.args);
}

}  // namespace

class ReplaceEventDataMapperBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, ReplaceEventDataMapperBasicSuite,
    ::testing::Values(
        BasicTestParam{
            OperationArgsV{
                {"src_type", std::string{"stringified_json"}},
                {"src", std::vector<std::string>{"key", "sub_key"}},
            },
            R"({
              "key": {
                "sub_key": "{\"internal_key\": \"value\"}"
              }
            })",
            R"({"internal_key":"value"})",
            R"(stringified_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_type", std::string{"native_json"}},
                {"src", std::vector<std::string>{"key"}},
            },
            R"({
              "key": {
                    "internal_key": "value"
              }
            })",
            R"({"internal_key":"value"})",
            R"(native_)",
        }),
    PrintOperationArgsParam);

UTEST_P(ReplaceEventDataMapperBasicSuite, RunTest) {
  const auto& param = GetParam();

  using namespace test::common;

  auto mapper = MakeOperation<ReplaceEventDataMapper>(param.args);

  eventus::mappers::Event event(formats::json::FromString(param.input_event));

  if (std::holds_alternative<std::exception>(param.expected)) {
    EXPECT_THROW(mapper->Map(event), std::exception);
    ASSERT_EQ(event.GetData(), formats::json::FromString(param.input_event));
  } else {
    mapper->Map(event);
    const auto expect_data =
        formats::json::FromString(std::get<std::string>(param.expected));
    ASSERT_EQ(event.GetData(), expect_data) << event.AsString();
  }
}
