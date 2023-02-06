#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/modules/manager.hpp>

#include <agl/operators/state_manager/state.hpp>
#include <agl/operators_registry.hpp>

#include <userver/formats/yaml/serialize.hpp>

using namespace ::agl::core;

namespace processing::agl::operators {

namespace {

static const OperatorsRegistry kDefaultRegistry = [] {
  OperatorsRegistry r = OperatorsRegistry::BuiltinOperators();
  r.RegisterOperators(GetProcessingOperatorsList());
  return r;
}();

static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();

static const variant::YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                                  kEmptyModulesManager);

}  // namespace

TEST(TestOperator, StateManagerHappyPath) {
  using namespace ::processing::agl::operators;

  static const std::vector<std::pair<std::string, std::string>> kExpected{
      {"foo", "nope"},  // initial
      {"bar", "nope"},  // first step
      {"baz", "foo"},   // second step
      {"qux", "bar"},   // third step
      {"qux", "bar"},   // all next steps
      {"qux", "bar"},   // all next steps
  };

  static const std::string kOperands = R"(
    initial:
      status: foo
      prev_status: nope
    
    mutators:
      - name: foo-to-bar
        condition#equal:
          - value#xget: /state/current/status
          - value#string: foo
        effects#object:
            - key: status
              value#string: bar
      - name: bar-to-baz
        condition#equal:
          - value#xget: /state/current/status
          - value#string: bar
        effects:
            status: baz
            prev_status#xget: /state/previous/status
      - name: baz-to-qux
        condition#equal:
          - value#xget: /state/current/status
          - value#string: baz
        effects:
            status: qux
            prev_status#xget: /state/previous/status

  )";

  // build executable
  const variant::YamlParser& parser = variant::GetYamlParser(
      "__agl_processing_state_manager", kDefaultRegistry);
  const Variant executable =
      parser.Parse(formats::yaml::FromString(kOperands), kEmptyDeps);

  // build mutable state
  ExecuterState executer_state;
  state_manager::State state;

  // perform steps
  for (const auto& expected : kExpected) {
    Binder::ScopedBinding sb(state, executer_state);
    Variant next_state = executable.Evaluate(executer_state);

    EXPECT_TRUE(next_state.IsMap());
    const auto& map = next_state.AsMap();
    EXPECT_EQ(map.Get<std::string>("status"), expected.first);
    EXPECT_EQ(map.Get<std::string>("prev_status"), expected.second);

    state.Advance(std::move(next_state), "(none)");
  }
}

}  // namespace processing::agl::operators
