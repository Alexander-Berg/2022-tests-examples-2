#include <gtest/gtest.h>

#include <userver/formats/json/inline.hpp>

#include <radio/selectors/request_container.hpp>
#include <radio/selectors/time_series_selector.hpp>
#include <radio/spec/templates/flows/flow_template_params.hpp>
#include <radio/spec/templates/solomon_flow_spec_template_factory.hpp>

namespace hejmdal::radio {

models::Host MockHost() {
  return models::Host{models::HostName{"host3"},
                      models::DataCenter{"datacenter"}};
}

models::BranchDomain MockDomain() {
  return models::BranchDomain{"domain_name", "domain_solomon_object"};
}

models::ServiceBranch MockBranch() {
  return models::ServiceBranch{models::BranchId{1},
                               {MockHost()},
                               models::EnvironmentType::kStable,
                               "service2_branch_direct_link",
                               "branch_name",
                               {MockDomain()}};
}

models::ServiceCPtr MockService() {
  auto service = std::make_shared<models::Service>(
      models::ServiceId(2), "service2", models::ClusterType::kNanny,
      models::ServiceLink("service_link"), models::ProjectId(1),
      models::ProjectName("project"),
      std::vector<models::UserName>{models::UserName("user1")},
      models::TvmName("service2"), std::nullopt);
  service->AddBranch(MockBranch());
  return service;
}

static const models::Host kHost = MockHost();
static const models::BranchDomain kDomain = MockDomain();
static const models::ServiceBranch kBranch = MockBranch();
static const models::ServiceCPtr kService = MockService();

void TestRequestPrograms(
    const std::unique_ptr<spec::FlowSpecificationTemplate>& flow_tpl,
    const spec::FlowParams& flow_params, const std::string& expected_program,
    const std::string& expected_batch_program, const char* test_case) {
  auto flow_spec =
      flow_tpl->Build({kService, kBranch, kHost, kDomain, flow_params});
  auto now = std::chrono::system_clock::from_time_t(1000000);
  selectors::RequestContainer requests;
  auto getter = flow_spec.selector->MakeRequest(
      time::TimeRange(now - time::Minutes(10), now), requests);

  ASSERT_EQ(requests.GetSolomonRequests().size(), 1u);
  auto& req = requests.GetSolomonRequests().back();
  EXPECT_EQ(req->selector.Get(), expected_program) << test_case;
  EXPECT_EQ(req->batch_fields_selector.Get(), expected_batch_program)
      << test_case;
}

TEST(TestSolomonFlowSpecificationTemplate, MainTest) {
  auto now = time::Now();
  auto selector = hejmdal::clients::utils::SolomonSelectorBuilder{}
                      .Cluster("production_mongo")
                      .Service("mongo_stats")
                      .Application("mongo-stats")
                      .Sensor("test-query-find-one-oplog-duration-ms");
  auto flow_template =
      spec::SolomonFlowSpecTplFactory::MongoLxcQueriesDuration("entry");

  auto flow_spec =
      flow_template->Build({kService,
                            {},
                            models::Host{models::HostName{"host3"},
                                         models::DataCenter{"datacenter"}},
                            {},
                            {}});

  selectors::RequestContainer requests;
  auto getter = flow_spec.selector->MakeRequest(
      time::TimeRange(now - time::Minutes(10), now), requests);

  ASSERT_EQ(requests.GetSolomonRequests().size(), 1u);
  auto& req = requests.GetSolomonRequests().back();
  EXPECT_EQ(req->batch_fields_selector, selector);
  selector.Host("host3").Group("service2_branch_direct_link");
  EXPECT_EQ(req->selector, selector);
}

TEST(TestSolomonFlowSpecificationTemplate, BadRps) {
  auto params1 = formats::json::MakeObject("exclude_codes", "404_rps");
  spec::FlowParams empty_params{};

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluRpsWithExclusion("entry");

    TestRequestPrograms(
        flow_template, params1, "{}",
        "group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='*"
        "_rps',service='dorblu'})",
        "DorbluRpsWithExclusion");
  }

  {
    auto flow_template = spec::SolomonFlowSpecTplFactory::DorbluBadRps("entry");

    TestRequestPrograms(
        flow_template, params1, "{}",
        "group_lines('sum',{cluster='production',"
        "group='dorblu_rtc_service2_branch_direct_link',host='cluster',"
        "object='domain_solomon_object',sensor='errors_rps|"
        "timeouts_rps|4*_rps'"
        ",service='dorblu',sensor!='404_rps'})",
        "DorbluBadRps");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluBadRpsBound("entry");

    TestRequestPrograms(
        flow_template, params1, "{}",
        "\ngroup_lines('max',\nflatten(\nmoving_percentile(avg(shift(group_"
        "lines('sum',{cluster='production',group='dorblu_rtc_service2_branch_"
        "direct_link',host='cluster',object='domain_solomon_object',sensor='"
        "errors_rps|timeouts_rps|4*_rps',service='dorblu',sensor!='404_rps'}), "
        "7d)) by 5m, 1h, "
        "50),\nmoving_percentile(avg(shift(group_lines('sum',{cluster='"
        "production',group='dorblu_rtc_service2_branch_direct_link',host='"
        "cluster',object='domain_solomon_object',sensor='errors_rps|timeouts_"
        "rps|4*_rps',service='dorblu',sensor!='404_rps'}), 14d)) by 5m, 1h, "
        "50)\n)\n)\n",
        "DorbluBadRpsBound");
  }

  {
    auto flow_template = spec::SolomonFlowSpecTplFactory::DorbluBadRps("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "group_lines('sum',{cluster='production',group='dorblu_rtc_service2_"
        "branch_direct_link',host='cluster',object='domain_solomon_object',"
        "sensor='errors_rps|timeouts_rps|4*_rps',service='dorblu'})",
        "DorbluBadRps - empty flow params");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluBadRpsBound("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "\ngroup_lines('max',\nflatten(\nmoving_percentile(avg(shift(group_"
        "lines('sum',{cluster='production',group='dorblu_rtc_service2_branch_"
        "direct_link',host='cluster',object='domain_solomon_object',sensor='"
        "errors_rps|timeouts_rps|4*_rps',service='dorblu'}), 7d)) by 5m, 1h, "
        "50),\nmoving_percentile(avg(shift(group_lines('sum',{cluster='"
        "production',group='dorblu_rtc_service2_branch_direct_link',host='"
        "cluster',object='domain_solomon_object',sensor='errors_rps|timeouts_"
        "rps|4*_rps',service='dorblu'}), 14d)) by 5m, 1h, 50)\n)\n)\n",
        "DorbluBadRpsBound - empty flow params");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluBadRpsFraction("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "\nmoving_percentile(last(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='"
        "errors_rps|timeouts_rps|4*_rps',service='dorblu'})) by 1h "
        "/\nlast(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='*"
        "_rps',service='dorblu'})) by 1h, 1d, 50)\n",
        "DorbluBadRpsFraction - empty flow params");
  }

  auto params2 = formats::json::MakeObject(
      "exclude_codes", "404_rps", "exclude_dorblu_objects",
      "some-service_yandex_net_some_handler_GET");

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluBadRpsFraction("entry");

    TestRequestPrograms(
        flow_template, params2, "{}",
        "\nmoving_percentile(last(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='"
        "errors_rps|timeouts_rps|4*_rps',service='dorblu',sensor!='404_rps'}) "
        "- group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler_GET',"
        "sensor='errors_rps|timeouts_rps|4*_rps',service='"
        "dorblu',sensor!='404_rps'})) by 1h /\nlast(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='*"
        "_rps',service='dorblu'}) - group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler_GET',"
        "sensor='*_rps',service='dorblu'})) by 1h, 1d, 50)\n",
        "DorbluBadRpsFraction - exclude handler");
  }

  auto params3 = formats::json::MakeObject(
      "exclude_codes", "403_rps", "exclude_dorblu_objects",
      "some-service_yandex_net_some_handler_GET", "exclude",
      formats::json::MakeArray(
          formats::json::MakeObject("dorblu_object",
                                    "some-service_yandex_net_some_handler2_GET",
                                    "codes", "404_rps"),
          formats::json::MakeObject("dorblu_object",
                                    "some-service_yandex_net_some_handler3_GET",
                                    "codes", "404_rps|409_rps")));

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluBadRpsFraction("entry");

    TestRequestPrograms(
        flow_template, params3, "{}",
        "\nmoving_percentile(last(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='"
        "errors_rps|timeouts_rps|4*_rps',service='dorblu',sensor!='403_rps'}) "
        "- group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler_GET',"
        "sensor='errors_rps|timeouts_rps|4*_rps',service='"
        "dorblu',sensor!='403_rps'}) - group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler2_GET',"
        "sensor='404_rps',service='dorblu',sensor!='403_rps'}) "
        "- group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler3_GET',"
        "sensor='404_rps|409_rps',service='dorblu',sensor!='403_"
        "rps'})) by 1h /\nlast(group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',sensor='*"
        "_rps',service='dorblu'}) - group_lines('sum',"
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='some-service_yandex_net_some_handler_GET',"
        "sensor='*_rps',service='dorblu'})) by 1h, 1d, 50)\n",
        "DorbluBadRpsFraction - exclude handler "
        "and two (handler, code) pairs");
  }
}

TEST(TestSolomonFlowSpecificationTemplate, MdbCpuLowUsage) {
  spec::FlowParams empty_params{};

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::MdbLowCpuUsage("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{cid='service2_branch_direct_link'}",
        "100 * "
        "avg({cid='service2_branch_direct_link',cluster='internal-mdb_dom0',"
        "host='by_cid_container',name='/porto/cpu_usage',service='dom0'} / "
        "{cid='service2_branch_direct_link',cluster='internal-mdb_dom0',"
        "host='by_cid_container',name='/porto/cpu_limit',service='dom0'}) by "
        "cid",
        "MdbLowCpuUsage");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::MdbLowCpuLimit("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{cid='service2_branch_direct_link'}",
        "avg({cid='service2_branch_direct_link',cluster='internal-mdb_dom0',"
        "host='by_cid_container',name='/porto/cpu_limit',service='dom0'}) by "
        "cid",
        "MdbLowCpuLimit");
  }
}

TEST(TestSolomonFlowSpecificationTemplate, PostgresSlowQueries) {
  spec::FlowParams empty_params{};

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::PostgresSlowQueries("entry");

    TestRequestPrograms(
        flow_template, empty_params,
        "{dc='by_host',host='host3',"
        "name='postgres-log_slow_queries',node='by_host',service='mdb'}",
        "{cluster='mdb_service2_branch_direct_link',dc='by_host',"
        "name='postgres-log_slow_queries',node='by_host',service='mdb'}",
        "PostgresSlowQueries");
  }
}

TEST(TestSolomonFlowSpecificationTemplate, MongoLxcSlowQueries) {
  spec::FlowParams empty_params{};

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::MongoLxcSlowQueries("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "group_lines('sum',{application='mongo-stats',"
        "cluster='production_mongo',group='service2_branch_direct_link',"
        "sensor='slow-queries_total',service='mongo_stats'})",
        "MongoLxcSlowQueries");
  }
}

TEST(TestSolomonFlowSpecificationTemplate, DorbluTimings) {
  spec::FlowParams empty_params{};

  {
    auto flow_template = spec::SolomonFlowSpecTplFactory::DorbluRps("entry");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "group_lines('sum',{cluster='production',"
        "group='dorblu_rtc_service2_branch_direct_link',host='cluster',"
        "object='domain_solomon_object',"
        "sensor='*_rps',service='dorblu'})",
        "DorbluRps");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluTimings("entry", "95");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "{cluster='production',group='dorblu_rtc_service2_branch_direct_link',"
        "host='cluster',object='domain_solomon_object',percentile='95',"
        "sensor='ok_request_timings',service='dorblu'}",
        "DorbluTimings");
  }

  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::DorbluTimings7d("entry", "95");

    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "avg(shift({cluster='production',"
        "group='dorblu_rtc_service2_branch_direct_link',host='cluster',"
        "object='domain_solomon_object',percentile='95',"
        "sensor='ok_request_timings',service='dorblu'}, 10020m)) by 5m",
        "DorbluTimings7d");
  }
}

TEST(TestSolomonFlowSpecificationTemplate, RtcLowCpu) {
  spec::FlowParams empty_params{};
  models::EnvironmentTypes testing_env = {models::EnvironmentType::kTesting};
  models::EnvironmentTypes stable_prestable_envs = {
      models::EnvironmentType::kStable, models::EnvironmentType::kPreStable};

  // Stable envs
  {
    auto flow_template = spec::SolomonFlowSpecTplFactory::RtcLowCpuLimit(
        "entry", stable_prestable_envs);
    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "avg(histogram_avg(shift({cluster='host_0',ctype='pre_stable|stable',"
        "service='yasm',signal='portoinst-cpu_limit_slot_hgram'}, 30m))) "
        "by service",
        "RtcLowCpuLimit_stable-prestable");
  }
  {
    auto flow_template = spec::SolomonFlowSpecTplFactory::RtcLowCpuUsage(
        "entry", stable_prestable_envs);
    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "avg(histogram_avg(shift({cluster='host_0',ctype='pre_stable|stable',"
        "service='yasm',signal='portoinst-cpu_limit_usage_perc_hgram'}, 30m)))"
        " by service",
        "RtcLowCpuUsage_stable-prestable");
  }

  // testing env
  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::RtcLowCpuLimit("entry", testing_env);
    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "avg(histogram_avg(shift({cluster='host_0',ctype='testing',service="
        "'yasm',signal='portoinst-cpu_limit_slot_hgram'}, 30m))) by service",
        "RtcLowCpuLimit_testing");
  }
  {
    auto flow_template =
        spec::SolomonFlowSpecTplFactory::RtcLowCpuUsage("entry", testing_env);
    TestRequestPrograms(
        flow_template, empty_params, "{}",
        "avg(histogram_avg(shift({cluster='host_0',ctype='testing',service='"
        "yasm',"
        "signal='portoinst-cpu_limit_usage_perc_hgram'}, 30m))) by service",
        "RtcLowCpuUsage_testing");
  }
}

}  // namespace hejmdal::radio
