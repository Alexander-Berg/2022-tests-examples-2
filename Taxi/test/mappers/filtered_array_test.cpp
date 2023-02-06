#include <userver/utest/utest.hpp>

#include <eventus/mappers/filtered_array_mapper.hpp>
#include <test/common.hpp>

namespace {

using namespace test::common;

template <typename T>
formats::json::Value MakeObjectItem(const std::string& match_key,
                                    const T& value) {
  formats::json::ValueBuilder builder;
  builder["some_other_value"] = true;
  builder[match_key] = value;
  return builder.ExtractValue();
}

struct BasicTestParam {
  OperationArgsV args;
  std::string src_array_value;
  std::string dst_array_expect;
  std::optional<std::string> initial_value{};
};

std::string PrintOperationArgsParam(
    const ::testing::TestParamInfo<BasicTestParam>& param) {
  return test::common::PrintOperationArgs(param.param.args);
}

}  // namespace

class FilteredArrayMapperBasicSuite
    : public ::testing::TestWithParam<BasicTestParam> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, FilteredArrayMapperBasicSuite,
    ::testing::Values(
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "native"},
                {"match_value", "match_this"},
                {"matched_item_policy", "include"},
            },
            R"([ "mismatched_value", "match_this" ])",
            R"([ "match_this" ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "native"},
                {"match_value", "match_out_off"},
                {"matched_item_policy", "include"},
            },
            R"([ "mismatched_value", "mismatched_value" ])",
            R"([ ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "native"},
                {"match_value", "match_this"},
                {"matched_item_policy", "exclude"},
            },
            R"([ "mismatched_value", "match_this" ])",
            R"([ "mismatched_value" ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "object"},
                {"match_object_item_subkey", "object_key"},
                {"match_value", "match_this"},
                {"matched_item_policy", "include"},
            },
            R"([
               {"id":1,"object_key":"match_this"},
               {"id":2,"object_key":"mismatched_value"},
               {"id":3,"object_key":"match_this"}
            ])",
            R"([
               {"id":1,"object_key":"match_this"},
               {"id":3,"object_key":"match_this"}
            ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "object"},
                {"match_object_item_subkey", "object_key"},
                {"match_value", "match_this"},
                {"matched_item_policy", "exclude"},
            },
            R"([
                {"id":1,"object_key":"match_this"},
                {"id":2,"object_key":"mismatched_value"},
                {"id":3,"object_key":"match_this"}
            ])",
            R"([
                {"id":2,"object_key":"mismatched_value"}
            ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "object"},
                {"match_object_item_subkey", "object_key_missed"},
                {"match_value", "match_this"},
                {"matched_item_policy", "exclude"},
            },
            R"([
                {"id":1},
                {"id":2},
                {"id":3}
            ])",
            R"([ ])",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "object"},
                {"match_object_item_subkey", "object_key"},
                {"match_src_key", "keyable_value"},
                {"matched_item_policy", "include"},
            },
            R"([
                {"id":1,"object_key":"match_this"},
                {"id":2,"object_key":"mismatched_value"},
                {"id":3,"object_key":"match_this"}
            ])",
            R"([
                {"id":1,"object_key":"match_this"},
                {"id":3,"object_key":"match_this"}
            ])",
            R"({"keyable_value":"match_this"})",
        },
        BasicTestParam{
            OperationArgsV{
                {"array_items_type", "object"},
                {"match_object_item_subkey", "object_key"},
                {"match_src_key", "keyable_value"},
                {"matched_item_policy", "exclude"},
            },
            R"([
                {"id":1,"object_key":"match_this_value"},
                {"id":2,"object_key":"mismatched_value"},
                {"id":3,"object_key":"match_this_value"},
                {"id":4,"object_key":"match_this_but_miss"}
            ])",
            R"([
                {"id":2,"object_key":"mismatched_value"},
                {"id":4,"object_key":"match_this_but_miss"}
            ])",
            R"({"keyable_value":"match_this_value"})",
        }  //
        ),
    PrintOperationArgsParam);

UTEST_P(FilteredArrayMapperBasicSuite, RunTest) {
  const auto& param = GetParam();

  using namespace test::common;

  OperationArgsV base_args{
      {"array_src_key", "src_array"},
      {"array_dst_key", "dst_array"},
  };
  base_args.insert(base_args.end(), param.args.begin(), param.args.end());

  auto mapper = MakeOperation<eventus::mappers::FilteredArrayMapper>(base_args);

  eventus::mappers::Event event(
      formats::json::FromString(param.initial_value.value_or("{}")));

  event.Set("src_array", formats::json::FromString(param.src_array_value));

  mapper->Map(event);
  const auto expect_array = formats::json::FromString(param.dst_array_expect);
  ASSERT_EQ(event.Get<formats::json::Value>("dst_array"), expect_array);
}

UTEST(FilteredArrayMapperSuite, BadArgsTest) {
  using namespace test::common;

  {
    OperationArgsV args{
        {"array_src_key", "src_array"},     {"array_dst_key", "dst_array"},
        {"array_items_type", "object"},     {"match_value", "abc"},
        {"matched_item_policy", "exclude"},
    };
    EXPECT_THROW(MakeOperation<eventus::mappers::FilteredArrayMapper>(args),
                 std::exception);
  }

  {
    OperationArgsV args{
        {"array_src_key", "src_array"}, {"array_dst_key", "dst_array"},
        {"array_items_type", "object"}, {"match_object_item_subkey", StringV{}},
        {"match_value", "abc"},         {"matched_item_policy", "exclude"},
    };
    EXPECT_THROW(MakeOperation<eventus::mappers::FilteredArrayMapper>(args),
                 std::exception);
  }
}

UTEST(FilteredArrayMapperSuite, BadDataTest) {
  using namespace test::common;

  OperationArgsV args{
      {"array_src_key", "src_array"},
      {"array_dst_key", "dst_array"},
      {"array_items_type", "object"},
      {"match_object_item_subkey", "object_key"},
      {"match_value", "abc"},
      {"matched_item_policy", "exclude"},
  };

  auto mapper = MakeOperation<eventus::mappers::FilteredArrayMapper>(args);

  {
    eventus::mappers::Event event({});
    EXPECT_THROW(mapper->Map(event), std::exception);
    ASSERT_FALSE(event.HasKey("dst_array"));
  }

  {
    const auto data = formats::json::FromString(R"({
          "src_array": {"field":"x"}
      })");
    eventus::mappers::Event event(data);

    EXPECT_THROW(mapper->Map(event), std::exception);
    ASSERT_FALSE(event.HasKey("dst_array"));
  }
}
