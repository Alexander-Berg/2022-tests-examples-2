#include <trackstory/parsers/driver_gps_point_parser.hpp>
#include <trackstory/parsers/logbroker_parser.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>

using trackstory::parsers::DriverGpsPointParser;
using trackstory::parsers::LogbrokerParser;

namespace {

const std::string kGoodDriverData =
    "tskv\ttimestamp_raw=2020-05-07T17:56:38.735170Z\ttimestamp="
    "1588863398\treceive_time=1588863398\tdb_id="
    "df98ffa680714291882343e7df1ca5ab\tclid=10000004142\tuuid="
    "e5e6fc4eb20449ceaac196afc1ba53c7\tdirection=0.000000\tlat=55.717860\tlon="
    "37.383498\tspeed=0.000000\tbad=0\tstatus=2\ttime_gps_orig="
    "1588863398000\ttime_system_orig=1588863398000\ttime_system_sync="
    "1588863398000\tchoose_reason=";

const std::string kGoodDriverDataLonAtTheEnd =
    "tskv\ttimestamp_raw=2020-05-07T17:56:38.735170Z\ttimestamp="
    "1588863398\treceive_time=1588863398\tdb_id="
    "df98ffa680714291882343e7df1ca5ab\tclid=10000004142\tuuid="
    "e5e6fc4eb20449ceaac196afc1ba53c7\tdirection=0.000000\tlat=55.717860"
    "\tspeed=0.000000\tbad=0\tstatus=2\ttime_gps_orig="
    "1588863398000\ttime_system_orig=1588863398000\ttime_system_sync="
    "1588863398000\tchoose_reason=\tlon=37.5435";

const std::string kDriverDataNoSpeed =
    "tskv\ttimestamp_raw=2020-05-07T17:56:38.735170Z\ttimestamp="
    "1588863398\treceive_time=1588863398\tdb_id="
    "df98ffa680714291882343e7df1ca5ab\tclid=10000004142\tuuid="
    "e5e6fc4eb20449ceaac196afc1ba53c7\tdirection=0.000000\tlat=55.717860\tlon="
    "37.383498\tbad=0\tstatus=2\ttime_gps_orig="
    "1588863398000\ttime_system_orig=1588863398000\ttime_system_sync="
    "1588863398000\tchoose_reason=";

}  // namespace

TEST(LogbrokerParser, ParseTwoGood) {
  auto driver_parser = std::make_shared<DriverGpsPointParser>();
  LogbrokerParser parser(driver_parser);
  parser.ParseChunk(kGoodDriverData + '\n' + kGoodDriverData + '\n');
  const auto& points = driver_parser->GetPoints();

  ASSERT_EQ(points.size(), 2);
}

TEST(LogbrokerParser, ParseOneGoodOneBad) {
  auto driver_parser = std::make_shared<DriverGpsPointParser>();
  LogbrokerParser parser(driver_parser);
  parser.ParseChunk(kGoodDriverData + '\n' + kDriverDataNoSpeed + '\n');
  const auto& points = driver_parser->GetPoints();

  ASSERT_EQ(points.size(), 1);
  ASSERT_EQ(parser.GetFailedCount(), 1);
}

TEST(LogbrokerParser, ParseStickWithoutNewLine) {
  auto driver_parser = std::make_shared<DriverGpsPointParser>();
  LogbrokerParser parser(driver_parser);
  parser.ParseChunk(kGoodDriverData + kGoodDriverData);
  const auto& points = driver_parser->GetPoints();

  ASSERT_EQ(points.size(), 1);
  ASSERT_EQ(parser.GetFailedCount(), 0);
}

TEST(LogbrokerParser, ParseFailParseStickedWhenLonAtTheEnd) {
  auto driver_parser = std::make_shared<DriverGpsPointParser>();
  LogbrokerParser parser(driver_parser);
  parser.ParseChunk(kGoodDriverDataLonAtTheEnd + kGoodDriverDataLonAtTheEnd +
                    '\n' + kGoodDriverDataLonAtTheEnd);
  const auto& points = driver_parser->GetPoints();

  ASSERT_EQ(points.size(), 1);
  ASSERT_EQ(parser.GetFailedCount(), 1);
}
