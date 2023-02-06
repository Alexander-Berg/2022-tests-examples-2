#include <trackstory-shared/types.hpp>
#include <trackstory-shorttracks/shorttracks.hpp>
#include <trackstory-shorttracks/track.hpp>

#include <gtest/gtest.h>
#include <gpssignal/test/gpssignal_plugin_test.hpp>

using gpssignal::test::GpsSignalTestPlugin;

/// TODO: https://st.yandex-team.ru/TAXIGRAPH-1074

TEST(ShorttracksTrackFixture, TrackCheckAdd) {
  trackstory::GpsPoint orig{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  trackstory::shorttracks::Track<trackstory::GpsPointEx> track;
  track.SetCapacity(5);
  track.AddPoint(orig);

  ASSERT_EQ(track.points.size(), 1);
}

TEST(ShorttracksTrackFixture, TrackCheckDoNotAddTwiceTheSame) {
  trackstory::GpsPoint orig{
      37 * ::gpssignal::lon,
      55 * ::gpssignal::lat,
      ::gpssignal::Speed::from_value(16.0),
      2.0 * ::geometry::meter,
      ::gpssignal::Azimuth::from_value(42),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  trackstory::shorttracks::Track<trackstory::GpsPointEx> track;
  track.SetCapacity(5);
  track.AddPoint(orig);
  track.AddPoint(orig);
  track.AddPoint(orig);

  ASSERT_EQ(track.points.size(), 1);
}

TEST(ShorttracksTrackFixture, TrackCheckAddAdjusted) {
  trackstory::shorttracks::GpsAdjustedPoint orig{
      ::geobus::types::ProbableEdgePosition(
          37 * ::gpssignal::lon, 55 * ::gpssignal::lat, 0, 0.0, 1.0, 0.0),
      trackstory::TimePoint(std::chrono::milliseconds(111))};
  trackstory::shorttracks::GpsAdjustedPoint orig2{
      ::geobus::types::ProbableEdgePosition(
          37 * ::gpssignal::lon, 55 * ::gpssignal::lat, 0, 0.0, 1.0, 0.0),
      trackstory::TimePoint(std::chrono::milliseconds(110))};

  /// Check don't add same timepoint more than one time
  trackstory::shorttracks::Track<trackstory::shorttracks::GpsAdjustedPoint>
      track;
  track.SetCapacity(5);
  track.AddPoint(orig);
  track.AddPoint(orig);
  track.AddPoint(orig);

  ASSERT_EQ(track.points.size(), 1);

  /// Check add timepoint with just another timestamp (test for operator== in
  /// GpsAdjustedPoint structure).
  track.AddPoint(orig2);
  ASSERT_EQ(track.points.size(), 2);
}

TEST(ShorttracksTrackFixture, FilterByTime) {
  trackstory::GpsPoint orig{37 * ::gpssignal::lon,
                            55 * ::gpssignal::lat,
                            ::gpssignal::Speed::from_value(16.0),
                            2.0 * ::geometry::meter,
                            ::gpssignal::Azimuth::from_value(42),
                            trackstory::TimePoint(std::chrono::seconds(10))};
  trackstory::shorttracks::Track<trackstory::GpsPointEx> track;
  track.SetCapacity(5);
  track.AddPoint(orig);
  ASSERT_EQ(1, track.points.size());

  auto point2 = orig;
  point2.timestamp = trackstory::TimePoint{std::chrono::seconds{20}};
  track.AddPoint(point2);
  ASSERT_EQ(2, track.points.size());

  track.FilterByTime(trackstory::TimePoint(std::chrono::seconds{15}));
  ASSERT_EQ(1, track.points.size());
  ASSERT_EQ(point2.timestamp, track.points[0].timestamp);
}

TEST(ShorttracksTrackFixture, FilterByTime2) {
  trackstory::GpsPoint orig{37 * ::gpssignal::lon,
                            55 * ::gpssignal::lat,
                            ::gpssignal::Speed::from_value(16.0),
                            2.0 * ::geometry::meter,
                            ::gpssignal::Azimuth::from_value(42),
                            trackstory::TimePoint(std::chrono::seconds(10))};
  trackstory::shorttracks::Track<trackstory::GpsPointEx> track;

  track.SetCapacity(15);
  for (size_t i = 1; i <= 10; ++i) {
    auto point = orig;
    point.timestamp = trackstory::TimePoint{std::chrono::seconds{i * 10}};
    track.AddPoint(point);
  }
  ASSERT_EQ(10, track.points.size());

  track.FilterByTime(trackstory::TimePoint(std::chrono::seconds{50}));
  ASSERT_EQ(5, track.points.size());
}

TEST(ShorttracksTrackFixture, Iteration) {
  trackstory::GpsPoint orig{37 * ::gpssignal::lon,
                            55 * ::gpssignal::lat,
                            ::gpssignal::Speed::from_value(16.0),
                            2.0 * ::geometry::meter,
                            ::gpssignal::Azimuth::from_value(42),
                            trackstory::TimePoint(std::chrono::seconds(10))};
  trackstory::shorttracks::Track<trackstory::GpsPointEx> track;
  track.SetCapacity(5);
  track.AddPoint(orig);
  ASSERT_EQ(1, track.points.size());

  auto point2 = orig;
  point2.timestamp = trackstory::TimePoint{std::chrono::seconds{20}};
  track.AddPoint(point2);
  ASSERT_EQ(2, track.points.size());

  EXPECT_GT(track.BeginFromMostRecentToOldest()->timestamp,
            (track.BeginFromMostRecentToOldest() + 1)->timestamp);
  EXPECT_LT(track.BeginFromOldestToMostRecent()->timestamp,
            (track.BeginFromOldestToMostRecent() + 1)->timestamp);
}
