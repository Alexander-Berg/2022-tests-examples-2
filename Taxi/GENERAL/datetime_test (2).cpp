#include "transformer/agl/datetime.hpp"

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/modules/manager.hpp>

#include <gtest/gtest.h>

namespace tests {

namespace {

static const agl::core::OperatorsRegistry operators = [] {
  auto res = agl::core::OperatorsRegistry::BuiltinOperators();
  res.RegisterOperators(
      {{"reformat-datetime",
        std::make_shared<transformer::agl::ParserDatetime>()}});
  return res;
}();

static const agl::modules::Manager manager = [] {
  return agl::modules::Manager(operators);
}();

static const agl::core::variant::YamlParser::Deps deps(operators, manager);
}  // namespace

TEST(ReformatDateTime, TestReformatDateTime) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#reformat-datetime:
        value#string: 2020-11-09T13:22:30
    - value#reformat-datetime:
        value#string: 2020-11-09T13:22:30+03
    - value#reformat-datetime:
        value#string: 2020-11-09T13:22:30+0300
    - value#reformat-datetime:
        value#string: 2020-11-09T13:22:30+0100
    - value#reformat-datetime:
        value#string: 2020-11-09T13:22:30-0100
    - value#reformat-datetime:
        value#string: 2021-10-01T00:00:00Z
  )");

  const auto& parser =
      agl::core::variant::GetYamlParser("array", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);

  EXPECT_EQ("2020-11-09T13:22:30+03:00", result_list.Get<std::string>(0));
  EXPECT_EQ("2020-11-09T13:22:30+03:00", result_list.Get<std::string>(1));
  EXPECT_EQ("2020-11-09T13:22:30+03:00", result_list.Get<std::string>(2));
  EXPECT_EQ("2020-11-09T15:22:30+03:00", result_list.Get<std::string>(3));
  EXPECT_EQ("2020-11-09T17:22:30+03:00", result_list.Get<std::string>(4));
  EXPECT_EQ("2021-10-01T03:00:00+03:00", result_list.Get<std::string>(5));
}

}  // namespace tests
