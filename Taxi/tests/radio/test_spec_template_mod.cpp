#include <gtest/gtest.h>

#include <set>

#include <userver/formats/json/inline.hpp>

#include <models/events/event_factory.hpp>
#include <models/models_fwd.hpp>
#include <models/postgres/external_event.hpp>
#include <models/postgres/spec_template_mod.hpp>
#include <models/relation_request.hpp>
#include <models/service.hpp>
#include <radio/spec/templates/mods/mod_factory.hpp>
#include <radio/spec/templates/mods/mods_matcher.hpp>
#include <radio/spec/templates/mods/spec_template_mod.hpp>

namespace hejmdal::radio::spec {

namespace {

static const models::Service kService = []() {
  auto service = models::Service(
      models::ServiceId(139), models::ServiceName("hejmdal"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("taxi"), {},
      models::TvmName("hejmdal"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{17},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{18},
      {models::Host{models::HostName{"h2"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h3"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"domain1", "domain1_object"}}});
  return service;
}();

}

TEST(TestSpecTemplateMod, TestRelationMatch) {
  auto relation =
      ModRelation{models::ServiceId{139}, models::EnvironmentType::kStable,
                  std::nullopt, std::nullopt, std::nullopt};
  EXPECT_EQ(RelationPriority::kServiceEnv, relation.GetPriority());
  {
    auto request_relation =
        models::RelationRequest{std::nullopt,
                                models::ServiceId{139},
                                models::EnvironmentType::kPreStable,
                                models::HostName("some_host"),
                                std::nullopt,
                                std::nullopt};
    EXPECT_FALSE(relation.Match(request_relation));
  }
  {
    auto request_relation =
        models::RelationRequest{std::nullopt,
                                models::ServiceId{139},
                                models::EnvironmentType::kStable,
                                models::HostName("some_host"),
                                std::nullopt,
                                std::nullopt};
    EXPECT_TRUE(relation.Match(request_relation));
  }
  {
    auto request_relation =
        models::RelationRequest{std::nullopt, models::ServiceId{139},
                                std::nullopt, models::HostName("some_host"),
                                std::nullopt, std::nullopt};
    EXPECT_FALSE(relation.Match(request_relation));
  }
  {
    auto request_relation = models::RelationRequest{
        std::nullopt, std::nullopt, std::nullopt, models::HostName("some_host"),
        std::nullopt, std::nullopt};
    EXPECT_FALSE(relation.Match(request_relation));
  }
  {
    auto request_relation = models::RelationRequest{
        std::nullopt, models::ServiceId{139}, std::nullopt,
        std::nullopt, std::nullopt,           std::nullopt};
    EXPECT_FALSE(relation.Match(request_relation));
  }
}

TEST(TestSpecTemplateMod, TestRelationToService) {
  {
    auto relation = ModRelation{std::nullopt, models::EnvironmentType::kStable,
                                std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kEnv, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation =
        ModRelation{std::nullopt, models::EnvironmentType::kPreStable,
                    std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kEnv, relation.GetPriority());
    EXPECT_FALSE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{models::ServiceId{139}, std::nullopt,
                                std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kService, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{models::ServiceId{140}, std::nullopt,
                                std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kService, relation.GetPriority());
    EXPECT_FALSE(relation.IsRelatedToService(kService));
  }
  {
    auto relation =
        ModRelation{models::ServiceId{139}, models::EnvironmentType::kStable,
                    std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kServiceEnv, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation =
        ModRelation{models::ServiceId{139}, models::EnvironmentType::kPreStable,
                    std::nullopt, std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kServiceEnv, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation =
        ModRelation{std::nullopt, std::nullopt, models::HostName("h2"),
                    std::nullopt, std::nullopt};
    EXPECT_EQ(RelationPriority::kHostName, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{std::nullopt, std::nullopt,
                                models::HostName("unknown_host"), std::nullopt,
                                std::nullopt};
    EXPECT_EQ(RelationPriority::kHostName, relation.GetPriority());
    EXPECT_FALSE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{std::nullopt, std::nullopt,
                                models::HostName("unknown_host"), std::nullopt,
                                std::nullopt};
    EXPECT_EQ(RelationPriority::kHostName, relation.GetPriority());
    EXPECT_FALSE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{std::nullopt, std::nullopt, std::nullopt,
                                "domain1", std::nullopt};
    EXPECT_EQ(RelationPriority::kDomain, relation.GetPriority());
    EXPECT_TRUE(relation.IsRelatedToService(kService));
  }
  {
    auto relation = ModRelation{std::nullopt, std::nullopt, std::nullopt,
                                "unknown_domain", std::nullopt};
    EXPECT_EQ(RelationPriority::kDomain, relation.GetPriority());
    EXPECT_FALSE(relation.IsRelatedToService(kService));
  }
}

TEST(TestSpecTemplateMod, TestInvalidRelation) {
  auto relation =
      ModRelation{std::nullopt, models::EnvironmentType::kPreStable,
                  models::HostName("some_host"), std::nullopt, "hello"};
  EXPECT_ANY_THROW(relation.ValidateOrThrow());
}

TEST(TestSpecTemplateMod, TestFactoryFail) {
  auto db_mod = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      "unknown_type",
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false};

  std::string ex_what;
  try {
    auto mod = ModFactory::Build(std::move(db_mod));
  } catch (const std::exception& ex) {
    ex_what = ex.what();
  }
  EXPECT_FALSE(ex_what.empty());
}

TEST(TestSpecTemplateMod, TestSpecDisable) {
  auto db_mod = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false};

  auto mod = ModFactory::Build(std::move(db_mod));

  EXPECT_EQ(1, mod->GetId());
  EXPECT_EQ("template_id", mod->GetTemplateId());
  EXPECT_EQ(RelationPriority::kServiceEnv, mod->GetRelationPriority());

  EXPECT_EQ(true, mod->IsSpecDisabled());
  formats::json::Value fake_schema;
  EXPECT_EQ(false, mod->ApplyToSchema(fake_schema));
}

TEST(TestSpecTemplateMod, TestSchemaOverride) {
  auto schema = formats::json::MakeObject(
      "type", "schema", "blocks",
      formats::json::MakeArray(
          formats::json::MakeObject("id", "block_id", "type", "block_type",
                                    "some_param", 1, "another_param", "hello")),
      "out_points", formats::json::MakeArray(), "entry_points",
      formats::json::MakeArray());
  auto db_mod = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kSchemaOverrideModType,
      formats::json::MakeObject(
          "params",
          formats::json::MakeObject(
              "block_id", formats::json::MakeObject("another_param", "world",
                                                    "some_param", 10))),
      1,
      false,
      "always",
      std::nullopt,
      false};

  auto mod = ModFactory::Build(std::move(db_mod));

  EXPECT_EQ(std::nullopt, mod->IsSpecDisabled());
  EXPECT_EQ(true, mod->ApplyToSchema(schema));

  auto expected_schema = formats::json::MakeObject(
      "type", "schema", "blocks",
      formats::json::MakeArray(formats::json::MakeObject(
          "id", "block_id", "type", "block_type", "some_param", 10,
          "another_param", "world")),
      "out_points", formats::json::MakeArray(), "entry_points",
      formats::json::MakeArray());
  EXPECT_EQ(expected_schema, schema);
}

TEST(TestSpecTemplateMod, TestSpecParamsOverride) {
  auto db_mod1 = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kFlowParamsOverrideModType,
      formats::json::MakeObject(
          "flow_params", formats::json::MakeObject("another_param", "world",
                                                   "some_param", "15")),
      1,
      false,
      "always",
      std::nullopt,
      false};

  auto db_mod2 = models::postgres::SpecTemplateMod{
      2,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      std::nullopt,
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kFlowParamsOverrideModType,
      formats::json::MakeObject("flow_params",
                                formats::json::MakeObject("some_param", "10")),
      1,
      false,
      "always",
      std::nullopt,
      false};

  auto mod1 = spec::ModFactory::Build(std::move(db_mod1));
  auto mod2 = spec::ModFactory::Build(std::move(db_mod2));

  std::set<models::events::ExternalEventCPtr> events{};
  spec::ModsMatcher matcher({mod1, mod2}, events);

  auto matched = matcher.Match(std::nullopt, models::ServiceId(139),
                               models::EnvironmentType::kPreStable,
                               std::nullopt, std::nullopt, std::nullopt);

  auto flow_params = matched.GetFlowParams();
  auto expected_flow_params =
      formats::json::MakeObject("some_param", "15", "another_param", "world");
  EXPECT_EQ(expected_flow_params, flow_params);
}

TEST(TestSpecTemplateMod, TestSpecDisableHighestPriorityFirst) {
  auto mod_service_priority = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false};
  auto mod_circuit_priority = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      "circuit_id",
      mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", false),
      1,
      false,
      "always",
      std::nullopt,
      false};

  auto disable_mod = spec::ModFactory::Build(std::move(mod_service_priority));
  auto enable_mod = spec::ModFactory::Build(std::move(mod_circuit_priority));

  std::set<models::events::ExternalEventCPtr> events{};
  spec::ModsMatcher matcher({disable_mod, enable_mod}, events);

  auto matched =
      matcher.Match(std::nullopt, models::ServiceId(139), std::nullopt,
                    std::nullopt, std::nullopt, "circuit_id");
  EXPECT_FALSE(matched.IsSpecDisabled().value());
}

TEST(TestSpecTemplateMod, TestEventsAndModsInteraction) {
  auto db_mod = models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "template_id",
      models::ServiceId{139},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "drills",
      std::nullopt,
      false};

  auto mod = spec::ModFactory::Build(std::move(db_mod));

  {
    auto db_event = models::postgres::ExternalEvent{
        models::ExternalEventId{1},
        models::ExternalEventLink{"drillstaxivla"},
        time::Now() - time::Minutes(5),
        std::nullopt,
        "drills",
        formats::json::FromString(
            "{\"datacenters\": [\"vla\"], \"project_ids\": [1]}"),
        1,
        std::nullopt};
    auto event = models::events::EventFactory::Build(std::move(db_event));
    std::set<models::events::ExternalEventCPtr> events{event};
    auto matcher = spec::ModsMatcher({mod}, events);

    auto matched =
        matcher.Match(models::ProjectId{1}, models::ServiceId(139),
                      std::nullopt, std::nullopt, std::nullopt, "circuit_id");
    EXPECT_EQ(matched.GetModIds().size(), 1);
    EXPECT_TRUE(matched.IsSpecDisabled());
    auto matched_2 =
        matcher.Match(models::ProjectId{0}, models::ServiceId(139),
                      std::nullopt, std::nullopt, std::nullopt, "circuit_id");
    EXPECT_EQ(matched_2.GetModIds().size(), 0);
    EXPECT_FALSE(matched_2.IsSpecDisabled());
  }
  {
    auto db_event = models::postgres::ExternalEvent{
        models::ExternalEventId{1},
        models::ExternalEventLink{"testlink"},
        time::Now() - time::Minutes(5),
        std::nullopt,
        "drills",
        formats::json::FromString(
            "{\"datacenters\": [\"vla\"], \"project_ids\": [2]}"),
        1,
        std::nullopt};
    auto event = models::events::EventFactory::Build(std::move(db_event));
    std::set<models::events::ExternalEventCPtr> events{event};

    auto matcher = spec::ModsMatcher({mod}, events);

    auto matched =
        matcher.Match(models::ProjectId{1}, models::ServiceId(139),
                      std::nullopt, std::nullopt, std::nullopt, "circuit_id");
    EXPECT_EQ(matched.GetModIds().size(), 0);
    EXPECT_FALSE(matched.IsSpecDisabled());
  }
  {
    std::set<models::events::ExternalEventCPtr> events;
    auto matcher = spec::ModsMatcher({mod}, events);

    auto matched =
        matcher.Match(models::ProjectId{1}, models::ServiceId(139),
                      std::nullopt, std::nullopt, std::nullopt, "circuit_id");
    EXPECT_EQ(matched.GetModIds().size(), 0);
    EXPECT_FALSE(matched.IsSpecDisabled());
  }
}

}  // namespace hejmdal::radio::spec
