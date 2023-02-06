#include <test/time_helpers.h>
#include <geobus/channels/universal_signals/universal_signals.hpp>
#include <geobus/channels/universal_signals/universal_signals_generator.hpp>
#include <lowlevel/fb_serialization_test.hpp>
#include "lowlevel.hpp"
#include "test_traits.hpp"

#include <gtest/gtest.h>

namespace geobus::lowlevel {

TEST(GeobusUniversalPositions, TestParseNoCompressionMessage) {
  const types::DriverId kContractorId1{"1_01234"};
  const std::chrono::time_point kClientTimestamp1 =
      helpers::time::CropTo<std::chrono::microseconds>(
          std::chrono::system_clock::now());
  const std::string kSource1{"AndroidGps"};
  const std::vector<std::pair<std::string, std::vector<unsigned char>>>
      kSensors1{{"key1", {'v', 'a', 'l', 'u', 'e', '1'}},
                {"key2", {'v', 'a', 'l', 'u', 'e', '2'}}};

  const geometry::Latitude kLat11 = geometry::Latitude::from_value(34.123645);
  const geometry::Longitude kLon11 = geometry::Longitude::from_value(46.132645);
  const gpssignal::Speed kSpeed11 = gpssignal::Speed::from_value(1.65);
  const geometry::Distance kAccuracy11 = geometry::Distance::from_value(15.0);
  const geometry::Azimuth kDirection11 = geometry::Azimuth::from_value(45);
  const geometry::Distance kAltitude11 = geometry::Distance::from_value(500);
  const std::chrono::seconds kPredictionShift11{40};
  const std::chrono::system_clock::time_point kSignalTimestamp11 =
      kClientTimestamp1 + kPredictionShift11;
  const gpssignal::GpsSignal kSignal11{
      kLat11,       kLon11,      kSpeed11,          kAccuracy11,
      kDirection11, kAltitude11, kSignalTimestamp11};
  const types::PositionOnEdge kPositionOnEdge11{123456ul, 37567.0 / 65535.0};
  const float kProbability11 = 228.0 / 255.0;
  const double kLogLikelihood11 = 436.986234;

  const geometry::Latitude kLat12 = geometry::Latitude::from_value(34.123678);
  const geometry::Longitude kLon12 = geometry::Longitude::from_value(46.132612);
  const gpssignal::Speed kSpeed12 = gpssignal::Speed::from_value(1.36);
  const geometry::Distance kAccuracy12 = geometry::Distance::from_value(1.50);
  const geometry::Azimuth kDirection12 = geometry::Azimuth::from_value(47);
  const geometry::Distance kAltitude12 = geometry::Distance::from_value(478);
  const std::chrono::seconds kPredictionShift12{40};
  const std::chrono::system_clock::time_point kSignalTimestamp12 =
      kClientTimestamp1 + kPredictionShift12;
  const gpssignal::GpsSignal kSignal12{
      kLat12,       kLon12,      kSpeed12,          kAccuracy12,
      kDirection12, kAltitude12, kSignalTimestamp12};
  const types::PositionOnEdge kPositionOnEdge12{7689124ul, 0.0};
  const float kProbability12 = 200.0 / 255.0;
  const double kLogLikelihood12 = 432.454657;

  const types::DriverId kContractorId2{"2_67890"};
  const std::chrono::time_point kClientTimestamp2 =
      helpers::time::CropTo<std::chrono::microseconds>(
          std::chrono::system_clock::now());
  const std::string kSource2{"Raw"};
  const std::vector<std::pair<std::string, std::vector<unsigned char>>>
      kSensors2{{"key3", {'v', 'a', 'l', 'u', 'e', '3'}},
                {"key4", {'v', 'a', 'l', 'u', 'e', '4'}}};

  const geometry::Latitude kLat21 = geometry::Latitude::from_value(65.678321);
  const geometry::Longitude kLon21 = geometry::Longitude::from_value(5.870123);
  const gpssignal::Speed kSpeed21 = gpssignal::Speed::from_value(0.0);
  const geometry::Distance kAccuracy21 = geometry::Distance::from_value(0.0);
  const geometry::Azimuth kDirection21 = geometry::Azimuth::from_value(347);
  const geometry::Distance kAltitude21 = geometry::Distance::from_value(0);
  const std::chrono::seconds kPredictionShift21{60};
  const std::chrono::system_clock::time_point kSignalTimestamp21 =
      kClientTimestamp2 + kPredictionShift21;
  const gpssignal::GpsSignal kSignal21{
      kLat21,       kLon21,      kSpeed21,          kAccuracy21,
      kDirection21, kAltitude21, kSignalTimestamp21};
  const types::PositionOnEdge kPositionOnEdge21{3243245ul, 1.0};
  const float kProbability21 = 248.0 / 255.0;
  const double kLogLikelihood21 = 50.8;

  const types::UniversalSignals kSignals1{
      kContractorId1,
      kClientTimestamp1,
      kSource1,
      kSensors1,
      {{kSignal11, kPositionOnEdge11, kPredictionShift11, kProbability11,
        kLogLikelihood11},
       {kSignal12, kPositionOnEdge12, kPredictionShift12, kProbability12,
        kLogLikelihood12}}};
  const types::UniversalSignals kSignals2{
      kContractorId2,
      kClientTimestamp2,
      kSource2,
      kSensors2,
      {{kSignal21, kPositionOnEdge21, kPredictionShift21, kProbability21,
        kLogLikelihood21}}};
  std::vector<types::UniversalSignals> expected{kSignals1, kSignals2};

  const std::string data = universal_signals::SerializeMessage(expected);

  statistics::PayloadStatistics<universal_signals::ParseInvalidStats> stats;
  auto actual = universal_signals::ParseData(data, stats);

  test::DataTypeTestTraits<types::UniversalSignals>::TestElementsAreEqual(
      expected.begin(), expected.end(), actual.begin(), actual.end(),
      test::ComparisonPrecision::FbsPrecision);
}

TEST(GeobusUniversalPositions, TestSerializeParseDataMethod) {
  generators::UniversalSignalsGenerator generator;
  std::vector<types::UniversalSignals> expected = {
      generator.CreateElement(18), generator.CreateElement(31),
      generator.CreateElement(60), generator.CreateElement(61),
      generator.CreateElement(90), generator.CreateElement(95)};

  // Serialize payload. Those methods only test 'data' part of payload
  flatbuffers::FlatBufferBuilder builder;
  lowlevel::universal_signals::SerializeData(expected, builder);
  std::string_view fb_data{
      reinterpret_cast<const char*>(builder.GetBufferPointer()),
      builder.GetSize()};

  // Now, parse it back
  statistics::PayloadStatistics<lowlevel::universal_signals::ParseInvalidStats>
      parse_stats;
  auto unpacked_data =
      lowlevel::universal_signals::ParseData(fb_data, parse_stats);

  test::DataTypeTestTraits<types::UniversalSignals>::TestElementsAreEqual(
      expected.begin(), expected.end(), unpacked_data.begin(),
      unpacked_data.end(), test::ComparisonPrecision::FbsPrecision);
}

TEST(GeobusUniversalPositions, TestParseNoCompressionGenMessage) {
  generators::UniversalSignalsGenerator generator;
  std::vector<types::UniversalSignals> expected = {generator.CreateElement(14),
                                                   generator.CreateElement(30)};

  const std::string& data = universal_signals::SerializeMessage({expected});

  statistics::PayloadStatistics<universal_signals::ParseInvalidStats> stats;
  auto actual = universal_signals::ParseData(data, stats);

  test::DataTypeTestTraits<types::UniversalSignals>::TestElementsAreEqual(
      expected.begin(), expected.end(), actual.begin(), actual.end(),
      test::ComparisonPrecision::FbsPrecision);
}

namespace universal_signals {

INSTANTIATE_TYPED_TEST_SUITE_P(UniversalSignalsSerializationTest,
                               FlatbuffersSerializationTest,
                               types::UniversalSignals);

}  // namespace universal_signals
}  // namespace geobus::lowlevel
