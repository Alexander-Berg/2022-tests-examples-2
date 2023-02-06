#include <gtest/gtest.h>

#include <external/detail/services_updater.hpp>
#include <models/service.hpp>
#include <views/postgres/services.hpp>

namespace hejmdal {

namespace {

hejmdal::external::detail::services::TablesUpdates AsUpdates(
    const views::postgres::TablesData& data) {
  hejmdal::external::detail::services::TablesUpdates result;
  result.services.to_update = data.services;
  result.branches.to_update = data.branches;
  result.domains.to_update = data.domains;
  result.hosts.to_update = data.hosts;
  return result;
}

models::Service CreateModelService1() {
  auto service = models::Service(
      models::ServiceId(1), models::ServiceName("s1"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"), {},
      models::TvmName("s1"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{1},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"d1", "domain1"},
       models::BranchDomain{"d2", "domain2"}}});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{2},
      {models::Host{models::HostName{"h2"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt});
  return service;
}

models::Service CreateModelService1WithMaintainer() {
  auto service = models::Service(
      models::ServiceId(1), models::ServiceName("s1"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"),
      {models::UserName{"user1"}}, models::TvmName("s1"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{1},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"d1", "domain1"},
       models::BranchDomain{"d2", "domain2"}}});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{2},
      {models::Host{models::HostName{"h2"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt});
  return service;
}

models::Service CreateModelService1WithBranch1AsPreStable() {
  auto service = models::Service(
      models::ServiceId(1), models::ServiceName("s1"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"), {},
      models::TvmName("s1"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{1},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kPreStable,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"d1", "domain1"},
       models::BranchDomain{"d2", "domain2"}}});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{2},
      {models::Host{models::HostName{"h2"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt});
  return service;
}

models::Service CreateModelService1WithoutBranch2() {
  auto service = models::Service(
      models::ServiceId(1), models::ServiceName("s1"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"), {},
      models::TvmName("s1"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{1},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"d1", "domain1"},
       models::BranchDomain{"d2", "domain2"}}});
  return service;
}

models::Service CreateModelService1WithHost6() {
  auto service = models::Service(
      models::ServiceId(1), models::ServiceName("s1"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"), {},
      models::TvmName("s1"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{1},
      {models::Host{models::HostName{"h1"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h5"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt,
      std::string(),
      {models::BranchDomain{"d1", "domain1"},
       models::BranchDomain{"d2", "domain2"}}});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{2},
      {models::Host{models::HostName{"h2"}, models::DataCenter{"vla"}},
       models::Host{models::HostName{"h6"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt});
  return service;
}

models::Service CreateModelService1WithTwoStableBranches() {
  auto service = CreateModelService1();
  service.AddBranch(models::ServiceBranch{
      models::BranchId{3}, {}, models::EnvironmentType::kStable, std::nullopt});
  return service;
}

models::Service CreateModelService2() {
  auto service = models::Service(
      models::ServiceId(2), models::ServiceName("s2"),
      models::AsClusterType("nanny"), models::ServiceLink("service_link"),
      models::ProjectId(1), models::ProjectName("project"),
      std::vector<models::UserName>{}, models::TvmName("s2"), std::nullopt);
  service.AddBranch(models::ServiceBranch{
      models::BranchId{3},
      {models::Host{models::HostName{"h3"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kTesting,
      std::nullopt});
  service.AddBranch(models::ServiceBranch{
      models::BranchId{4},
      {models::Host{models::HostName{"h4"}, models::DataCenter{"vla"}}},
      models::EnvironmentType::kStable,
      std::nullopt,
      std::string(),
      {},
      "grafana url"});
  return service;
}

views::postgres::TablesData CreateTableService1() {
  views::postgres::TablesData tables;
  tables.services = {models::postgres::Service{models::ServiceId(1),
                                               models::ServiceName("s1"),
                                               "nanny",
                                               time::TimePoint(),
                                               false,
                                               models::ProjectId(1),
                                               models::ProjectName("project"),
                                               {},
                                               "service_link",
                                               models::TvmName("s1"),
                                               std::nullopt}};
  tables.branches = {
      models::postgres::Branch{models::BranchId{1}, models::ServiceId(1),
                               models::EnvironmentType::kTesting, std::nullopt,
                               std::nullopt, std::string()},
      models::postgres::Branch{models::BranchId{2}, models::ServiceId(1),
                               models::EnvironmentType::kStable, std::nullopt,
                               std::nullopt, std::string()}};
  tables.hosts = {
      models::postgres::BranchHost{models::HostName("h1"), models::BranchId{1},
                                   models::DataCenter{"vla"}},
      models::postgres::BranchHost{models::HostName("h2"), models::BranchId{2},
                                   models::DataCenter{"vla"}},
      models::postgres::BranchHost{models::HostName("h5"), models::BranchId{1},
                                   models::DataCenter{"vla"}}};
  tables.domains = {
      models::postgres::BranchDomain{models::BranchId{1}, "domain1", "d1"},
      models::postgres::BranchDomain{models::BranchId{1}, "domain2", "d2"},
  };
  return tables;
}

views::postgres::TablesData CreateTableService2() {
  views::postgres::TablesData tables;
  tables.services.push_back(
      models::postgres::Service{models::ServiceId(2),
                                models::ServiceName("s2"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s2"),
                                std::nullopt});
  tables.branches.push_back(
      models::postgres::Branch{models::BranchId{3}, models::ServiceId(2),
                               models::EnvironmentType::kTesting, std::nullopt,
                               std::nullopt, std::string()});
  tables.branches.push_back(
      models::postgres::Branch{models::BranchId{4}, models::ServiceId(2),
                               models::EnvironmentType::kStable, std::nullopt,
                               "grafana url", std::string()});
  tables.hosts.push_back(models::postgres::BranchHost{
      models::HostName("h3"), models::BranchId{3}, models::DataCenter{"vla"}});
  tables.hosts.push_back(models::postgres::BranchHost{
      models::HostName("h4"), models::BranchId{4}, models::DataCenter{"vla"}});
  return tables;
}

views::postgres::TablesData CreateTableServices() {
  auto tables = CreateTableService1();
  tables.services.push_back(
      models::postgres::Service{models::ServiceId(2),
                                models::ServiceName("s2"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s2"),
                                std::nullopt});
  tables.branches.push_back(
      models::postgres::Branch{models::BranchId{3}, models::ServiceId(2),
                               models::EnvironmentType::kTesting, std::nullopt,
                               std::nullopt, std::string()});
  tables.branches.push_back(
      models::postgres::Branch{models::BranchId{4}, models::ServiceId(2),
                               models::EnvironmentType::kStable, std::nullopt,
                               "grafana url", std::string()});
  tables.hosts.push_back(models::postgres::BranchHost{
      models::HostName("h3"), models::BranchId{3}, models::DataCenter{"vla"}});
  tables.hosts.push_back(models::postgres::BranchHost{
      models::HostName("h4"), models::BranchId{4}, models::DataCenter{"vla"}});
  return tables;
}

}  // namespace

TEST(TestServicesUpdater, TestEmptyTables) {
  views::postgres::TablesData empty_tables;
  auto empty_result =
      external::detail::services::CollectTablesData(empty_tables);
  ASSERT_TRUE(empty_result.size() == 0);
}

TEST(TestServicesUpdater, CollectTablesData) {
  auto tables = CreateTableServices();
  auto services = external::detail::services::CollectTablesData(tables);
  models::ServiceMap expected;
  expected[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  expected[models::ServiceId(2)] =
      std::make_shared<models::Service>(CreateModelService2());

  ASSERT_EQ(services.size(), 2u);
  const auto& serv1 = *services[models::ServiceId(1)];
  const auto& expected_serv1 = *expected[models::ServiceId(1)];
  for (const auto& host :
       expected_serv1.GetBranches(models::EnvironmentType::kTesting)
           .front()
           .GetHosts()) {
    EXPECT_EQ(serv1.GetBranches(models::EnvironmentType::kTesting)
                  .front()
                  .GetHosts()
                  .count(host),
              1);
  }
  for (const auto& d :
       expected_serv1.GetBranches(models::EnvironmentType::kTesting)
           .front()
           .GetDomains()) {
    EXPECT_EQ(serv1.GetBranches(models::EnvironmentType::kTesting)
                  .front()
                  .GetDomains()
                  .count(d),
              1);
  }
  EXPECT_EQ(expected_serv1, serv1);
  EXPECT_EQ(*expected[models::ServiceId(2)], *services[models::ServiceId(2)]);
}

TEST(TestServicesUpdater, GetTableData) {
  auto service = CreateModelService1();
  auto expected_tables = CreateTableService1();
  auto result_tables = external::detail::services::GetTablesData(service);

  EXPECT_EQ(result_tables.services, expected_tables.services);
  EXPECT_EQ(result_tables.branches, expected_tables.branches);
  EXPECT_EQ(result_tables.domains, expected_tables.domains);
  EXPECT_EQ(result_tables.hosts, expected_tables.hosts);
}

TEST(TestServicesUpdater, TestGetUpdatesNoUpdates) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  table_services_map[models::ServiceId(2)] =
      std::make_shared<models::Service>(CreateModelService2());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  clownductor_services_map[models::ServiceId(2)] =
      std::make_shared<models::Service>(CreateModelService2());

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  EXPECT_TRUE(updates.services.to_update.empty() &&
              updates.services.to_delete.empty());
  EXPECT_TRUE(updates.branches.to_update.empty() &&
              updates.branches.to_delete.empty());
  EXPECT_TRUE(updates.hosts.to_update.empty() &&
              updates.hosts.to_delete.empty());
  EXPECT_TRUE(updates.domains.to_update.empty() &&
              updates.domains.to_delete.empty());
}

TEST(TestServicesUpdater, TestGetUpdatesNewService) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  clownductor_services_map[models::ServiceId(2)] =
      std::make_shared<models::Service>(CreateModelService2());

  hejmdal::external::detail::services::TablesUpdates expected_table_updates =
      AsUpdates(CreateTableService2());

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 2u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 2u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesServiceUpdated) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1WithMaintainer());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {models::UserName{"user1"}},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesServiceDeleted) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_delete = {models::ServiceId(1)};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 0u);
  ASSERT_EQ(updates.services.to_delete.size(), 1u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesNewBranch) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  clownductor_services_map[models::ServiceId(1)]->AddBranch(
      models::ServiceBranch{
          models::BranchId{5}, {}, models::EnvironmentType::kUnstable});

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.branches.to_update = {
      models::postgres::Branch{models::BranchId{5}, models::ServiceId{1},
                               models::EnvironmentType::kUnstable, std::nullopt,
                               std::nullopt, std::string()}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 1u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesBranchUpdated) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(
          CreateModelService1WithBranch1AsPreStable());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.branches.to_update = {
      models::postgres::Branch{models::BranchId{1}, models::ServiceId{1},
                               models::EnvironmentType::kPreStable,
                               std::nullopt, std::nullopt, std::string()}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.branches.to_update.size(), 1u);
  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesBranchDeleted) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1WithoutBranch2());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.branches.to_delete = {models::BranchId{2}};
  expected_table_updates.hosts.to_delete = {models::HostName("h2")};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 1u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 1u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesNewDomain) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  clownductor_services_map[models::ServiceId(1)]
      ->GetAllEnvBranches()
      .at(models::EnvironmentType::kStable)
      .front()
      .AddDomain(models::BranchDomain{"domain.name", "domain_solomon_object"});

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.domains.to_update = {models::postgres::BranchDomain{
      models::BranchId{2}, "domain_solomon_object", "domain.name"}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 1u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesDomainDeleted) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());
  table_services_map[models::ServiceId(1)]
      ->GetAllEnvBranches()
      .at(models::EnvironmentType::kStable)
      .front()
      .AddDomain(models::BranchDomain{"domain.name", "domain_solomon_object"});

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.domains.to_delete = {
      {models::BranchId{2}, "domain_solomon_object"}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 1u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesDomainUpdated) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  table_services_map[models::ServiceId(1)]
      ->GetAllEnvBranches()
      .at(models::EnvironmentType::kStable)
      .front()
      .AddDomain(models::BranchDomain{"domain.name", "domain_solomon_object"});

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  clownductor_services_map[models::ServiceId(1)]
      ->GetAllEnvBranches()
      .at(models::EnvironmentType::kStable)
      .front()
      .AddDomain(
          models::BranchDomain{"CHANGED_domain.name", "domain_solomon_object"});

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.domains.to_update = {models::postgres::BranchDomain{
      models::BranchId{2}, "domain_solomon_object", "CHANGED_domain.name"}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 1u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesNewHost) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1WithHost6());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.hosts.to_update = {models::postgres::BranchHost{
      models::HostName{"h6"}, models::BranchId{2}, models::DataCenter{"vla"}}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 1u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesHostDeleted) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1WithHost6());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.hosts.to_delete = {models::HostName{"h6"}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 0u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 1u);

  EXPECT_EQ(updates, expected_table_updates);
}

TEST(TestServicesUpdater, TestGetUpdatesNewBranchSameEnv) {
  models::ServiceMap table_services_map;
  table_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(CreateModelService1());

  models::ServiceMap clownductor_services_map;
  clownductor_services_map[models::ServiceId(1)] =
      std::make_shared<models::Service>(
          CreateModelService1WithTwoStableBranches());

  external::detail::services::TablesUpdates expected_table_updates;
  expected_table_updates.services.to_update = {
      models::postgres::Service{models::ServiceId(1),
                                models::ServiceName("s1"),
                                "nanny",
                                time::TimePoint(),
                                false,
                                models::ProjectId(1),
                                models::ProjectName("project"),
                                {},
                                "service_link",
                                models::TvmName("s1"),
                                std::nullopt}};
  expected_table_updates.branches.to_update = {
      models::postgres::Branch{models::BranchId{3}, models::ServiceId{1},
                               models::EnvironmentType::kStable, std::nullopt,
                               std::nullopt, std::string()}};

  auto updates = external::detail::services::GetServicesUpdates(
      clownductor_services_map, table_services_map);

  ASSERT_EQ(updates.services.to_update.size(), 1u);
  ASSERT_EQ(updates.services.to_delete.size(), 0u);
  ASSERT_EQ(updates.branches.to_update.size(), 1u);
  ASSERT_EQ(updates.branches.to_delete.size(), 0u);
  ASSERT_EQ(updates.domains.to_update.size(), 0u);
  ASSERT_EQ(updates.domains.to_delete.size(), 0u);
  ASSERT_EQ(updates.hosts.to_update.size(), 0u);
  ASSERT_EQ(updates.hosts.to_delete.size(), 0u);

  EXPECT_EQ(updates, expected_table_updates);
}

}  // namespace hejmdal
