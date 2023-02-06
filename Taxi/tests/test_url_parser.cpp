#include <gtest/gtest.h>

#include <fmt/format.h>
#include <utils/url_parser.hpp>

#include <boost/algorithm/string.hpp>

namespace hejmdal {

namespace {

void CheckHostAndPath(const utils::Url& url, std::string host,
                      std::vector<std::string> path) {
  EXPECT_EQ(url.GetHost(), host);
  ASSERT_EQ(url.GetPath().size(), path.size());
  std::size_t i = 0;
  for (const auto& f1 : url.GetPath()) {
    EXPECT_EQ(f1, path[i++]);
  }
}

}  // namespace

void CheckArg(std::string key, std::string exp_val, const utils::Url& url) {
  ASSERT_TRUE(url.HasArg(key));
  EXPECT_EQ(url.GetArg(key), exp_val);
}

TEST(TestUrlParser, MainTest) {
  {
    auto url_str =
        "https://solomon.yandex-team.ru/?"
        "project=taxi&"
        "cluster=production&"
        "service=sys&"
        "l.host=accelerometer-metrics-man-01.taxi.yandex.net&"
        "l.path=%2FCpu%2FPhysicalCpuFrequency%2FAvg&"
        "l.PhysicalCpuId=0&"
        "graph=auto&"
        "b=1d&"
        "e=";
    auto url = utils::UrlParser::Parse(url_str);
    EXPECT_EQ(url.GetHost(), "https://solomon.yandex-team.ru");
    EXPECT_EQ(url.GetPath().size(), 0u);
    CheckArg("project", "taxi", url);
    CheckArg("cluster", "production", url);
    CheckArg("service", "sys", url);
    CheckArg("l.host", "accelerometer-metrics-man-01.taxi.yandex.net", url);
    CheckArg("l.path", "/Cpu/PhysicalCpuFrequency/Avg", url);
    CheckArg("l.PhysicalCpuId", "0", url);
    CheckArg("graph", "auto", url);
    CheckArg("b", "1d", url);
    CheckArg("e", "", url);
  }
  {
    auto url_str =
        "https://solomon.yandex-team.ru/?"
        "project=taxi&"
        "cluster=production_mongo&"
        "service=mongo_stats&"
        "l.sensor=replication-lag&"
        "l.host=main-mrs-shard3-myt-01&"
        "graph=auto&"
        "b=2020-04-14T01%3A44%3A02.879Z&"
        "e=2020-04-15T02%3A10%3A04.325Z";
    auto url = utils::UrlParser::Parse(url_str);
    EXPECT_EQ(url.GetHost(), "https://solomon.yandex-team.ru");
    CheckArg("project", "taxi", url);
    CheckArg("cluster", "production_mongo", url);
    CheckArg("service", "mongo_stats", url);
    CheckArg("l.host", "main-mrs-shard3-myt-01", url);
    CheckArg("l.sensor", "replication-lag", url);
    CheckArg("graph", "auto", url);
    CheckArg("b", "2020-04-14T01:44:02.879Z", url);
    CheckArg("e", "2020-04-15T02:10:04.325Z", url);
  }
}

TEST(TestUrlParser, TestGetArgsIf) {
  auto url_str =
      "https://solomon.yandex-team.ru/?"
      "project=taxi&"
      "cluster=production_mongo&"
      "service=mongo_stats&"
      "l.sensor=replication-lag&"
      "l.host=main-mrs-shard3-myt-01&"
      "graph=auto&"
      "b=2020-04-14T01%3A44%3A02.879Z&"
      "e=2020-04-15T02%3A10%3A04.325Z";
  auto url = utils::UrlParser::Parse(url_str);
  EXPECT_EQ(url.GetHost(), "https://solomon.yandex-team.ru");
  auto args = url.GetArgsIf([](std::string_view key) -> bool {
    return boost::algorithm::starts_with(key, "l.");
  });
  ASSERT_EQ(args.size(), 2u);
  EXPECT_TRUE(args.find("l.sensor") != args.end());
  EXPECT_TRUE(args.find("l.host") != args.end());
}

TEST(TestUrlParser, TestNoParams) {
  auto url_str = "https://solomon.yandex-team.ru";
  auto url = utils::UrlParser::Parse(url_str);
  EXPECT_EQ(url.GetHost(), "https://solomon.yandex-team.ru");
}

TEST(TestUrlParser, TestErrors) {
  auto url_str = "https://solomon.yandex-team.ru/?a=1&a=2";
  EXPECT_ANY_THROW(utils::UrlParser::Parse(url_str));
  url_str = "https://solomon.yandex-team.ru/?a1&b1";
  EXPECT_ANY_THROW(utils::UrlParser::Parse(url_str));
}

TEST(TestUrlParser, TestPathParsing) {
  {
    std::string url_str =
        "https://solomon.yandex-team.ru/admin/projects/taxi/autoGraph";
    auto url = utils::UrlParser::Parse(url_str);
    CheckHostAndPath(url, "https://solomon.yandex-team.ru",
                     {"admin", "projects", "taxi", "autoGraph"});
  }
  {
    std::string url_str =
        "https://solomon.yandex-team.ru/admin/projects/taxi/autoGraph/";
    auto url = utils::UrlParser::Parse(url_str);
    CheckHostAndPath(url, "https://solomon.yandex-team.ru",
                     {"admin", "projects", "taxi", "autoGraph"});
  }
  {
    std::string url_str =
        "https://solomon.yandex-team.ru/admin/projects/taxi/autoGraph/?";
    auto url = utils::UrlParser::Parse(url_str);
    CheckHostAndPath(url, "https://solomon.yandex-team.ru",
                     {"admin", "projects", "taxi", "autoGraph"});
  }
}

TEST(TestUrlParser, TestUrlPath) {
  {
    std::string url_str =
        "https://solomon.yandex-team.ru/admin/projects/taxi/autoGraph";
    auto url = utils::UrlParser::Parse(url_str);
    EXPECT_TRUE(url.GetPath().Has("autoGraph"));
    EXPECT_TRUE(url.GetPath().Has("taxi"));
    EXPECT_TRUE(url.GetPath().Has("admin"));
    EXPECT_TRUE(url.GetPath().Has("projects"));
    EXPECT_FALSE(url.GetPath().Has("missing_folder"));
    EXPECT_EQ(url.GetPath().GetNextTo("projects"), "taxi");
    EXPECT_ANY_THROW(url.GetPath().GetNextTo("autoGraph"));
  }
  {
    std::string url_str = "https://solomon.yandex-team.ru/";
    auto url = utils::UrlParser::Parse(url_str);
    EXPECT_FALSE(url.GetPath().Has("autoGraph"));
    EXPECT_ANY_THROW(url.GetPath().GetNextTo("autoGraph"));
  }
}

TEST(TestUrlParser, TestFindUrls) {
  {
    std::string str =
        "      * 2020-06-11 03:01 (432 min, closed), Warning\n"
        "         description: "
        "taxi-taxi-admin-data-stable-1.sas.yp-c.yandex.net::rtc_resource_usage:"
        ":cpu, limit has been reached: current value = 0.869\n"
        "         links:\n"
        "           * limit, usage -- "
        "https://yasm.yandex-team.ru/chart/"
        "itype=taxi-admin-data;hosts=taxi-taxi-admin-data-stable-1.sas.yp-c."
        "yandex.net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%20max)%"
        "2Cportoinst-cpu_usage_cores_tmmv%7D/\n"
        "      * 2020-06-09 02:40 (429 min, closed), Warning\n"
        "         description: "
        "taxi-taxi-admin-data-stable-1.sas.yp-c.yandex.net::rtc_resource_usage:"
        ":cpu, limit has been reached: current value = 0.801\n"
        "         links:\n"
        "           * limit, usage -- "
        "https://yasm.yandex-team.ru/chart/"
        "itype=taxi-admin-data;hosts=taxi-taxi-admin-data-stable-1.sas.yp-c."
        "yandex.net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%20max)%"
        "7D/\n"
        "more lines";
    auto result = utils::FindUrls(str);
    ASSERT_EQ(2u, result.size());
    EXPECT_EQ(result[0].Str(),
              "https://yasm.yandex-team.ru/chart/"
              "itype=taxi-admin-data;hosts=taxi-taxi-admin-data-stable-1.sas."
              "yp-c.yandex.net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%"
              "2C%20max)%2Cportoinst-cpu_usage_cores_tmmv%7D/");
    EXPECT_EQ(result[1].Str(),
              "https://yasm.yandex-team.ru/chart/"
              "itype=taxi-admin-data;hosts=taxi-taxi-admin-data-stable-1.sas."
              "yp-c.yandex.net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%"
              "2C%20max)%7D/");
  }
  {
    std::string str =
        "taxi-toll-roads-pre-stable-4.sas.yp-c.yandex.net::rtc_resource_usage::"
        "cpu, limit has been reached: current value = 5.975\n"
        "Links:\n"
        " * limit, usage: "
        "https://yasm.yandex-team.ru/chart/"
        "itype=toll-roads;hosts=taxi-toll-roads-pre-stable-4.sas.yp-c.yandex."
        "net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%20max)%"
        "2Cportoinst-cpu_usage_cores_tmmv%7D/"
        "?from=1592583325618&to=1592590525618";
    auto result = utils::FindUrls(str);
    ASSERT_EQ(1u, result.size());
    EXPECT_EQ(result[0].Str(),
              "https://yasm.yandex-team.ru/chart/"
              "itype=toll-roads;hosts=taxi-toll-roads-pre-stable-4.sas.yp-c."
              "yandex.net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%"
              "20max)%2Cportoinst-cpu_usage_cores_tmmv%7D/"
              "?from=1592583325618&to=1592590525618");
  }
  {
    std::string str =
        "taxi-toll-roads-pre-stable-4.sas.yp-c.yandex.net::rtc_resource_usage::"
        "cpu, limit has been reached: current value = 5.975\n"
        "Links:\n"
        " * limit, usage: "
        "yasm.yandex-team.ru/chart/"
        "itype=toll-roads;hosts=taxi-toll-roads-pre-stable-4.sas.yp-c.yandex."
        "net;signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%20max)%"
        "2Cportoinst-cpu_usage_cores_tmmv%7D/"
        "?from=1592583325618&to=1592590525618";
    auto result = utils::FindUrls(str);
    ASSERT_EQ(0u, result.size());
  }
  {
    std::string str =
        "WARN на b2b-authproxy:hejmdal-timings-p98 в 18:30:22: "
        "b2b-authproxy_354077::timings-p98, limit has been reached: current "
        "value = 1640.000\n"
        "Links:\n"
        " * entry_timings: "
        "https://solomon.yandex-team.ru/admin/projects/taxi/"
        "autoGraph?expression=%7Bcluster%3D'production'%2Cgroup%3D'dorblu_rtc_"
        "taxi_b2b-authproxy_stable'%2Chost%3D'cluster'%2Cobject%3D'*_yandex_"
        "net'%2Cpercentile%3D'98'%2Csensor%3D'ok_request_timings'%2Cservice%3D'"
        "dorblu'%7D&b=2020-06-22T14%3A29%3A15Z&e=2020-06-22T16%3A29%3A15Z\n"
        " * entry_rps: "
        "https://solomon.yandex-team.ru/admin/projects/taxi/"
        "autoGraph?expression=%0Agroup_lines('sum'%2C%20%7Bcluster%3D%"
        "22production%22%2C%20service%3D%22dorblu%22%2C%20host%3D%22cluster%22%"
        "2C%20group%3D%22dorblu_rtc_taxi_b2b-authproxy_stable%22%2C%20object%"
        "3D%22*_yandex_net%22%2C%20sensor%3D%22*_rps%22%7D)%0A&b=2020-06-22T14%"
        "3A29%3A15Z&e=2020-06-22T16%3A29%3A15Z";
    auto result = utils::FindUrls(str);
    ASSERT_EQ(2u, result.size());
    EXPECT_EQ(
        result[0].Str(),
        "https://solomon.yandex-team.ru/admin/projects/taxi/"
        "autoGraph?expression=%7Bcluster%3D'production'%2Cgroup%3D'dorblu_rtc_"
        "taxi_b2b-authproxy_stable'%2Chost%3D'cluster'%2Cobject%3D'*_yandex_"
        "net'%2Cpercentile%3D'98'%2Csensor%3D'ok_request_timings'%2Cservice%3D'"
        "dorblu'%7D&b=2020-06-22T14%3A29%3A15Z&e=2020-06-22T16%3A29%3A15Z");
    EXPECT_EQ(
        result[1].Str(),
        "https://solomon.yandex-team.ru/admin/projects/taxi/"
        "autoGraph?expression=%0Agroup_lines('sum'%2C%20%7Bcluster%3D%"
        "22production%22%2C%20service%3D%22dorblu%22%2C%20host%3D%22cluster%22%"
        "2C%20group%3D%22dorblu_rtc_taxi_b2b-authproxy_stable%22%2C%20object%"
        "3D%22*_yandex_net%22%2C%20sensor%3D%22*_rps%22%7D)%0A&b=2020-06-22T14%"
        "3A29%3A15Z&e=2020-06-22T16%3A29%3A15Z");
  }
  {
    std::string format_tpl = " * entry_rps: {}\n---\nSome text.";
    auto url =
        "https://solomon.yandex-team.ru/admin/projects/taxi/"
        "autoGraph?expression=" +
        http::UrlEncode(
            "group_lines('sum',{cluster='production',group='dorblu_rtc_taxi_"
            "callcenter-frontend_stable',host='cluster',object='*_yandex_net',"
            "project='taxi',sensor='errors_rps|timeouts_rps|4*_rps',service='"
            "dorblu',sensor!=''})");
    auto str = fmt::format(format_tpl, url);
    auto result = utils::FindUrls(str);
    ASSERT_EQ(1u, result.size());
    EXPECT_EQ(result[0].Str(),
              "https://solomon.yandex-team.ru/admin/projects/taxi/"
              "autoGraph?expression=group_lines('sum'%2C%7Bcluster%3D'"
              "production'%2Cgroup%3D'dorblu_rtc_taxi_callcenter-frontend_"
              "stable'%2Chost%3D'cluster'%2Cobject%3D'*_yandex_net'%2Cproject%"
              "3D'taxi'%2Csensor%3D'errors_rps%7Ctimeouts_rps%7C4*_rps'%"
              "2Cservice%3D'dorblu'%2Csensor!%3D''%7D)");
  }
}

}  // namespace hejmdal
