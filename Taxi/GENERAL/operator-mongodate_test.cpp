#include <userver/utest/utest.hpp>

#include <agl/core/aliases.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>
#include <userver/formats/bson/value.hpp>
#include <userver/formats/bson/value_builder.hpp>

#include "core/default_operators_registry.hpp"

namespace agl::core::variant::test {

const auto kTimepoint = std::chrono::system_clock::from_time_t(1630471241);
const std::string kTimestring = "2021-09-01T07:40:41+0300";

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

namespace {
struct TestExecuterState {
  Aliases aliases;
  ExecuterState executer_state;

  TestExecuterState() {
    aliases.Register("sample-timestring", kTimestring);
    executer_state.RegisterBinding(aliases);
  }
};
}  // namespace

TEST(TestOperator, Mongodate) {
  const auto& parser = GetYamlParser("mongodate", kDefaultRegistry);
  auto value = formats::yaml::FromString(R"(
      timestring#xget: /aliases/sample-timestring
  )");
  Variant parsed = parser.Parse(value, kEmptyDeps);
  TestExecuterState test_executer_state;
  Variant result = parsed.Evaluate(test_executer_state.executer_state);

  const auto* bson = result.GetP<formats::bson::Value>();
  EXPECT_NE(bson, nullptr);

  formats::bson::ValueBuilder expected(kTimepoint);
  EXPECT_EQ(*bson, expected.ExtractValue());
}

}  // namespace agl::core::variant::test
