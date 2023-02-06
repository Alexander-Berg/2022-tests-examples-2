#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>

#include "core/default_operators_registry.hpp"

namespace agl::core::variant::test {

namespace {
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

Variant ParseAndExec(const OperatedFields& fields, const std::string& field) {
  ParserContext deps(kDefaultRegistry, kEmptyModulesManager);
  Variant parsed = GetOperatorAndParse(
      Require(fields, field, agl::core::Location("")), deps);
  core::ExecuterState executer_state;
  return parsed.Evaluate(executer_state);
}
}  // namespace

TEST(TestOperator, Regex) {
  auto yaml = formats::yaml::FromString(R"(
    foo#regex:
        pattern: "^([^_]+)_(.+)$"
        value#string: "643753730233_c136a920a0b543a3bf4268283b910cbc"
    bar#regex:
        pattern: "^([^_]+)_(.+)$"
        value#string: ""
    baz#regex:
        pattern: "^([^_]+)_(.+)$"
        value#string: "notmatched"
    fail#regex:
        pattern: "^([^_]+)_(.+)$"
        value#number: 42
  )");

  auto fields = core::GetOperatedFields(yaml);

  {
    Variant result = ParseAndExec(fields, "foo");
    EXPECT_TRUE(result.IsList());

    const Variant::List& list = result.AsList();
    EXPECT_EQ(list.Size(), 2);
    EXPECT_EQ(list[0].AsString(), "643753730233");
    EXPECT_EQ(list[1].AsString(), "c136a920a0b543a3bf4268283b910cbc");
  }

  {
    core::Variant result = ParseAndExec(fields, "bar");
    EXPECT_TRUE(result.IsNone());
  }

  {
    core::Variant result = ParseAndExec(fields, "baz");
    EXPECT_TRUE(result.IsNone());
  }

  { EXPECT_THROW(ParseAndExec(fields, "fail"), std::runtime_error); }
}
}  // namespace agl::core::variant::test
