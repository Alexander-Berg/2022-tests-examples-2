//
#include <userver/formats/bson/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
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

Variant EvaluateFromString(const formats::yaml::Value& ast,
                           const OperatorsRegistry& r,
                           const YamlParser::Deps& deps) {
  const auto& parser = agl::core::variant::GetYamlParser("array", r);
  agl::core::Variant executable = parser.Parse(ast, deps);

  // execute the operator
  ExecuterState executer_state;
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  return result;
}

TEST(TestOperator, Coalesce) {
  auto ast = formats::yaml::FromString(R"(
    - value#coalesce:
      - value#integer: 1
    - value#coalesce:
      - value#null: {}
      - value#integer: 1
    - value#coalesce:
      - value#null:
      - value#integer: 1
    - value#coalesce:
      - value#null:
      - value#null: {}
  )");

  auto result = EvaluateFromString(ast, kDefaultRegistry, kEmptyDeps);

  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 4);
  EXPECT_EQ(result_list.Get<int64_t>(0), 1);
  EXPECT_EQ(result_list.Get<int64_t>(1), 1);
  EXPECT_EQ(result_list.Get<int64_t>(2), 1);
  EXPECT_TRUE(result_list.IsNone(3));
}

namespace {

const formats::json::Value foo_bar_json = [] {
  formats::json::ValueBuilder builder;
  builder["foo"] = "bar";
  return builder.ExtractValue();
}();

class YamlParserJson : public YamlParserBase<YamlParserJson> {
 public:
  template <typename T>
  static void EnsureOperandsValid(T&&, const Deps&) {}

  template <typename T>
  static Variant ParseImpl(const T& operands, const Deps&) {
    if (operands.template As<std::string>() == "nullJson") {
      return formats::json::ValueBuilder(formats::json::Type::kNull)
          .ExtractValue();
    } else if (operands.template As<std::string>() == "missJson") {
      return formats::json::Value()["missing"];
    } else if (operands.template As<std::string>() == "foobar") {
      return foo_bar_json;
    }
    return Variant();
  }
};

class YamlParserBson : public YamlParserBase<YamlParserBson> {
 public:
  template <typename T>
  static void EnsureOperandsValid(T&&, const Deps&) {}

  template <typename T>
  static Variant ParseImpl(const T& operands, const Deps&) {
    if (operands.template As<std::string>() == "nullBson") {
      return formats::bson::ValueBuilder(formats::common::Type::kNull)
          .ExtractValue();
    } else if (operands.template As<std::string>() == "missBson") {
      return formats::bson::Value()["missing"];
    }
    return Variant();
  }
};
}  // namespace

TEST(TestOperator, CoalesceNullJson) {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  r.RegisterOperators({{"json", std::make_shared<YamlParserJson>()}});
  YamlParser::Deps deps(r, kEmptyModulesManager);

  auto ast = formats::yaml::FromString(R"(
    - value#coalesce:
      - value#json: nullJson
      - value#integer: 1
    - value#coalesce:
      - value#json: nullJson
        inspect-value: false
      - value#integer: 1
    - value#coalesce:
      - value#json: nullJson
        inspect-value: true
      - value#integer: 1
    - value#coalesce:
      - value#json: missJson
        inspect-value: false
      - value#integer: 1
    - value#coalesce:
      - value#json: missJson
        inspect-value: true
      - value#integer: 1
    - value#coalesce:
      - value#json: nullJson
        inspect-value: true
      - value#json: missJson
        inspect-value: true
    - value#coalesce:
      - value#json: foobar
      - value#integer: 1
  )");

  auto result = EvaluateFromString(ast, r, deps);

  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 7);
  EXPECT_TRUE(result_list.Get<agl::core::variant::io::JsonPromise>(0)
                  .AsJson()
                  .IsNull());
  EXPECT_TRUE(result_list.Get<agl::core::variant::io::JsonPromise>(1)
                  .AsJson()
                  .IsNull());
  EXPECT_EQ(result_list.Get<int64_t>(2), 1);
  EXPECT_TRUE(result_list.Get<agl::core::variant::io::JsonPromise>(3)
                  .AsJson()
                  .IsMissing());
  EXPECT_EQ(result_list.Get<int64_t>(4), 1);
  EXPECT_TRUE(result_list.IsNone(5));
  EXPECT_EQ(result_list.Get<agl::core::variant::io::JsonPromise>(6).AsJson(),
            foo_bar_json);
}

TEST(TestOperator, CoalesceNullBson) {
  OperatorsRegistry r;
  r.RegisterOperators(GetDefaultOperatorsList());
  r.RegisterOperators({{"bson", std::make_shared<YamlParserBson>()}});
  YamlParser::Deps deps(r, kEmptyModulesManager);

  auto ast = formats::yaml::FromString(R"(
    - value#coalesce:
      - value#bson: nullBson
      - value#integer: 1
    - value#coalesce:
      - value#bson: nullBson
        inspect-value: false
      - value#integer: 1
    - value#coalesce:
      - value#bson: nullBson
        inspect-value: true
      - value#integer: 1
    - value#coalesce:
      - value#bson: missBson
        inspect-value: false
      - value#integer: 1
    - value#coalesce:
      - value#bson: missBson
        inspect-value: true
      - value#integer: 1
    - value#coalesce:
      - value#bson: nullBson
        inspect-value: true
      - value#bson: missBson
        inspect-value: true
  )");

  auto result = EvaluateFromString(ast, r, deps);

  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 6);
  EXPECT_TRUE(result_list.Get<variant::io::BsonPromise>(0).AsBson().IsNull());
  EXPECT_TRUE(result_list.Get<variant::io::BsonPromise>(1).AsBson().IsNull());
  EXPECT_EQ(result_list.Get<int64_t>(2), 1);
  EXPECT_TRUE(
      result_list.Get<variant::io::BsonPromise>(3).AsBson().IsMissing());
  EXPECT_EQ(result_list.Get<int64_t>(4), 1);
  EXPECT_TRUE(result_list.IsNone(5));
}

}  // namespace agl::core::variant::test
