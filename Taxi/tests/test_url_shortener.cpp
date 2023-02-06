#include <gtest/gtest.h>

#include <utils/url_shortener.hpp>

namespace hejmdal {

TEST(TestUrlShortener, MainTest) {
  auto shortener = [](const std::string&) { return std::string("SHORT_LINK"); };
  {
    std::string str = "";
    utils::FindAndShortenUrlsInPlace(str, shortener);
    EXPECT_EQ("", str);
    str = "Hello world";
    utils::FindAndShortenUrlsInPlace(str, shortener);
    EXPECT_EQ("Hello world", str);
  }
  {
    std::string str =
        "taxi-admin-data\n"
        "      * "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_taxi_taxi-admin-data_stable";
    utils::FindAndShortenUrlsInPlace(str, shortener);
    std::string check_str =
        "taxi-admin-data\n"
        "      * SHORT_LINK";
    EXPECT_EQ(check_str, str);
  }
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
    utils::FindAndShortenUrlsInPlace(str, shortener);
    std::string check_str =
        "      * 2020-06-11 03:01 (432 min, closed), Warning\n"
        "         description: "
        "taxi-taxi-admin-data-stable-1.sas.yp-c.yandex.net::rtc_resource_usage:"
        ":cpu, limit has been reached: current value = 0.869\n"
        "         links:\n"
        "           * limit, usage -- SHORT_LINK\n"
        "      * 2020-06-09 02:40 (429 min, closed), Warning\n"
        "         description: "
        "taxi-taxi-admin-data-stable-1.sas.yp-c.yandex.net::rtc_resource_usage:"
        ":cpu, limit has been reached: current value = 0.801\n"
        "         links:\n"
        "           * limit, usage -- SHORT_LINK\n"
        "more lines";
    EXPECT_EQ(check_str, str);
  }
  {
    std::string str =
        "~\n"
        "Высокое использование CPU: 73.0%\n"
        " * limit: "
        "https://yasm.yandex-team.ru/chart/"
        "itype=core-jobs;hosts=eda-core-jobs-stable-12.vla.yp-c.yandex.net;"
        "signals=%7Bquant(portoinst-cpu_limit_slot_hgram%2C%20max)%7D/"
        "?from=1602515220000&to=1602522420000\n"
        " * usage: "
        "https://yasm.yandex-team.ru/chart/"
        "itype=core-jobs;hosts=eda-core-jobs-stable-12.vla.yp-c.yandex.net;"
        "signals=%7Bquant(portoinst-cpu_limit_usage_perc_hgram%2C%20med)%7D/"
        "?from=1602515220000&to=1602522420000\n"
        " * grafana dashboard: "
        "https://grafana.yandex-team.ru/d/z964909Wk/"
        "nanny_eda_core-jobs_stable?from=1602515220000&to=1602522420000\n"
        " * system dashboard: "
        "https://yasm.yandex-team.ru/panel/"
        "robot-taxi-clown.nanny_eda_core-jobs_stable?from=1602515220000&to="
        "1602522420000\n"
        "---\n"
        "Проект: eda\n"
        "Сервис: core-jobs\n"
        "Хост: eda-core-jobs-stable-12.vla.yp-c.yandex.net\n"
        "---\nОбратная связь: "
        "https://forms.yandex-team.ru/surveys/55259/"
        "?precedent_time=2020-10-12T16%3A07%3A00%2B0000&out_point_id=alert&"
        "alert_state=Warning&circuit_id=eda-core-jobs-stable-12.vla.yp-c."
        "yandex.net%3A%3Artc_cpu_usage&service_id=354198&service_name=core-"
        "jobs&alert_time=19%3A07%3A00%202020-10-12%20(MSK)\n"
        "------------------\n~";
    utils::FindAndShortenUrlsInPlace(str, shortener);
    std::string expected =
        "~\n"
        "Высокое использование CPU: 73.0%\n"
        " * limit: SHORT_LINK\n"
        " * usage: SHORT_LINK\n"
        " * grafana dashboard: SHORT_LINK\n"
        " * system dashboard: SHORT_LINK\n"
        "---\n"
        "Проект: eda\n"
        "Сервис: core-jobs\n"
        "Хост: eda-core-jobs-stable-12.vla.yp-c.yandex.net\n"
        "---\nОбратная связь: SHORT_LINK\n"
        "------------------\n~";
    EXPECT_EQ(str, expected);
  }
}

}  // namespace hejmdal
