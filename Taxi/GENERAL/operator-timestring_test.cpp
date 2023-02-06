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

const auto kTimepoint = std::chrono::system_clock::from_time_t(1535749201);

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
    aliases.Register("sample-datetime",
                     formats::bson::ValueBuilder(kTimepoint).ExtractValue());
    executer_state.RegisterBinding(aliases);
  }
};
}  // namespace

TEST(TestOperator, TimestringCustom) {
  const auto& parser = GetYamlParser("timestring", kDefaultRegistry);
  auto value = formats::yaml::FromString(R"(
      timestamp#xget: /aliases/sample-datetime
      format: "%Y-%m-%dTTTT%H:%M%S"
  )");
  Variant parsed = parser.Parse(value, kEmptyDeps);
  TestExecuterState test_executer_state;
  Variant result = parsed.Evaluate(test_executer_state.executer_state);
  std::string expected = utils::datetime::Timestring(
      kTimepoint, utils::datetime::kDefaultTimezone, "%Y-%m-%dTTTT%H:%M%S");
  EXPECT_EQ(result.AsString(), expected);
}

TEST(TestOperator, TimestringDefault) {
  const auto& parser = GetYamlParser("timestring", kDefaultRegistry);
  auto value = formats::yaml::FromString(R"(
      timestamp#xget: /aliases/sample-datetime
  )");
  Variant parsed = parser.Parse(value, kEmptyDeps);
  TestExecuterState test_executer_state;
  Variant result = parsed.Evaluate(test_executer_state.executer_state);
  std::string expected = utils::datetime::Timestring(kTimepoint);
  EXPECT_EQ(result.AsString(), expected);
}

}  // namespace agl::core::variant::test
