#include <tuple>

#include <gtest/gtest.h>

#include <utils/datetime.hpp>

using std::chrono::system_clock;
using utils::datetime::Stringtime;

TEST(datetime, add_days) {
  EXPECT_EQ(cctz::civil_second(2016, 03, 02), cctz::civil_second(2016, 02, 31));
  EXPECT_EQ(cctz::civil_second(2015, 03, 03), cctz::civil_second(2015, 02, 31));
}

TEST(datetime, Stringtime) {
  EXPECT_EQ(1472114711,
            system_clock::to_time_t(utils::datetime::GuessStringtime(
                "2016-08-25T13:45:11.555+0500", "Asia/Yekaterinburg")));
  EXPECT_EQ(1472132711,
            system_clock::to_time_t(utils::datetime::GuessStringtime(
                "2016-08-25T13:45:11Z", "Asia/Yekaterinburg")));
  EXPECT_EQ(1472114711, system_clock::to_time_t(Stringtime(
                            "2016-08-25T13:45:11", "Asia/Yekaterinburg",
                            "%Y-%m-%dT%H:%M:%E*S")));

  system_clock::time_point res;
  EXPECT_NO_THROW(res = Stringtime("2017-07-14T02:40:00.000000Z", "UTC",
                                   utils::datetime::kRfc3339Format));
  EXPECT_EQ(1500000000l, system_clock::to_time_t(res));
}

class TestDatetimeTZData : public ::testing::TestWithParam<
                               std::tuple<time_t, std::string, std::string>> {};

TEST_P(TestDatetimeTZData, Timestring) {
  EXPECT_EQ(std::get<1>(GetParam()),
            utils::datetime::Timestring(std::get<0>(GetParam()),
                                        std::get<2>(GetParam())));
}

TEST_P(TestDatetimeTZData, GuessStringtime) {
  EXPECT_EQ(std::get<0>(GetParam()),
            system_clock::to_time_t(utils::datetime::GuessStringtime(
                std::get<1>(GetParam()), std::get<2>(GetParam()))));
}

INSTANTIATE_TEST_CASE_P(
    TZDataValues, TestDatetimeTZData,
    ::testing::Values(
        std::make_tuple(1480608000, "2016-12-01T22:00:00+0600", "Asia/Almaty"),
        std::make_tuple(1480953600, "2016-12-05T22:00:00+0600", "Asia/Almaty"),
        std::make_tuple(1480608000, "2016-12-01T23:00:00+0700", "Asia/Barnaul"),
        std::make_tuple(1480953600, "2016-12-05T23:00:00+0700", "Asia/Barnaul"),
        std::make_tuple(1480608000, "2016-12-02T00:00:00+0800", "Asia/Irkutsk"),
        std::make_tuple(1480953600, "2016-12-06T00:00:00+0800", "Asia/Irkutsk"),
        std::make_tuple(1480608000, "2016-12-01T23:00:00+0700",
                        "Asia/Krasnoyarsk"),
        std::make_tuple(1480953600, "2016-12-05T23:00:00+0700",
                        "Asia/Krasnoyarsk"),
        std::make_tuple(1480608000, "2016-12-01T23:00:00+0700",
                        "Asia/Novosibirsk"),
        std::make_tuple(1480953600, "2016-12-05T23:00:00+0700",
                        "Asia/Novosibirsk"),
        std::make_tuple(1480608000, "2016-12-01T22:00:00+0600", "Asia/Omsk"),
        std::make_tuple(1480953600, "2016-12-05T22:00:00+0600", "Asia/Omsk"),
        std::make_tuple(1480608000, "2016-12-01T20:00:00+0400", "Asia/Tbilisi"),
        std::make_tuple(1480953600, "2016-12-05T20:00:00+0400", "Asia/Tbilisi"),
        std::make_tuple(1480608000, "2016-12-01T23:00:00+0700", "Asia/Tomsk"),
        std::make_tuple(1480953600, "2016-12-05T23:00:00+0700", "Asia/Tomsk"),
        std::make_tuple(1480608000, "2016-12-02T02:00:00+1000",
                        "Asia/Vladivostok"),
        std::make_tuple(1480953600, "2016-12-06T02:00:00+1000",
                        "Asia/Vladivostok"),
        std::make_tuple(1480608000, "2016-12-02T01:00:00+0900", "Asia/Yakutsk"),
        std::make_tuple(1480953600, "2016-12-06T01:00:00+0900", "Asia/Yakutsk"),
        std::make_tuple(1480608000, "2016-12-01T21:00:00+0500",
                        "Asia/Yekaterinburg"),
        std::make_tuple(1480953600, "2016-12-05T21:00:00+0500",
                        "Asia/Yekaterinburg"),
        std::make_tuple(1480608000, "2016-12-01T20:00:00+0400", "Asia/Yerevan"),
        std::make_tuple(1480953600, "2016-12-05T20:00:00+0400", "Asia/Yerevan"),
        std::make_tuple(1480608000, "2016-12-01T18:00:00+0200",
                        "Europe/Kaliningrad"),
        std::make_tuple(1480953600, "2016-12-05T18:00:00+0200",
                        "Europe/Kaliningrad"),
        std::make_tuple(1480608000, "2016-12-01T18:00:00+0200", "Europe/Kiev"),
        std::make_tuple(1480953600, "2016-12-05T18:00:00+0200", "Europe/Kiev"),
        std::make_tuple(1480608000, "2016-12-01T19:00:00+0300", "Europe/Minsk"),
        std::make_tuple(1480953600, "2016-12-05T19:00:00+0300", "Europe/Minsk"),
        std::make_tuple(1480608000, "2016-12-01T19:00:00+0300",
                        "Europe/Moscow"),
        std::make_tuple(1480953600, "2016-12-05T19:00:00+0300",
                        "Europe/Moscow"),
        std::make_tuple(1480608000, "2016-12-01T20:00:00+0400",
                        "Europe/Samara"),
        std::make_tuple(1480953600, "2016-12-05T20:00:00+0400",
                        "Europe/Samara"),
        std::make_tuple(1480608000, "2016-12-01T19:00:00+0300",
                        "Europe/Volgograd"),
        std::make_tuple(1480953600, "2016-12-05T19:00:00+0300",
                        "Europe/Volgograd"),
        std::make_tuple(1480608000, "2016-12-01T19:00:00+0300",
                        "Europe/Saratov"),
        std::make_tuple(1480953600, "2016-12-05T20:00:00+0400",
                        "Europe/Saratov")), );
