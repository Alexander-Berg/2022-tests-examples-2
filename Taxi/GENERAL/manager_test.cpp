#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/modules/manager.hpp>
#include <agl/modules/operators-registry.hpp>
#include <core/default_operators_registry.hpp>
#include <modules/factories/agl/factory.hpp>

namespace agl::modules::tests {

static const core::OperatorsRegistry kDefaultRegistry = [] {
  core::OperatorsRegistry r;
  r.RegisterOperators(core::GetDefaultOperatorsList());
  r.RegisterOperators(modules::GetDefaultOperatorsList());
  return r;
}();

UTEST(TestModules, Agl) {
  Manager modules_manager(kDefaultRegistry);

  // load factories
  modules_manager.RegisterFactory<factories::agl::Factory>();

  // load modules
  const std::string module_contents = R"(
    module: test-agl-module
    operators:
      - id: test-op
        visibility: public
        value#concat-strings:
          - value#string: foo
          - value#string: _
          - value#string: bar
  )";
  modules_manager.LoadModuleFromContents("agl", module_contents);

  // load test sample
  const std::string sample = R"(
    test-value#xget: /external/test-agl-module/test-op
  )";
  core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
  const formats::yaml::Value yaml = formats::yaml::FromString(sample);
  auto op_fields = core::GetOperatedFields(yaml);
  core::Variant parsed = core::variant::GetOperatorAndParse(
      Require(op_fields, "test-value", agl::core::Location("")), parser_deps);

  // evaluate test sample
  core::ExecuterState executer_state;
  core::Variant result = parsed.Evaluate(executer_state);
  EXPECT_EQ(result.AsString(), "foo_bar");
  EXPECT_NO_THROW(modules_manager.CheckRecursiveCalls());
}

UTEST(TestModules, AglCrossModule) {
  Manager modules_manager(kDefaultRegistry);

  // load factories
  modules_manager.RegisterFactory<factories::agl::Factory>();

  // load modules
  modules_manager.LoadModuleFromContents("agl", R"(
        module: first-module
        operators:
          - id: local-foo
            visibility: public
            value: Yep, it is a foo
    )");
  modules_manager.LoadModuleFromContents("agl", R"(
        module: second-module
        operators:
          - id: remote-foo
            visibility: public
            value#xget: /external/first-module/local-foo
    )");

  // load test sample
  core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
  const auto yaml =
      formats::yaml::FromString("v#xget: /external/second-module/remote-foo");
  auto op_fields = core::GetOperatedFields(yaml);
  core::Variant parsed = core::variant::GetOperatorAndParse(
      Require(op_fields, "v", agl::core::Location("")), parser_deps);

  // evaluate test sample
  core::ExecuterState executer_state;
  core::Variant result = parsed.Evaluate(executer_state);
  EXPECT_EQ(result.AsString(), "Yep, it is a foo");
  EXPECT_NO_THROW(modules_manager.CheckRecursiveCalls());
}

UTEST(TestModules, AglPrivateOperatorValid) {
  Manager modules_manager(kDefaultRegistry);

  // load factories
  modules_manager.RegisterFactory<factories::agl::Factory>();

  // load modules
  modules_manager.LoadModuleFromContents("agl", R"(
        module: first-module
        operators:
          - id: local-foo
            visibility: public
            value: Yep, it is a foo
          - id: local-foo-pvt
            visibility: private
            value#xget: /external/first-module/local-foo
          - id: local-foo-pvt-backdoor
            visibility: public
            value#xget: /external/first-module/local-foo-pvt
    )");

  // load test sample
  {
    core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
    const auto yaml =
        formats::yaml::FromString("v#xget: /external/first-module/local-foo");
    auto op_fields = core::GetOperatedFields(yaml);
    core::Variant parsed = core::variant::GetOperatorAndParse(
        Require(op_fields, "v", agl::core::Location("")), parser_deps);

    // evaluate test sample
    core::ExecuterState executer_state;
    core::Variant result = parsed.Evaluate(executer_state);
    EXPECT_EQ(result.AsString(), "Yep, it is a foo");
  }

  // now try to access private field
  {
    core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
    const auto yaml = formats::yaml::FromString(
        "v#xget: /external/first-module/local-foo-pvt");
    auto callDescriptor =
        Require(core::GetOperatedFields(yaml), "v", agl::core::Location(""));
    auto op = core::variant::GetOperatorAndParse(callDescriptor, parser_deps);
    EXPECT_THROW(op.IsConstant(), std::runtime_error);
  }

  // now try access private field throuht the publice backdoor
  {
    core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
    const auto yaml = formats::yaml::FromString(
        "v#xget: /external/first-module/local-foo-pvt-backdoor");
    auto op_fields = core::GetOperatedFields(yaml);
    core::Variant parsed = core::variant::GetOperatorAndParse(
        Require(op_fields, "v", agl::core::Location("")), parser_deps);
    core::ExecuterState executer_state;
    core::Variant result = parsed.Evaluate(executer_state);
    EXPECT_EQ(result.AsString(), "Yep, it is a foo");
  }

  EXPECT_NO_THROW(modules_manager.CheckRecursiveCalls());
}

UTEST(TestModules, AglCrossModulePvt) {
  const std::string modhardened = R"(
        module: hardened-module
        operators:
          - id: foo
            visibility: private
            value: Super secret
    )";
  const std::string modsneaky = R"(
        module: sneaky-module
        operators:
          - id: bar
            visibility: public
            value#xget: /external/hardened-module/foo
    )";

  // load factories
  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  // load modules
  modules_manager.LoadModuleFromContents("agl", modhardened);

  core::variant::ParserContext parser_deps(kDefaultRegistry, modules_manager);
  const auto yaml =
      formats::yaml::FromString("v#xget: /external/sneaky-module/bar");
  auto callDescriptor =
      Require(core::GetOperatedFields(yaml), "v", agl::core::Location(""));
  auto op = core::variant::GetOperatorAndParse(callDescriptor, parser_deps);
  EXPECT_THROW(op.IsConstant(), std::runtime_error);

  EXPECT_NO_THROW(modules_manager.CheckRecursiveCalls());
}

UTEST(TestModules, InfiteRecursionSelf) {
  static const std::string kModuleA = R"(
            module: module-a
            operators:
              - id: foo
                visibility: public
                value#xget: /external/module-a/foo
          )";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  modules_manager.LoadModuleFromContents("agl", kModuleA);

  EXPECT_THROW(modules_manager.CheckRecursiveCalls(), std::exception);
}

UTEST(TestModules, InfiteRecursionLocal) {
  static const std::string kModuleA = R"(
            module: module-a
            operators:
              - id: foo
                visibility: public
                value#xget: /external/module-a/bar
              - id: bar
                visibility: public
                value#xget: /external/module-a/foo
          )";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  modules_manager.LoadModuleFromContents("agl", kModuleA);

  EXPECT_THROW(modules_manager.CheckRecursiveCalls(), std::exception);
}

UTEST(TestModules, InfiteRecursionLocalTransitive) {
  static const std::string kModuleA = R"(
            module: module-a
            operators:
              - id: foo
                visibility: public
                value#xget: /external/module-a/bar
              - id: bar
                visibility: public
                value#xget: /external/module-a/baz
              - id: baz
                visibility: public
                value#xget: /external/module-a/foo
          )";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  modules_manager.LoadModuleFromContents("agl", kModuleA);

  EXPECT_THROW(modules_manager.CheckRecursiveCalls(), std::exception);
}

UTEST(TestModules, InfiteRecursionCrossModule) {
  static const std::string kModuleA = R"(
            module: module-a
            operators:
              - id: foo
                visibility: public
                value#xget: /external/module-b/bar
          )";
  static const std::string kModuleB = R"(
            module: module-b
            operators:
              - id: bar
                visibility: public
                value#xget: /external/module-a/foo
          )";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  modules_manager.LoadModuleFromContents("agl", kModuleA);
  modules_manager.LoadModuleFromContents("agl", kModuleB);

  EXPECT_THROW(modules_manager.CheckRecursiveCalls(), std::exception);
}

UTEST(TestModules, InfiteRecursionCrossModuleTransitive) {
  static const std::string kModuleA = R"(
            module: module-a
            operators:
              - id: foo
                visibility: public
                value#xget: /external/module-b/bar
          )";
  static const std::string kModuleB = R"(
            module: module-b
            operators:
              - id: bar
                visibility: public
                value#xget: /external/module-c/baz
          )";
  static const std::string kModuleC = R"(
            module: module-c
            operators:
              - id: baz
                visibility: public
                value#xget: /external/module-a/foo
          )";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<factories::agl::Factory>();

  modules_manager.LoadModuleFromContents("agl", kModuleA);
  modules_manager.LoadModuleFromContents("agl", kModuleB);
  modules_manager.LoadModuleFromContents("agl", kModuleC);

  EXPECT_THROW(modules_manager.CheckRecursiveCalls(), std::exception);
}

}  // namespace agl::modules::tests
