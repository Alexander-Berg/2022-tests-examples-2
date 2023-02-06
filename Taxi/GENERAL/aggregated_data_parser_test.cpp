#include "aggregated_data_parser.h"
#include <userver/utest/utest.hpp>

namespace {

struct NoParseParams : public ::testing::TestWithParam<std::string> {};
struct GoodParseParams : public ::testing::TestWithParam<std::string> {};

UTEST_P(NoParseParams, NoParse) {
  std::string s = GetParam();
  geobus::types::DriverId id("dbid_uuid1");
  std::vector<geobus::types::SignalV2> parse_result =
      yagr::internal::aggregated_data_parser::ParseAggregatedData(std::move(id),
                                                                  s);
  ASSERT_TRUE(parse_result.empty());
}

UTEST_P(GoodParseParams, GoodParse) {
  using TimePoint = yagr::internal::aggregated_data_parser::TimePoint;
  // clang-format off
          std::string s = GetParam();
  // clang-format on
  geobus::types::DriverId id("dbid_uuid1");
  std::vector<geobus::types::SignalV2> parse_result =
      yagr::internal::aggregated_data_parser::ParseAggregatedData(std::move(id),
                                                                  s);
  ASSERT_FALSE(parse_result.empty());
  ASSERT_TRUE(parse_result.size() == 4);

  // p=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,25.25,null,passive,false,false
  ASSERT_EQ(parse_result[0].position.latitude, 55.833934 * geometry::lat);
  ASSERT_EQ(parse_result[0].position.longitude, 37.6319115 * geometry::lon);
  /*ASSERT_EQ(parse_result[0].rtc_unix_time,
            TimePoint(std::chrono::milliseconds(1908013264)));*/
  ASSERT_EQ(parse_result[0].accuracy.value(), 13.0 * geometry::meters);
  ASSERT_EQ(parse_result[0].altitude.value(), 121.97385509 * geometry::meters);
  ASSERT_EQ(parse_result[0].unix_time,
            TimePoint(std::chrono::milliseconds(1587471462786)));
  ASSERT_EQ(parse_result[0].speed.value(), 25.25 * geometry::meters_per_second);
  ASSERT_FALSE(parse_result[0].direction.has_value());
  ASSERT_EQ(parse_result[0].source,
            geobus::types::SignalV2Source::kAndroidPassive);

  // "l=55.9014206,37.5801659,1908008694,140.0,0.0,1587471458215,null,null,lbs-wifi,false,false
  ASSERT_EQ(parse_result[1].position.latitude, 55.9014206 * geometry::lat);
  ASSERT_EQ(parse_result[1].position.longitude, 37.5801659 * geometry::lon);
  /*ASSERT_EQ(parse_result[1].rtc_unix_time,
            TimePoint(std::chrono::milliseconds(1908008694)));*/
  ASSERT_EQ(parse_result[1].accuracy.value(), 140.0 * geometry::meters);
  ASSERT_EQ(parse_result[1].altitude.value(), 0.0 * geometry::meters);
  ASSERT_EQ(parse_result[1].unix_time,
            TimePoint(std::chrono::milliseconds(1587471458215)));
  ASSERT_FALSE(parse_result[1].speed.has_value());
  ASSERT_FALSE(parse_result[1].direction.has_value());
  ASSERT_EQ(parse_result[1].source,
            geobus::types::SignalV2Source::kYandexLbsWifi);

  // n=55.834,37.632,1908013262,542.0,null,1587471462784,null,null,network,false,false
  ASSERT_EQ(parse_result[2].position.latitude, 55.834 * geometry::lat);
  ASSERT_EQ(parse_result[2].position.longitude, 37.632 * geometry::lon);
  /*ASSERT_EQ(parse_result[2].rtc_unix_time,
            TimePoint(std::chrono::milliseconds(1908013262)));*/
  ASSERT_EQ(parse_result[2].accuracy.value(), 542.0 * geometry::meters);
  ASSERT_FALSE(parse_result[2].altitude.has_value());
  ASSERT_EQ(parse_result[2].unix_time,
            TimePoint(std::chrono::milliseconds(1587471462784)));
  ASSERT_FALSE(parse_result[2].speed.has_value());
  ASSERT_FALSE(parse_result[2].direction.has_value());
  ASSERT_EQ(parse_result[2].source,
            geobus::types::SignalV2Source::kAndroidNetwork);

  // gps=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,0.0,123,gps,false,false
  ASSERT_EQ(parse_result[3].position.latitude, 55.833934 * geometry::lat);
  ASSERT_EQ(parse_result[3].position.longitude,
            37.6319115 * geometry::units::lon);
  /*ASSERT_EQ(parse_result[3].rtc_unix_time,
            TimePoint(std::chrono::milliseconds(1908013264)));*/
  ASSERT_EQ(parse_result[3].accuracy.value(), 13.0 * geometry::meters);
  ASSERT_EQ(parse_result[3].altitude.value(), 121.97385509 * geometry::meters);
  ASSERT_EQ(parse_result[3].unix_time,
            TimePoint(std::chrono::milliseconds(1587471462786)));
  ASSERT_EQ(parse_result[3].speed.value(), 0.0 * geometry::meters_per_second);
  ASSERT_EQ(parse_result[3].direction.value(), 123 * geometry::degree);
  ASSERT_EQ(parse_result[3].source, geobus::types::SignalV2Source::kAndroidGps);
}

// clang-format off
std::vector<std::string> GoodParseParamsValues {
        "p=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,25.25,null,passive,false,false;"
        "l=55.9014206,37.5801659,1908008694,140.0,0.0,1587471458215,null,null,lbs-wifi,false,false;"
        "n=55.834,37.632,1908013262,542.0,null,1587471462784,null,null,network,false,false;"
        "gps=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,0.0,123,gps,false,false",

        "p=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,25.25,null,passive,false,false;"
        "l=55.9014206,37.5801659,1908008694,140.0,0.0,1587471458215,null,null,lbs-wifi,false,false;"
        ";;;;" /* empty sources */
        "n=null,37.632,1908013262,542.0,null,1587471462784,null,null,network,false,false;" /* null lat */
        "n=54.0,null,1908013262,542.0,null,1587471462784,null,null,network,false,false;" /* null lon */
        "n=55.834,37.632,null,542.0,null,1587471462784,null,null,network,false,false;" /* null realtime */
        "n=55.834,37.632,1908013262,542.0,null,null,null,null,network,false,false;" /* null time */
        "n=55.834,37.632,1908013262,542.0,null,1587471462784,null,null,network,false,false;"
        "gps=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,0.0,123,gps,false,false"
};
// clang-format on
INSTANTIATE_UTEST_SUITE_P(GoodParse, GoodParseParams,
                          ::testing::ValuesIn(GoodParseParamsValues));

// clang-format off
std::vector<std::string> NoParseParamsValues {
        "", // simple empty string

        "p=55.833934,37.6319115,1908013264,13.0,121.97385509,1587471462786,25.25,null,passive;" // last two fields were deleted
        "l=,37.5801659,1908008694,140.0,0.0,1587471458215,null,null", // incorrect , after =

        ";;;;;;;" // a lot of empty sources
};
// clang-format on
INSTANTIATE_UTEST_SUITE_P(NoParse, NoParseParams,
                          ::testing::ValuesIn(NoParseParamsValues));

}  // namespace
