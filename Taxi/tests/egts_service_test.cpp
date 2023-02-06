#include <helpers/egts.hpp>

#include <vector>

#include <cctz/civil_time.h>
#include <cctz/time_zone.h>
#include <gtest/gtest.h>

#include "helpers/egts/egts_response.hpp"

class EGTSServiceTest : public ::testing::Test, public helpers::Egts {
 public:
  EGTSServiceTest()
      : Egts("127.0.0.1", 80, 2001, std::chrono::milliseconds(4000)) {}

 protected:
};

TEST_F(EGTSServiceTest, SerializeAuth) {
  auto actual_auth_req = SerializeAuth(2001);
  std::vector<uint8_t> expected_auth_req{
      0x01, 0x00, 0x03, 0x0b, 0x00, 0x0f, 0x00,
      0x00, 0x00, 0x01, 0x9b,                    // PACKET_HEADER
      0x08, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01,  // EGTS_RECORD_HEADER
      0x05, 0x05, 0x00,                          // EGTS_SUBRECORD_HEADER
      0x00, 0xd1, 0x07, 0x00, 0x00,              // EGTS_SR_DISPATCHER_IDENTITY
      0xde, 0x87};                               // CHECKSUM

  ASSERT_EQ(expected_auth_req, actual_auth_req);
}

TEST_F(EGTSServiceTest, SerializeCars) {
  std::vector<models::telemetry::CarState> cars;
  models::telemetry::CarState car1;
  models::telemetry::CarState car2;

  car1.id = 123456;
  // longitude = 30, latitude = 60
  car1.coords = models::geometry::Point(30, 60);
  car1.direction = 60;
  car1.speed = 100;
  // 20.11.2011 09:05:45 UTC
  auto timestamp = cctz::convert(cctz::civil_second(2011, 11, 20, 9, 5, 45),
                                 cctz::utc_time_zone());
  car1.timestamp = timestamp;
  car1.free = true;

  car2.id = 654321;
  // longitude = 160, latitude = 0
  car2.coords = models::geometry::Point(160, 0);
  car2.direction = 300;
  car2.speed = 5;
  car2.timestamp = timestamp;
  car2.free = false;

  cars.push_back(car1);
  cars.push_back(car2);

  auto actual_cars_req = SerializeCars(cars.cbegin(), cars.cend());

  std::vector<uint8_t> expected_cars_req{
      0x01, 0x00, 0x00, 0x0b, 0x00, 0x46, 0x00, 0x01, 0x00, 0x01,
      0x2a,  // PACKET_HEADER
      // FIRST CAR
      0x18, 0x00, 0x00, 0x00, 0x01, 0x40, 0xe2, 0x01, 0x00, 0x02,
      0x02,              // RECORD_HEADER
      0x10, 0x15, 0x00,  // SUBRECORD_HEADER
      0xe9, 0x87, 0x8b, 0x03, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0x2a,
      0x15, 0xe8, 0x03, 0x3c, 0x00, 0x00, 0x00, 0x00,
      0x0d,  // SR_POS_DATA_RECORD
      // SECOND CAR
      0x18, 0x00, 0x01, 0x00, 0x01, 0xf1, 0xfb, 0x09, 0x00, 0x02,
      0x02,              // RECORD_HEADER
      0x10, 0x15, 0x00,  // SUBRECORD_HEADER
      0xe9, 0x87, 0x8b, 0x03, 0x00, 0x00, 0x00, 0x00, 0xe2, 0x38, 0x8e, 0xe3,
      0x15, 0x32, 0x80, 0x2c, 0x00, 0x00, 0x00, 0x80,
      0x0d,  // SR_POS_DATA_RECORD
      // CHECKSUM
      0x0c, 0x87};

  ASSERT_EQ(expected_cars_req, actual_cars_req);
}

TEST_F(EGTSServiceTest, SerializeCarWithUndefinedAngle) {
  std::vector<models::telemetry::CarState> cars;
  models::telemetry::CarState car1;

  car1.id = 123456;
  // longitude = 30, latitude = 60
  car1.coords = models::geometry::Point(30, 60);
  car1.direction = -1;
  car1.speed = 100;
  // 20.11.2011 09:05:45 UTC
  auto timestamp = cctz::convert(cctz::civil_second(2011, 11, 20, 9, 5, 45),
                                 cctz::utc_time_zone());
  car1.timestamp = timestamp;
  car1.free = true;

  cars.push_back(car1);

  auto actual_cars_req = SerializeCars(cars.cbegin(), cars.cend());

  std::vector<uint8_t> expected_cars_req{
      0x01, 0x00, 0x00, 0x0b, 0x00, 0x23, 0x00, 0x02, 0x00, 0x01,
      0x15,  // PACKET_HEADER
      // FIRST CAR
      0x18, 0x00, 0x02, 0x00, 0x01, 0x40, 0xe2, 0x01, 0x00, 0x02,
      0x02,              // RECORD_HEADER
      0x10, 0x15, 0x00,  // SUBRECORD_HEADER
      0xe9, 0x87, 0x8b, 0x03, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0x2a,
      0x15, 0xe8, 0x03, 0x1, 0x00, 0x00, 0x00, 0x00,
      0x0d,  // SR_POS_DATA_RECORD
      // CHECKSUM
      0xf9, 0xad};

  ASSERT_EQ(expected_cars_req, actual_cars_req);
}

TEST_F(EGTSServiceTest, SerializeCarWithKisArtId) {
  std::vector<models::telemetry::CarState> cars;
  models::telemetry::CarState car1;

  car1.id = 123456;
  // longitude = 30, latitude = 60
  car1.coords = models::geometry::Point(30, 60);
  car1.direction = 60;
  car1.speed = 100;
  // 20.11.2011 09:05:45 UTC
  auto timestamp = cctz::convert(cctz::civil_second(2011, 11, 20, 9, 5, 45),
                                 cctz::utc_time_zone());
  car1.timestamp = timestamp;
  car1.free = true;
  car1.kis_art_id = 0xa6e7d8;

  cars.push_back(car1);

  auto actual_cars_req = SerializeCars(cars.cbegin(), cars.cend());

  std::vector<uint8_t> expected_cars_req{
      0x01, 0x00, 0x00, 0x0b, 0x00, 0x2a, 0x00, 0x03, 0x00, 0x01,
      0xbe,  // PACKET_HEADER
      // FIRST CAR
      0x1f, 0x00, 0x03, 0x00, 0x01, 0x40, 0xe2, 0x01, 0x00, 0x02,
      0x02,              // RECORD_HEADER
      0x10, 0x15, 0x00,  // SUBRECORD_HEADER
      0xe9, 0x87, 0x8b, 0x03, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0x2a,
      0x15, 0xe8, 0x03, 0x3c, 0x00, 0x00, 0x00, 0x00,
      0x0d,                    // SR_POS_DATA_RECORD
      0x18, 0x04, 0x00,        // SUBRECORD_HEADER
      0xde, 0xd8, 0xe7, 0xa6,  // SR_ABS_AN_SENS_DATA
      // CHECKSUM
      0xde, 0x20};

  ASSERT_EQ(expected_cars_req, actual_cars_req);
}

TEST_F(EGTSServiceTest, ResponseWithPT) {
  std::vector<uint8_t> response_content{
      0x01, 0x00, 0x03, 0x0b, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00,
      0xb3, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x18, 0x01,
      0x01, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x8e};

  telemetry::EGTSResponse response(response_content.data());

  ASSERT_EQ(0, response.GetPacketHeader()->PT);
  ASSERT_NE(true, response.IsPtResponseHeaderNull());
  ASSERT_EQ(0, response.GetPtResponseHeaderRPID());
  ASSERT_EQ(0, response.GetPtResponseHeaderPR());

  auto it_records = response.GetRecordsIter();

  ASSERT_TRUE(it_records.HasNext());
  auto record = it_records.Next();

  ASSERT_EQ(6, record.GetHeaderRL());
  ASSERT_FALSE(it_records.HasNext());

  auto it_subrecords = record.SubrecordsIter();

  ASSERT_TRUE(it_subrecords.HasNext());
  auto subrecord = it_subrecords.Next();

  ASSERT_EQ(3, subrecord.GetHeaderSRL());
  ASSERT_EQ(0, subrecord.GetHeaderSRT());
  ASSERT_EQ(0, subrecord.GetData()[0]);
  ASSERT_FALSE(it_subrecords.HasNext());
}

TEST_F(EGTSServiceTest, ResponseWithoutPT) {
  std::vector<uint8_t> response_content{
      0x01, 0x00, 0x03, 0x0b, 0x00, 0x0b, 0x00, 0x01, 0x00, 0x01, 0xc2, 0x04,
      0x00, 0x01, 0x00, 0x58, 0x01, 0x01, 0x09, 0x01, 0x00, 0x00, 0xe7, 0x3c};

  telemetry::EGTSResponse response(response_content.data());

  ASSERT_EQ(1, response.GetPacketHeader()->PT);
  ASSERT_EQ(true, response.IsPtResponseHeaderNull());

  auto it_records = response.GetRecordsIter();

  ASSERT_TRUE(it_records.HasNext());
  auto record = it_records.Next();

  ASSERT_EQ(4, record.GetHeaderRL());
  ASSERT_FALSE(it_records.HasNext());

  auto it_subrecords = record.SubrecordsIter();

  ASSERT_TRUE(it_subrecords.HasNext());
  auto subrecord = it_subrecords.Next();

  ASSERT_EQ(1, subrecord.GetHeaderSRL());
  ASSERT_EQ(9, subrecord.GetHeaderSRT());
  ASSERT_EQ(0, subrecord.GetData()[0]);
  ASSERT_FALSE(it_subrecords.HasNext());
}

TEST_F(EGTSServiceTest, CarsResponse) {
  std::vector<uint8_t> response_content{
      0x01, 0x00, 0x03, 0x0b, 0x00, 0x16, 0x00, 0x02, 0x00, 0x00, 0xb7, 0x01,
      0x00, 0x00, 0x0c, 0x00, 0x02, 0x00, 0x18, 0x02, 0x02, 0x00, 0x03, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x00, 0x5a, 0xbf};

  telemetry::EGTSResponse response(response_content.data());

  ASSERT_EQ(0, response.GetPacketHeader()->PT);
  ASSERT_NE(true, response.IsPtResponseHeaderNull());

  auto it_records = response.GetRecordsIter();

  ASSERT_TRUE(it_records.HasNext());
  auto record = it_records.Next();

  ASSERT_EQ(12, record.GetHeaderRL());
  ASSERT_FALSE(it_records.HasNext());

  auto it_subrecords = record.SubrecordsIter();

  ASSERT_TRUE(it_subrecords.HasNext());
  auto subrecord = it_subrecords.Next();

  ASSERT_EQ(3, subrecord.GetHeaderSRL());
  ASSERT_EQ(0, subrecord.GetHeaderSRT());
  ASSERT_EQ(0, subrecord.GetData()[0]);

  ASSERT_TRUE(it_subrecords.HasNext());
  subrecord = it_subrecords.Next();

  ASSERT_EQ(3, subrecord.GetHeaderSRL());
  ASSERT_EQ(0, subrecord.GetHeaderSRT());
  ASSERT_EQ(1, subrecord.GetData()[0]);

  ASSERT_FALSE(it_subrecords.HasNext());
}
