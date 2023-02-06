#include <agl/core/executer_state.hpp>
#include <agl/core/variant.hpp>
#include <agl/modules/manager.hpp>
#include <bindings/operators-registry.hpp>
#include <userver/formats/yaml/serialize.hpp>
#include <userver/utest/utest.hpp>

#include "request-binding.hpp"

namespace api_proxy::bindings::operator_request::tests {
namespace {
static const agl::core::OperatorsRegistry kDefaultRegistry = [] {
  auto r = agl::core::OperatorsRegistry::BuiltinOperators();
  r.RegisterOperators(api_proxy::core::variant::GetApiProxyOperatorList());
  return r;
}();
static const ::agl::modules::Manager kEmptyModulesManager = [] {
  return ::agl::modules::Manager(kDefaultRegistry);
}();
static const agl::core::variant::YamlParser::Deps kEmptyDeps(
    kDefaultRegistry, kEmptyModulesManager);
}  // namespace

UTEST(TestOperator, RequestQuery) {
  const formats::yaml::Value ast = formats::yaml::FromString(R"(
    - value#request-query: a
    - value#request-query: b
    - value#request-query: c
  )");

  // fetch parser
  const auto& parser =
      agl::core::variant::GetYamlParser("array", kDefaultRegistry);
  agl::core::Variant executable = parser.Parse(ast, kEmptyDeps);
  EXPECT_FALSE(executable.IsConstant());
  EXPECT_FALSE(executable.IsNone());

  // execute the operator
  agl::core::ExecuterState executer_state;
  agl::core::Variant::Map args;
  args.Set("a", "0");
  args.Set("b", "true");
  args.Set("c", "foo");
  api_proxy::core::variant::RequestBinding request({}, {}, std::move(args));
  executer_state.RegisterBinding(request);
  agl::core::Variant result = executable.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  EXPECT_FALSE(result.IsNone());

  // check the result
  EXPECT_NO_THROW(result.AsList());
  agl::core::Variant::List result_list = result.AsList();
  EXPECT_EQ(result_list.Size(), 3);
  EXPECT_EQ(result_list.Get<std::string>(0), "0");
  EXPECT_EQ(result_list.Get<std::string>(1), "true");
  EXPECT_EQ(result_list.Get<std::string>(2), "foo");
}

}  // namespace api_proxy::bindings::operator_request::tests
