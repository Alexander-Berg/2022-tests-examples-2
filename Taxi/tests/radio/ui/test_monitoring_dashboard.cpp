#include <gtest/gtest.h>

#include <models/link.hpp>
#include <models/service.hpp>
#include <radio/meta_data_fields.hpp>
#include <radio/spec/templates/flows/flow_template_params.hpp>
#include <radio/spec/templates/ui/monitoring_dashboard_builder.hpp>
#include <radio/spec/templates/ui/monitoring_dashboard_info.hpp>

namespace hejmdal::radio::spec {

namespace {

struct TestData {
  models::ServiceCPtr service;
  models::ServiceBranch branch;
  models::Host host;
  models::BranchDomain domain;
};

TestData GetTestData(const std::string& service_name,
                     const std::string& branch_name,
                     const std::string& host_name,
                     const std::string& datacenter,
                     const std::string& direct_link) {
  const auto host =
      models::Host{models::HostName{host_name}, models::DataCenter{datacenter}};
  const auto domain = models::BranchDomain{"domain_name", "solomon_object"};
  const auto branch = models::ServiceBranch(
      models::BranchId(1), {host}, models::EnvironmentType::kStable,
      direct_link, branch_name, {domain},
      "https://grafana.yandex-team.ru/d/abcd12345/test_test");
  auto service = std::make_shared<models::Service>(
      models::ServiceId(1), service_name, models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("maintainer")},
      models::TvmName(service_name), std::nullopt);
  service->AddBranch(branch);

  return TestData{service, branch, host, domain};
}

TestData GetDefaultTestData() {
  return GetTestData("service_name", "branch_name", "host_name", "datacenter",
                     "direct_link");
}

void CheckLink(std::optional<models::Link> link, std::string url_base,
               const http::Args& expected_args) {
  // Check type
  EXPECT_TRUE(link.has_value());
  EXPECT_EQ(link->type, models::LinkType::kYandexMonitoringDashboard);

  // Check url base
  const auto& url = link->address;
  EXPECT_EQ(http::ExtractMetaTypeFromUrl(url), url_base);

  // Check url args
  const auto url_args = http::UrlDecode(url.substr(url_base.size()));
  for (const auto& [expected_arg_name, expected_arg_val] : expected_args) {
    auto pos = url_args.find(expected_arg_name);
    EXPECT_NE(pos, std::string::npos);
    const auto actual_arg_name = url_args.substr(pos, expected_arg_name.size());
    EXPECT_EQ(actual_arg_name, expected_arg_name);
    const auto actual_arg_val = url_args.substr(
        pos + expected_arg_name.size() + 1, expected_arg_val.size());
    EXPECT_EQ(actual_arg_val, expected_arg_val);
  }
}

}  // namespace

TEST(TestMonitoringDashboard, BuildDorbluAlertDashboardMeta) {
  const auto test_data = GetDefaultTestData();
  const auto base_url =
      "https://monitoring.yandex-team.ru/projects/hejmdal/dashboards/"
      "monf71d8rjp4lu3dcm2c";
  FlowTemplateParams params{test_data.service,
                            test_data.branch,
                            test_data.host,
                            test_data.domain,
                            {}};
  /// Build
  auto dashboard_info = BadRpsDashboardBuilder().BuildMeta(params).value();

  /// Serialize and check
  ASSERT_EQ(dashboard_info["base_url"].As<std::string>(), base_url);
  ASSERT_EQ(dashboard_info["params"].GetSize(), 12);

  /// Create meta
  formats::json::ValueBuilder builder;
  builder[meta::kProjectName] = test_data.service->GetProjectName();
  builder[meta::kServiceName] = test_data.service->GetName();
  builder[meta::kServiceId] = test_data.service->GetId();
  builder[meta::kBranchName] = test_data.branch.GetBranchName();
  builder[meta::kEnv] = models::ToString(test_data.branch.GetEnv());
  builder[meta::kGrafanaDashboardLink] =
      test_data.service->GetGrafanaDashboardLink(test_data.branch).value();
  builder[meta::kYasmDashboardLink] =
      test_data.service->GetYasmDashboardLink(test_data.branch).value();
  builder[meta::kDomain] =
      test_data.domain.name + "::" + test_data.domain.solomon_object;
  builder[meta::kYandexMonitoringDashboardLink] = dashboard_info;
  builder[meta::kDomains] = "first.domain, second.domain";
  builder[meta::kDorbluObjects] = "first_object|second_object";

  /// Parse and build link
  blocks::State state{blocks::State::Value::kWarn, "alert description"};
  blocks::Meta meta(builder.ExtractValue());
  time::TimePoint tp = time::From<time::Seconds>(100);
  auto link =
      MonitoringDashboardInfo::BuildDashboardLinkFromMeta(state, meta, tp);
  http::Args args;
  args["p.project_name"] = test_data.service->GetProjectName().GetUnderlying();
  args["p.service_name"] = test_data.service->GetName();
  args["p.service_id"] =
      std::to_string(test_data.service->GetId().GetUnderlying());
  args["p.branch_name"] = test_data.branch.GetBranchName();
  args["p.env"] = models::ToString(test_data.branch.GetEnv());
  args["p.dorblu_group"] = "dorblu_rtc_direct_link";
  args["p.root_dorblu_object"] = "solomon_object";
  args["p.admin_page_link"] = test_data.service->GetAdminPageLink().address;
  args["p.domains"] = "first.domain, second.domain";
  args["p.dorblu_objects"] = "first_object|second_object";
  CheckLink(link, base_url, args);
}

}  // namespace hejmdal::radio::spec
