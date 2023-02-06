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

struct TestCase {
  std::string state_;
  std::vector<std::string> expected_keys_;
};

}  // namespace

class KeysMappingHappyPathCases : public ::testing::TestWithParam<TestCase> {};

TEST_P(KeysMappingHappyPathCases, KeysMappingHappyPath) {
  const TestCase& test_case = GetParam();

  static const std::string kOperands = R"(
    rules:
      - condition#boolean: false
        keys:
          - never-possible
          - wont-happen
      - condition#equal:
          - value#xget: /state/current/state
          - value: initial
        keys:
          - handle-start
          - handle-begin
      - condition#equal:
          - value#xget: /state/current/state
          - value: finish
        keys:
          - handle-finish
          - handle-stop
    default-keys:
      - handle-default
  )";

  // build executable
  const variant::YamlParser& parser =
      variant::GetYamlParser("__agl_processing_keys_mapping", kDefaultRegistry);
  const Variant executable =
      parser.Parse(formats::yaml::FromString(kOperands), kEmptyDeps);

  // build mutable state
  ExecuterState executer_state;
  state_manager::State state;
  state.Advance(Variant(Variant::Map().Set("state", test_case.state_)),
                "(none)");
  Binder::ScopedBinding sb(state, executer_state);

  // test default-keys
  Variant keys = executable.Evaluate(executer_state);
  const auto& list = keys.AsList();
  EXPECT_EQ(list.Size(), test_case.expected_keys_.size());
  for (size_t i(0); i < list.Size(); ++i) {
    EXPECT_EQ(list.Get<std::string>(i), test_case.expected_keys_.at(i));
  }
}

INSTANTIATE_TEST_SUITE_P(
    KeysMappingTests, KeysMappingHappyPathCases,
    ::testing::Values(TestCase{"none", {"handle-default"}},
                      TestCase{"initial", {"handle-start", "handle-begin"}},
                      TestCase{"finish", {"handle-finish", "handle-stop"}}));

}  // namespace processing::agl::operators
