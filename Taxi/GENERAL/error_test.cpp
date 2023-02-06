#include "transformer/agl/error.hpp"

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/modules/manager.hpp>
#include <exception>
#include <userver/logging/log.hpp>

#include <gtest/gtest.h>

namespace tests {

namespace {

static const agl::core::OperatorsRegistry operators = [] {
  auto res = agl::core::OperatorsRegistry::BuiltinOperators();
  res.RegisterOperators(
      {{"error", std::make_shared<transformer::agl::ParserError>()}});
  return res;
}();

static const agl::modules::Manager manager = [] {
  return agl::modules::Manager(operators);
}();

static const agl::core::variant::YamlParser::Deps deps(operators, manager);
}  // namespace

TEST(OperatorError, SimpleError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error: "test"
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test", std::string(error.what()));
  }
}

TEST(OperatorError, FormatIntegerError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value#integer: 1
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test 1", std::string(error.what()));
  }
}

TEST(OperatorError, FormatDoubleError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value#real: 1.2
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test 1.200000", std::string(error.what()));
  }
}

TEST(OperatorError, FormatNullError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value:
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test null", std::string(error.what()));
  }
}

TEST(OperatorError, FormatStringError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value#string: test
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test test", std::string(error.what()));
  }
}

TEST(OperatorError, FormatBoolError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value#boolean: true
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test true", std::string(error.what()));
  }
}

TEST(OperatorError, FormatObjectError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "test {}"
        args:
          - value#array:
              - value: test1
              - value: test2
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("test object", std::string(error.what()));
  }
}

TEST(OperatorError, FormatError) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "param1 {}, param2 {}, param3 {}, param4 {}, param5 {}, test"
        args:
          - value: test
          - value: true
          - value: 1
          - value: -10
          - value: 1.234567
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ(
        "param1 test, param2 true, param3 1, param4 -10, param5 1.234567, test",
        std::string(error.what()));
  }
}

TEST(OperatorError, IncorrectArgs) {
  const formats::yaml::Value scheme = formats::yaml::FromString(R"(
    - client_id#error:
        format: "param1 {}{}{}{}"
        args:
          - value: test
          - value: true
  )");
  const auto& parser =
      agl::core::variant::GetYamlParser("object", tests::operators);
  agl::core::Variant executable = parser.Parse(scheme, tests::deps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::ExecuterState executer_state;
  try {
    executable.Evaluate(executer_state);
  } catch (const std::runtime_error& error) {
    EXPECT_EQ("Operator \"error\" format {} count > args count",
              std::string(error.what()));
  }
}

}  // namespace tests
