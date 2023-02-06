#include <agl/core/constants.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/modules/manager.hpp>
#include <agl/sourcing/operators-registry.hpp>
#include <agl/sourcing/sources-polling-state.hpp>

#include "controller.hpp"
#include "operators/operator-agl-sources-prefetch.hpp"

#include <userver/formats/yaml/serialize.hpp>

#include <core/default_operators_registry.hpp>

#include <userver/utest/utest.hpp>

namespace agl::sourcing::tests {

namespace {
static const core::OperatorsRegistry kDefaultRegistry = [] {
  core::OperatorsRegistry r;
  r.RegisterOperators(core::GetDefaultOperatorsList());
  r.RegisterOperators(GetOperatorList());
  return r;
}();
static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();
static const core::variant::YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                                        kEmptyModulesManager);
}  // namespace

TEST(TestOperator, SourceEnabled) {
  std::vector<std::string> sources{"a", "b", "c"};
  core::ExecuterState executer_state;
  core::variant::YamlParser::Deps parser_deps(kDefaultRegistry,
                                              kEmptyModulesManager);
  parser_deps.GetKeyEncoder("sources").SetKeys(sources);

  SourcesPollingState responses;
  responses.Init(sources.size());
  responses.DisableSource(0);
  responses.DisableSource(2);
  executer_state.RegisterBinding(responses);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#source-enabled: a
    - value#source-enabled: b
    - value#source-enabled: c
  )");

  // fetch parser
  const core::variant::YamlParser& parser =
      core::variant::GetYamlParser("array", kDefaultRegistry);
  core::Variant executable = parser.Parse(ast, parser_deps);
  EXPECT_FALSE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ(result_list.Get<bool>(0), false);
  EXPECT_EQ(result_list.Get<bool>(1), true);
  EXPECT_EQ(result_list.Get<bool>(2), false);
}

TEST(TestOperator, SourceMetricUUID) {
  core::variant::YamlParser::Deps parser_deps(kDefaultRegistry,
                                              kEmptyModulesManager);

  parser_deps.AddContextVariable(agl::core::kResourceMetricTagVariable,
                                 "scope.queue");
  EXPECT_EQ(
      parser_deps.GetContextVariable(agl::core::kResourceMetricTagVariable),
      "scope.queue");

  const auto& yaml = formats::yaml::FromString(R"(
  - id: upstream-src
    resource: upstream
  )");

  // fetch parser
  const core::variant::YamlParser& parser = core::variant::GetYamlParser(
      "agl-sourcing-sources-prefetch", kDefaultRegistry);

  core::Variant executable = parser.Parse(yaml, parser_deps);
  auto exec_operator =
      executable.GetP<std::shared_ptr<core::Variant::Operator>>();
  EXPECT_TRUE(exec_operator);
  EXPECT_TRUE(*exec_operator);
  auto& source_prefetch = dynamic_cast<agl::sourcing::OperatorSourcesPrefetch&>(
      *exec_operator->get());
  auto& controller = source_prefetch.GetController();
  const auto& source = controller.GetSource(0);

  EXPECT_EQ(source.ResourceUUID(), "scope.queue.upstream");
  EXPECT_EQ(source.FallbackName(), "resource.scope.queue.upstream.fallback");
}

}  // namespace agl::sourcing::tests
