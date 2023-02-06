#include <gtest/gtest.h>

#include <boost/algorithm/string/join.hpp>

#include <list>
#include <set>

#include <userver/formats/json/inline.hpp>

#include <models/circuit_schema.hpp>
#include <models/service.hpp>
#include <names/circuit_schema.hpp>
#include <radio/spec/running_spec_container.hpp>
#include <radio/spec/templates/mods/mods_matcher.hpp>
#include <radio/spec/templates/mods/spec_disable_mod.hpp>
#include <radio/spec/templates/spec_template_builder.hpp>

namespace hejmdal::models {

namespace {

CircuitSchemaPtr MockCircuitSchemaPtr(const std::string& id) {
  CircuitSchema result;
  result.id = CircuitSchemaId(id);
  return std::make_shared<const CircuitSchema>(std::move(result));
}

}  // namespace

}  // namespace hejmdal::models

namespace hejmdal::radio::spec {

namespace {

void CheckSpecList(
    const std::list<radio::spec::Specification>& spec_list,
    std::set<std::string> enabled_ids,
    std::optional<std::set<std::string>> disabled_ids = std::nullopt) {
  for (const auto& spec : spec_list) {
    if (spec.IsDisabled()) {
      if (disabled_ids.has_value()) {
        EXPECT_EQ(1, disabled_ids.value().erase(spec.GetId()))
            << "Extra disabled spec found in list: " + spec.GetId();
      }
    } else {
      EXPECT_EQ(1, enabled_ids.erase(spec.GetId()))
          << "Extra enabled spec found in list: " + spec.GetId();
    }
  }

  EXPECT_TRUE(enabled_ids.empty()) << "Some enabled specs not found in list: " +
                                          boost::join(enabled_ids, ", ");

  EXPECT_TRUE(!disabled_ids.has_value() || disabled_ids.value().empty())
      << "Some disabled specs not found in list: " +
             boost::join(disabled_ids.value(), ", ");
}

}  // namespace

TEST(TestSpecByDomain, MainTest) {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(1), "service1", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("user1"),
                                    models::UserName("user2")},
      models::TvmName("service1"), std::nullopt);
  service->AddBranch(models::ServiceBranch{
      models::BranchId{0},
      {models::Host{models::HostName{"host"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host2"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kStable,
      "taxi_service1_stable",
      "branch_name",
      {{"some.yandex.net", "some_yandex_net"},
       {"some.yandex.net/handle1", "some_yandex_net_handle1"}},
      std::nullopt});
  models::ServiceMap service_map{{models::ServiceId{1}, service}};

  models::CircuitSchemaMap schema_map{
      {models::CircuitSchemaId{"schema_timings_p95"},
       models::MockCircuitSchemaPtr("schema_timings_p95")},
      {models::CircuitSchemaId{"schema_timings_p98"},
       models::MockCircuitSchemaPtr("schema_timings_p98")}};

  auto spec_tpl_id = "timings_p98";

  auto json_true = formats::json::MakeObject("disable", true);
  auto json_false = formats::json::MakeObject("disable", false);

  spec::RunningSpecContainer running_specs;

  {
    auto spec_tpl =
        spec::SpecTemplateBuilder::ByDomain(
            spec_tpl_id, models::CircuitSchemaId{"schema_timings_p98"},
            {models::ClusterType::kNanny},
            std::vector<models::EnvironmentType>{
                models::EnvironmentType::kStable},
            SpecByDomainCreationPolicy::kOnlyRootDomains)
            .GetSpecTemplate();

    {
      ModsMatcher mods_matcher{{}, {}};

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list, {"taxi_service1_stable::some.yandex.net::timings_p98"},
          std::set<std::string>{
              "taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }

    {
      spec::ModRelation rel(models::ServiceId{10}, std::nullopt, std::nullopt,
                            "other.yandex.net/other_handler", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_true);

      // mod for another service shouldn't affect our specs
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(spec_list,
                    {"taxi_service1_stable::some.yandex.net::timings_p98"});
    }

    {
      spec::ModRelation rel(models::ServiceId{1}, std::nullopt, std::nullopt,
                            "some.yandex.net/handle1", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_false);
      // enable second domain by an additional mod
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list,
          {"taxi_service1_stable::some.yandex.net::timings_p98",
           "taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }
  }

  {
    auto spec_tpl =
        spec::SpecTemplateBuilder::ByDomain(
            spec_tpl_id, models::CircuitSchemaId{"schema_timings_p98"},
            {models::ClusterType::kNanny},
            std::vector<models::EnvironmentType>{
                models::EnvironmentType::kStable},
            SpecByDomainCreationPolicy::kAllDomains)
            .GetSpecTemplate();

    {
      ModsMatcher mods_matcher{{}, {}};

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list,
          {"taxi_service1_stable::some.yandex.net::timings_p98",
           "taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }

    {
      spec::ModRelation rel(models::ServiceId{10}, std::nullopt, std::nullopt,
                            "other.yandex.net/other_handler", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_false);

      // mod for another service shouldn't affect our specs
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list,
          {"taxi_service1_stable::some.yandex.net::timings_p98",
           "taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }

    {
      spec::ModRelation rel(models::ServiceId{1}, std::nullopt, std::nullopt,
                            "some.yandex.net", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_true);
      // disable second domain by an additional mod
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list,
          {"taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }
  }

  {
    auto spec_tpl =
        spec::SpecTemplateBuilder::ByDomain(
            spec_tpl_id, models::CircuitSchemaId{"schema_timings_p98"},
            {models::ClusterType::kNanny},
            std::vector<models::EnvironmentType>{
                models::EnvironmentType::kStable},
            SpecByDomainCreationPolicy::kDontCreate)
            .GetSpecTemplate();

    {
      ModsMatcher mods_matcher{{}, {}};

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(spec_list, {});
    }

    {
      spec::ModRelation rel(models::ServiceId{10}, std::nullopt, std::nullopt,
                            "other.yandex.net/other_handler", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_true);

      // mod for another service shouldn't affect our specs
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(spec_list, {});
    }

    {
      spec::ModRelation rel(models::ServiceId{1}, std::nullopt, std::nullopt,
                            "some.yandex.net/handle1", std::nullopt);

      auto mod = std::make_shared<spec::SpecDisableMod>(
          1, spec_tpl_id, std::move(rel), spec::ApplyWhen::kAlways, json_false);
      // enable second domain by an additional mod
      ModsMatcher mods_matcher({mod}, {});

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(
          spec_list,
          {"taxi_service1_stable::some.yandex.net/handle1::timings_p98"});
    }
  }
}

TEST(TestSpecByDomain, TankFilteringTest) {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(1), "service1", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("user1"),
                                    models::UserName("user2")},
      models::TvmName("service1"), std::nullopt);
  service->AddBranch(models::ServiceBranch{
      models::BranchId{0},
      {models::Host{models::HostName{"host"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host2"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kStable,
      "taxi_service1",
      "tank_branch_name",
      {{"some.yandex.net", "some_yandex_net"},
       {"some.yandex.net/handle1", "some_yandex_net_handle1"}},
      std::nullopt});
  models::ServiceMap service_map{{models::ServiceId{1}, service}};

  models::CircuitSchemaMap schema_map{
      {models::CircuitSchemaId{"schema_timings_p95"},
       models::MockCircuitSchemaPtr("schema_timings_p95")},
      {models::CircuitSchemaId{"schema_timings_p98"},
       models::MockCircuitSchemaPtr("schema_timings_p98")}};

  auto spec_tpl_id = "timings_p98";

  spec::RunningSpecContainer running_specs;

  {
    auto spec_tpl =
        spec::SpecTemplateBuilder::ByDomain(
            spec_tpl_id, models::CircuitSchemaId{"schema_timings_p98"},
            {models::ClusterType::kNanny},
            std::vector<models::EnvironmentType>{
                models::EnvironmentType::kStable},
            SpecByDomainCreationPolicy::kOnlyRootDomains)
            .GetSpecTemplate();

    {
      ModsMatcher mods_matcher{{}, {}};

      auto spec_list =
          spec_tpl->Build(service_map, schema_map, mods_matcher, running_specs);

      CheckSpecList(spec_list, {});
    }
  }
}

}  // namespace hejmdal::radio::spec
