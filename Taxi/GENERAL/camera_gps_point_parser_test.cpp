#include <trackstory/parsers/camera_gps_point_parser.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>

using trackstory::parsers::CameraGpsPointParser;

namespace {

const std::string kGoodDriverData =
    "{\"timestamp\":\"2021-03-11T09:00:16.85215222+03:00\","
    "\"contractor_uuid\":\"080a08bcdec32076f2dcff8416e06a9b\","
    "\"contractor_dbid\":\"f428cfd51eba4eb5b5d93bff94aad66a\","
    "\"source\":\"Camera\",\"lat\":55.739995,\"lon\":37.545986,"
    "\"unix_timestamp\":1615442416840,\"backend_recieve_unix_timestamp\":"
    "1615442416}";

const std::string kDriverDataWOSpeed = R"json(
{"timestamp":"2021-10-04T16:00:07.932565237+03:00",
 "contractor_uuid":"212020E10486C",
 "contractor_dbid":"4dd761431a3d438c95801e8df82ded8e",
 "source":"Camera",
 "lat":55.81886672973633,"lon":36.98496627807617,
 "unix_timestamp":0,
 "backend_recieve_unix_timestamp":1633352407,
 "altitude":0.0,"direction":0,"accuracy":0.0}
)json";

const std::string kDriverDataNoUuid =
    "{\"timestamp\":\"2021-03-11T09:00:16.85215222+03:00\","
    "\"contractor_dbid\":\"f428cfd51eba4eb5b5d93bff94aad66a\","
    "\"source\":\"Camera\",\"lat\":55.739995,\"lon\":37.545986,"
    "\"unix_timestamp\":1615442416840,\"backend_recieve_unix_timestamp\":"
    "1615442416}";

const ::driver_id::DriverId kDriverId{
    ::driver_id::DriverDbid{"f428cfd51eba4eb5b5d93bff94aad66a"},
    ::driver_id::DriverUuid{"080a08bcdec32076f2dcff8416e06a9b"}};
const ::driver_id::DriverId kDriverIdWOSpeed{
    ::driver_id::DriverDbid{"4dd761431a3d438c95801e8df82ded8e"},
    ::driver_id::DriverUuid{"212020E10486C"}};

}  // namespace

TEST(CameraGpsPointParser, ParseGood) {
  CameraGpsPointParser parser;
  parser.Parse(kGoodDriverData);
  const auto& points = parser.GetPoints();

  ASSERT_EQ(points.size(), 1);
  const auto& data = points[0];

  ASSERT_EQ(data.driver_id, kDriverId);
  ASSERT_DOUBLE_EQ(data.point.latitude.value(), 55.739995);
  ASSERT_DOUBLE_EQ(data.point.longitude.value(), 37.545986);
  ASSERT_FALSE(data.point.direction);
  ASSERT_FALSE(data.point.speed);
  ASSERT_FALSE(data.point.accuracy);
  ASSERT_EQ(data.point.timestamp,
            trackstory::TimePoint{std::chrono::milliseconds{1615442416840}});
}

TEST(CameraGpsPointParser, ParseWithSlashN) {
  CameraGpsPointParser parser;
  parser.Parse(kDriverDataWOSpeed);
  const auto& points = parser.GetPoints();

  ASSERT_EQ(points.size(), 1);
  const auto& data = points[0];

  ASSERT_EQ(data.driver_id, kDriverIdWOSpeed);
  ASSERT_DOUBLE_EQ(data.point.latitude.value(), 55.81886672973633);
  ASSERT_DOUBLE_EQ(data.point.longitude.value(), 36.98496627807617);
  ASSERT_EQ(data.point.direction, 0 * geometry::degree);
  ASSERT_EQ(data.point.accuracy, 0 * geometry::meter);
  ASSERT_EQ(data.point.timestamp,
            trackstory::TimePoint{std::chrono::milliseconds{0}});
}

TEST(CameraGpsPointParser, ParseNoUuid) {
  CameraGpsPointParser parser;
  EXPECT_THROW(parser.Parse(kDriverDataNoUuid), std::exception);

  const auto& points = parser.GetPoints();
  ASSERT_EQ(points.size(), 0);
}
