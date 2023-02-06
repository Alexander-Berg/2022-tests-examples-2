#include <gtest/gtest.h>

#include <fmt/format.h>

#include <userver/formats/json/inline.hpp>

#include <models/link.hpp>
#include <models/service.hpp>
#include <radio/spec/templates/flows/flow_template_params.hpp>
#include <radio/spec/templates/solomon_flow_spec_template_factory.hpp>
#include <radio/spec/templates/ui/spec_template_monitoring.hpp>

namespace hejmdal::radio::spec {

std::string GetMonitoringServiceName(models::ServiceCPtr service_ptr) {
  const auto service_name = service_ptr->GetName();
  if (!service_name.empty() && service_name != "taxi" &&
      service_name != "internal-mdb") {
    return "yasm_" + service_name;
  }
  return service_name;
}

struct TestData {
  models::ServiceCPtr service;
  models::ServiceBranch branch;
  models::Host host;
};

TestData GetTestData(const std::string& service_name,
                     const std::string& branch_name,
                     const std::string& host_name,
                     const std::string& datacenter,
                     const std::string& direct_link) {
  const auto host =
      models::Host{models::HostName{host_name}, models::DataCenter{datacenter}};
  const auto branch = models::ServiceBranch(models::BranchId(1), {host},
                                            models::EnvironmentType::kStable,
                                            direct_link, branch_name);
  auto service = std::make_shared<models::Service>(
      models::ServiceId(1), service_name, models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("maintainer")},
      models::TvmName(service_name), std::nullopt);
  service->AddBranch(branch);

  return TestData{service, branch, host};
}

TestData GetTestData() {
  return GetTestData("service_name", "branch_name", "host_name", "datacenter",
                     "direct_link");
}

void CheckLink(std::optional<models::Link> link, std::string service_name,
               const http::Args& expected_args) {
  // Check type
  EXPECT_TRUE(link.has_value());
  EXPECT_EQ(link->type, models::LinkType::kYandexMonitoring);

  // Check url base
  const auto& url = link->address;
  const auto url_base_tpl =
      "https://monitoring.yandex-team.ru/projects/{}/explorer/legend";
  const auto url_base = fmt::format(url_base_tpl, service_name);
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

TEST(TestSpecMonitoring, YasmSignalCpu) {
  Monitoring cpu_monitoring;
  cpu_monitoring.SetYTitle("CPU usage, %")
      .AddGraph({std::move(spec::MonitoringQuery::FromYasmSignal(
                               "portoinst-cpu_limit_usage_perc_hgram")
                               .AddFunction<spec::Quant>(50)),
                 "used/limit"});

  const auto [service, branch, host] =
      GetTestData("core-jobs", "",
                  "eda-core-jobs-stable-21.sas.yp-c.yandex.net", "sas", "");
  auto monitoring_link = cpu_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias(histogram_percentile(50,{project='yasm_core-jobs',service='yasm',"
      "cluster='host_0',host='eda-core-jobs-stable-21.sas.yp-c.yandex.net',"
      "signal='portoinst-cpu_limit_usage_perc_hgram'}),'used/limit')";
  args["y_title"] = "CPU usage, %";
  CheckLink(monitoring_link, "taxi", args);
};

TEST(TestSpecMonitoring, YasmSignalCpuForAllHosts) {
  Monitoring cpu_monitoring;
  cpu_monitoring.SetYTitle("CPU usage, %")
      .AddGraph({std::move(spec::MonitoringQuery::FromYasmSignalForAllHosts(
                               "portoinst-cpu_limit_usage_perc_hgram")
                               .AddFunction<spec::Average>()),
                 "CPU usage ({{host}})"});

  const auto [service, branch, host] =
      GetTestData("core-jobs", "", "", "sas", "");
  auto monitoring_link = cpu_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias(histogram_avg({project='yasm_core-jobs',service='yasm',"
      "cluster='host_0',host='*',ctype='stable',"
      "signal='portoinst-cpu_limit_usage_perc_hgram'}),'CPU usage ({{host}})')";
  args["y_title"] = "CPU usage, %";
  CheckLink(monitoring_link, "taxi", args);
};

TEST(TestSpecMonitoring, YasmSignalMemory) {
  spec::Monitoring memory_monitoring;
  memory_monitoring.SetYTitle("RAM usage, %")
      .AddGraph(
          {std::move(spec::MonitoringQuery::FromYasmSignal(
                         "portoinst-memory_anon_unevict_limit_usage_perc_hgram")
                         .AddFunction<spec::Quant>(50)),
           "used/limit"});

  const auto [service, branch, host] =
      GetTestData("core-jobs", "",
                  "eda-core-jobs-stable-21.sas.yp-c.yandex.net", "sas", "");
  auto monitoring_link = memory_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias(histogram_percentile(50,{project='yasm_core-jobs',service='yasm',"
      "cluster='host_0',host='eda-core-jobs-stable-21.sas.yp-c.yandex.net',"
      "signal='portoinst-memory_anon_unevict_limit_usage_perc_hgram'}),"
      "'used/limit')";
  args["y_title"] = "RAM usage, %";
  CheckLink(monitoring_link, "taxi", args);
}

TEST(TestSpecMonitoring, MdbCpu) {
  spec::Monitoring cpu_monitoring("internal-mdb");
  cpu_monitoring.SetYTitle("CPU usage")
      .AddGraph({spec::MonitoringQuery::FromMdbCpuRamUsageSensor(
                     spec::sensors::kMdbCpuUsage),
                 "usage"})
      .AddGraph({spec::MonitoringQuery::FromMdbCpuRamUsageSensor(
                     spec::sensors::kMdbCpuTotal),
                 "limit"});

  const auto [service, branch, host] =
      GetTestData("driver-hiring-mongo", "",
                  "vla-t376x3ti06gv0hab.db.yandex.net", "vla", "");
  auto monitoring_link = cpu_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias({project='internal-mdb',service='dom0',cluster='internal-mdb_dom0'"
      ","
      "container='vla-t376x3ti06gv0hab.db.yandex.net',cid='by_container',"
      "name='/porto/cpu_usage'},'usage')";
  args["q.1.text"] =
      "alias({project='internal-mdb',service='dom0',cluster='internal-mdb_dom0'"
      ","
      "container='vla-t376x3ti06gv0hab.db.yandex.net',cid='by_container',"
      "name='/porto/cpu_limit'},'limit')";
  args["y_title"] = "CPU usage";
  CheckLink(monitoring_link, "internal-mdb", args);
}

TEST(TestSpecMonitoring, MdbRam) {
  spec::Monitoring ram_monitoring("internal-mdb");
  ram_monitoring.SetYTitle("RAM usage")
      .AddGraph({spec::MonitoringQuery::FromMdbCpuRamUsageSensor(
                     spec::sensors::kMdbRamUsage),
                 "usage"})
      .AddGraph({spec::MonitoringQuery::FromMdbCpuRamUsageSensor(
                     spec::sensors::kMdbRamTotal),
                 "limit"});

  const auto [service, branch, host] = GetTestData(
      "grocery-order-log", "", "sas-18wzh4gxt7qvstha.db.yandex.net", "sas", "");
  auto monitoring_link = ram_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias({project='internal-mdb',service='dom0',cluster='internal-mdb_dom0'"
      ","
      "container='sas-18wzh4gxt7qvstha.db.yandex.net',cid='by_container',"
      "name='/porto/anon_usage'},'usage')";
  args["q.1.text"] =
      "alias({project='internal-mdb',service='dom0',cluster='internal-mdb_dom0'"
      ","
      "container='sas-18wzh4gxt7qvstha.db.yandex.net',cid='by_container',"
      "name='/porto/anon_limit'},'limit')";
  args["y_title"] = "RAM usage";
  CheckLink(monitoring_link, "internal-mdb", args);
}

TEST(TestSpecMonitoring, MdbDisk) {
  spec::Monitoring disk_monitoring("internal-mdb");
  disk_monitoring.SetYTitle("Disk usage")
      .AddGraph({spec::MonitoringQuery::FromMdbDiskUsageSensor(
                     std::move("disk-used_bytes_pgdata")),
                 "usage"})
      .AddGraph({spec::MonitoringQuery::FromMdbDiskUsageSensor(
                     std::move("disk-total_bytes_pgdata")),
                 "limit"});

  const auto [service, branch, host] = GetTestData(
      "dwh-pgaas", "", "sas-nvemmzgj2pnozmvz.db.yandex.net", "sas", "");
  auto monitoring_link = disk_monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias({project='internal-mdb',dc='by_host',"
      "host='sas-nvemmzgj2pnozmvz.db.yandex.net',"
      "name='disk-used_bytes_pgdata'},'usage')";
  args["q.1.text"] =
      "alias({project='internal-mdb',dc='by_host',"
      "host='sas-nvemmzgj2pnozmvz.db.yandex.net',"
      "name='disk-total_bytes_pgdata'},'limit')";
  args["y_title"] = "Disk usage";
  CheckLink(monitoring_link, "internal-mdb", args);
}

TEST(TestSpecMonitoring, TimingsAndRps) {
  spec::Monitoring monitoring("taxi");
  monitoring.SetYTitle("Timings")
      .SetRightYTitle("RPS")
      .AddGraph({MonitoringQuery::FromFlowTemplate(
                     SolomonFlowSpecTplFactory::DorbluTimings("", "95")),
                 "timings"})
      .AddGraph({MonitoringQuery::FromFlowTemplate(
                     SolomonFlowSpecTplFactory::DorbluTimings7d("", "95")),
                 "timings-7d"})
      .AddRightGraph({MonitoringQuery::FromFlowTemplate(
                          SolomonFlowSpecTplFactory::DorbluRps("")),
                      "rps"});

  const auto [service, branch, host] = GetTestData(
      "taxi-billing-reports", "", "", "", "taxi_taxi-billing-reports_stable");
  const auto domain =
      models::BranchDomain{"domain", "billing-reports_taxi_yandex_net"};
  auto monitoring_link = monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, domain, {}});
  http::Args args;
  args["q.0.text"] =
      "alias({cluster='production',"
      "group='dorblu_rtc_taxi_taxi-billing-reports_stable',host='cluster',"
      "object='billing-reports_taxi_yandex_net',percentile='95',project='taxi',"
      "sensor='ok_request_timings',service='dorblu'},'timings')";
  args["q.1.text"] =
      "alias(avg(shift({cluster='production',"
      "group='dorblu_rtc_taxi_taxi-billing-reports_stable',host='cluster',"
      "object='billing-reports_taxi_yandex_net',percentile='95',project='taxi',"
      "sensor='ok_request_timings',service='dorblu'}, 10020m)) by 5m,"
      "'timings-7d')";
  args["q.2.text"] =
      "alias(group_lines('sum',{cluster='production',"
      "group='dorblu_rtc_taxi_taxi-billing-reports_stable',"
      "host='cluster',object='billing-reports_taxi_yandex_net',project='taxi',"
      "sensor='*_rps',service='dorblu'}),'rps')";
  args["q.2.axis"] = "r";
  args["y_title"] = "Timings";
  args["yr_title"] = "RPS";
  CheckLink(monitoring_link, "taxi", args);
}

TEST(TestSpecMonitoring, MongoOplogQuery) {
  spec::Monitoring monitoring("taxi");
  monitoring.SetYTitle("Duration, ms")
      .SetRightYTitle("Failures")
      .AddGraph({MonitoringQuery::FromFlowTemplate(
                     SolomonFlowSpecTplFactory::MongoLxcQueriesDuration("")),
                 "duration"})
      .AddRightGraph(
          spec::MonitoringGraph(
              spec::MonitoringQuery::FromFlowTemplate(
                  spec::SolomonFlowSpecTplFactory::MongoLxcQueriesFailures("")),
              "failures")
              .SetColor(180, 0, 0))
      .SetConnectPoints(false);

  const auto [service, branch, host] =
      GetTestData("minor", "", "minor-mrs-shard2-dev-vla-01.taxi.yandex.net",
                  "vla", "taxi_db_mongo_minor_shard2_dev");
  auto monitoring_link = monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] =
      "alias({application='mongo-stats',cluster='production_mongo',"
      "group='taxi_db_mongo_minor_shard2_dev',"
      "host='minor-mrs-shard2-dev-vla-01.taxi.yandex.net',project='taxi',"
      "sensor='test-query-find-one-oplog-duration-ms',service='mongo_stats'},"
      "'duration')";
  args["q.1.text"] =
      "alias({application='mongo-stats',cluster='production_mongo',"
      "group='taxi_db_mongo_minor_shard2_dev',"
      "host='minor-mrs-shard2-dev-vla-01.taxi.yandex.net',project='taxi',"
      "sensor='test-query-find-one-oplog-failure',service='mongo_stats'},"
      "'failures')";
  args["q.1.axis"] = "r";
  args["y_title"] = "Duration, ms";
  args["yr_title"] = "Failures";
  args["dsp_fill"] = "null";
  args["legend.failures.color"] = "b40000";
  CheckLink(monitoring_link, "taxi", args);
}

TEST(TestSpecMonitoring, BadRps) {
  spec::Monitoring monitoring("taxi");
  monitoring.SetLinkText("RPS и Bad RPS")
      .SetYTitle("Bad RPS")
      .SetRightYTitle("RPS")
      .AddGraph(
          MonitoringGraph(MonitoringQuery::FromFlowTemplate(
                              SolomonFlowSpecTplFactory::DorbluBadRps("")),
                          "bad rps")
              .SetColor(255, 0, 0))
      .AddRightGraph(
          MonitoringGraph(
              MonitoringQuery::FromFlowTemplate(
                  SolomonFlowSpecTplFactory::DorbluRpsWithExclusion("")),
              "rps")
              .SetColor(0, 255, 0));

  const auto [service, branch, host] =
      GetTestData("", "", "", "", "taxi_order-core_stable");
  const auto domain = models::BranchDomain{"order-core.taxi.yandex.net",
                                           "order-core_taxi_yandex_net"};
  auto monitoring_link = monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, domain, {}});
  http::Args args;
  args["q.0.text"] =
      "alias(group_lines('sum',{cluster='production',"
      "group='dorblu_rtc_taxi_order-core_stable',host='cluster',"
      "object='order-core_taxi_yandex_net',project='taxi',"
      "sensor='errors_rps|timeouts_rps|4*_rps',service='dorblu'}),'bad rps')";
  args["q.1.text"] =
      "alias(group_lines('sum',{cluster='production',"
      "group='dorblu_rtc_taxi_order-core_stable',host='cluster',"
      "object='order-core_taxi_yandex_net',project='taxi',sensor='*_rps',"
      "service='dorblu'}),"
      "'rps')";
  args["q.1.axis"] = "r";
  args["y_title"] = "Bad RPS";
  args["yr_title"] = "RPS";
  args["legend.rps.color"] = "00ff00";
  args["legend.bad rps.color"] = "ff0000";
  CheckLink(monitoring_link, "taxi", args);
}

TEST(TestSpecMonitoring, BadRpsWithExcludedDomains) {
  spec::Monitoring monitoring("taxi");
  monitoring.SetLinkText("RPS и Bad RPS")
      .SetYTitle("Bad RPS")
      .SetRightYTitle("RPS")
      .AddGraph(
          MonitoringGraph(MonitoringQuery::FromFlowTemplate(
                              SolomonFlowSpecTplFactory::DorbluBadRps("")),
                          "bad rps")
              .SetColor(255, 0, 0))
      .AddRightGraph(
          MonitoringGraph(
              MonitoringQuery::FromFlowTemplate(
                  SolomonFlowSpecTplFactory::DorbluRpsWithExclusion("")),
              "rps")
              .SetColor(0, 255, 0));

  auto params = formats::json::MakeObject(
      "exclude_codes", "404_rps", "exclude_dorblu_objects",
      "order-core_taxi_yandex_net_v1_tc_active-orders");
  const auto [service, branch, host] =
      GetTestData("", "", "", "", "taxi_order-core_stable");
  const auto domain = models::BranchDomain{"order-core.taxi.yandex.net",
                                           "order-core_taxi_yandex_net"};
  auto monitoring_link = monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, domain, params});
  http::Args args;
  args["q.0.text"] =
      "alias(group_lines('sum',{cluster='production',"
      "group='dorblu_rtc_taxi_order-core_stable',host='cluster',"
      "object='order-core_taxi_yandex_net',project='taxi',"
      "sensor='errors_rps|timeouts_rps|4*_rps',"
      "service='dorblu',sensor!='404_rps'}) - group_lines('sum',"
      "{cluster='production',"
      "group='dorblu_rtc_taxi_order-core_stable',host='cluster',"
      "object='order-core_taxi_yandex_net_v1_tc_active-orders',"
      "project='taxi',sensor='errors_rps|timeouts_rps|4*_rps',"
      "service='dorblu',sensor!='404_rps'}),'bad rps')";
  args["q.1.text"] =
      "alias(group_lines('sum',{cluster='production',"
      "group='dorblu_rtc_taxi_order-core_stable',host='cluster',"
      "object='order-core_taxi_yandex_net',project='taxi',sensor='*_rps',"
      "service='dorblu'}) - group_lines('sum',"
      "{cluster='production',group='dorblu_rtc_taxi_order-core_stable',"
      "host='cluster',object='order-core_taxi_yandex_net_v1_tc_active-orders',"
      "project='taxi',sensor='*_rps',service='dorblu'}),'rps')";
  args["q.1.axis"] = "r";
  args["y_title"] = "Bad RPS";
  args["yr_title"] = "RPS";
  args["legend.rps.color"] = "00ff00";
  args["legend.bad rps.color"] = "ff0000";
  CheckLink(monitoring_link, "taxi", args);
}

TEST(TestSpecMonitoring, AliasWithLet) {
  spec::Monitoring monitoring("taxi");
  monitoring.SetYTitle("Ok rps deviation")
      .AddGraph({spec::MonitoringQuery::FromFlowTemplate(
                     spec::SolomonFlowSpecTplFactory::DorbluOkRpsDeviation("")),
                 "rps deviation"});

  const auto [service, branch, host] =
      GetTestData("driver-hiring-mongo", "",
                  "vla-t376x3ti06gv0hab.db.yandex.net", "vla", "");
  auto monitoring_link = monitoring.GetMonitoringLink(
      FlowTemplateParams{service, branch, host, {}, {}});
  http::Args args;
  args["q.0.text"] = R"=(
let ok_rps_1m = avg({cluster='production',group='dorblu_rtc_',host='cluster',object='',project='taxi',sensor='ok_rps',service='dorblu'}) by 1m;
let ok_rps_5m = avg({cluster='production',group='dorblu_rtc_',host='cluster',object='',project='taxi',sensor='ok_rps',service='dorblu'}) by 5m;
let ok_rps_5m_fixed = ok_rps_5m + shift(ok_rps_5m, 1m) + shift(ok_rps_5m, 2m) + shift(ok_rps_5m, 3m) + shift(ok_rps_5m, 4m);
let ok_rps_1w = shift(ok_rps_5m_fixed, 10050m);
let ok_rps_2w = shift(ok_rps_5m_fixed, 20130m);
let ok_rps_3w = shift(ok_rps_5m_fixed, 30210m);
let valid_points = group_lines('count', flatten(
ok_rps_1m,
ok_rps_1w,
ok_rps_2w,
ok_rps_3w
));
let ok_rps_1w_avg = moving_avg(ok_rps_1w, 1h);
let ok_rps_2w_avg = moving_avg(ok_rps_2w, 1h);
let ok_rps_3w_avg = moving_avg(ok_rps_3w, 1h);
let ok_rps_dev_1w = moving_avg(abs(ok_rps_1w - ok_rps_1w_avg), 1d);
let ok_rps_dev_2w = moving_avg(abs(ok_rps_1w - ok_rps_2w_avg), 1d);
let ok_rps_dev_3w = moving_avg(abs(ok_rps_1w - ok_rps_3w_avg), 1d);
let ok_rps_min_dev = group_lines('min',flatten(ok_rps_dev_1w, ok_rps_dev_2w, ok_rps_dev_3w));
let value = group_lines('min',flatten(
ramp(abs(ok_rps_1m - ok_rps_1w_avg) - ok_rps_min_dev)/ok_rps_1w,
ramp(abs(ok_rps_1m - ok_rps_2w_avg) - ok_rps_min_dev)/ok_rps_2w,
ramp(abs(ok_rps_1m - ok_rps_3w_avg) - ok_rps_min_dev)/ok_rps_3w));
let interval = time_interval(ok_rps_1m);
let valid_value = drop_if(valid_points - 4, value);
let smooth_value = moving_percentile(valid_value, 5m, 50);
let result = crop(drop_above(drop_nan(smooth_value), inf()), interval);alias(
result
,'rps deviation'))=";
  args["y_title"] = "Ok rps deviation";
  CheckLink(monitoring_link, "taxi", args);
}

}  // namespace hejmdal::radio::spec
