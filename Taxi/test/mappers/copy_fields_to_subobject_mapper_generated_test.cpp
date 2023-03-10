/// This test was generated by tools/create-new-operation
#include <userver/utest/utest.hpp>

#include <optional>
#include <variant>

#include <eventus/mappers/copy_fields_to_subobject_mapper.hpp>
#include <test/common.hpp>

namespace {

using namespace test::common;
using eventus::mappers::CopyFieldsToSubobjectMapper;

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

class CopyFieldsToSubobjectMapperBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, CopyFieldsToSubobjectMapperBasicSuite,
    ::testing::Values(
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1", "key_2"}},
                {"dst_key", std::vector<std::string>{"key_4"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ],
              "key_4":{
                "key_1":1,
                "key_2":"2"
              }
            })",
            R"(copy_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2"}},
                {"dst_key", std::vector<std::string>{"key_4"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ],
              "key_4":{
                "key_666":1,
                "key_2":"2"
              }
            })",
            R"(copy_and_rename_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2 key_777"}},
                {"dst_key", std::vector<std::string>{"key_4"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ],
              "key_4":{
                "key_666":1,
                "key_777":"2"
              }
            })",
            R"(copy_and_rename_2_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping", std::vector<std::string>{}},
                {"dst_key", std::vector<std::string>{"key_4"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ],
              "key_4":{}
            })",
            R"(copy_empty_list_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2 key_777"}},
                {"dst_key", std::vector<std::string>{"key_4"}},
            },
            R"({})",
            R"({
              "key_4":{}
            })",
            R"(empty_object_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2 key_777"}},
                {"dst_key",
                 std::vector<std::string>{"key_4", "key_123", "key_11"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ],
              "key_4":{
                "key_123":{
                  "key_11":{
                    "key_666":1,
                    "key_777":"2"
                  }
                }
              }
            })",
            R"(recursive_path_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2 key_777",
                                          "key_3"}},
                {"dst_key", std::vector<std::string>{}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_666":1,
              "key_777":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"(empty_path_1_)",
        },
        BasicTestParam{
            OperationArgsV{
                {"src_keys_mapping",
                 std::vector<std::string>{"key_1 key_666", "key_2 key_777",
                                          "key_3"}},
            },
            R"({
              "key_1":1,
              "key_2":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"({
              "key_1":1,
              "key_2":"2",
              "key_666":1,
              "key_777":"2",
              "key_3":[
                1,
                2
              ]
            })",
            R"(empty_path_2_)",
        }),
    PrintOperationArgsParam);

UTEST_P(CopyFieldsToSubobjectMapperBasicSuite, RunTest) {
  const auto& param = GetParam();

  using namespace test::common;

  auto mapper = MakeOperation<CopyFieldsToSubobjectMapper>(param.args);

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
