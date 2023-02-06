#include <trackstory/filter.hpp>
#include <trackstory/types.hpp>

#include <gtest/gtest.h>
#include <boost/range/numeric.hpp>
#include <gpssignal/test/gpssignal_plugin_test.hpp>

using gpssignal::test::GpsSignalTestPlugin;

namespace {

const double kEpsilon = 0.0001;

using ::geometry::degree;

}  // namespace

TEST(MergeClosePositions, SamePointsToTwoPoints) {
  const trackstory::TimePoint first_timestamp(std::chrono::milliseconds(111));
  gpssignal::GpsSignal pos{37 * ::gpssignal::lon,
                           55 * ::gpssignal::lat,
                           ::gpssignal::Speed::from_value(16.0),
                           2.0 * ::geometry::meter,
                           ::gpssignal::Azimuth::from_value(42),
                           first_timestamp};

  std::vector<gpssignal::GpsSignal> track;

  for (int i = 0; i < 10; i++) {
    pos.accuracy = i * 2.0 * ::geometry::meter;
    pos.timestamp = first_timestamp + i * std::chrono::seconds(5);

    track.push_back(pos);
  }

  const auto& filtered_track =
      trackstory::filter::MergeClosePositions(track, 0.0003 * degree);
  ASSERT_EQ(filtered_track.size(), 2ull);
  ASSERT_EQ(filtered_track[0].timestamp, first_timestamp);
  ASSERT_EQ(filtered_track[0].accuracy->value(), 0.0);
  ASSERT_EQ(filtered_track[1].timestamp,
            first_timestamp + std::chrono::seconds(5 * 9));
  ASSERT_EQ(filtered_track[1].accuracy->value(), 9 * 2.0);
}

TEST(MergeClosePositions, TwoSamePointsToFourPoints) {
  const trackstory::TimePoint first_timestamp(std::chrono::milliseconds(111));
  const trackstory::TimePoint second_timestamp(first_timestamp +
                                               +std::chrono::minutes(10));
  gpssignal::GpsSignal pos{37 * ::gpssignal::lon,
                           55 * ::gpssignal::lat,
                           ::gpssignal::Speed::from_value(16.0),
                           2.0 * ::geometry::meter,
                           ::gpssignal::Azimuth::from_value(42),
                           first_timestamp};

  gpssignal::GpsSignal pos2{38 * ::gpssignal::lon,
                            55 * ::gpssignal::lat,
                            ::gpssignal::Speed::from_value(16.0),
                            2.0 * ::geometry::meter,
                            ::gpssignal::Azimuth::from_value(42),
                            second_timestamp};

  std::vector<gpssignal::GpsSignal> track;
  for (int i = 0; i < 10; i++) {
    pos.accuracy = i * 2.0 * ::geometry::meter;
    pos.timestamp = first_timestamp + i * std::chrono::seconds(5);

    track.push_back(pos);
  }
  for (int i = 0; i < 10; i++) {
    pos2.accuracy = i * 2.0 * ::geometry::meter;
    pos2.timestamp = second_timestamp + i * std::chrono::seconds(5);

    track.push_back(pos2);
  }

  const auto& filtered_track =
      trackstory::filter::MergeClosePositions(track, 0.0003 * degree);
  ASSERT_EQ(filtered_track.size(), 4ull);
  ASSERT_EQ(filtered_track[0].timestamp, first_timestamp);
  ASSERT_EQ(filtered_track[0].accuracy->value(), 0.0);
  ASSERT_EQ(filtered_track[1].timestamp,
            first_timestamp + std::chrono::seconds(5 * 9));
  ASSERT_EQ(filtered_track[1].accuracy->value(), 9 * 2.0);
  ASSERT_EQ(filtered_track[2].timestamp, second_timestamp);
  ASSERT_EQ(filtered_track[2].accuracy->value(), 0.0);
  ASSERT_EQ(filtered_track[3].timestamp,
            second_timestamp + std::chrono::seconds(5 * 9));
  ASSERT_EQ(filtered_track[3].accuracy->value(), 9 * 2.0);
}

TEST(MergeWithLastRawPosition, None) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  const auto& merged_pos =
      trackstory::filter::MergeWithLastRawPosition(pos, std::nullopt);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(merged_pos, pos);
}

TEST(MergeWithLastRawPosition, ChooseRawPos) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal raw_pos{
      38 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  const auto& merged_pos =
      trackstory::filter::MergeWithLastRawPosition(pos, raw_pos);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(merged_pos, raw_pos);
}

TEST(MergeWithLastRawPosition, ChooseAdjustPosNoAccuracy) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal raw_pos{
      38 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      std::nullopt,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  const auto& merged_pos =
      trackstory::filter::MergeWithLastRawPosition(pos, raw_pos);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(merged_pos, pos);
}

TEST(MergeWithLastRawPosition, ChooseAdjustPosWithRawPosAccuracy) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal raw_pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};

  const auto& merged_pos =
      trackstory::filter::MergeWithLastRawPosition(pos, raw_pos);
  pos.accuracy = raw_pos.accuracy;
  GpsSignalTestPlugin::TestGpsSignalsAreClose(merged_pos, pos);
}

TEST(FilterUnique, SamePointAndDifferent) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal pos1{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(112))};
  gpssignal::GpsSignal pos2{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(113))};
  gpssignal::GpsSignal pos3{
      37 * ::gpssignal::lon,
      56 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(113))};

  auto track = std::vector<gpssignal::GpsSignal>{pos, pos1, pos2, pos3};
  trackstory::filter::FilterUnique(track, kEpsilon);

  ASSERT_EQ(track.size(), 2ull);
  ASSERT_EQ(track[0], pos);
  ASSERT_EQ(track[1], pos3);
}

TEST(MedianFilter, MedianTest) {
  std::vector<double> data = {10, 1, 2, 3, 4, 18, 6, 7, 8, 9, 10, 25};
  trackstory::filter::MedianFilter(
      data, [](double* z) { return z; }, 3);
  std::vector<double> diffs;
  ASSERT_EQ(*std::prev(data.end()), 25);  // do nothing on borders
  data.erase(std::prev(data.end()));
  boost::adjacent_difference(data, std::back_inserter(diffs));
  ASSERT_LE(boost::accumulate(diffs, 0u), data.size());
}

TEST(MedianFilter, MedianSmallTest) {
  std::vector<double> data = {1, 200, 3};
  trackstory::filter::MedianFilter(
      data, [](double* z) { return z; }, 5);
  std::vector<double> data_eq{1, 200, 3};
  ASSERT_EQ(data, data_eq);
}

TEST(MedianFilter, MedianNoWindowTest) {
  std::vector<double> data = {1, 200, 3, 4, 5};
  trackstory::filter::MedianFilter(
      data, [](double* z) { return z; }, 0);
  std::vector<double> data_eq{1, 200, 3, 4, 5};
  ASSERT_EQ(data, data_eq);
}

TEST(SplitToSegments, SplitByDistance) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal pos1{
      37 * ::gpssignal::lon,
      56 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal pos2{
      37 * ::gpssignal::lon,
      56 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal pos3{
      37 * ::gpssignal::lon,
      57 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  std::vector<gpssignal::GpsSignal> track{pos, pos1, pos2, pos3};

  auto result = trackstory::filter::SplitToSegments(track, 10, 10);
  ASSERT_EQ(result.size(), 3);

  ASSERT_EQ(result[0].size(), 1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[0][0], pos);

  ASSERT_EQ(result[1].size(), 2);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[1][0], pos1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[1][1], pos2);

  ASSERT_EQ(result[2].size(), 1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[2][0], pos3);
}

TEST(SplitToSegments, SplitByTime) {
  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  gpssignal::GpsSignal pos1{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(3111))};
  gpssignal::GpsSignal pos2{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(4111))};
  gpssignal::GpsSignal pos3{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      10.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(7111))};
  std::vector<gpssignal::GpsSignal> track{pos, pos1, pos2, pos3};

  auto result = trackstory::filter::SplitToSegments(track, 2, 10);
  ASSERT_EQ(result.size(), 3);

  ASSERT_EQ(result[0].size(), 1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[0][0], pos);

  ASSERT_EQ(result[1].size(), 2);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[1][0], pos1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[1][1], pos2);

  ASSERT_EQ(result[2].size(), 1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[2][0], pos3);
}

TEST(FilterTrack, MainTest) {
  std::vector<gpssignal::GpsSignal> track;

  gpssignal::GpsSignal pos{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  auto orig_pos = pos;

  // retain, the first one
  track.push_back(pos);

  // remove, not unique
  pos.timestamp += std::chrono::milliseconds(1);
  track.push_back(pos);

  // remove, not unique
  pos.timestamp += std::chrono::milliseconds(1);
  track.push_back(pos);

  // remove, not unique
  pos.timestamp += std::chrono::milliseconds(1);
  track.push_back(pos);

  gpssignal::GpsSignal pos1{
      37 * ::gpssignal::lon,
      56 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(1111))};
  auto orig_pos1 = pos1;

  // retain, too big distance.
  track.push_back(pos1);

  // retain, too big time difference.
  pos1.timestamp += std::chrono::seconds(10);
  track.push_back(pos1);

  trackstory::filter::FilterParams filter_params{2, 10, 5, 1, kEpsilon};
  auto result = trackstory::filter::Filter(track, filter_params);

  ASSERT_EQ(result.size(), 3);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[0], orig_pos);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[1], orig_pos1);
  GpsSignalTestPlugin::TestGpsSignalsAreClose(result[2], pos1);
}
