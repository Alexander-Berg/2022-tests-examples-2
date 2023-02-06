#include <gtest/gtest.h>

#include "driver_positions.hpp"

using geobus::types::PositionSource;
using gpssignal::GpsSignal;
using models::geometry::PointSource;
using models::geometry::TrackPoint;

TEST(ChooseTrackPoint, Sample) {
  using geobus::helpers::ChooseTrackPoint;

  const std::chrono::seconds max_adjust_obsolescence{5};
  const std::chrono::system_clock::time_point now =
      std::chrono::system_clock::now();
  geobus::helpers::AdjustTrack adjust_track;
  auto& track{adjust_track.data};
  for (int i = 0; i < 7; ++i) {
    track.emplace_back(
        GpsSignal{i * ::geometry::lon, 0 * ::geometry::lat,
                  0.0 * ::geometry::meters_per_second, 0.0 * ::geometry::meters,
                  static_cast<int_fast16_t>(0) * ::geometry::degree,
                  now - std::chrono::seconds(i)},
        PositionSource::Gps);
  }
  track[6].source = PositionSource::Adjuster;
  auto point = ChooseTrackPoint(adjust_track, max_adjust_obsolescence);
  EXPECT_EQ(point.lon, 0);

  track[5].source = PositionSource::Adjuster;
  point = ChooseTrackPoint(adjust_track, max_adjust_obsolescence);
  EXPECT_EQ(point.lon, 5);

  point = ChooseTrackPoint(adjust_track, std::chrono::seconds(10));
  EXPECT_EQ(point.lon, 5);

  std::reverse(track.begin(), track.end());

  point = ChooseTrackPoint(adjust_track, std::chrono::seconds(4));
  EXPECT_EQ(point.lon, 0);

  point = ChooseTrackPoint(adjust_track, std::chrono::seconds(5));
  EXPECT_EQ(point.lon, 5);

  point = ChooseTrackPoint(adjust_track, std::chrono::seconds(10));
  EXPECT_EQ(point.lon, 5);

  for (auto& track_point : track) {
    track_point.source = PositionSource::Gps;
  }

  point = ChooseTrackPoint(adjust_track, std::chrono::seconds(10));
  EXPECT_EQ(point.lon, 0);
}

TEST(NeedUpdatePoint, Sample) {
  using geobus::helpers::NeedUpdatePoint;

  const std::chrono::seconds max_adjust_obsolescence{5};
  const std::chrono::system_clock::time_point now =
      std::chrono::system_clock::now();

  TrackPoint point1(0, 0, 0, 0, 0, now, PointSource::Gps);
  TrackPoint point2(0, 0, 0, 0, 0, now, PointSource::Adjuster);
  EXPECT_TRUE(NeedUpdatePoint(point1, point2, max_adjust_obsolescence));
  EXPECT_FALSE(NeedUpdatePoint(point2, point1, max_adjust_obsolescence));

  point2.timestamp = now + max_adjust_obsolescence;
  EXPECT_TRUE(NeedUpdatePoint(point1, point2, max_adjust_obsolescence));
  EXPECT_FALSE(NeedUpdatePoint(point2, point1, max_adjust_obsolescence));

  point2.timestamp = now - max_adjust_obsolescence;
  EXPECT_TRUE(NeedUpdatePoint(point1, point2, max_adjust_obsolescence));
  EXPECT_FALSE(NeedUpdatePoint(point2, point1, max_adjust_obsolescence));

  point2.timestamp -= std::chrono::seconds(1);
  EXPECT_FALSE(NeedUpdatePoint(point1, point2, max_adjust_obsolescence));
  EXPECT_TRUE(NeedUpdatePoint(point2, point1, max_adjust_obsolescence));

  point2.source = PointSource::Gps;
  point2.timestamp = now + std::chrono::seconds(1);
  EXPECT_TRUE(NeedUpdatePoint(point1, point2, max_adjust_obsolescence));
  EXPECT_FALSE(NeedUpdatePoint(point2, point1, max_adjust_obsolescence));
}
