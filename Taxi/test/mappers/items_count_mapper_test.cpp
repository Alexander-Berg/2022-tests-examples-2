#include <userver/utest/utest.hpp>

#include <eventus/mappers/items_count_mapper.hpp>
#include <test/common.hpp>

namespace {

using namespace test::common;
using eventus::mappers::ItemsCountMapper;

struct BasicTestParam {
  OperationArgsV args;
  std::string input_event;
  std::string expected;
  std::optional<std::string> testname_prefix{};
  bool exception_on_map_call{false};
};

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<BasicTestParam>& param) {
  return param.param.testname_prefix.value_or("") +
         test::common::PrintOperationArgs(param.param.args);
}

}  // namespace

class ItemsCountMapperBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, ItemsCountMapperBasicSuite,
    ::testing::Values(
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"array"}},
                {"count_dst_key", "array_size"},
            },
            R"({
              "array":[
                "abc",
                "def"
              ]
            })",
            R"({
              "array":[
                "abc",
                "def"
              ],
              "array_size":2
            })",
            R"(array_with_items__)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"array"}},
                {"count_dst_key", "array_size"},
            },
            R"({
              "array":[]
            })",
            R"({
              "array":[],
              "array_size":0
            })",
            R"(empty_array__)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"object"}},
                {"count_dst_key", "object_size"},
            },
            R"({
              "object":{
                "abc":true,
                "def":true
              }
            })",
            R"({
              "object":{
                "abc":true,
                "def":true
              },
              "object_size":2
            })",
            R"(object_with_items__)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"object"}},
                {"count_dst_key", "object_size"},
            },
            R"({
              "object":{}
            })",
            R"({
              "object":{},
              "object_size":0
            })",
            R"(empty_object__)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"key_missed"}},
                {"count_dst_key", "missed_size"},
            },
            R"({})",
            R"({})",
            {},
            true,
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"other_type"}},
                {"count_dst_key", "object_size"},
            },
            R"({
              "other_type":"but_string"
            })",
            R"({
              "other_type":"but_string"
            })",
            R"(src_type_string__)",
            true,
        },
        BasicTestParam{
            OperationArgsV{
                {"src_key", std::vector<std::string>{"other_type"}},
                {"count_dst_key", "object_size"},
            },
            R"({
              "other_type":4.0
            })",
            R"({
              "other_type":4.0
            })",
            R"(src_type_double__)",
            true,
        }),
    PrintOperationArgsParam);

UTEST_P(ItemsCountMapperBasicSuite, RunTest) {
  const auto& param = GetParam();

  using namespace test::common;

  auto mapper = MakeOperation<ItemsCountMapper>(param.args);

  eventus::mappers::Event event(formats::json::FromString(param.input_event));

  if (param.exception_on_map_call) {
    EXPECT_THROW(mapper->Map(event), std::exception);
  } else {
    mapper->Map(event);
  }
  const auto expect_data = formats::json::FromString(param.expected);
  ASSERT_EQ(event.GetData(), expect_data);
}
