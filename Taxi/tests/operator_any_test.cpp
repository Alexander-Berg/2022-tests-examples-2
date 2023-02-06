#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/modules/manager.hpp>

#include <userver/formats/yaml/serialize.hpp>

#include <core/default_operators_registry.hpp>

#include <userver/utest/utest.hpp>

namespace agl::core::tests {

static const OperatorsRegistry kDefaultRegistry = [] {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  return r;
}();
static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();
static const variant::YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                                  kEmptyModulesManager);

UTEST(TestAnyOperator, TestEqual) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#equal:
      - value#any: {}
      - value: true
    - value#equal:
      - value#any: {}
      - value: test
    - value#equal:
      - value#any: {}
      - value: 42
    - value#equal:
      - value#any: {}
      - value: 1.5
    - value#equal:
      - value#any: {}
      - value#array:
        - 1
    - value#equal:
      - value#any: {}
      - value#map:
          input#array:
            - value#string: test
          iterator: it
          element#concat-strings:
            - value#string: test
    - value#equal:
      - value: true
      - value#any: {}
    - value#equal:
      - value: test
      - value#any: {}
    - value#equal:
      - value: 42
      - value#any: {}
    - value#equal:
      - value: 1.5
      - value#any: {}
    - value#equal:
      - value#array:
        - 1
      - value#any: {}
    - value#equal:
      - value#map:
          input#array:
            - value#string: test
          iterator: it
          element#concat-strings:
            - value#string: test
      - value#any: {}
    - value#equal:
      - value#array:
        - value#array:
          - 1
      - value#array:
        - value#array:
          - value#any: {}
    - value#equal:
      - value#object:
          - field1: foo
          - field2: test
          - field3: bar
      - value#object:
          - field1: foo
          - field2#any: {}
          - field3: bar
)");

  // fetch parser
  const auto& parser = variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 14);
  for (unsigned i = 0; i < result_list.Size(); ++i) {
    EXPECT_TRUE(result_list.Get<bool>(i));
  }
}

TEST(TestOperator, TestEval) {
  const auto& parser = variant::GetYamlParser("array", kDefaultRegistry);

  auto full_yaml = formats::yaml::FromString(R"(
    - value#string: the answer
    - value#integer: 42
  )");

  auto any_yaml = formats::yaml::FromString(R"(
      - value#string: the answer
      - value#any: {}
    )");

  auto other_yaml = formats::yaml::FromString(R"(
    - value#string: something
    - value#string: else
  )");

  agl::core::Variant full_op = parser.Parse(full_yaml, kEmptyDeps);
  agl::core::Variant any_op = parser.Parse(any_yaml, kEmptyDeps);
  agl::core::Variant other_op = parser.Parse(other_yaml, kEmptyDeps);

  ExecuterState executer_state;
  auto full = full_op.Evaluate(executer_state);
  auto any = any_op.Evaluate(executer_state);
  auto other = other_op.Evaluate(executer_state);

  EXPECT_TRUE(full.Equals(any));
  EXPECT_FALSE(any.Equals(other));

  agl::core::Variant any_eval = any.Evaluate(executer_state);

  EXPECT_TRUE(any.Equals(any_eval));
  EXPECT_TRUE(full.Equals(any_eval));
  EXPECT_FALSE(any_eval.Equals(other));
}

TEST(TestAnyOperator, TestSwitch) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#switch:
        input#any: {}
        cases:
          - case#string: 'foo'
            value: 'it is a foo'
          - case#string: 'bar'
            value: 'it is a bar'
        default-value#string: 'neither foo nor bar'
    - value#switch:
        input#string: test
        cases:
          - case#string: wrong
            value: 'WRONG!'
          - case#any: {}
            value: 'Correct'
          - case#string: test
            value: 'WRONG!'
        default-value#string: 'NO MATCHES!'
    - value#switch:
        input#object:
          - field1: foo
          - field2: test
          - field3: bar
        cases:
          - case#object:
              - field1: foo
            value: option1
          - case#object:
              - field1: foo
              - field2#any: {}
            value: option2
          - case#object:
              - field1: foo
              - field2#any: {}
              - field3: bar
            value: option3
          - case#object:
              - field1: foo
              - field2: test
              - field3: bar
            value: option4
  )");

  // fetch parser
  const auto& parser = variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ(result_list.Get<std::string>(0), "it is a foo");
  EXPECT_EQ(result_list.Get<std::string>(1), "Correct");
  EXPECT_EQ(result_list.Get<std::string>(2), "option3");
}

}  // namespace agl::core::tests
