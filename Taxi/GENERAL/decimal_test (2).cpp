#include "transformer/agl/decimal.hpp"

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
      {{"neg", std::make_shared<transformer::agl::ParserDecimalNeg>()},
       {"add", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kAdd>>()},
       {"sub", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kSub>>()},
       {"mul", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kMul>>()},
       {"div", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kDiv>>()},
       {"min", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kMin>>()},
       {"max", std::make_shared<transformer::agl::ParserDecimalOp<
                   transformer::agl::DecimalOperator::kMax>>()}});
  return res;
}();

static const agl::modules::Manager manager = [] {
  return agl::modules::Manager(operators);
}();

static const agl::core::variant::YamlParser::Deps deps(operators, manager);
}  // namespace

TEST(Decimal, TestNeg) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#neg:
          value#string: 10
    - value#neg:
          value#string: -10
    - value#neg:
          value#string: 0
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
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ("-10", result_list.Get<std::string>(0));
  EXPECT_EQ("10", result_list.Get<std::string>(1));
  EXPECT_EQ("0", result_list.Get<std::string>(2));
}

TEST(Decimal, TestMin) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#min:
          values#array:
            - value#string: 1.10
            - value#string: 2.10
    - value#min:
          values#array:
            - value#string: -10
    - value#min:
          values#array:
            - value#string: 20
            - value#string: 10
            - value#string: -1.9
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
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ("1.1", result_list.Get<std::string>(0));
  EXPECT_EQ("-10", result_list.Get<std::string>(1));
  EXPECT_EQ("-1.9", result_list.Get<std::string>(2));
}

TEST(Decimal, TestMax) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#max:
        values#array:
          - value#string: 1.10
          - value#string: 2.10
    - value#max:
          values#array:
            - value#string: -10
    - value#max:
          values#array:
            - value#string: 20
            - value#string: 10
            - value#string: -1.9
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
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ("2.1", result_list.Get<std::string>(0));
  EXPECT_EQ("-10", result_list.Get<std::string>(1));
  EXPECT_EQ("20", result_list.Get<std::string>(2));
}

TEST(Decimal, TestAdd) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#add:
          values#array:
            - value#string: 1.10
            - value#string: 2.10
    - value#add:
          values#array:
            - value#string: 2
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
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ("3.2", result_list.Get<std::string>(0));
  EXPECT_EQ("2", result_list.Get<std::string>(1));
}

TEST(Decimal, TestSub) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#sub:
          values#array:
            - value#string: 10
            - value#string: 2
            - value#string: 5
    - value#sub:
          values#array:
            - value#string: 5
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
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ("3", result_list.Get<std::string>(0));
  EXPECT_EQ("5", result_list.Get<std::string>(1));
}

TEST(Decimal, TestMul) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#mul:
          values#array:
            - value#string: 1
            - value#string: 2
            - value#string: -5
    - value#mul:
          values#array:
            - value#string: 9
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
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ("-10", result_list.Get<std::string>(0));
  EXPECT_EQ("9", result_list.Get<std::string>(1));
}

TEST(Decimal, TestDiv) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#div:
          values#array:
            - value#string: 10
            - value#string: 2
            - value#string: 5
    - value#div:
          values#array:
            - value#string: 18
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
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ("1", result_list.Get<std::string>(0));
  EXPECT_EQ("18", result_list.Get<std::string>(1));
}

TEST(Decimal, TestDivideByZero) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - value#div:
          values#array:
            - value#string: 10
            - value#string: 2
            - value#string: 0
  )");

  const auto& parser =
      agl::core::variant::GetYamlParser("array", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
}

}  // namespace tests
