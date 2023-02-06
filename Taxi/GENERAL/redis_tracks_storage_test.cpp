#include <geobus/channels/edge_positions/edge_positions_generator.hpp>
#include <geobus/channels/positions/positions_generator.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>
#include <simple-zookeeper/redis_zookeeper_tester.hpp>
#include <userver/hostinfo/blocking/get_hostname.hpp>
#include <userver/storages/redis/mock_client_base.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <trackstory/gps_read.hpp>
#include <trackstory/redis_mock.hpp>
#include <trackstory/redis_tracks_storage.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>

namespace {

const std::string kHostname{hostinfo::blocking::GetRealHostName()};
std::chrono::milliseconds kUpdateInterval{100500};
const std::string kMachineListKey{"machine_list_hash"};
std::chrono::seconds kMachineTimeout{100500};
const trackstory::TrackstoryRedisPrefix kRedisPrefix{"pos"};

const trackstory::TrackProcessType kProcessType(
    trackstory::TrackProcessType::kPreprocessDefault);
const double kEplision = 0.001;
const trackstory::filter::FilterParams kFilterParams{10, 30, 5, 3, 0.0001};

using trackstory::test::RedisMock;
using trackstory::test::RedisTransaction;
using trackstory::test::RedisTransactionTest;

double RoundDouble(double value) {
  auto val = (uint64_t)(value * 10.0);
  return ((double)val) / 10.0;
}

}  // namespace

UTEST(redis_tracks_storage, ProcessPayload) {
  RedisTransactionTest<RedisMock, RedisTransaction> transaction_test;
  auto& redis_client = transaction_test.Client();

  simple_zookeeper::RedisZookeeper::RedisConfig zookeeper_redis_config{
      {}, kMachineTimeout};
  std::shared_ptr<simple_zookeeper::RedisZookeeper> keeper =
      std::make_shared<simple_zookeeper::RedisZookeeper>(
          redis_client, kUpdateInterval, kMachineListKey,
          zookeeper_redis_config);

  simple_zookeeper::RedisZookeeperTester tester(*keeper);
  tester.UpdateMachinesList();

  trackstory::RedisTracksStorage tracks_storage(redis_client, kRedisPrefix,
                                                keeper);
  trackstory::redis::RedisConfig redis_config{};
  redis_config.process_drivers_percent = 100;
  tracks_storage.SetRedisConfig(redis_config);

  trackstory::TimePoint first_timestamp{trackstory::BucketHoursDuration{1} +
                                        std::chrono::milliseconds{500}};
  ::geobus::types::Message<::geobus::types::DriverPosition> payload;
  auto pos = geobus::generators::PositionsGenerator::CreateDriverPosition(5);
  pos.signal.timestamp = first_timestamp;
  pos.signal.speed =
      ::gpssignal::Speed::from_value(RoundDouble(pos.signal.speed->value()));
  payload.data.push_back(pos);

  tracks_storage.ProcessPayload(payload);

  const auto& keys = redis_client->GetKeys();
  std::unordered_set<std::string> exp_keys{
      "machine_list_hash",
      "pos/"
      "****************5****************_****************6****************/"
      "19700101/1/0",
      "driver_latest_positions/"
      "****************5****************_****************6****************"};
  ASSERT_EQ(keys, exp_keys);

  utils::datetime::MockNowSet(first_timestamp);

  trackstory::gps_read::RedisReadContext redis_read_context{
      *redis_client, kRedisPrefix, redis_config};
  trackstory::gps_read::ReadContext read_context{
      redis_read_context, std::nullopt, std::nullopt, kFilterParams, kEplision};
  auto data = trackstory::gps_read::ReadPositions(
      pos.driver_id.GetDbidUndscrUuid(),
      trackstory::TimePoint{trackstory::BucketHoursDuration{1}},
      first_timestamp + std::chrono::seconds(1), read_context, kProcessType);

  ASSERT_EQ(data.min_bucket_timepoint,
            trackstory::TimePoint{trackstory::BucketHoursDuration{1}});
  ASSERT_EQ(data.pos_map.size(), 1);
  const auto& item = *data.pos_map.begin();
  ASSERT_EQ(item.first, 3600500);
  const auto& point = item.second;
  ASSERT_EQ(point.timestamp, first_timestamp);
  ASSERT_DOUBLE_EQ(point.latitude.value(), -37.0);
  ASSERT_DOUBLE_EQ(point.longitude.value(), -103.0);
  ASSERT_DOUBLE_EQ(point.speed->value(), 15.199999999999999);
  ASSERT_DOUBLE_EQ(point.direction->value(), 5);
  ASSERT_DOUBLE_EQ(point.accuracy->value(), 5);
}

UTEST(redis_tracks_storage, ProcessEdgePayload) {
  RedisTransactionTest<RedisMock, RedisTransaction> transaction_test;
  auto& redis_client = transaction_test.Client();

  simple_zookeeper::RedisZookeeper::RedisConfig zookeeper_redis_config{
      {}, kMachineTimeout};
  std::shared_ptr<simple_zookeeper::RedisZookeeper> keeper =
      std::make_shared<simple_zookeeper::RedisZookeeper>(
          redis_client, kUpdateInterval, kMachineListKey,
          zookeeper_redis_config);

  simple_zookeeper::RedisZookeeperTester tester(*keeper);
  tester.UpdateMachinesList();

  trackstory::RedisTracksStorage tracks_storage(redis_client, kRedisPrefix,
                                                keeper);
  trackstory::redis::RedisConfig redis_config{};
  redis_config.process_drivers_percent = 100;
  tracks_storage.SetRedisConfig(redis_config);

  trackstory::TimePoint first_timestamp{trackstory::BucketHoursDuration{1} +
                                        std::chrono::milliseconds{500}};
  ::geobus::types::Message<::geobus::types::DriverEdgePosition> payload;
  auto pos =
      geobus::generators::EdgePositionsGenerator::CreateValidEdgePosition(5);
  pos.timestamp = first_timestamp;
  payload.data.push_back(pos);

  tracks_storage.ProcessPayload(payload);

  const auto& keys = redis_client->GetKeys();
  std::unordered_set<std::string> exp_keys{
      "machine_list_hash",
      "pos/"
      "****************5****************_****************6****************/"
      "19700101/1/0"};
  ASSERT_EQ(keys, exp_keys);

  utils::datetime::MockNowSet(first_timestamp);

  trackstory::gps_read::RedisReadContext redis_read_context{
      *redis_client, kRedisPrefix, redis_config};
  trackstory::gps_read::ReadContext read_context{
      redis_read_context, std::nullopt, std::nullopt, kFilterParams, kEplision};
  auto data = trackstory::gps_read::ReadPositions(
      pos.driver_id.GetDbidUndscrUuid(),
      trackstory::TimePoint{trackstory::BucketHoursDuration{1}},
      first_timestamp + std::chrono::seconds(1), read_context, kProcessType);

  ASSERT_EQ(data.min_bucket_timepoint,
            trackstory::TimePoint{trackstory::BucketHoursDuration{1}});
  ASSERT_EQ(data.pos_map.size(), 1);
  const auto& item = *data.pos_map.begin();
  ASSERT_EQ(item.first, 3600500);
  const auto& point = item.second;
  ASSERT_EQ(point.timestamp, first_timestamp);
  ASSERT_DOUBLE_EQ(point.latitude.value(), -37.0);
  ASSERT_DOUBLE_EQ(point.longitude.value(), -103.0);
  ASSERT_DOUBLE_EQ(point.direction->value(), 5);
  ASSERT_TRUE(point.speed);
  ASSERT_DOUBLE_EQ(point.speed->value(), 0);
  ASSERT_FALSE(point.accuracy);
}

UTEST(redis_tracks_storage, ProcessPayloadBulk) {
  RedisTransactionTest<RedisMock, RedisTransaction> transaction_test;
  auto& redis_client = transaction_test.Client();

  simple_zookeeper::RedisZookeeper::RedisConfig zookeeper_redis_config{
      {}, kMachineTimeout};
  std::shared_ptr<simple_zookeeper::RedisZookeeper> keeper =
      std::make_shared<simple_zookeeper::RedisZookeeper>(
          redis_client, kUpdateInterval, kMachineListKey,
          zookeeper_redis_config);

  simple_zookeeper::RedisZookeeperTester tester(*keeper);
  tester.UpdateMachinesList();

  trackstory::RedisTracksStorage tracks_storage(redis_client, kRedisPrefix,
                                                keeper);
  trackstory::redis::RedisConfig redis_config{};
  redis_config.process_drivers_percent = 100;
  redis_config.batch_write_size = 2;
  tracks_storage.SetRedisConfig(redis_config);

  trackstory::TimePoint first_timestamp{trackstory::BucketHoursDuration{1} +
                                        std::chrono::milliseconds{500}};
  ::geobus::types::Message<::geobus::types::DriverPosition> payload;
  auto pos = geobus::generators::PositionsGenerator::CreateDriverPosition(5);
  pos.signal.timestamp = first_timestamp;
  payload.data.push_back(pos);

  tracks_storage.ProcessPayload(payload);

  const auto& keys = redis_client->GetKeys();
  /// There is no position buckets, because batch_write_size == 2.
  std::unordered_set<std::string> exp_keys{"machine_list_hash"};
  ASSERT_EQ(keys, exp_keys);

  trackstory::TimePoint second_timestamp{first_timestamp +
                                         trackstory::BucketMinutesDuration{1}};
  pos.signal.timestamp = second_timestamp;
  payload.data.clear();
  payload.data.push_back(pos);

  tracks_storage.ProcessPayload(payload);

  const auto& keys2 = redis_client->GetKeys();
  /// There is two buckets with positions, because difference with timepoints
  /// >= trackstory::BucketMinutesDuration .
  std::unordered_set<std::string> exp_keys2{
      "machine_list_hash",
      "pos/"
      "****************5****************_****************6****************/"
      "19700101/1/0",
      "pos/"
      "****************5****************_****************6****************/"
      "19700101/1/1",
      "driver_latest_positions/"
      "****************5****************_****************6****************"};
  ASSERT_EQ(keys2, exp_keys2);

  auto latest_position = tracks_storage.GetLatestPositions(
      ::driver_id::DriverDbidUndscrUuid{"****************5****************_****"
                                        "************6****************"},
      std::chrono::system_clock::time_point{});
  ASSERT_TRUE(latest_position != std::nullopt);
  gpssignal::test::GpsSignalTestPlugin::TestPositionsAreClose(*latest_position,
                                                              pos.signal);

  auto non_exist_latest_position = tracks_storage.GetLatestPositions(
      ::driver_id::DriverDbidUndscrUuid{"****************4****************_****"
                                        "************6****************"},
      std::chrono::system_clock::time_point{});
  ASSERT_EQ(non_exist_latest_position, std::nullopt);
}
