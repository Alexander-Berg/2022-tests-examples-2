#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
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

TEST(TestOperator, Uuid4) {
  const auto& parser = GetYamlParser("uuid4", kDefaultRegistry);

  agl::core::Variant uuid_operator =
      parser.Parse(formats::yaml::Value(), kEmptyDeps);
  EXPECT_FALSE(uuid_operator.IsConstant());

  ExecuterState executer_state;
  agl::core::Variant result = uuid_operator.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  const auto& uuid = result.AsString();
  EXPECT_EQ(uuid.size(), 32U);
  result = uuid_operator.Evaluate(executer_state);

  // every time new uuid
  EXPECT_NE(uuid, uuid_operator.Evaluate(executer_state).AsString());
}
}  // namespace agl::core::variant::test
