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

namespace {
class TestFactory : public Factory {
 public:
  std::string const& Name() const override {
    static const std::string kTest("test-factory");
    return kTest;
  }

  void RegisterOperators(const std::string& contents,
                         const core::OperatorsRegistry&,
                         modules::Manager& modules_manager,
                         std::optional<std::string>) const override {
    modules_manager.RegisterOperator("test-mod", "test-op", Visibility::kPublic,
                                     core::Variant(contents),
                                     core::Location(""));
  }
};
}  // namespace

UTEST(TestExternal, Basic) {
  const std::string contents = "hello world";

  Manager modules_manager(kDefaultRegistry);
  modules_manager.RegisterFactory<TestFactory>();
  modules_manager.LoadModuleFromContents("test-factory", contents);

  const std::string sample = "v#xget: /external/test-mod/test-op";
  const formats::yaml::Value yaml = formats::yaml::FromString(sample);
  auto fields = core::GetOperatedFields(yaml);

  core::variant::ParserContext deps(kDefaultRegistry, modules_manager);
  core::Variant parsed = core::variant::GetOperatorAndParse(
      Require(fields, "v", agl::core::Location("")), deps);

  core::ExecuterState executer_state;
  core::Variant result = parsed.Evaluate(executer_state);
  EXPECT_EQ(result.AsString(), contents);
}

}  // namespace agl::modules::tests
