#include <userver/formats/bson/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <agl/core/dynamic_config.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/stackable-experiments.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/yaml-helpers.hpp>
#include <agl/modules/manager.hpp>
#include <core/variant/operator-xcommon/errors.hpp>

#include <agl/core/errors.hpp>
#include <experiments3/models/for_lib/cache_manager_full.hpp>

#include "core/default_operators_registry.hpp"
#include "curry_error.hpp"

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

Variant RunXEmptyAndCheck(const std::string& parameter,
                          ExecuterState& executer_state) {
  // build executable
  const auto& parser =
      agl::core::variant::GetYamlParser("xempty", kDefaultRegistry);
  Variant executable = parser.Parse(
      formats::yaml::ValueBuilder(parameter).ExtractValue(), kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());  // fetched value is const
  EXPECT_FALSE(result.IsNone());

  // check the result
  return result;
  // return false;
}

struct TestCase {
  agl::core::Location path_;
  std::string expected_;
};

}  // namespace

TEST(TestOperator, XEmptyTaxiConfig) {
  // prepare executor state routines
  formats::json::ValueBuilder some_config_builder;
  some_config_builder["foo"] = "bar";
  {
    formats::json::ValueBuilder array;
    array.PushBack("0th");
    array.PushBack("1st");
    array.PushBack("2nd");
    some_config_builder["baz"] = array;
  }
  {
    formats::json::ValueBuilder array;
    array.PushBack("single");
    some_config_builder["fffooo"] = array;
  }
  {
    formats::json::ValueBuilder array(formats::json::Type::kArray);
    some_config_builder["bbaarr"] = array;
  }
  auto some_config = some_config_builder.ExtractValue();

  DynamicConfig dynamic_config({{"SOME_CONFIG", some_config}});
  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG", executer_state).AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/foo", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SME_CONFIG", executer_state).AsBool());
  EXPECT_THROW(
      RunXEmptyAndCheck("/taxi-configs2/SOME_CONFIG", executer_state).AsBool(),
      std::runtime_error);
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SME_CONFIG/value", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/fffooo", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/nobbaarr", executer_state)
          .AsBool());

  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-6", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-5", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-4", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-3", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-2", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/-1", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/0", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/1", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/2", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/3", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/4", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/baz/5", executer_state)
          .AsBool());

  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/fffooo/-2", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/fffooo/-1", executer_state)
          .AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/fffooo/0", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/fffooo/1", executer_state)
          .AsBool());

  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/-2", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/-1", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/-0", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/1", executer_state)
          .AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/2", executer_state)
          .AsBool());
}

TEST(TestOperator, XEmptyExperiments) {
  // prepare executer_state
  DynamicConfig dynamic_config;
  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // setup experiment
  formats::json::ValueBuilder exp_value_builder;
  exp_value_builder["foo"] = "bar";
  formats::json::Value exp_value = exp_value_builder.ExtractValue();
  ::experiments3::models::ClientsCache::MappedData experiments{
      {"BAZ", experiments3::models::ExperimentResult{
                  "BAZ", exp_value,
                  experiments3::models::ResultMetaInfo{0, 0, true}}}};
  static const ::experiments3::models::ClientsCache::MappedData kNoConfigsData;

  StackableExperiments stackable_experiments(std::move(experiments),
                                             kNoConfigsData, nullptr);
  ExecuterState::ScopedBinding experiments_binding(stackable_experiments,
                                                   executer_state);

  EXPECT_FALSE(
      RunXEmptyAndCheck("/experiments/BAZ/value", executer_state).AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/experiments/BAZ/value/foo", executer_state).AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/experiments/BAZ/effective", executer_state).AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/experiments/BAA/value", executer_state).AsBool());
  EXPECT_THROW(
      RunXEmptyAndCheck("/experiments/BAZ/vaue", executer_state).AsBool(),
      std::runtime_error);
}

TEST(TestOperator, XEmptyConfigs3) {
  // prepare executer_state
  DynamicConfig dynamic_config;
  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // setup experiment
  formats::json::ValueBuilder exp_value_builder;
  exp_value_builder["foo"] = "bar";
  formats::json::Value exp_value = exp_value_builder.ExtractValue();
  ::experiments3::models::ClientsCache::MappedData configs{
      {"BAZ", experiments3::models::ExperimentResult{
                  "BAZ", exp_value,
                  experiments3::models::ResultMetaInfo{0, 0, true}}}};
  static const ::experiments3::models::ClientsCache::MappedData
      kNoExperimentsData;

  StackableExperiments stackable_configs(kNoExperimentsData, std::move(configs),
                                         nullptr);
  ExecuterState::ScopedBinding configs_binding(stackable_configs,
                                               executer_state);

  EXPECT_FALSE(
      RunXEmptyAndCheck("/configs/BAZ/value", executer_state).AsBool());
  EXPECT_FALSE(
      RunXEmptyAndCheck("/configs/BAZ/value/foo", executer_state).AsBool());
  EXPECT_TRUE(
      RunXEmptyAndCheck("/configs/BAZ/effective", executer_state).AsBool());
  EXPECT_TRUE(RunXEmptyAndCheck("/configs/BAA/value", executer_state).AsBool());
  EXPECT_THROW(RunXEmptyAndCheck("/configs/BAZ/vaue", executer_state).AsBool(),
               std::runtime_error);
}

TEST(TestOperator, XEmptyWithArgs) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xempty:
      path: /taxi-configs/FOO/$path/0
      args:
        path: value
  - value#xempty:
      path: /taxi-configs/FOO/$path
      args:
        path: value/0
  - value#xempty:
      path: /taxi-configs/FOO/value/$index
      args:
        index#xget: /taxi-configs/FOO/default-index
  - value#xempty:
      path: /taxi-configs/FOO/value/$index
      args:
        index#xget:
          path: /taxi-configs/FOO/not-exists
          default-value: 0
  - value#xempty: /taxi-configs/FOO/$$value
)");

  formats::json::ValueBuilder foo_builder;
  foo_builder["default-index"] = 0;
  foo_builder["value"] = formats::json::MakeArray("foo_value");
  foo_builder["$value"] = "foo_$_value";
  agl::core::DynamicConfig dynamic_config(
      {{"FOO", foo_builder.ExtractValue()}});

  const auto& parser = GetYamlParser("array", kDefaultRegistry);
  Variant executable = parser.Parse(yaml, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // execute the operator
  Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());  // fetched value is const
  ASSERT_TRUE(result.IsList());
  const auto& result_array = result.AsList();

  ASSERT_EQ(5, result_array.Size());
  EXPECT_FALSE(result_array[0].AsBool());
  EXPECT_TRUE(result_array[1].AsBool());
  EXPECT_FALSE(result_array[2].AsBool());
  EXPECT_FALSE(result_array[3].AsBool());
  EXPECT_FALSE(result_array[4].AsBool());
}

TEST(TestOperator, XEmptyWithArgsBad_1) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xempty:
      path: /$configs/FOO/value/0
      args:
        configs: taxi-configs)");
  const auto& parser = GetYamlParser("array", kDefaultRegistry);
  EXPECT_THROW(parser.Parse(yaml, kEmptyDeps),
               operator_xcommon::ArgsSubstitutionError);
}

TEST(TestOperator, XEmptyWithArgsBad_2) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xempty:
      path: /taxi-configs/$config/value/0
      args:
        config: FOO)");
  const auto& parser = GetYamlParser("array", kDefaultRegistry);
  EXPECT_THROW(parser.Parse(yaml, kEmptyDeps),
               operator_xcommon::ArgsSubstitutionError);
}

namespace {
class YamlParserBson : public YamlParserBase<YamlParserBson> {
 public:
  template <typename T>
  static void EnsureOperandsValid(T&&, const Deps&) {}

  template <typename T>
  static Variant ParseImpl(const T& operands, const Deps&) {
    if (operands.template As<std::string>() == "path") {
      return formats::bson::ValueBuilder("value").ExtractValue();
    } else {
      return formats::bson::ValueBuilder(0).ExtractValue();
    }
  }
};
}  // namespace

TEST(TestOperator, XEmptyWithArgsBson) {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  r.RegisterOperators({{"bson", std::make_shared<YamlParserBson>()}});
  YamlParser::Deps deps(r, kEmptyModulesManager);
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xempty:
      path: /taxi-configs/FOO/$path/$index
      args:
        path#bson: path
        index#bson: index)");
  const auto& parser = GetYamlParser("array", r);
  const auto& executable = parser.Parse(yaml, deps);

  formats::json::ValueBuilder foo_builder;
  foo_builder["default-index"] = 0;
  foo_builder["value"] = formats::json::MakeArray("foo_value");
  foo_builder["$value"] = "foo_$_value";
  agl::core::DynamicConfig dynamic_config(
      {{"FOO", foo_builder.ExtractValue()}});

  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // execute the operator
  Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());  // fetched value is const
  ASSERT_TRUE(result.IsList());
  const auto& result_array = result.AsList();
  ASSERT_EQ(1, result_array.Size());
  EXPECT_FALSE(result_array[0].AsBool());
}

}  // namespace agl::core::variant::test
