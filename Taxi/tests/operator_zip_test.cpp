#include <agl/core/dynamic_config.hpp>
#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/io/encoded-string.hpp>
#include <agl/modules/manager.hpp>
#include <core/default_operators_registry.hpp>
#include <userver/formats/bson.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/utest/utest.hpp>

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

UTEST(TestOperator, ZipMap) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#array:
              - value#string: A
              - value#string: B
              - value#string: C
            iterator: it1
          - iterable#array:
              - value#string: X
              - value#string: Y
            iterator: it2
          - iterable#array:
              - value#string: 1
              - value#string: 2
              - value#string: 3
              - value#string: 4
            iterator: it3
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it1
          - value#iterator: it2
          - value#iterator: it3
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
  EXPECT_EQ(mapped.Size(), 2);
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello AX1!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello BY2!");
}

UTEST(TestOperator, ZipMultitype) {
  core::ExecuterState executer_state;

  auto json_builder = formats::json::ValueBuilder(formats::json::Type::kArray);
  json_builder.PushBack(std::string("A"));
  json_builder.PushBack(std::string("B"));
  json_builder.PushBack(std::string("C"));
  agl::core::DynamicConfig dynamic_config(
      {{"test_json_arr", json_builder.ExtractValue()}});
  executer_state.RegisterBinding(dynamic_config);

  auto bson_builder =
      formats::bson::ValueBuilder(formats::common::Type::kArray);
  bson_builder.PushBack(std::string("X"));
  bson_builder.PushBack(std::string("Y"));
  bson_builder.PushBack(std::string("Z"));
  CustomValues custom{{"test_bson_arr", bson_builder.ExtractValue()}};
  executer_state.RegisterBinding(custom);

  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#taxi-config: test_json_arr
            iterator: it1
          - iterable#custom: test_bson_arr
            iterator: it2
          - iterable#array:
              - value#string: 1
              - value#string: 2
              - value#string: 3
              - value#string: 4
            iterator: it3
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it1
          - value#iterator: it2
          - value#iterator: it3
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
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello AX1!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello BY2!");
  EXPECT_EQ(mapped.Get<std::string>(2), "Hello CZ3!");
}

UTEST(TestOperator, ZipEmptyInpty) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#array:
            iterator: it1
          - iterable#array:
              - value#string: A
              - value#string: B
              - value#string: C
            iterator: it2
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it1
          - value#iterator: it2
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
  EXPECT_EQ(mapped.Size(), 0);
}

UTEST(TestOperator, ZipSingleInpty) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#array:
              - value#string: A
              - value#string: B
              - value#string: C
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
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello A!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello B!");
  EXPECT_EQ(mapped.Get<std::string>(2), "Hello C!");
}

UTEST(TestOperator, ZipStrict) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#array:
              - value#string: A
              - value#string: B
            iterator: it1
          - iterable#array:
              - value#string: X
              - value#string: Y
            iterator: it2
          - iterable#array:
              - value#string: 1
              - value#string: 2
            iterator: it3
        strict#boolean: true
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it1
          - value#iterator: it2
          - value#iterator: it3
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
  EXPECT_EQ(mapped.Size(), 2);
  EXPECT_EQ(mapped.Get<std::string>(0), "Hello AX1!");
  EXPECT_EQ(mapped.Get<std::string>(1), "Hello BY2!");
}

UTEST(TestOperator, ZipStrictError) {
  // prepare arguments for operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#zip:
        input#array:
          - iterable#array:
              - value#string: A
              - value#string: B
            iterator: it1
          - iterable#array:
              - value#string: X
              - value#string: Y
            iterator: it2
          - iterable#array:
              - value#string: 1
              - value#string: 2
              - value#string: 3
            iterator: it3
        strict#boolean: true
        element#concat-strings:
          - value#string: "Hello "
          - value#iterator: it1
          - value#iterator: it2
          - value#iterator: it3
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
  EXPECT_THROW(executable.Evaluate(executer_state), std::runtime_error);
}

}  // namespace agl::core::tests
