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

TEST(TestOperator, Count) {
  core::ExecuterState executor_state;

  auto bson_arr = formats::bson::ValueBuilder(formats::common::Type::kArray);
  bson_arr.PushBack("TEST");
  bson_arr.PushBack(true);
  bson_arr.PushBack(101);

  auto bson_obj = formats::bson::ValueBuilder(formats::common::Type::kObject);
  bson_obj["key_1"] = "";
  bson_obj["str"] = "hello";

  auto json_arr = formats::json::ValueBuilder(formats::common::Type::kArray);
  json_arr.PushBack("TEST");
  json_arr.PushBack(true);
  json_arr.PushBack(101);

  auto json_obj = formats::json::ValueBuilder(formats::common::Type::kObject);
  json_obj["str"] = "qq";

  CustomValues custom{
      {"test_bson_arr", bson_arr.ExtractValue()},
      {"test_bson_obj", bson_obj.ExtractValue()},
      {"test_json_arr", json_arr.ExtractValue()},
      {"test_json_obj", json_obj.ExtractValue()},
  };
  executor_state.RegisterBinding(custom);

  // prepare an endpoint config for the operator
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
     - value#count:
         value#object:
           - key: key_a
             value#integer: 0
           - key: key_b
             value#string: nope
     - value#count:
         value#object:
     - value#count:
         value#array:
           - value#string: privetik
           - value#string: paketik
           - value#integer: 0
     - value#count:
         value#array:
     - value#count:
         value#string: this_is_string
     - value#count:
         value#custom: test_bson_arr
     - value#count:
         value#custom: test_bson_obj
     - value#count:
         value#get:
             key: str
             object#custom: test_json_obj
     - value#count:
         value#custom: test_json_arr
     - value#count:
         value#custom: test_json_obj
  )");

  // fetch a parser
  const agl::core::variant::YamlParser& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);

  // execute the operator
  agl::core::Variant result = executable.Evaluate(executor_state);

  // unpack a root list
  agl::core::Variant::List result_list = result.AsList();

  // check the result
  EXPECT_EQ(result_list.Get<int64_t>(0), 2);   // map
  EXPECT_EQ(result_list.Get<int64_t>(1), 0);   // empty map
  EXPECT_EQ(result_list.Get<int64_t>(2), 3);   // list
  EXPECT_EQ(result_list.Get<int64_t>(3), 0);   // empty list
  EXPECT_EQ(result_list.Get<int64_t>(4), 14);  // string
  EXPECT_EQ(result_list.Get<int64_t>(5), 3);   // bson arr
  EXPECT_EQ(result_list.Get<int64_t>(6), 2);   // bson obj
  EXPECT_EQ(result_list.Get<int64_t>(7), 2);   // json str
  EXPECT_EQ(result_list.Get<int64_t>(8), 3);   // json arr
  EXPECT_EQ(result_list.Get<int64_t>(9), 1);   // json obj
}

}  // namespace agl::core::tests
