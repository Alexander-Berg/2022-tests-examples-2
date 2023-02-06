#include <userver/formats/bson/value_builder.hpp>

#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <agl/core/dynamic_config.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/stackable-experiments.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/yaml-helpers.hpp>
#include <agl/modules/manager.hpp>
#include <core/variant/operator-xcommon/errors.hpp>

#include <experiments3/models/for_lib/cache_manager_full.hpp>

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

Variant RunXGetAndCheck(const std::string& parameter,
                        ExecuterState& executer_state) {
  // build executable
  const auto& parser =
      agl::core::variant::GetYamlParser("xget", kDefaultRegistry);
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
}

struct TestCase {
  agl::core::Location path_;
  std::string expected_;
};

}  // namespace

TEST(TestOperator, XGetTaxiConfig) {
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

  EXPECT_EQ(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG", executer_state).AsJson(),
      some_config);
  EXPECT_EQ(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/foo", executer_state).AsJson(),
      some_config["foo"]);
  EXPECT_EQ(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz", executer_state).AsJson(),
      some_config["baz"]);
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/fffooo", executer_state)
                .AsJson(),
            some_config["fffooo"]);
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr", executer_state)
                .AsJson(),
            some_config["bbaarr"]);

  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-6", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-5", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-4", executer_state),
      std::runtime_error);
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-3", executer_state)
                .AsJson()
                .As<std::string>(),
            "0th");
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-2", executer_state)
                .AsJson()
                .As<std::string>(),
            "1st");
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/-1", executer_state)
                .AsJson()
                .As<std::string>(),
            "2nd");
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/0", executer_state)
                .AsJson()
                .As<std::string>(),
            "0th");
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/1", executer_state)
                .AsJson()
                .As<std::string>(),
            "1st");
  EXPECT_EQ(RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/2", executer_state)
                .AsJson()
                .As<std::string>(),
            "2nd");
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/3", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/4", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/baz/5", executer_state),
      std::runtime_error);

  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/fffooo/-2", executer_state),
      std::runtime_error);
  EXPECT_EQ(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/fffooo/-1", executer_state)
          .AsJson()
          .As<std::string>(),
      "single");
  EXPECT_EQ(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/fffooo/0", executer_state)
          .AsJson()
          .As<std::string>(),
      "single");
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/fffooo/1", executer_state),
      std::runtime_error);

  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/-2", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/-1", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/0", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/1", executer_state),
      std::runtime_error);
  EXPECT_THROW(
      RunXGetAndCheck("/taxi-configs/SOME_CONFIG/bbaarr/2", executer_state),
      std::runtime_error);
}

TEST(TestOperator, XGetExperiments) {
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

  EXPECT_EQ(RunXGetAndCheck("/experiments/BAZ/value", executer_state).AsJson(),
            exp_value);
  EXPECT_EQ(
      RunXGetAndCheck("/experiments/BAZ/value/foo", executer_state).AsJson(),
      exp_value["foo"]);
  EXPECT_TRUE(
      RunXGetAndCheck("/experiments/BAZ/effective", executer_state).AsBool());
  EXPECT_FALSE(
      RunXGetAndCheck("/experiments/BAT/effective", executer_state).IsNone());

  Variant::Map map =
      RunXGetAndCheck("/experiments/BAZ", executer_state).AsMap();
  EXPECT_EQ(map.Get<agl::core::variant::io::JsonPromise>("value").AsJson(),
            exp_value);
  EXPECT_TRUE(map.Get<bool>("effective"));
}

TEST(TestOperator, XGetConfigs) {
  // prepare executer_state
  DynamicConfig dynamic_config;
  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // setup experiment
  formats::json::ValueBuilder config_value_builder;
  config_value_builder["foo"] = "bar";
  formats::json::Value config_value = config_value_builder.ExtractValue();
  ::experiments3::models::ClientsCache::MappedData configs{
      {"BAZ", experiments3::models::ExperimentResult{
                  "BAZ", config_value,
                  experiments3::models::ResultMetaInfo{0, 0, true}}}};

  static const ::experiments3::models::ClientsCache::MappedData
      kNoExperimentsData;

  StackableExperiments stackable_experiments(kNoExperimentsData,
                                             std::move(configs), nullptr);
  ExecuterState::ScopedBinding experiments_binding(stackable_experiments,
                                                   executer_state);

  EXPECT_EQ(RunXGetAndCheck("/configs/BAZ/value", executer_state).AsJson(),
            config_value);
  EXPECT_EQ(RunXGetAndCheck("/configs/BAZ/value/foo", executer_state).AsJson(),
            config_value["foo"]);
  EXPECT_TRUE(
      RunXGetAndCheck("/configs/BAZ/effective", executer_state).AsBool());

  Variant::Map map = RunXGetAndCheck("/configs/BAZ", executer_state).AsMap();
  EXPECT_EQ(map.Get<agl::core::variant::io::JsonPromise>("value").AsJson(),
            config_value);
  EXPECT_TRUE(map.Get<bool>("effective"));
}

class XGetNestedDeps : public ::testing::TestWithParam<TestCase> {};

UTEST_P(XGetNestedDeps, XGetNestedDependecies) {
  TestCase params = GetParam();

  // prepare element elements with inner structure
  formats::json::ValueBuilder foo;
  formats::json::ValueBuilder baz;
  formats::json::ValueBuilder bar;

  {
    formats::json::ValueBuilder foo_a;
    foo_a["foo_b"] = "42";
    foo["foo_a"] = foo_a;
  }

  {
    formats::json::ValueBuilder baz_a;
    baz_a["a"] = "test";
    baz.PushBack(std::move(baz_a));
  }

  {
    formats::json::ValueBuilder bar_a;
    bar_a.PushBack("123");
    bar.PushBack(std::move(bar_a));
  }

  // parse test config
  const formats::yaml::Value ast =
      formats::yaml::FromString(fmt::format(R"(
  test-field#xget:
      path: {}
      default-value#concat-strings:
        - value#xget: /taxi-configs/BAZ/0/a
        - value#string: ', '
        - value#xget: /taxi-configs/BAR/0/0
  )",
                                            params.path_.GetPath()));
  ParserContext parser_deps(kDefaultRegistry, kEmptyModulesManager);
  auto op_fields = GetOperatedFields(ast);
  Variant parsed = GetOperatorAndParse(
      Require(op_fields, "test-field", agl::core::Location("")), parser_deps);

  // prepare executer_state
  DynamicConfig dynamic_config({{"FOO", foo.ExtractValue()},
                                {"BAZ", baz.ExtractValue()},
                                {"BAR", bar.ExtractValue()}});
  ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // try evaluate
  Variant result = parsed.Evaluate(executer_state);
  EXPECT_EQ(result.AsString(), params.expected_);

  // check dependecies evaluation
  Dependencies deps;
  EXPECT_NO_THROW(parsed.GetDependencies(deps));
  EXPECT_TRUE(deps.FullPath().IsEmpty());
}

INSTANTIATE_UTEST_SUITE_P(
    XGetNestedDependecies, XGetNestedDeps,
    ::testing::Values(
        TestCase{agl::core::Location("/taxi-configs/FOO/foo_a/foo_b"), "42"},
        TestCase{
            agl::core::Location("/taxi-configs/FOO/foo_a/foo_b/not-exists"),
            "test, 123"}));

TEST(TestOperator, XGetWithArgs) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xget:
      path: /taxi-configs/FOO/$path/0
      args:
        path: value
  - value#xget:
      path: /taxi-configs/FOO/$path
      args:
        path: value/0
      default-value: 'Wont work like that'
  - value#xget:
      path: /taxi-configs/FOO/value/$index
      args:
        index#xget: /taxi-configs/FOO/default-index
  - value#xget:
      path: /taxi-configs/FOO/value/$index
      args:
        index#xget:
          path: /taxi-configs/FOO/not-exists
          default-value: 0
  - value#xget: /taxi-configs/FOO/$$value
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
  EXPECT_EQ("foo_value", result_array[0].AsString());
  EXPECT_EQ("Wont work like that", result_array[1].AsString());
  EXPECT_EQ("foo_value", result_array[2].AsString());
  EXPECT_EQ("foo_value", result_array[3].AsString());
  EXPECT_EQ("foo_$_value", result_array[4].AsString());
}

TEST(TestOperator, XGetWithArgsBad_1) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xget:
      path: /$configs/FOO/value/0
      args:
        configs: taxi-configs)");
  const auto& parser = GetYamlParser("array", kDefaultRegistry);
  EXPECT_THROW(parser.Parse(yaml, kEmptyDeps),
               operator_xcommon::ArgsSubstitutionError);
}

TEST(TestOperator, XGetWithArgsBad_2) {
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xget:
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

TEST(TestOperator, XGetWithArgsBson) {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  r.RegisterOperators({{"bson", std::make_shared<YamlParserBson>()}});
  YamlParser::Deps deps(r, kEmptyModulesManager);
  const auto& yaml = formats::yaml::FromString(R"(
  - value#xget:
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

  // execute the operator``
  Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());  // fetched value is const
  ASSERT_TRUE(result.IsList());
  const auto& result_array = result.AsList();
  ASSERT_EQ(1, result_array.Size());
  EXPECT_EQ("foo_value", result_array[0].AsString());
}

}  // namespace agl::core::variant::test
