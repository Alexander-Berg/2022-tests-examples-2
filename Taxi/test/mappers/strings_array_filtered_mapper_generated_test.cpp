/// This test was generated by tools/create-new-operation
#include <userver/utest/utest.hpp>

#include <optional>
#include <variant>

#include <eventus/mappers/strings_array_filtered_mapper.hpp>
#include <test/common.hpp>

namespace {

using namespace test::common;
using eventus::mappers::StringsArrayFilteredMapper;

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

class StringsArrayFilteredMapperBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, StringsArrayFilteredMapperBasicSuite,
    ::testing::Values(
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_1"}},
                {"policy", "accept_only"},
            },
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ]
            })",
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ],
              "to":[
                "value_1"
              ]
            })",
            R"(accept_only_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_1"}},
                {"policy", "reject_only"},
            },
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ]
            })",
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ],
              "to":[
                "value_2"
              ]
            })",
            R"(reject_only_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_1"}},
                {"policy", "accept_only"},
            },
            R"({
              "from":[]
            })",
            R"({
              "from":[]
            })",
            R"(accept_only_empty_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_1"}},
                {"policy", "reject_only"},
            },
            R"({
              "from":[]
            })",
            R"({
              "from":[]
            })",
            R"(reject_only_empty_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_3"}},
                {"policy", "accept_only"},
            },
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ]
            })",
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ]
            })",
            R"(nothing_to_accept_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_3"}},
                {"policy", "reject_only"},
            },
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ]
            })",
            R"({
              "from":[
                "value_1",
                "value_1",
                "value_2",
                "value_2"
              ],
              "to":[
                "value_1",
                "value_2"
              ]
            })",
            R"(nothing_to_reject_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", "from"},
                {"dst_key", "to"},
                {"filter_values", std::vector<std::string>{"value_3"}},
                {"policy", "reject_only"},
            },
            R"({
              "from":[
                "value_3",
                "value_3",
                "value_3"
              ]
            })",
            R"({
              "from":[
                "value_3",
                "value_3",
                "value_3"
              ]
            })",
            R"(reject_all_)",
        }),
    PrintOperationArgsParam);

UTEST_P(StringsArrayFilteredMapperBasicSuite, RunTest) {
  const auto& param = GetParam();

  using namespace test::common;

  auto mapper = MakeOperation<StringsArrayFilteredMapper>(param.args);

  eventus::mappers::Event event(formats::json::FromString(param.input_event));

  if (std::holds_alternative<std::exception>(param.expected)) {
    EXPECT_THROW(mapper->Map(event), std::exception);
    ASSERT_EQ(event.GetData(), formats::json::FromString(param.input_event));
  } else {
    mapper->Map(event);
    const auto expect_data =
        formats::json::FromString(std::get<std::string>(param.expected));
    ASSERT_EQ(event.GetData(), expect_data);
  }
}