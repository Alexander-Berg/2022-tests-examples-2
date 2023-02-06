#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>

#include "core/default_operators_registry.hpp"

namespace agl::core::variant::test {

static const OperatorsRegistry kDefaultRegistry = [] {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  return r;
}();
static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();
static const YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                         kEmptyModulesManager);

TEST(TestOperator, AliasHappyPath) {
  const auto& store_parser = GetYamlParser("agl-aliases", kDefaultRegistry);

  // prepare arguments for alias storage
  const formats::yaml::Value store_operands = formats::yaml::FromString(R"(
    alias_hello_world#string: "Hello world"
    alias_false#not:
        value#boolean: true
    alias_ref#xget: /aliases/alias_hello_world
  )");

  Variant alias_operator = store_parser.Parse(store_operands, kEmptyDeps);
  EXPECT_FALSE(alias_operator.IsConstant());

  // setup alias storage
  ExecuterState executer_state;
  alias_operator.Evaluate(executer_state);
  EXPECT_FALSE(alias_operator.IsConstant());

  // eval aliases by it names
  const auto& parser = GetYamlParser("xget", kDefaultRegistry);
  Variant expr =
      parser.Parse(formats::yaml::FromString("/aliases"), kEmptyDeps);
  EXPECT_FALSE(expr.IsConstant());

  Variant result = expr.Evaluate(executer_state);
  const auto& map = result.AsMap();
  EXPECT_EQ(map.Size(), 3);
  EXPECT_EQ(map.Get<std::string>("alias_hello_world"), "Hello world");
  EXPECT_EQ(map.Get<bool>("alias_false"), false);
  EXPECT_EQ(map.Get<std::string>("alias_ref"),
            map.Get<std::string>("alias_hello_world"));
}

class AliasSadPathCases : public ::testing::TestWithParam<std::string> {};

TEST_P(AliasSadPathCases, AliasSadPath) {
  const std::string& sad_case = GetParam();

  const auto& store_parser = GetYamlParser("agl-aliases", kDefaultRegistry);

  EXPECT_THROW(
      store_parser.Parse(formats::yaml::FromString(sad_case), kEmptyDeps),
      std::runtime_error);
}

static const std::string kSadPathCases[] = {
    "foo#xget: /aliases",
    "foo#xget: /aliases/foo",
    R"(
    foo#xget: /aliases/bar
    bar#xget: /aliases/foo
  )",
    R"(
    bar#xget: /aliases/foo
    foo#xget: /aliases/bar
  )",
    R"(
    foo#xget: /aliases/bar
    bar#xget: /aliases/baz
    baz#xget: /aliases/foo
  )",
};

INSTANTIATE_TEST_SUITE_P(AliasSadPaths, AliasSadPathCases,
                         ::testing::ValuesIn(kSadPathCases));

}  // namespace agl::core::variant::test
