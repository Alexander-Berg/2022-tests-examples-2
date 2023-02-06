#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>
#include <ua_parser/application.hpp>

#include "core/default_operators_registry.hpp"

namespace agl::core::variant::test {

namespace {

static const OperatorsRegistry kDefaultRegistry = [] {
  return OperatorsRegistry::BuiltinOperators();
}();

static const modules::Manager kEmptyModulesManager = [] {
  return modules::Manager(kDefaultRegistry);
}();

static const YamlParser::Deps kEmptyDeps(kDefaultRegistry,
                                         kEmptyModulesManager);

}  // namespace

TEST(TestOperator, ApplicationVersion) {
  static const std::string kOperands = R"(
    major#string: "42"
    minor#string: "11"
    build#string: "1234"
  )";
  // build executable
  const variant::YamlParser& parser =
      variant::GetYamlParser("application-version", kDefaultRegistry);
  const Variant executable =
      parser.Parse(formats::yaml::FromString(kOperands), kEmptyDeps);

  // executer operator
  ExecuterState executer_state;
  Variant result = executable.Evaluate(executer_state);

  const Opaque& opaque = result.AsOpaque();
  const ua_parser::ApplicationVersion& app_ver =
      opaque.Cast<ua_parser::ApplicationVersion>();

  EXPECT_EQ(app_ver.GetVerMajor(), 42);
  EXPECT_EQ(app_ver.GetVerMinor(), 11);
  EXPECT_EQ(app_ver.GetVerBuild(), 1234);
}
}  // namespace agl::core::variant::test
