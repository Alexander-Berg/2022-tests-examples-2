#include <trackstory/gps_point.hpp>

#include <gtest/gtest.h>
#include <geobus/channels/positions/positions_generator.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>

using gpssignal::test::GpsSignalTestPlugin;

namespace {

long TimePointToLong(trackstory::TimePoint timestamp) {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
             timestamp.time_since_epoch())
      .count();
}

}  // namespace

TEST(trackstory, FbsSerialize) {
  trackstory::GpsPoint orig{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  const auto serialized = trackstory::redis::SerializeGpsPoint(orig);
  const auto deserialized = trackstory::redis::DeserializeGpsPoint(
      serialized, TimePointToLong(orig.timestamp));

  const std::size_t exp_size =
      sizeof(int32_t) * 2 + sizeof(char) + 3 * sizeof(uint16_t);
  ASSERT_EQ(serialized.size(), exp_size);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig, deserialized);
}

TEST(trackstory, FbsSerializeWithOptionals) {
  trackstory::TimePoint timestamp(std::chrono::milliseconds(111));
  trackstory::GpsPoint orig_no_speed{37 * ::gpssignal::lon,
                                     55 * ::gpssignal::lat,
                                     std::nullopt,
                                     2.0 * ::geometry::meter,
                                     ::gpssignal::Azimuth::from_value(42),
                                     timestamp};
  const auto serialized_no_speed =
      trackstory::redis::SerializeGpsPoint(orig_no_speed);
  const auto deserialized_no_speed = trackstory::redis::DeserializeGpsPoint(
      serialized_no_speed, TimePointToLong(timestamp));
  const std::size_t exp_size_no_speed =
      sizeof(int32_t) * 2 + sizeof(char) + 2 * sizeof(uint16_t);
  ASSERT_EQ(serialized_no_speed.size(), exp_size_no_speed);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_speed,
                                              deserialized_no_speed);

  trackstory::GpsPoint orig_no_direction{37 * ::gpssignal::lon,
                                         55 * ::gpssignal::lat,
                                         ::gpssignal::Speed::from_value(16.0),
                                         2.0 * ::geometry::meter,
                                         std::nullopt,
                                         timestamp};
  const auto serialized_no_direction =
      trackstory::redis::SerializeGpsPoint(orig_no_direction);
  const auto deserialized_no_direction = trackstory::redis::DeserializeGpsPoint(
      serialized_no_direction, TimePointToLong(timestamp));
  const std::size_t exp_size_no_direction =
      sizeof(int32_t) * 2 + sizeof(char) + 2 * sizeof(uint16_t);
  ASSERT_EQ(serialized_no_direction.size(), exp_size_no_direction);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_direction,
                                              deserialized_no_direction);

  trackstory::GpsPoint orig_no_accuracy{37 * ::gpssignal::lon,
                                        55 * ::gpssignal::lat,
                                        ::gpssignal::Speed::from_value(16.0),
                                        std::nullopt,
                                        ::gpssignal::Azimuth::from_value(42),
                                        timestamp};
  const auto serialized_no_accuracy =
      trackstory::redis::SerializeGpsPoint(orig_no_accuracy);
  const auto deserialized_no_accuracy = trackstory::redis::DeserializeGpsPoint(
      serialized_no_accuracy, TimePointToLong(timestamp));
  const std::size_t exp_size_no_accuracy =
      sizeof(int32_t) * 2 + sizeof(char) + 2 * sizeof(uint16_t);
  ASSERT_EQ(serialized_no_accuracy.size(), exp_size_no_accuracy);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_accuracy,
                                              deserialized_no_accuracy);

  trackstory::GpsPoint orig_no_all{37 * ::gpssignal::lon, 55 * ::gpssignal::lat,
                                   std::nullopt,          std::nullopt,
                                   std::nullopt,          timestamp};
  const auto serialized_no_all =
      trackstory::redis::SerializeGpsPoint(orig_no_all);
  const auto deserialized_no_all = trackstory::redis::DeserializeGpsPoint(
      serialized_no_all, TimePointToLong(timestamp));
  const std::size_t exp_size_no_all = sizeof(int32_t) * 2 + sizeof(char);
  ASSERT_EQ(serialized_no_all.size(), exp_size_no_all);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_all, deserialized_no_all);
}

TEST(trackstory, FbsDeserializeFailureNotAllData) {
  trackstory::TimePoint timestamp(std::chrono::milliseconds(111));
  trackstory::GpsPoint orig_no_speed{37 * ::gpssignal::lon,
                                     55 * ::gpssignal::lat,
                                     std::nullopt,
                                     2.0 * ::geometry::meter,
                                     ::gpssignal::Azimuth::from_value(42),
                                     timestamp};
  auto serialized_no_speed =
      trackstory::redis::SerializeGpsPoint(orig_no_speed);
  serialized_no_speed.resize(serialized_no_speed.size() - 1);
  ASSERT_THROW(trackstory::redis::DeserializeGpsPoint(
                   serialized_no_speed, TimePointToLong(timestamp)),
               std::runtime_error);

  trackstory::GpsPoint orig_no_all{37 * ::gpssignal::lon, 55 * ::gpssignal::lat,
                                   std::nullopt,          std::nullopt,
                                   std::nullopt,          timestamp};
  auto serialized_no_all = trackstory::redis::SerializeGpsPoint(orig_no_all);
  serialized_no_all.resize(serialized_no_all.size() - 1);
  ASSERT_THROW(trackstory::redis::DeserializeGpsPoint(
                   serialized_no_all, TimePointToLong(timestamp)),
               std::runtime_error);
}

TEST(trackstory, FbsSerializeWithTime) {
  trackstory::GpsPoint orig{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  const auto serialized = trackstory::redis::SerializeGpsPoint(orig, true);
  const auto deserialized = trackstory::redis::DeserializeGpsPoint(
      serialized, trackstory::redis::kReadTimepointFromMessage);

  const std::size_t exp_size = sizeof(int32_t) * 2 + sizeof(char) +
                               3 * sizeof(uint16_t) + sizeof(uint64_t);
  ASSERT_EQ(serialized.size(), exp_size);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig, deserialized);
  ASSERT_EQ(orig.timestamp, deserialized.timestamp);
}

TEST(trackstory, FbsSerializeWithOptionalsWithTime) {
  uint64_t timestamp_ms = 111;
  trackstory::TimePoint timestamp(std::chrono::milliseconds{timestamp_ms});
  trackstory::GpsPoint orig_no_speed{37 * ::gpssignal::lon,
                                     55 * ::gpssignal::lat,
                                     std::nullopt,
                                     2.0 * ::geometry::meter,
                                     ::gpssignal::Azimuth::from_value(42),
                                     timestamp};
  const auto serialized_no_speed =
      trackstory::redis::SerializeGpsPoint(orig_no_speed, true);
  const auto deserialized_no_speed = trackstory::redis::DeserializeGpsPoint(
      serialized_no_speed, trackstory::redis::kReadTimepointFromMessage);
  const std::size_t exp_size_no_speed = sizeof(int32_t) * 2 + sizeof(char) +
                                        2 * sizeof(uint16_t) + sizeof(uint64_t);
  ASSERT_EQ(serialized_no_speed.size(), exp_size_no_speed);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_speed,
                                              deserialized_no_speed);
  ASSERT_EQ(orig_no_speed.timestamp, deserialized_no_speed.timestamp);

  trackstory::GpsPoint orig_no_direction{37 * ::gpssignal::lon,
                                         55 * ::gpssignal::lat,
                                         ::gpssignal::Speed::from_value(16.0),
                                         2.0 * ::geometry::meter,
                                         std::nullopt,
                                         timestamp};
  const auto serialized_no_direction =
      trackstory::redis::SerializeGpsPoint(orig_no_direction, true);
  const auto deserialized_no_direction = trackstory::redis::DeserializeGpsPoint(
      serialized_no_direction, trackstory::redis::kReadTimepointFromMessage);
  const std::size_t exp_size_no_direction = sizeof(int32_t) * 2 + sizeof(char) +
                                            2 * sizeof(uint16_t) +
                                            sizeof(uint64_t);
  ASSERT_EQ(serialized_no_direction.size(), exp_size_no_direction);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_direction,
                                              deserialized_no_direction);
  ASSERT_EQ(orig_no_direction.timestamp, deserialized_no_direction.timestamp);

  trackstory::GpsPoint orig_no_accuracy{37 * ::gpssignal::lon,
                                        55 * ::gpssignal::lat,
                                        ::gpssignal::Speed::from_value(16.0),
                                        std::nullopt,
                                        ::gpssignal::Azimuth::from_value(42),
                                        timestamp};
  const auto serialized_no_accuracy =
      trackstory::redis::SerializeGpsPoint(orig_no_accuracy, true);
  const auto deserialized_no_accuracy = trackstory::redis::DeserializeGpsPoint(
      serialized_no_accuracy, trackstory::redis::kReadTimepointFromMessage);
  const std::size_t exp_size_no_accuracy = sizeof(int32_t) * 2 + sizeof(char) +
                                           2 * sizeof(uint16_t) +
                                           sizeof(uint64_t);
  ASSERT_EQ(serialized_no_accuracy.size(), exp_size_no_accuracy);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_accuracy,
                                              deserialized_no_accuracy);
  ASSERT_EQ(orig_no_accuracy.timestamp, deserialized_no_accuracy.timestamp);

  trackstory::GpsPoint orig_no_all{37 * ::gpssignal::lon, 55 * ::gpssignal::lat,
                                   std::nullopt,          std::nullopt,
                                   std::nullopt,          timestamp};
  const auto serialized_no_all =
      trackstory::redis::SerializeGpsPoint(orig_no_all, true);
  const auto deserialized_no_all = trackstory::redis::DeserializeGpsPoint(
      serialized_no_all, trackstory::redis::kReadTimepointFromMessage);
  const std::size_t exp_size_no_all =
      sizeof(int32_t) * 2 + sizeof(char) + sizeof(uint64_t);
  ASSERT_EQ(serialized_no_all.size(), exp_size_no_all);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(orig_no_all, deserialized_no_all);
  ASSERT_EQ(orig_no_all.timestamp, deserialized_no_all.timestamp);
}
