#include <core/default_operators_registry.hpp>

#include <userver/formats/bson.hpp>
#include <userver/formats/serialize/common_containers.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/utest/utest.hpp>

#include <agl/core/dynamic_config.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/io/encoded-string.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>

#include <boost/algorithm/string.hpp>

namespace agl::core::tests {

namespace {

struct CustomValues : std::unordered_map<std::string, Variant> {
  using std::unordered_map<std::string, Variant>::unordered_map;
};

class OperatorCustomValue : public Variant::Operator {
 public:
  Variant EvaluateImpl(ExecuterState& executer_state) const override {
    return executer_state.Binding<CustomValues>().at(custom_id_);
  }
  void GetDependencies(variant::Dependencies&) const override {}
  bool IsConstant() const override { return false; }

 public:
  explicit OperatorCustomValue(const agl::core::Location& location,
                               const std::string& config_id)
      : Operator(location), custom_id_(config_id) {}

 private:
  std::string custom_id_;
};

class YamlParserCustomValue
    : public variant::YamlParserBase<YamlParserCustomValue> {
 public:
  template <typename JsonOrYaml>
  static void EnsureOperandsValid(JsonOrYaml&& operands,
                                  const variant::ParserContext& /*context*/) {
    if (!operands.IsString()) {
      throw ParseError("expected a string", GetLocation(operands));
    }
  }
  template <typename Value>
  static Variant ParseImpl(const Value& operands, const Deps&) {
    return std::make_shared<OperatorCustomValue>(
        agl::core::GetLocation(operands), operands.template As<std::string>());
  }
};

static const OperatorsRegistry kDefaultRegistry = [] {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  r.RegisterOperators({{"custom", std::make_shared<YamlParserCustomValue>()}});
  return r;
}();
static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();
static const variant::YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                                  kEmptyModulesManager);

}  // namespace

TEST(TestOperator, Null) {
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("null", kDefaultRegistry);

  agl::core::Variant executable =
      parser.Parse(formats::yaml::Value(), kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_TRUE(result.IsNone());
}

namespace {

template <typename T>
T ScalarGetter(const agl::core::Variant&) {
  return T();
}
template <>
bool ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsBool();
}
template <>
int64_t ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsInt();
}
template <>
double ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsDouble();
}
template <>
std::string ScalarGetter<>(const agl::core::Variant& v) {
  return v.AsString();
}

template <typename T>
void TestOperatorPodHelper(const std::string operator_id, T value) {
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser(operator_id, kDefaultRegistry);

  agl::core::Variant executable = parser.Parse(
      formats::yaml::ValueBuilder(value).ExtractValue(), kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());
  EXPECT_EQ(ScalarGetter<T>(result), value);
}
}  // namespace

TEST(TestOperator, Pods) {
  TestOperatorPodHelper<bool>("boolean", true);
  TestOperatorPodHelper<bool>("boolean", false);
  TestOperatorPodHelper<int64_t>("integer", 0);
  TestOperatorPodHelper<int64_t>("integer", 1234);
  TestOperatorPodHelper<double>("real", 0);
  TestOperatorPodHelper<double>("real", 2.7182818284);
  TestOperatorPodHelper<std::string>("string", std::string());
  TestOperatorPodHelper<std::string>("string", "test string");
}

TEST(TestOperator, Array) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#boolean: false
    - value#integer: 18
    - value#string: test line
    - value#integer: 145
      enabled#boolean: false
    - value#real: 3.1415
    - value#null:
    - value#array:
      - value#integer: 127
      - value#integer: 0
      - value#integer: 0
      - value#integer: 1
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_EQ(result_list.Get<bool>(0), false);
  EXPECT_EQ(result_list.Get<int64_t>(1), 18);
  EXPECT_EQ(result_list.Get<std::string>(2), "test line");
  EXPECT_EQ(result_list.Get<double>(3), 3.1415);
  EXPECT_EQ(result_list.Get<agl::core::Variant::None>(4),
            agl::core::Variant::None());
  EXPECT_TRUE(result_list.IsNone(4));

  agl::core::Variant::List nested_list =
      result_list.Get<agl::core::Variant::List>(5);
  EXPECT_EQ(nested_list.Size(), 4);
  EXPECT_EQ(nested_list.Get<int64_t>(0), 127);
  EXPECT_EQ(nested_list.Get<int64_t>(1), 0);
  EXPECT_EQ(nested_list.Get<int64_t>(2), 0);
  EXPECT_EQ(nested_list.Get<int64_t>(3), 1);
}

TEST(TestOperator, ArraySimple) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - false
    - 18
    - test line
    - value#integer: 145
      enabled#boolean: false
    - value: 256
    - value: 367
      enabled: true
    - 3.1415
    - value#with#sharps#
    - null
    -
      - 127
      - 0
      - 0
      - 1
    - key1: val1
      key2: val2
    - value:
        value: 17
)");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 11);
  EXPECT_EQ(result_list.Get<bool>(0), false);
  EXPECT_EQ(result_list.Get<int64_t>(1), 18);
  EXPECT_EQ(result_list.Get<std::string>(2), "test line");
  EXPECT_EQ(result_list.Get<int64_t>(3), 256);
  EXPECT_EQ(result_list.Get<int64_t>(4), 367);
  EXPECT_EQ(result_list.Get<double>(5), 3.1415);
  EXPECT_EQ(result_list.Get<std::string>(6), "value#with#sharps#");
  EXPECT_EQ(result_list.Get<agl::core::Variant::None>(7),
            agl::core::Variant::None());
  EXPECT_TRUE(result_list.IsNone(7));

  agl::core::Variant::List nested_list =
      result_list.Get<agl::core::Variant::List>(8);
  EXPECT_EQ(nested_list.Size(), 4);
  EXPECT_EQ(nested_list.Get<int64_t>(0), 127);
  EXPECT_EQ(nested_list.Get<int64_t>(1), 0);
  EXPECT_EQ(nested_list.Get<int64_t>(2), 0);
  EXPECT_EQ(nested_list.Get<int64_t>(3), 1);

  agl::core::Variant::Map nested_map =
      result_list.Get<agl::core::Variant::Map>(9);
  EXPECT_EQ(nested_map.Size(), 2);
  EXPECT_EQ(nested_map.Get<std::string>("key1"), "val1");
  EXPECT_EQ(nested_map.Get<std::string>("key2"), "val2");

  agl::core::Variant::Map exotic_map =
      result_list.Get<agl::core::Variant::Map>(10);
  EXPECT_EQ(exotic_map.Size(), 1);
  EXPECT_EQ(exotic_map.Get<int64_t>("value"), 17);
}

TEST(TestOperator, Object) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - key: true value
      value#boolean: true
    - key: some integer
      value#integer: 42
    - key: string value
      value#string: test line
    - simple key1: simple val1
    - simple_key2#real: 3.141592
    - simple_key3: simple_val3
      enabled: false
    - key: won't be created
      value#integer: 145
      enabled#boolean: false
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("object", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsMap());
  agl::core::Variant::Map result_map = result.AsMap();
  EXPECT_EQ(result_map.Size(), 5);
  EXPECT_EQ(result_map.Get<bool>("true value"), true);
  EXPECT_EQ(result_map.Get<int64_t>("some integer"), 42);
  EXPECT_EQ(result_map.Get<std::string>("string value"), "test line");
  EXPECT_EQ(result_map.Get<std::string>("simple key1"), "simple val1");
  EXPECT_EQ(result_map.Get<double>("simple_key2"), 3.141592);
  EXPECT_THROW(result_map.Get<std::string>("simple_key3"), std::runtime_error);
  EXPECT_THROW(result_map.Get<std::string>("won't be created"),
               std::runtime_error);
}

TEST(TestOperator, ObjectEvaluated) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#get:
          object#object:
            - key: ok
              value#string: 200
            - key#string: 200
              value: ok
          key#string: ok
    - value#get:
          object#object:
            - key: ok
              value#string: 200
            - key#string: 200
              value: ok
          key#string: 200
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<std::string>(0), "200");
  EXPECT_EQ(result_list.Get<std::string>(1), "ok");
}

TEST(TestOperator, ObjectSimple) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    true_value: true
    some_integer: 42
    string_value: test line
    key with op#real: 3.141592
    value: 17
    enabled: false
    nested:
      key1: val1
      key2: val2
      key3#object:
        - key: old_key1
          value: old_val1
        - key: old_key2
          value: old_val2
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("object_simple", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsMap());
  agl::core::Variant::Map result_map = result.AsMap();
  EXPECT_EQ(result_map.Size(), 7);
  EXPECT_EQ(result_map.Get<bool>("true_value"), true);
  EXPECT_EQ(result_map.Get<int64_t>("some_integer"), 42);
  EXPECT_EQ(result_map.Get<std::string>("string_value"), "test line");
  EXPECT_EQ(result_map.Get<double>("key with op"), 3.141592);
  EXPECT_EQ(result_map.Get<int64_t>("value"), 17);
  EXPECT_EQ(result_map.Get<bool>("enabled"), false);

  agl::core::Variant::Map nested_map_1 =
      result_map.Get<agl::core::Variant::Map>("nested");
  EXPECT_EQ(nested_map_1.Size(), 3);
  EXPECT_EQ(nested_map_1.Get<std::string>("key1"), "val1");
  EXPECT_EQ(nested_map_1.Get<std::string>("key2"), "val2");

  agl::core::Variant::Map nested_map_2 =
      nested_map_1.Get<agl::core::Variant::Map>("key3");
  EXPECT_EQ(nested_map_2.Size(), 2);
  EXPECT_EQ(nested_map_2.Get<std::string>("old_key1"), "old_val1");
  EXPECT_EQ(nested_map_2.Get<std::string>("old_key2"), "old_val2");
}

TEST(TestOperator, TaxiConfig) {
  // prepare executor state routines
  formats::json::ValueBuilder some_config_builder(std::string("some value"));
  auto some_config = some_config_builder.ExtractValue();

  agl::core::DynamicConfig dynamic_config({{"SOME_CONFIG", some_config}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // build executable
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("taxi-config", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(
      formats::yaml::ValueBuilder("SOME_CONFIG").ExtractValue(), kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // not const (depend on taxi-config)
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());  // fetched taxi-config value is const
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_EQ(result.AsJson(), some_config);
}

TEST(TestOperator, GetMap) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#get:
        object#get:
          object#object:
            - key: key_a
              value#object:
              - key: key_1
                value#string: bingo!
              - key: key_2
                value#string: nope
            - key: key_b
              value#string: nope
          key#string: key_a
        key#string: key_1
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  EXPECT_EQ(result_list.Get<std::string>(0), "bingo!");
}

UTEST(TestOperator, GetJson) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kObject);
  some_config_builder["key_a"] = std::string("nope");
  some_config_builder["key_b"] = std::string("bingo!");

  agl::core::DynamicConfig dynamic_config(
      {{"TEST_SAMPLE", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#get:
        object#taxi-config: TEST_SAMPLE
        key#string: key_b
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  auto result_json = result_list.Get<agl::core::variant::io::JsonPromise>(0);
  EXPECT_TRUE(result_json.AsJson().IsString());
  EXPECT_EQ(result_json.AsJson().As<std::string>(), "bingo!");
  EXPECT_EQ(result_json.AsString().data, "\"bingo!\"");
}

TEST(TestOperator, GetMapWithDef) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#get:
        object#object:
          - key: key_a
            value#string: nope
          - key: key_b
            value#string: nope
        key#string: key_c
        default-value#string: bingo!
        default-key#string: not-existing-key
    - value#get:
        object#object:
          - key: key_a
            value#string: nope
          - key: key_b
            value#string: nope
          - key: __default__
            value#string: bingo!
        key#string: key_c
        default-key#string: __default__
        default-value#string: nope
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<std::string>(0), "bingo!");
  EXPECT_EQ(result_list.Get<std::string>(1), "bingo!");
}

TEST(TestOperator, GetJsonWithDef) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kObject);
  some_config_builder["key_a"] = std::string("nope");
  some_config_builder["key_b"] = std::string("bingo!");
  some_config_builder["__default__"] = std::string("another bingo!");

  agl::core::DynamicConfig dynamic_config(
      {{"TEST_SAMPLE", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#get:
        object#taxi-config: TEST_SAMPLE
        key#string: key_c
        default-key#string: not-existing-key
        default-value#string: bingo!
    - value#get:
        object#taxi-config: TEST_SAMPLE
        key#string: key_c
        default-key#string: __default__
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<std::string>(0), "bingo!");
  EXPECT_EQ(
      result_list.Get<variant::io::JsonPromise>(1).AsJson().As<std::string>(),
      "another bingo!");
}

TEST(TestOperator, ContainsMap) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#contains:
        object#object:
          - key: key_a
            value#integer: 0
          - key: key_b
            value#string: nope
        key#string: key_a
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  EXPECT_TRUE(result_list.Get<bool>(0));
}

TEST(TestOperator, ContainsList) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
        object#array:
          - value#string: key_a
          - value#string: nope
        key#string: key_a
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("contains", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsBool());
  EXPECT_TRUE(result.AsBool());
}

TEST(TestOperator, ContainsJson) {
  using namespace formats::json;

  // prepare taxi-config (as a source of raw JSON)
  ValueBuilder some_array_builder(Type::kArray);
  some_array_builder.PushBack("card");
  some_array_builder.PushBack("apple");
  some_array_builder.PushBack("google");
  some_array_builder.PushBack("");

  auto some_config_builder = ValueBuilder(Type::kObject);
  some_config_builder["key_a"] = std::string("nope");
  some_config_builder["key_b"] = std::string("bingo!");

  auto keys_object_builder = ValueBuilder(Type::kObject);
  keys_object_builder["key_1"] = std::string("key_u");
  keys_object_builder["key_2"] = std::string("key_b");

  agl::core::DynamicConfig dynamic_config({
      {"TEST_SAMPLE", some_config_builder.ExtractValue()},
      {"TEST_ARRAY", some_array_builder.ExtractValue()},
      {"KEY_VALUE", ValueBuilder("apple").ExtractValue()},
      {"KEY_VALUE_2", ValueBuilder("not-exists").ExtractValue()},
      {"KEYS_OBJECT", keys_object_builder.ExtractValue()},
  });
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#contains:
        object#taxi-config: TEST_SAMPLE
        key#string: key_b
    - value#contains:
        object#taxi-config: TEST_SAMPLE
        key#string: key_u
    - value#contains:
        object#taxi-config: TEST_ARRAY
        key#string: apple
    - value#contains:
        object#taxi-config: TEST_ARRAY
        key#string: corp
    - value#contains:
        object#taxi-config: TEST_ARRAY
        key#taxi-config: KEY_VALUE
    - value#contains:
        object#taxi-config: TEST_ARRAY
        key#taxi-config: KEY_VALUE_2
    - value#contains:
        object#taxi-config: TEST_SAMPLE
        key#xget: /taxi-configs/KEYS_OBJECT/key_2
    - value#contains:
        object#taxi-config: TEST_SAMPLE
        key#get:
            object#taxi-config: KEYS_OBJECT
            key#string: key_1
    - value#contains:
        object#taxi-config: TEST_ARRAY
        key#string: ""
    - value#contains:
        object#taxi-config: TEST_SAMPLE
        key#string: ""
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 10);
  EXPECT_TRUE(result_list.Get<bool>(0));
  EXPECT_FALSE(result_list.Get<bool>(1));
  EXPECT_TRUE(result_list.Get<bool>(2));
  EXPECT_FALSE(result_list.Get<bool>(3));
  EXPECT_TRUE(result_list.Get<bool>(4));
  EXPECT_FALSE(result_list.Get<bool>(5));
  EXPECT_TRUE(result_list.Get<bool>(6));
  EXPECT_FALSE(result_list.Get<bool>(7));
  EXPECT_TRUE(result_list.Get<bool>(8));
  EXPECT_FALSE(result_list.Get<bool>(9));
}

UTEST(TestOperator, MapMap) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#map:
        input#array:
          - value#string: Linus
          - value#string: Denis
          - value#string: Richard
          - value#string: Bill
            enabled#boolean: false
        iterator: it
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it
          - value#string: "!"
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  agl::core::Variant::List mapped =
      result_list.Get<agl::core::Variant::List>(0);
  EXPECT_EQ(mapped.Size(), 3);
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello Linus!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello Denis!");
  EXPECT_EQ(mapped.Get<std::string>(2), "Hello Richard!");
}

UTEST(TestOperator, MapJson) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kArray);
  some_config_builder.PushBack(std::string("Kirk"));
  some_config_builder.PushBack(std::string("Spock"));
  some_config_builder.PushBack(std::string("Chekhov"));

  agl::core::DynamicConfig dynamic_config(
      {{"CREW_MEMBERS", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#map:
        input#taxi-config: CREW_MEMBERS
        iterator: it
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it
          - value#string: "!"
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  agl::core::Variant::List mapped =
      result_list.Get<agl::core::Variant::List>(0);
  EXPECT_EQ(mapped.Size(), 3);
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello Kirk!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello Spock!");
  EXPECT_EQ(mapped.Get<std::string>(2), "Hello Chekhov!");
}

UTEST(TestOperator, FoldArray) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#foldl:
        input#array:
          - value: 1
          - value: 43
          - value: 2
          - value: 42
            enabled#boolean: false
        init: 0
        element#sum:
          - value#xget: /iterators/it/accumulator
          - value#xget: /iterators/it/iterator
        iterator: it
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  int64_t folded = result_list.Get<int64_t>(0);
  EXPECT_EQ(folded, 46);
}

UTEST(TestOperator, FoldLJson) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kArray);
  some_config_builder.PushBack(std::string("Bob"));
  some_config_builder.PushBack(std::string("Charlie"));
  some_config_builder.PushBack(std::string("Davie"));

  agl::core::DynamicConfig dynamic_config(
      {{"MEMBERS", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#foldl:
        input#taxi-config: MEMBERS
        init#string: "Alice"
        element#concat-strings:
          - value#xget: /iterators/it/accumulator
          - value#string: ", "
          - value#xget: /iterators/it/iterator
        iterator: it
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  std::string folded = result_list.Get<std::string>(0);
  EXPECT_EQ(folded, "Alice, Bob, Charlie, Davie");
}

UTEST(TestOperator, FoldRJson) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kArray);
  some_config_builder.PushBack(std::string("Alice"));
  some_config_builder.PushBack(std::string("Bob"));
  some_config_builder.PushBack(std::string("Charlie"));

  agl::core::DynamicConfig dynamic_config(
      {{"MEMBERS", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#foldr:
        input#taxi-config: MEMBERS
        init#string: "Davie"
        element#concat-strings:
          - value#xget: /iterators/it/iterator
          - value#string: ", "
          - value#xget: /iterators/it/accumulator
        iterator: it
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 1);
  std::string folded = result_list.Get<std::string>(0);
  EXPECT_EQ(folded, "Alice, Bob, Charlie, Davie");
}

TEST(TestOperator, ConcatObjects) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kObject);
  some_config_builder["json_key_1"] = "test";
  some_config_builder["json_key_2"] = false;
  some_config_builder["json_key_3"] = 42;

  agl::core::DynamicConfig dynamic_config(
      {{"TEST_CFG", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#taxi-config: TEST_CFG
    - value#object:
      - key: inline_key_1
        value#boolean: true
      - key: inline_key_2
        value#string: inline test
    - value#object:
      - key: json_key_3
        value#string: not 42
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("concat-objects", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsMap());
  agl::core::Variant::Map result_map = result.AsMap();
  EXPECT_EQ(result_map.Size(), 5);
  EXPECT_EQ(result_map.Get<variant::io::JsonPromise>("json_key_1")
                .AsJson()
                .As<std::string>(),
            "test");
  EXPECT_EQ(result_map.Get<variant::io::JsonPromise>("json_key_2")
                .AsJson()
                .As<bool>(),
            false);
  EXPECT_EQ(
      result_map.Get<variant::io::JsonPromise>("json_key_3").AsJson().As<int>(),
      42);
  EXPECT_EQ(result_map.Get<bool>("inline_key_1"), true);
  EXPECT_EQ(result_map.Get<std::string>("inline_key_2"), "inline test");
}

TEST(TestOperator, ConcatArrays) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kArray);
  some_config_builder.PushBack("test");
  some_config_builder.PushBack(false);
  some_config_builder.PushBack(42);

  agl::core::DynamicConfig dynamic_config(
      {{"TEST_CFG", some_config_builder.ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  auto bson_arr = formats::bson::ValueBuilder(formats::common::Type::kArray);
  bson_arr.PushBack("TEST");
  bson_arr.PushBack(true);
  bson_arr.PushBack(108);
  CustomValues custom{{"test_bson", bson_arr.ExtractValue()}};
  executer_state.RegisterBinding(custom);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#taxi-config: TEST_CFG
    - value#array:
      - value#boolean: true
      - value#string: inline test
    - value#array:
      - value#string: not
      - value#string: appears
      enabled#boolean: false
    - value#array:
      - value#string: not 42
    - value#custom: test_bson
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("concat-arrays", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());  // due to taxi-config dependency
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_map = result.AsList();
  EXPECT_EQ(result_map.Size(), 9);
  EXPECT_EQ(
      result_map.Get<variant::io::JsonPromise>(0).AsJson().As<std::string>(),
      "test");
  EXPECT_EQ(result_map.Get<variant::io::JsonPromise>(1).AsJson().As<bool>(),
            false);
  EXPECT_EQ(result_map.Get<variant::io::JsonPromise>(2).AsJson().As<int>(), 42);
  EXPECT_EQ(result_map.Get<bool>(3), true);
  EXPECT_EQ(result_map.Get<std::string>(4), "inline test");
  EXPECT_EQ(result_map.Get<std::string>(5), "not 42");
  EXPECT_EQ(
      result_map.Get<variant::io::BsonPromise>(6).AsBson().As<std::string>(),
      "TEST");
  EXPECT_EQ(result_map.Get<variant::io::BsonPromise>(7).AsBson().As<bool>(),
            true);
  EXPECT_EQ(result_map.Get<variant::io::BsonPromise>(8).AsBson().As<int>(),
            108);
}

TEST(TestOperator, LogicNot) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#not:
        value#boolean: true
    - value#not:
        value#boolean: false
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_FALSE(result_list.Get<bool>(0));
  EXPECT_TRUE(result_list.Get<bool>(1));
}

TEST(TestOperator, LogicsAndOr) {
  std::string source;
  std::vector<bool> answers;
  for (const std::string& operator_name : {"and", "or"}) {
    for (size_t operands_count(1); operands_count < 4; ++operands_count) {
      std::vector<bool> operands(operands_count, false);

      while (true) {
        source += "- value#" + operator_name + ":\n";
        bool answer = operator_name == "and" ? true : false;
        for (bool operand : operands) {
          source +=
              ("  - value#boolean: " + std::string(operand ? "true" : "false") +
               "\n");
          answer =
              operator_name == "and" ? answer and operand : answer or operand;
        }
        answers.push_back(answer);

        if (std::all_of(operands.cbegin(), operands.cend(),
                        [](bool v) { return v; })) {
          source += "\n";
          break;
        }

        for (int i = operands.size() - 1; i >= 0; --i) {
          operands[i] = !operands[i];
          if (operands[i]) break;
        }
      }
    }
  }

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(source);

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), answers.size());
  for (size_t i = 0; i < answers.size(); ++i) {
    EXPECT_EQ(result_list.Get<bool>(i), bool(answers[i]));
  }
}

TEST(TestOperator, Empty) {
  // prepare taxi-config (as a source of raw JSON)
  auto some_config_builder =
      formats::json::ValueBuilder(formats::json::Type::kObject);
  some_config_builder["empty_array"] = std::vector<std::string>();
  some_config_builder["nonempty_array"] = std::vector<std::string>{"foo"};
  some_config_builder["empty_object"] = std::map<std::string, std::string>();
  some_config_builder["nonempty_object"] =
      std::map<std::string, std::string>({{"foo", "bar"}});

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#empty:
        value#object:
        - key: key
          value#string: value
    - value#empty:
        value#array:
        - value#string: value
    - value#empty:
        value#array:
    - value#empty:
        value#object:
    - value#empty:
        value#get:
          object#taxi-config: TEST_CFG
          key#string: empty_array
    - value#empty:
        value#get:
          object#taxi-config: TEST_CFG
          key#string: nonempty_array
    - value#empty:
        value#get:
          object#taxi-config: TEST_CFG
          key#string: empty_object
    - value#empty:
        value#get:
          object#taxi-config: TEST_CFG
          key#string: nonempty_object
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::DynamicConfig dynamic_config(
      {{"TEST_CFG", some_config_builder.ExtractValue()}});
  std::vector<std::string> sources;
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 8);
  EXPECT_FALSE(result_list.Get<bool>(0));
  EXPECT_FALSE(result_list.Get<bool>(1));
  EXPECT_TRUE(result_list.Get<bool>(2));
  EXPECT_TRUE(result_list.Get<bool>(3));
  EXPECT_TRUE(result_list.Get<bool>(4));
  EXPECT_FALSE(result_list.Get<bool>(5));
  EXPECT_TRUE(result_list.Get<bool>(6));
  EXPECT_FALSE(result_list.Get<bool>(7));
}

TEST(TestOperator, Equal) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#equal:
      - value#boolean: true
      - value#boolean: true
    - value#equal:
      - value#boolean: true
      - value#string: "true"
    - value#equal:
      - value#string: "foo"
      - value#string: "foo"
    - value#equal:
      - value#string: "foo"
      - value#string: "bar"
    - value#equal:
      - value#string: "bar"
      - value#string: "bar"
      - value#string: "bar"
      - value#string: "bar"
    - value#equal:
      - value#string: "bar"
      - value#string: "bar"
      - value#integer: 34
      - value#string: "bar"
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_TRUE(result_list.Get<bool>(0));
  EXPECT_FALSE(result_list.Get<bool>(1));
  EXPECT_TRUE(result_list.Get<bool>(2));
  EXPECT_FALSE(result_list.Get<bool>(3));
  EXPECT_TRUE(result_list.Get<bool>(4));
  EXPECT_FALSE(result_list.Get<bool>(5));
}

TEST(TestOperator, If) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#if:
        condition#boolean: true
        then#string: "then value"
        else#string: "else value"
    - value#if:
        condition#boolean: false
        then#string: "then value"
        else#string: "else value"
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<std::string>(0), "then value");
  EXPECT_EQ(result_list.Get<std::string>(1), "else value");
}

TEST(TestOperator, Slice) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#slice-string:
        value#string: "abr/acadabra"
        start: 4
    - value#slice-string:
        value#string: "abr/acadabra"
        end: 4
    - value#slice-string:
        value#string: "abr/acadabra"
        start: 3
        end: 4
    - value#slice-string:
        value#string: "abr/acadabra"
        start: -5
    - value#slice-string:
        value#string: "abr/acadabra"
        end: -5
    - value#slice-string:
        value#string: "abr/acadabra"
        start: -5
        end: -2
  )");

  // fetch parser
  const auto& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_EQ(result_list.Get<std::string>(0), "acadabra");
  EXPECT_EQ(result_list.Get<std::string>(1), "abr/");
  EXPECT_EQ(result_list.Get<std::string>(2), "/");
  EXPECT_EQ(result_list.Get<std::string>(3), "dabra");
  EXPECT_EQ(result_list.Get<std::string>(4), "abr/aca");
  EXPECT_EQ(result_list.Get<std::string>(5), "dab");
}

TEST(TestOperator, CastToInteger) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#to-integer:
        value#string: 123
    - value#to-integer:
        value#string: "-9223372036854775807"
    - value#to-integer:
        value#real: 3.14
    - value#to-integer:
        value#real: 2.72
    - value#to-integer:
        value#integer: -9223372036854775806
    - value#to-integer:
        value#if:
          condition: false
          then#string: 42
          else#string: 24
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_EQ(result_list.Get<int64_t>(0), 123);
  EXPECT_EQ(result_list.Get<int64_t>(1), -9223372036854775807);
  EXPECT_EQ(result_list.Get<int64_t>(2), 3);
  EXPECT_EQ(result_list.Get<int64_t>(3), 2);
  EXPECT_EQ(result_list.Get<int64_t>(4), -9223372036854775806);
  EXPECT_EQ(result_list.Get<int64_t>(5), 24);
}

TEST(TestOperator, ToIntegerException) {
  std::vector<formats::yaml::Value> values = {
      formats::yaml::FromString(R"(
      - value#to-integer:
          value#object:
            - key: key1
              value: val1
    )"),
      formats::yaml::FromString(R"(
      - value#to-integer:
          value#boolean: false
    )"),
      formats::yaml::FromString(R"(
      - value#to-integer:
          value#null:
    )"),
      formats::yaml::FromString(R"(
      - value#to-integer:
          value#array:
            - value: val1
    )"),
  };

  for (const auto& ast : values) {
    const agl::core::variant::YamlParser& parser =
        agl::core::variant::GetYamlParser("array", kDefaultRegistry);
    agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);

    core::ExecuterState executer_state;
    EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
  }
}

TEST(TestOperator, CastToReal) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#to-real:
        value#string: 123.9
    - value#to-real:
        value#integer: 123
    - value#to-real:
        value#real: 3.14
    - value#to-real:
        value#string: "-9223372036854775807.5"
    - value#to-real:
        value#string: "-922337.20368547758075"
    - value#to-real:
        value#real: -9223372036854775806.5
    - value#to-real:
        value#if:
          condition: false
          then#string: 42.5
          else#string: 24.2
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 7);
  EXPECT_EQ(result_list.Get<double>(0), 123.9);
  EXPECT_EQ(result_list.Get<double>(1), 123.0);
  EXPECT_EQ(result_list.Get<double>(2), 3.14);
  EXPECT_EQ(result_list.Get<double>(3), -9223372036854775807.5);
  EXPECT_EQ(result_list.Get<double>(4), -922337.20368547758075);
  EXPECT_EQ(result_list.Get<double>(5), -9223372036854775806.5);
  EXPECT_EQ(result_list.Get<double>(6), 24.2);
}

TEST(TestOperator, ToRealException) {
  std::vector<formats::yaml::Value> values = {
      formats::yaml::FromString(R"(
      - value#to-real:
          value#object:
            - key: key1
              value: val1
    )"),
      formats::yaml::FromString(R"(
      - value#to-real:
          value#boolean: false
    )"),
      formats::yaml::FromString(R"(
      - value#to-real:
          value#null:
    )"),
      formats::yaml::FromString(R"(
      - value#to-real:
          value#array:
            - value: val1
    )"),
  };

  for (const auto& ast : values) {
    const agl::core::variant::YamlParser& parser =
        agl::core::variant::GetYamlParser("array", kDefaultRegistry);
    agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);

    core::ExecuterState executer_state;
    EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
  }
}

TEST(TestOperator, CastToString) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#to-string:
        value#integer: 123
    - value#to-string:
        value#integer: -9223372036854775807
    - value#to-string:
        value#real: 3.14
    - value#to-string:
        value#real: 2.72
    - value#to-string:
        value#string: "hello, world!"
    - value#to-string:
        value#if:
          condition: false
          then#string: 42
          else#string: 24
  )");

  // fetch parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  core::ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_EQ(result_list.Get<std::string>(0), "123");
  EXPECT_EQ(result_list.Get<std::string>(1), "-9223372036854775807");
  EXPECT_TRUE(
      boost::algorithm::starts_with(result_list.Get<std::string>(2), "3.14"));
  EXPECT_TRUE(
      boost::algorithm::starts_with(result_list.Get<std::string>(3), "2.72"));
  EXPECT_EQ(result_list.Get<std::string>(4), "hello, world!");
  EXPECT_EQ(result_list.Get<std::string>(5), "24");
}

TEST(TestOperator, ToStringException) {
  std::vector<formats::yaml::Value> values = {
      formats::yaml::FromString(R"(
      - value#to-string:
          value#object:
            - key: key1
              value: 1
    )"),
      formats::yaml::FromString(R"(
      - value#to-string:
          value#boolean: false
    )"),
      formats::yaml::FromString(R"(
      - value#to-string:
          value#null:
    )"),
      formats::yaml::FromString(R"(
      - value#to-string:
          value#array:
            - value: 10
    )"),
  };

  for (const auto& ast : values) {
    const agl::core::variant::YamlParser& parser =
        agl::core::variant::GetYamlParser("array", kDefaultRegistry);
    agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);

    core::ExecuterState executer_state;
    EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
  }
}

TEST(TestOperator, OperatorSum) {
  formats::yaml::Value ast = formats::yaml::FromString(R"(
      - value#sum:
          - value: -1
          - value: 2
          - value: -3
          - value: 4
      - value#sum:
          - value#sum:
              - value: 1
              - value#to-integer:
                    value#real: 3.14
          - value#sum:
              - value#to-integer:
                    value#string: 123
              - value: '4'
              - value#sum:
                  - value: 5
    )");

  agl::core::DynamicConfig dynamic_config(
      {{"INT_CONFIG", formats::json::ValueBuilder(10).ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_TRUE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<int64_t>(0), 2);
  EXPECT_EQ(result_list.Get<int64_t>(1), 136);
}

TEST(TestOperator, OperatorSumOthers) {
  formats::yaml::Value ast = formats::yaml::FromString(R"(
      - value#sum:
          - value#taxi-config: INT_JSON
          - value: 5
      - value#sum:
          - value#custom: int_bson
          - value: 15
    )");

  agl::core::DynamicConfig dynamic_config(
      {{"INT_JSON", formats::json::ValueBuilder(10).ExtractValue()}});
  core::ExecuterState executer_state;
  executer_state.RegisterBinding(dynamic_config);

  CustomValues custom{
      {"int_bson", formats::bson::ValueBuilder(10).ExtractValue()}};
  executer_state.RegisterBinding(custom);

  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());  // due to taxi-config

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 2);
  EXPECT_EQ(result_list.Get<int64_t>(0), 15);
  EXPECT_EQ(result_list.Get<int64_t>(1), 25);
}

TEST(TestOperator, OperatorSumExceptions) {
  std::vector<formats::yaml::Value> values = {formats::yaml::FromString(R"(
      - value#sum:
          - value: 1.1
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value: one
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#string: 123
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#real: 3.14
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#boolean: false
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#object:
              - one: 1
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#array:
              - 1
    )"),
                                              formats::yaml::FromString(R"(
      - value#sum:
          - value#null:
    )")};

  for (const auto& ast : values) {
    const agl::core::variant::YamlParser& parser =
        agl::core::variant::GetYamlParser("array", kDefaultRegistry);
    agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
    EXPECT_TRUE(executable.IsConstant());
    EXPECT_FALSE(executable.IsNone());

    core::ExecuterState executer_state;
    EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
  }
}

TEST(TestOperator, OperatorSnakeToCamel) {
  struct TestCase {
    formats::yaml::Value value;
    std::string expected;
  };

  std::vector<TestCase> test_cases = {
      {
          formats::yaml::FromString(R"(
            - value#snake-to-camel:
                value#string: 'lower_camel_case'
          )"),
          "lowerCamelCase",
      },
      {
          formats::yaml::FromString(R"(
            - value#snake-to-camel:
                value#string: 'lower_camel_case'
                to-upper#boolean: false
          )"),
          "lowerCamelCase",
      },
      {
          formats::yaml::FromString(R"(
            - value#snake-to-camel:
                value#string: 'upper_camel_case'
                to-upper#boolean: true
          )"),
          "UpperCamelCase",
      },
      {
          formats::yaml::FromString(R"(
            - value#snake-to-camel:
                value#string: '_SoMe_StRaNge_string_'
                to-upper#boolean: false
          )"),
          "someStrangeString",
      },
  };

  for (const auto& test_case : test_cases) {
    const auto& parser =
        agl::core::variant::GetYamlParser("array", kDefaultRegistry);
    core::ExecuterState executer_state;
    const auto result = parser.Parse(test_case.value, kEmptyDeps)
                            .Evaluate(executer_state)
                            .AsList()
                            .Get<std::string>(0);
    EXPECT_EQ(result, test_case.expected);
  }
}
}  // namespace agl::core::tests
