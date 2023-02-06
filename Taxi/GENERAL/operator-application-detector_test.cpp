#include <userver/utest/utest.hpp>

#include <agl/core/executer_state.hpp>
#include <agl/core/operators-registry.hpp>
#include <agl/core/variant.hpp>
#include <agl/core/variant/parser.hpp>
#include <agl/modules/manager.hpp>
#include <testing/taxi_config.hpp>

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

TEST(TestOperator, ApplicationDetectorHappyPath) {
  static const std::string kOperands = R"(
    user-agent: 'yandex-taxi/3.96.0.60672 Android/8.0.0 (samsung; SM-G930F)'
  )";

  static const std::string kDetectionRulesNew = R"#(
  {
    "rules": [
      {
        "match": [
            "^(?:yandex-taxi/|ru\\.yandex\\.ytaxi/|ru\\.yandex\\.taxi\\.).+darwin",
            "^(?:test/|ru\\.yandex\\.ytaxi/|ru\\.yandex\\.taxi\\.).+darwin"
        ],
        "$app_name": "test_string",
        "actions": [
          "#ytaxi_ver",
          "#build"
        ]
      },
      {
        "match": "^yandex[-\\.]taxi/.+windows",
        "$app_name": "win",
        "actions": "#ytaxi_ver"
      },
      {
        "header": "X-Taxi",
        "match": "^mobile$",
        "$app_name": "mobileweb"
      },
      {
        "$app_name": "web"
      }
    ],
    "subrules": [
      {
        "name": "#ytaxi_ver",
        "match": "(?:taxi)(?:\\.\\w+)?/(\\d+)\\.(\\d+)\\.(\\d+)",
        "$app_ver1": "{1}",
        "$app_ver2": "{2}",
        "$app_ver3": "{3}"
      },
      {
        "name": "#build",
        "any": [
          {
            "match": "\\.alpha/",
            "$app_build": "alpha"
          },
          {
            "match": "\\.beta/",
            "$app_build": "beta"
          },
          {"$app_build": "release"}
        ]
      }
    ]
  })#";

  // build executable
  const variant::YamlParser& parser =
      variant::GetYamlParser("application-detector", kDefaultRegistry);
  const Variant executable =
      parser.Parse(formats::yaml::FromString(kOperands), kEmptyDeps);

  // build plain config
  const auto config_source = dynamic_config::GetDefaultSource();
  const auto config = config_source.GetSnapshot();

  // executer operator
  ExecuterState executer_state;
  executer_state.RegisterBinding(config);
  Variant app_vars_var = executable.Evaluate(executer_state);

  EXPECT_TRUE(app_vars_var.IsMap());
  Variant::Map const& app_vars = app_vars_var.AsMap();
  EXPECT_EQ(app_vars.Get<std::string>("app_brand"), "yataxi");
}
}  // namespace agl::core::variant::test
