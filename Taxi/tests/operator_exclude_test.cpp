#include <agl/core/variant.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/modules/manager.hpp>

#include <userver/formats/yaml/serialize.hpp>

#include <core/default_operators_registry.hpp>

#include <userver/utest/utest.hpp>

namespace agl::core::tests {

namespace {
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

}  // namespace

TEST(TestOperator, ExcludeKeys) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#exclude:
          object#object:
            - key: key_a
              value#object:
              - key: key_1
                value#string: bingo!
              - key: key_2
                value#string: nope
            - key: key_b
              value#string: nope
            - key: key_c
              value#integer: 42
            - key: key_d
              value#string: ignore
          keys:
            - key_b
            - key_d
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
  EXPECT_NO_THROW(result_list.Get<agl::core::Variant::Map>(0));
  auto result_map = result_list.Get<agl::core::Variant::Map>(0);
  EXPECT_EQ(result_map.Size(), 2);
  auto value_a = result_map.Get<agl::core::Variant::Map>("key_a");
  EXPECT_EQ(value_a.Get<std::string>("key_1"), "bingo!");
  EXPECT_EQ(value_a.Get<std::string>("key_2"), "nope");
  EXPECT_EQ(result_map.Get<int64_t>("key_c"), 42);
  EXPECT_THROW(result_map.Get<std::string>("key_b"), std::runtime_error);
  EXPECT_THROW(result_map.Get<std::string>("key_d"), std::runtime_error);
}

}  // namespace agl::core::tests
