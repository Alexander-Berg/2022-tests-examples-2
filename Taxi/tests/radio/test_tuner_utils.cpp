#include <gtest/gtest.h>

#include <models/events/event_factory.hpp>
#include <radio/blocks/commutation/output_consumer.hpp>
#include <radio/detail/tuner/tuner_utils.hpp>
#include <radio/spec/templates/mods/mod_factory.hpp>

#include "../tools/services.hpp"

#include <list>
#include <set>

namespace hejmdal::radio {

namespace {

class MockSpecTemplate : public spec::SpecTemplate {
 public:
  MockSpecTemplate(std::string template_id = "test_template_id",
                   std::string schema_id = "test_schema_id")
      : spec::SpecTemplate(std::move(template_id),
                           models::CircuitSchemaId{schema_id}) {}

  virtual std::list<spec::Specification> Build(
      const models::ServiceMap& /*service_map*/,
      const models::CircuitSchemaMap& /*schema_map*/,
      const spec::ModsMatcher& /*mods*/,
      const spec::RunningSpecContainer&) const override {
    return {};
  }
};

struct SpecParams {
  std::optional<models::ProjectId> project_id;
  std::optional<models::ServiceId> service_id;
  std::optional<models::EnvironmentType> env;
  std::optional<models::HostName> host_name;
  std::optional<models::BranchDomain> domain;
  bool is_disabled = false;
};

spec::Specification BuildSpec(std::string template_id,
                              std::string id = "test_id",
                              SpecParams params = SpecParams{}) {
  return spec::Specification{
      nullptr,           id,
      params.project_id, params.service_id,
      params.env,        params.host_name,
      params.domain,     {},
      template_id,       spec::SpecificationSubjectType::Fixed,
      params.is_disabled};
}

spec::RunningSpecPtr BuildRunningSpec(std::string id,
                                      std::string template_id = "",
                                      SpecParams params = SpecParams{}) {
  if (template_id.empty()) template_id = id + "_template";
  return std::make_shared<spec::RunningSpec>(
      BuildSpec(template_id, id, params), TimeSeriesFlowGroupPtr{},
      std::vector<blocks::OutputConsumerPtr>{});
}

std::set<spec::RunningSpecPtr> NoDeps(const spec::RunningSpecPtr&) {
  return {};
}

}  // namespace

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedEvent) {
  auto changed_event =
      models::events::EventFactory::Build(models::postgres::ExternalEvent{
          models::ExternalEventId{1}, models::ExternalEventLink{"test_link"},
          time::Now() - time::Minutes{5}, std::nullopt, "drills",
          formats::json::FromString(
              "{\"datacenters\": [\"vla\"], \"project_ids\": [1]}"),
          1, std::nullopt});

  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{2},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "drills",
      std::nullopt,
      false});

  std::set<spec::SpecTemplateModPtr> mods{mod};

  SpecParams params;
  params.project_id = models::ProjectId{1};
  params.service_id = models::ServiceId{2};
  params.host_name = models::HostName{"host3"};
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  params.host_name = models::HostName{"host4"};
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);
  params.host_name = std::nullopt;
  auto spec_3 = BuildRunningSpec("spec_3", "spec_3_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_2, spec_3](
          models::ServiceId id,
          spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 2) {
      return {spec_1, spec_2, spec_3};
    }
    return {};
  };
  auto deps_collector =
      [spec_3](
          const spec::RunningSpecPtr& spec) -> std::set<spec::RunningSpecPtr> {
    if (spec->GetId() == "spec_1" || spec->GetId() == "spec_2") {
      return {spec_3};
    }
    return {};
  };
  auto result = detail::impl::FindRunningSpecsOfChangedEvent(
      changed_event, kServices, mods, spec_by_service_getter, deps_collector);

  EXPECT_EQ(result.size(), 2u);
  std::set<std::string> expected_result_ids = {std::string("spec_2"),
                                               std::string("spec_3")};
  for (const auto& res : result) {
    EXPECT_EQ(expected_result_ids.count(res->GetId()), 1);
  }
}

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedEventNoDeps) {
  auto changed_event =
      models::events::EventFactory::Build(models::postgres::ExternalEvent{
          models::ExternalEventId{1}, models::ExternalEventLink{"test_link"},
          time::Now() - time::Minutes{5}, std::nullopt, "drills",
          formats::json::FromString(
              "{\"datacenters\": [\"vla\"], \"project_ids\": [1]}"),
          1, std::nullopt});

  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{2},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "drills",
      std::nullopt,
      false});

  std::set<spec::SpecTemplateModPtr> mods{mod};

  SpecParams params;
  params.project_id = models::ProjectId{1};
  params.service_id = models::ServiceId{2};
  params.host_name = models::HostName{"host3"};
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  params.host_name = models::HostName{"host4"};
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);
  params.host_name = std::nullopt;
  auto spec_3 = BuildRunningSpec("spec_3", "spec_3_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_2, spec_3](
          models::ServiceId id,
          spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 2) {
      return {spec_1, spec_2, spec_3};
    }
    return {};
  };
  auto result = detail::impl::FindRunningSpecsOfChangedEvent(
      changed_event, kServices, mods, spec_by_service_getter, &NoDeps);

  EXPECT_EQ(result.size(), 1u);
  std::set<std::string> expected_result_ids = {std::string("spec_2")};
  for (const auto& res : result) {
    EXPECT_EQ(expected_result_ids.count(res->GetId()), 1);
  }
}

TEST(TestTunerUtils, TestAddChangedEventsToTuneMap) {
  auto changed_event =
      models::events::EventFactory::Build(models::postgres::ExternalEvent{
          models::ExternalEventId{1}, models::ExternalEventLink{"test_link"},
          time::Now() - time::Minutes{5}, std::nullopt, "drills",
          formats::json::FromString(
              "{\"datacenters\": [\"vla\"], \"project_ids\": [2]}"),
          1, std::nullopt});

  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "test_template_1",
      models::ServiceId{5},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "drills",
      std::nullopt,
      false});

  std::set<spec::SpecTemplateModPtr> mods{mod};
  std::set<models::events::ExternalEventPtr> events{changed_event};

  detail::TuneMap tune_map;

  detail::impl::AddChangedEventsToTuneMap(
      events, kServices, mods,
      [](const spec::SpecTemplateId& id) -> std::set<spec::SpecTemplatePtr> {
        if (id == "test_template_1") {
          return {std::make_shared<MockSpecTemplate>("test_template_1")};
        }
        return {};
      },
      tune_map);

  EXPECT_EQ(tune_map.size(), 1);
  for (const auto& [spec_tpl, services] : tune_map) {
    EXPECT_EQ(services.size(), 1);
  }
}

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedMod) {
  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{5},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false});

  SpecParams params;
  params.service_id = models::ServiceId{5};
  params.project_id = models::ProjectId(2);
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);
  auto spec_3 = BuildRunningSpec("spec_3", "spec_3_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_2, spec_3](
          models::ServiceId id,
          spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 5) {
      return {spec_1, spec_2, spec_3};
    }
    return {};
  };
  auto spec_by_mod_getter =
      [](spec::SpecTemplateModId,
         spec::CollectDeps) -> std::set<spec::RunningSpecPtr> { return {}; };
  auto deps_collector =
      [spec_3](
          const spec::RunningSpecPtr& spec) -> std::set<spec::RunningSpecPtr> {
    if (spec->GetId() == "spec_1" || spec->GetId() == "spec_2") {
      return {spec_3};
    }
    return {};
  };

  auto result = detail::impl::FindRunningSpecsOfChangedMod(
      *mod, kServices, {}, spec_by_service_getter, spec_by_mod_getter,
      deps_collector);

  EXPECT_EQ(result.size(), 2u);
  std::set<std::string> expected_result_ids = {std::string("spec_2"),
                                               std::string("spec_3")};
  for (const auto& res : result) {
    EXPECT_EQ(expected_result_ids.count(res->GetId()), 1);
  }
}

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedModByHost) {
  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{5},
      std::nullopt,
      models::HostName{"host22"},
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false});

  SpecParams params;
  params.service_id = models::ServiceId{5};
  params.project_id = models::ProjectId(2);
  params.env = models::EnvironmentType::kStable;
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  params.env = models::EnvironmentType::kTesting;
  params.host_name = models::HostName{"host22"};
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);
  params.host_name = models::HostName{"host23"};
  auto spec_3 = BuildRunningSpec("spec_3", "spec_2_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_2, spec_3](
          models::ServiceId id,
          spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 5) {
      return {spec_1, spec_2, spec_3};
    }
    return {};
  };
  auto spec_by_mod_getter =
      [](spec::SpecTemplateModId,
         spec::CollectDeps) -> std::set<spec::RunningSpecPtr> { return {}; };
  auto deps_collector =
      [spec_1](
          const spec::RunningSpecPtr& spec) -> std::set<spec::RunningSpecPtr> {
    if (spec->GetId() == "spec_2" || spec->GetId() == "spec_3") {
      return {spec_1};
    }
    return {};
  };

  auto result = detail::impl::FindRunningSpecsOfChangedMod(
      *mod, kServices, {}, spec_by_service_getter, spec_by_mod_getter,
      deps_collector);

  /// spec_1 depends on spec_2 and spec_3
  /// spec_2 is disabled by mod (by host)
  /// So spec_2 should be stopped because of the changed mod,
  /// spec_1 should be restarted because of dependency on spec_2
  /// spec_3 should be restarted cuz ByHost/ByDomain spec templates generates
  /// specs for a whole service
  EXPECT_EQ(result.size(), 3u);
  std::set<std::string> expected_result_ids = {
      std::string("spec_3"), std::string("spec_2"), std::string("spec_1")};
  for (const auto& res : result) {
    EXPECT_EQ(expected_result_ids.count(res->GetId()), 1);
  }
}

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedModNoDeps) {
  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{5},
      std::nullopt,
      std::nullopt,
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", true),
      1,
      false,
      "always",
      std::nullopt,
      false});

  SpecParams params;
  params.service_id = models::ServiceId{5};
  params.project_id = models::ProjectId(2);
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);
  auto spec_3 = BuildRunningSpec("spec_3", "spec_3_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_2, spec_3](
          models::ServiceId id,
          spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 5) {
      return {spec_1, spec_2, spec_3};
    }
    return {};
  };
  auto spec_by_mod_getter =
      [](spec::SpecTemplateModId,
         spec::CollectDeps) -> std::set<spec::RunningSpecPtr> { return {}; };

  auto result = detail::impl::FindRunningSpecsOfChangedMod(
      *mod, kServices, {}, spec_by_service_getter, spec_by_mod_getter, &NoDeps);

  EXPECT_EQ(result.size(), 1u);
}

TEST(TestTunerUtils, TestFindRunningSpecsOfChangedMod_DependentWithoutRunning) {
  // spec_2 is disabled by mod
  // mod changed: enabling spec_2
  // spec_3 depends on spec_2 but there's no RunningSpec of spec_2
  // FindRunningSpecsOfChangedMod must find this dependency by mod_view
  auto mod = spec::ModFactory::Build(models::postgres::SpecTemplateMod{
      1,
      "some_login",
      "SOMETICKET",
      {},
      "spec_2_template",
      models::ServiceId{5},
      std::nullopt,
      models::HostName{"host22"},
      std::nullopt,
      std::nullopt,
      spec::mod_types::kSpecDisableModType,
      formats::json::MakeObject("disable", false),
      1,
      false,
      "always",
      std::nullopt,
      false});

  SpecParams params;
  params.service_id = models::ServiceId{5};
  params.project_id = models::ProjectId(2);
  params.env = models::EnvironmentType::kStable;
  auto spec_1 = BuildRunningSpec("spec_1", "spec_1_template", params);
  params.env = models::EnvironmentType::kTesting;
  params.host_name = models::HostName{"host23"};
  auto spec_3 = BuildRunningSpec("spec_3", "spec_3_template", params);
  params.host_name = models::HostName{"host22"};
  params.is_disabled = true;
  auto spec_2 = BuildRunningSpec("spec_2", "spec_2_template", params);

  auto spec_by_service_getter =
      [spec_1, spec_3](models::ServiceId id,
                       spec::CollectDeps) -> std::set<spec::RunningSpecPtr> {
    if (id.GetUnderlying() == 5) {
      return {spec_1, spec_3};
    }
    return {};
  };
  auto spec_by_mod_getter = [spec_3](spec::SpecTemplateModId, spec::CollectDeps)
      -> std::set<spec::RunningSpecPtr> { return {spec_3}; };
  auto deps_collector =
      [spec_3](
          const spec::RunningSpecPtr& spec) -> std::set<spec::RunningSpecPtr> {
    if (spec->GetId() == "spec_1" || spec->GetId() == "spec_2") {
      return {spec_3};
    }
    return {};
  };

  auto result = detail::impl::FindRunningSpecsOfChangedMod(
      *mod, kServices, {}, spec_by_service_getter, spec_by_mod_getter,
      deps_collector);

  EXPECT_EQ(result.size(), 1u);
  std::set<std::string> expected_result_ids = {std::string("spec_3")};
  for (const auto& res : result) {
    EXPECT_EQ(expected_result_ids.count(res->GetId()), 1);
  }
}

TEST(TestTunerUtils, TestSortByDependencies) {
  auto t1 = std::make_shared<MockSpecTemplate>("template_1");
  auto t2 = std::make_shared<MockSpecTemplate>("template_2");
  auto t3 = std::make_shared<MockSpecTemplate>("template_3");

  t1->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_2", "out", "entry"));
  t1->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_3", "out", "entry"));
  t3->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_2", "out", "entry"));

  detail::TuneMap tune_map = {
      {t1, {}},
      {t2, {}},
      {t3, {}},
  };

  auto sorted = detail::impl::SortByDependencies(std::move(tune_map));

  ASSERT_EQ(sorted.size(), 3u);
  EXPECT_EQ(sorted[0].tpl->GetId(), "template_2");
  EXPECT_EQ(sorted[1].tpl->GetId(), "template_3");
  EXPECT_EQ(sorted[2].tpl->GetId(), "template_1");
}

TEST(TestTunerUtils, TestSortByDependenciesCircularSecondIter) {
  auto t1 = std::make_shared<MockSpecTemplate>("template_1");
  auto t2 = std::make_shared<MockSpecTemplate>("template_2");
  auto t3 = std::make_shared<MockSpecTemplate>("template_3");

  t1->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_2", "out", "entry"));
  t2->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_1", "out", "entry"));

  detail::TuneMap tune_map = {
      {t1, {}},
      {t2, {}},
      {t3, {}},
  };

  EXPECT_ANY_THROW(detail::impl::SortByDependencies(std::move(tune_map)));
}

TEST(TestTunerUtils, TestSortByDependenciesCircularFirstIter) {
  auto t1 = std::make_shared<MockSpecTemplate>("template_1");
  auto t2 = std::make_shared<MockSpecTemplate>("template_2");
  auto t3 = std::make_shared<MockSpecTemplate>("template_3");

  t1->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_2", "out", "entry"));
  t2->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_3", "out", "entry"));
  t3->AddConnector(
      std::make_shared<spec::ConnectorTemplate>("template_1", "out", "entry"));

  detail::TuneMap tune_map = {
      {t1, {}},
      {t2, {}},
      {t3, {}},
  };

  EXPECT_ANY_THROW(detail::impl::SortByDependencies(std::move(tune_map)));
}

}  // namespace hejmdal::radio
