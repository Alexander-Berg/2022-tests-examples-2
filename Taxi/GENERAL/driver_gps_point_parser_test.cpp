#include <trackstory/parsers/driver_gps_point_parser.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>

using trackstory::parsers::DriverGpsPointParser;

namespace {

const std::string kGoodDriverData =
    "tskv\ttimestamp_raw=2020-05-07T17:56:38.735170Z\ttimestamp="
    "1588863398\treceive_time=1588863398\tdb_id="
    "df98ffa680714291882343e7df1ca5ab\tclid=10000004142\tuuid="
    "e5e6fc4eb20449ceaac196afc1ba53c7\tdirection=0.000000\tlat=55.717860\tlon="
    "37.383498\tspeed=3.600000\tbad=0\tstatus=2\ttime_gps_orig="
    "1588863398000\ttime_system_orig=1588863398000\ttime_system_sync="
    "1588863398000\tchoose_reason=";

const std::string kDriverDataNoSpeed =
    "tskv\ttimestamp_raw=2020-05-07T17:56:38.735170Z\ttimestamp="
    "1588863398\treceive_time=1588863398\tdb_id="
    "df98ffa680714291882343e7df1ca5ab\tclid=10000004142\tuuid="
    "e5e6fc4eb20449ceaac196afc1ba53c7\tdirection=0.000000\tlat=55.717860\tlon="
    "37.383498\tbad=0\tstatus=2\ttime_gps_orig="
    "1588863398000\ttime_system_orig=1588863398000\ttime_system_sync="
    "1588863398000\tchoose_reason=";

const ::driver_id::DriverId kDriverId{
    ::driver_id::DriverDbid{"df98ffa680714291882343e7df1ca5ab"},
    ::driver_id::DriverUuid{"e5e6fc4eb20449ceaac196afc1ba53c7"}};

}  // namespace

TEST(DriverGpsPointParser, ParseGood) {
  DriverGpsPointParser parser;
  parser.Parse(kGoodDriverData);
  const auto& points = parser.GetPoints();

  ASSERT_EQ(points.size(), 1);
  const auto& data = points[0];

  ASSERT_EQ(data.driver_id, kDriverId);
  ASSERT_DOUBLE_EQ(data.point.latitude.value(), 55.717860);
  ASSERT_DOUBLE_EQ(data.point.longitude.value(), 37.383498);
  ASSERT_EQ(data.point.direction->value(), 0);
  ASSERT_NEAR(data.point.speed->value(), 1.0, 0.0001);
  ASSERT_FALSE(data.point.accuracy);
  ASSERT_EQ(data.point.timestamp,
            trackstory::TimePoint{std::chrono::seconds{1588863398}});
}

TEST(DriverGpsPointParser, ParseNoSpeed) {
  DriverGpsPointParser parser;
  EXPECT_THROW(parser.Parse(kDriverDataNoSpeed), std::runtime_error);

  const auto& points = parser.GetPoints();
  ASSERT_EQ(points.size(), 0);
}
