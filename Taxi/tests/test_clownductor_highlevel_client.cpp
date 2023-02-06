#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <clients/clownductor/client_mock_base.hpp>

#include <clients/clownductor/clownductor_highlevel_client.hpp>
#include <clients/clownductor/detail/clownductor_gen_client.hpp>

namespace hejmdal {

namespace {

namespace cc = ::clients::clownductor;

class MockClownductorGenClient : public ::clients::clownductor::ClientMockBase {
 public:
  cc::v1_services_search::get::Response tvmGetServicesSearch(
      const cc::v1_services_search::get::Request& request,
      const cc::CommandControl&) const override {
    EXPECT_EQ(request.name, std::string{});
    cc::v1_services_search::get::Response resp;
    auto project = cc::ServiceSearchEntry{1, "test_project", {}};
    {
      auto service = cc::ServiceResponse{};
      service.id = 1;
      service.name = "test_service1";
      service.cluster_type = "nanny";
      project.services.push_back(service);
    }
    {
      auto service = cc::ServiceResponse{};
      service.id = 2;
      service.name = "test_service2";
      service.cluster_type = "conductor";
      project.services.push_back(service);
    }
    resp.projects.push_back(project);
    return resp;
  }

  cc::v1_services::get::Response tvmGetServices(
      const cc::v1_services::get::Request& request,
      const cc::CommandControl&) const override {
    EXPECT_TRUE(request.service_id.has_value());
    cc::v1_services::get::Response resp;
    switch (request.service_id.value()) {
      case 1: {
        auto service = cc::ServiceResponse{};
        service.id = 1;
        service.name = "test_service1";
        service.cluster_type = "nanny";
        service.project_id = 1;
        service.project_name = "project";
        resp.body.push_back(service);
        break;
      }
      case 2: {
        auto service = cc::ServiceResponse{};
        service.id = 2;
        service.name = "test_service2";
        service.cluster_type = "conductor";
        service.project_id = 1;
        service.project_name = "project";
        resp.body.push_back(service);
        break;
      }
      default:
        break;
    }
    return resp;
  }

  cc::v1_parameters_service_values::get::Response tvmGetServiceValues(
      const cc::v1_parameters_service_values::get::Request& request,
      const cc::CommandControl&) const override {
    cc::v1_parameters_service_values::get::Response resp;
    switch (request.service_id) {
      case 1: {
        EXPECT_EQ(request.branch_id.value(), 13);
        auto subsystem = cc::SubsystemItem{};
        subsystem.subsystem_name = "abc";
        auto parameter = cc::ParameterItem{};
        parameter.name = "maintainers";
        std::vector<std::variant<std::string, double, bool, cc::ValueItemT3AT3>>
            maintainers{std::string{"user_1"}, std::string{"user_2"}};
        parameter.value = maintainers;
        subsystem.parameters.push_back(parameter);
        resp.subsystems.push_back(subsystem);
        break;
      }
      case 2: {
        EXPECT_EQ(request.branch_id.value(), 22);
        auto subsystem = cc::SubsystemItem{};
        subsystem.subsystem_name = "abc";
        auto parameter = cc::ParameterItem{};
        parameter.name = "maintainers";
        std::vector<std::variant<std::string, double, bool, cc::ValueItemT3AT3>>
            maintainers{std::string{"user_3"}, std::string{"user_4"}};
        parameter.value = maintainers;
        subsystem.parameters.push_back(parameter);
        resp.subsystems.push_back(subsystem);
        break;
      }
      default:
        break;
    }
    return resp;
  }

  cc::v1_branches::get::Response tvmGetBranches(
      const cc::v1_branches::get::Request& request,
      const cc::CommandControl&) const override {
    EXPECT_TRUE(request.service_id);
    cc::v1_branches::get::Response resp;
    switch (*request.service_id) {
      case 1: {
        {
          auto branch = cc::BranchResponse{};
          branch.id = 11;
          branch.env = "testing";
          branch.direct_link = "test_service1_test";
          branch.name = "test_branch_name";
          resp.body.push_back(branch);
        }
        {
          auto branch = cc::BranchResponse{};
          branch.id = 12;
          branch.env = "prestable";
          branch.direct_link = "test_service1_pre_stable";
          branch.name = "test_branch_name";
          resp.body.push_back(branch);
        }
        {
          auto branch = cc::BranchResponse{};
          branch.id = 13;
          branch.env = "stable";
          branch.direct_link = "test_service1_stable";
          branch.name = "test_branch_name";
          resp.body.push_back(branch);
        }
        break;
      }
      case 2: {
        {
          auto branch = cc::BranchResponse{};
          branch.id = 21;
          branch.env = "testing";
          branch.direct_link = "test_service2_test";
          branch.name = "test_branch_name";
          resp.body.push_back(branch);
        }
        {
          auto branch = cc::BranchResponse{};
          branch.id = 22;
          branch.env = "stable";
          branch.direct_link = "test_service2_stable";
          branch.name = "test_branch_name";
          resp.body.push_back(branch);
        }
        break;
      }
      default:
        break;
    }
    return resp;
  }

  cc::v1_hosts::get::Response tvmGetHosts(
      const cc::v1_hosts::get::Request& request,
      const cc::CommandControl&) const override {
    EXPECT_TRUE(request.branch_id);
    cc::v1_hosts::get::Response resp;
    switch (*request.branch_id) {
      case 11: {
        auto host = cc::HostInfoResponse{};
        host.branch_id = *request.branch_id;
        host.id = 111;
        host.name = "testing_host_111";
        host.datacenter = "vla";
        resp.body.push_back(host);
        break;
      }
      case 12: {
        auto host = cc::HostInfoResponse{};
        host.branch_id = *request.branch_id;
        host.id = 121;
        host.name = "prestable_host_121";
        host.datacenter = "vla";
        resp.body.push_back(host);
        break;
      }
      case 13: {
        {
          auto host = cc::HostInfoResponse{};
          host.branch_id = *request.branch_id;
          host.id = 131;
          host.name = "stable_host_131";
          host.datacenter = "vla";
          resp.body.push_back(host);
        }
        {
          auto host = cc::HostInfoResponse{};
          host.branch_id = *request.branch_id;
          host.id = 132;
          host.name = "stable_host_132";
          host.datacenter = "vla";
          resp.body.push_back(host);
        }
        break;
      }
      case 21: {
        {
          auto host = cc::HostInfoResponse{};
          host.branch_id = *request.branch_id;
          host.id = 211;
          host.name = "testing_host_211";
          host.datacenter = "vla";
          resp.body.push_back(host);
        }
        break;
      }
      case 22: {
        {
          auto host = cc::HostInfoResponse{};
          host.branch_id = *request.branch_id;
          host.id = 221;
          host.name = "stable_host_221";
          host.datacenter = "vla";
          resp.body.push_back(host);
        }
        {
          auto host = cc::HostInfoResponse{};
          host.branch_id = *request.branch_id;
          host.id = 222;
          host.name = "stable_host_222";
          host.datacenter = "vla";
          resp.body.push_back(host);
        }
        break;
      }
      default: {
        EXPECT_TRUE("Bad branch id" && false);
      }
    }
    return resp;
  }
};

}  // namespace

UTEST(TestClownductorHighLevelClient, MainTest) {
  auto gen_client = MockClownductorGenClient();
  auto lowlevel_client =
      std::make_shared<clients::detail::ClownductorGenClient>(gen_client);
  auto client = clients::ClownductorHighLevelClient(lowlevel_client, 4,
                                                    time::Milliseconds{50});

  auto services = client.GetAllServices().services;

  ASSERT_EQ(services.size(), 2);

  std::map<std::string, models::ServicePtr> service_map;
  for (const auto& [service_id, service] : services) {
    service_map.insert({service->GetName(), service});
  }
  EXPECT_EQ(services.size(), service_map.size());

  {
    auto service = service_map["test_service1"];
    EXPECT_EQ(service->GetId(), models::ServiceId(1));
    EXPECT_EQ(service->GetClusterType(), models::ClusterType::kNanny);
    EXPECT_EQ(service->GetName(), "test_service1");
    EXPECT_EQ(service->GetProjectId(), models::ProjectId(1));
    EXPECT_EQ(service->GetProjectName(), models::ProjectName("project"));
    std::vector<models::UserName> maintainers = {models::UserName("user_1"),
                                                 models::UserName("user_2")};
    EXPECT_EQ(service->GetMaintainers(), maintainers);
    std::map<models::EnvironmentType, std::vector<models::ServiceBranch>>
        branches = {
            {models::EnvironmentType::kTesting,
             {models::ServiceBranch{
                 models::BranchId{11},
                 {models::Host{models::HostName("testing_host_111"),
                               models::DataCenter{"vla"}}},
                 models::EnvironmentType::kTesting,
                 "test_service1_test",
                 "test_branch_name"}}},
            {models::EnvironmentType::kPreStable,
             {models::ServiceBranch{
                 models::BranchId{12},
                 {models::Host{models::HostName("prestable_host_121"),
                               models::DataCenter{"vla"}}},
                 models::EnvironmentType::kPreStable,
                 "test_service1_pre_stable",
                 "test_branch_name"}}},
            {models::EnvironmentType::kStable,
             {models::ServiceBranch{
                 models::BranchId{13},
                 {models::Host{models::HostName("stable_host_131"),
                               models::DataCenter{"vla"}},
                  models::Host{models::HostName("stable_host_132"),
                               models::DataCenter{"vla"}}},
                 models::EnvironmentType::kStable,
                 "test_service1_stable",
                 "test_branch_name"}}},
        };
    EXPECT_EQ(service->GetAllEnvBranches(), branches);
    EXPECT_EQ("test_service1_stable",
              *service->GetBranches(models::EnvironmentType::kStable)
                   .front()
                   .GetDirectLink());
  }
  {
    auto service = service_map["test_service2"];
    EXPECT_EQ(service->GetId(), models::ServiceId(2));
    EXPECT_EQ(service->GetClusterType(), models::ClusterType::kConductor);
    EXPECT_EQ(service->GetName(), "test_service2");
    EXPECT_EQ(service->GetProjectId(), models::ProjectId(1));
    EXPECT_EQ(service->GetProjectName(), models::ProjectName("project"));
    std::vector<models::UserName> maintainers = {models::UserName("user_3"),
                                                 models::UserName("user_4")};
    EXPECT_EQ(service->GetMaintainers(), maintainers);
    models::Service::EnvToBranchesMap branches = {
        {models::EnvironmentType::kTesting,
         {models::ServiceBranch{
             models::BranchId{21},
             {models::Host{models::HostName("testing_host_211"),
                           models::DataCenter{"vla"}}},
             models::EnvironmentType::kTesting,
             "test_service2_test",
             "test_branch_name"}}},
        {models::EnvironmentType::kStable,
         {models::ServiceBranch{
             models::BranchId{22},
             {models::Host{models::HostName("stable_host_221"),
                           models::DataCenter{"vla"}},
              models::Host{models::HostName("stable_host_222"),
                           models::DataCenter{"vla"}}},
             models::EnvironmentType::kStable,
             "test_service2_stable",
             "test_branch_name"}}},
    };
    EXPECT_EQ(service->GetAllEnvBranches(), branches);
    EXPECT_EQ("test_service2_stable",
              service->GetBranches(models::EnvironmentType::kStable)
                  .front()
                  .GetDirectLink()
                  .value());
  }
}

}  // namespace hejmdal
