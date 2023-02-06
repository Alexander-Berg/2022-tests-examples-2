#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

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

TEST(TestOperator, TimestampNow) {
  const auto now = utils::datetime::Now();
  utils::datetime::MockNowSet(now);

  const auto& parser = GetYamlParser("array", kDefaultRegistry);

  auto value = formats::yaml::FromString(R"(
    - value#timestamp-now: null
    - value#timestamp-now: "%Y-%m-%dT%H:%M:%SZ"
  )");

  agl::core::Variant timestamp_operator = parser.Parse(value, kEmptyDeps);
  EXPECT_FALSE(timestamp_operator.IsConstant());

  ExecuterState executer_state;
  agl::core::Variant result = timestamp_operator.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  agl::core::Variant::List list = result.AsList();
  EXPECT_EQ(list.Get<std::string>(0), utils::datetime::Timestring(now));
  EXPECT_EQ(list.Get<std::string>(1),
            utils::datetime::Timestring(now, utils::datetime::kDefaultTimezone,
                                        "%Y-%m-%dT%H:%M:%SZ"));
}

TEST(TestOperator, TimestampNowModificated) {
  const auto now = utils::datetime::Now();
  const auto timestamp =
      now + std::chrono::seconds(60) + std::chrono::minutes(30);
  utils::datetime::MockNowSet(now);

  const auto& parser = GetYamlParser("array", kDefaultRegistry);

  auto value = formats::yaml::FromString(R"(
    - value#timestamp-now:
    - value#timestamp-now:
        add-seconds: 60
        add-minutes: 30
    - value#timestamp-now:
        format: "%Y-%m-%dT%H:%M:%SZ"
        add-seconds: 60
        add-minutes: 30
    - value#timestamp-now:
        add-seconds: -15
  )");

  agl::core::Variant timestamp_operator = parser.Parse(value, kEmptyDeps);
  EXPECT_FALSE(timestamp_operator.IsConstant());

  ExecuterState executer_state;
  agl::core::Variant result = timestamp_operator.Evaluate(executer_state);
  EXPECT_TRUE(result.IsConstant());
  agl::core::Variant::List list = result.AsList();
  EXPECT_EQ(list.Get<std::string>(0), utils::datetime::Timestring(now));
  EXPECT_EQ(list.Get<std::string>(1), utils::datetime::Timestring(timestamp));
  EXPECT_EQ(
      list.Get<std::string>(2),
      utils::datetime::Timestring(timestamp, utils::datetime::kDefaultTimezone,
                                  "%Y-%m-%dT%H:%M:%SZ"));
  EXPECT_EQ(list.Get<std::string>(3),
            utils::datetime::Timestring(now + std::chrono::seconds(-15)));
}
}  // namespace agl::core::variant::test
