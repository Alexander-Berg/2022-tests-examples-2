#pragma once

#include <userver/formats/json.hpp>

#include <clients/sticker/sticker_client.hpp>
#include <models/circuit_state.hpp>
#include <models/link.hpp>
#include <models/service.hpp>

namespace hejmdal::radio {

struct Buffer : public clients::StickerClient {
 public:
  void SendEmail(const clients::models::StickerEmail& email,
                 const std::string& address) const override {
    email_ = email;
    address_ = address;
  }

  mutable clients::models::StickerEmail email_;
  mutable std::string address_;
};

static formats::json::Value kMetaData = [] {
  formats::json::ValueBuilder builder;
  models::Link link{"link text", "link address", std::nullopt};
  models::Link link2{"link text 2", "link address 2",
                     models::LinkType::kYasmChart};
  builder["metric_link_list"].PushBack(link);
  builder["metric_link_list"].PushBack(link2);
  return builder.ExtractValue();
}();

static models::ServicePtr kS1 = []() {
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
      models::EnvironmentType::kTesting,
      std::nullopt,
      "branch_name",
      {},
      std::nullopt});
  return service;
}();

static models::ServicePtr kS2 = []() {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(2), "service2", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("user1")},
      models::TvmName("service2"), std::nullopt);
  service->AddBranch(models::ServiceBranch{
      models::BranchId{2},
      {models::Host{models::HostName{"host3"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kStable,
      "service2_branch_direct_link",
      "branch_name",
      {},
      "https://grafana.yandex-team.ru/some_value/service2"});
  service->AddBranch(models::ServiceBranch{
      models::BranchId{3},
      {models::Host{models::HostName{"host4"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kTesting,
      "service2_testing_branch_direct_link",
      "testing_branch_name",
      {},
      "https://grafana.yandex-team.ru/some_value/service2_testing"});
  return service;
}();

static models::ServicePtr kS3 = std::make_shared<models::Service>(
    models::ServiceId(3), "service3_ignore", models::ClusterType::kNanny,
    models::ServiceLink("service_link"), models::ProjectId(1),
    models::ProjectName("project"),
    std::vector<models::UserName>{models::UserName("user5"),
                                  models::UserName("user6")},
    models::TvmName("service3_ignore"), std::nullopt);

static models::ServicePtr kS4 = []() {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(4), "service4", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("user1"),
                                    models::UserName("user2")},
      models::TvmName("service4"), std::nullopt);
  service->AddBranch(models::ServiceBranch{
      models::BranchId{10},
      {models::Host{models::HostName{"host10"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host12"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kStable,
      "service_4_stable",
      "branch_name",
      {},
      std::nullopt});
  service->AddBranch(models::ServiceBranch{
      models::BranchId{11},
      {models::Host{models::HostName{"host11"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host13"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kTesting,
      "service_4_testing",
      "branch_name",
      {},
      std::nullopt});
  return service;
}();

static models::ServicePtr kS5 = []() {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(5), "service5", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(2),
      models::ProjectName("project_2"), std::vector<models::UserName>{},
      models::TvmName("service5"), std::nullopt);
  service->AddBranch(models::ServiceBranch{
      models::BranchId{12},
      {models::Host{models::HostName{"host20"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host21"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kStable,
      "service_5_stable",
      "branch_name",
      {},
      std::nullopt});
  service->AddBranch(models::ServiceBranch{
      models::BranchId{13},
      {models::Host{models::HostName{"host22"}, models::DataCenter{"sas"}},
       models::Host{models::HostName{"host23"}, models::DataCenter{"sas"}}},
      models::EnvironmentType::kTesting,
      "service_5_testing",
      "branch_name",
      {},
      std::nullopt});
  return service;
}();

static models::ServiceMap kServices{{kS1->GetId(), kS1},
                                    {kS2->GetId(), kS2},
                                    {kS3->GetId(), kS3},
                                    {kS4->GetId(), kS4},
                                    {kS5->GetId(), kS5}};

[[maybe_unused]] static models::ServiceCPtr GetService(
    const models::Incident& inc) {
  if (!inc.meta_data || !(*inc.meta_data)["test_service_index"].IsInt()) {
    return kS1;
  }
  return kServices.at(
      models::ServiceId{(*inc.meta_data)["test_service_index"].As<int>() + 1});
}

}  // namespace hejmdal::radio
