#include <driver-trackstory/handlers/shorttracks_extended_response.fbs.h>
#include <driver-trackstory-client/fbs_conversion.hpp>
#include <gpssignal/gps_signal.hpp>
#include <userver/utest/utest.hpp>
#include <views/common/shorttrack_helper.hpp>

namespace {

void Check(const gpssignal::GpsSignal& value,
           const gpssignal::GpsSignal& should_be) {
  ASSERT_EQ(value.latitude, should_be.latitude);
  ASSERT_EQ(value.longitude, should_be.longitude);
  ASSERT_EQ(value.speed, should_be.speed);
  ASSERT_EQ(value.direction, should_be.direction);
  ASSERT_EQ(value.accuracy, should_be.accuracy);
  ASSERT_EQ(value.timestamp, should_be.timestamp);
}

void Check(const gpssignal::GpsSignal& value,
           const geobus::types::ProbableEdgePosition& should_be,
           const std::chrono::system_clock::time_point& should_be_timepoint) {
  ASSERT_EQ(value.latitude, should_be.GetLatitude());
  ASSERT_EQ(value.longitude, should_be.GetLongitude());
  ASSERT_EQ(value.speed, should_be.GetSpeed());
  ASSERT_EQ(value.direction, should_be.GetDirection());
  ASSERT_EQ(value.timestamp, should_be_timepoint);
}

// 04.08.2020 17:11:35
constexpr const size_t kTimestamp1 = 1596550295;
// 04.08.2020 17:11:45
constexpr const size_t kTimestamp2 = kTimestamp1 + 10;

UTEST(ConversionTest, ShorttracksBasic) {
  flatbuffers::FlatBufferBuilder bld;
  bld.ForceDefaults(true);

  namespace conversion =
      driver_trackstory::handlers::shorttrack_helpers::conversion;
  namespace fbs = driver_trackstory::fbs;
  std::vector<flatbuffers::Offset<fbs::ResponseForDriver>> response_for_drivers;

  std::vector<flatbuffers::Offset<fbs::GpsPosition>> raw_offsets;
  std::vector<flatbuffers::Offset<fbs::GpsPosition>> adjusted_offsets;
  // raw signals
  gpssignal::GpsSignal raw_full_signal(
      50.0 * geometry::lat, 37.0 * geometry::lon,
      14.0 * geometry::meters_per_second, 200 * geometry::meters,
      static_cast<uint16_t>(150) * geometry::degree,
      std::chrono::system_clock::from_time_t(kTimestamp1));

  gpssignal::GpsSignal raw_full_signal_zero_values(
      50.0 * geometry::lat, 37.0 * geometry::lon,
      0.0 * geometry::meters_per_second, 0.0 * geometry::meters,
      static_cast<uint16_t>(0) * geometry::degree,
      std::chrono::system_clock::from_time_t(kTimestamp1));

  gpssignal::GpsSignal raw_signal_with_optionals(
      51.0 * geometry::lat, 38.0 * geometry::lon, std::nullopt, std::nullopt,
      std::nullopt, std::chrono::system_clock::from_time_t(kTimestamp2));

  raw_offsets.push_back(
      driver_trackstory::handlers::shorttrack_helpers::conversion::ConvertToFbs(
          bld, raw_full_signal));
  raw_offsets.push_back(
      conversion::ConvertToFbs(bld, raw_full_signal_zero_values));
  raw_offsets.push_back(
      conversion::ConvertToFbs(bld, raw_signal_with_optionals));

  // adjusted signal (only one, because adjusted signal doesn't have optional
  // fields)
  geobus::types::ProbableEdgePosition adj_signal(
      37.0 * geometry::lon, 50.0 * geometry::lat, 0, 0, 0, 0);
  adj_signal.SetSpeed(15.0 * geometry::meters_per_second);
  adj_signal.SetDirection(::geometry::Azimuth::from_value(15));

  adjusted_offsets.push_back(conversion::ConvertToFbs(
      bld, adj_signal, std::chrono::system_clock::from_time_t(kTimestamp1)));

  constexpr const size_t drivers_count = 3;
  for (size_t i = 0; i < drivers_count; ++i) {
    const std::string id = std::string{"driver"} + std::to_string(i);
    response_for_drivers.push_back(
        driver_trackstory::fbs::CreateResponseForDriverDirect(
            bld, id.c_str(), &raw_offsets, &adjusted_offsets));
  }

  auto resp =
      driver_trackstory::fbs::CreateResponseDirect(bld, &response_for_drivers);
  bld.Finish(resp);
  std::string fbs_string{reinterpret_cast<const char*>(bld.GetBufferPointer()),
                         bld.GetSize()};

  clients::driver_trackstory::ShorttracksResponse response =
      driver_trackstory_client::conversion::from_fbs::ParseShorttracksFbs(
          fbs_string);

  ASSERT_EQ(response.extra.size(), drivers_count);
  for (size_t i = 0; i < drivers_count; ++i) {
    const std::string id = std::string{"driver"} + std::to_string(i);
    ASSERT_EQ(response.extra[id].raw.has_value(), true);
    ASSERT_EQ(response.extra[id].adjusted.has_value(), true);
    Check((*response.extra[id].raw)[0], raw_full_signal);
    Check((*response.extra[id].raw)[1], raw_full_signal_zero_values);
    Check((*response.extra[id].raw)[2], raw_signal_with_optionals);
    Check((*response.extra[id].adjusted)[0], adj_signal,
          std::chrono::system_clock::from_time_t(kTimestamp1));
  }
}

UTEST(ConversionTest, ShorttracksCorrectEmptyCheck1) {
  flatbuffers::FlatBufferBuilder bld;
  bld.ForceDefaults(true);

  namespace conversion =
      driver_trackstory::handlers::shorttrack_helpers::conversion;
  namespace fbs = driver_trackstory::fbs;
  std::vector<flatbuffers::Offset<fbs::ResponseForDriver>> response_for_drivers;

  std::vector<flatbuffers::Offset<fbs::GpsPosition>> raw_offsets;
  std::vector<flatbuffers::Offset<fbs::GpsPosition>> adjusted_offsets;

  response_for_drivers.push_back(
      driver_trackstory::fbs::CreateResponseForDriverDirect(
          bld, "driver1", &raw_offsets, nullptr));
  response_for_drivers.push_back(
      driver_trackstory::fbs::CreateResponseForDriverDirect(
          bld, "driver2", nullptr, &adjusted_offsets));
  response_for_drivers.push_back(
      driver_trackstory::fbs::CreateResponseForDriverDirect(
          bld, "driver3", &raw_offsets, &adjusted_offsets));
  response_for_drivers.push_back(
      driver_trackstory::fbs::CreateResponseForDriverDirect(bld, "driver4",
                                                            nullptr, nullptr));

  auto resp =
      driver_trackstory::fbs::CreateResponseDirect(bld, &response_for_drivers);
  bld.Finish(resp);
  std::string fbs_string{reinterpret_cast<const char*>(bld.GetBufferPointer()),
                         bld.GetSize()};

  clients::driver_trackstory::ShorttracksResponse response =
      driver_trackstory_client::conversion::from_fbs::ParseShorttracksFbs(
          fbs_string);

  ASSERT_EQ(response.extra.size(), 4);
  ASSERT_EQ(response.extra["driver1"].raw.has_value(), false);
  ASSERT_EQ(response.extra["driver1"].adjusted.has_value(), false);
  ASSERT_EQ(response.extra["driver2"].raw.has_value(), false);
  ASSERT_EQ(response.extra["driver2"].adjusted.has_value(), false);
  ASSERT_EQ(response.extra["driver3"].raw.has_value(), false);
  ASSERT_EQ(response.extra["driver3"].adjusted.has_value(), false);
  ASSERT_EQ(response.extra["driver4"].raw.has_value(), false);
  ASSERT_EQ(response.extra["driver4"].adjusted.has_value(), false);
}

UTEST(ConversionTest, ShorttracksCorrectEmptyCheck2) {
  flatbuffers::FlatBufferBuilder bld;
  bld.ForceDefaults(true);

  namespace conversion =
      driver_trackstory::handlers::shorttrack_helpers::conversion;
  namespace fbs = driver_trackstory::fbs;
  auto resp = driver_trackstory::fbs::CreateResponseDirect(bld, nullptr);
  bld.Finish(resp);
  std::string fbs_string{reinterpret_cast<const char*>(bld.GetBufferPointer()),
                         bld.GetSize()};

  clients::driver_trackstory::ShorttracksResponse response =
      driver_trackstory_client::conversion::from_fbs::ParseShorttracksFbs(
          fbs_string);

  ASSERT_EQ(response.extra.size(), 0);
}

}  // namespace
