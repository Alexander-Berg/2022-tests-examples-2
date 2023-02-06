#include "adjust_tracks.hpp"

#include <gtest/gtest.h>

static geobus::Point DummyPoint(double lon, double lat, time_t time) {
  return geobus::Point(lon, lat, utils::geometry::kNoDirection, 0, time);
}

static bool TracksEquals(const geobus::Tracks& tracks1,
                         const geobus::Tracks& tracks2) {
  if (tracks1.size() != tracks2.size()) return false;
  for (size_t i = 0; i < tracks1.size(); ++i) {
    const auto& t1 = tracks1[i];
    const auto& t2 = tracks2[i];
    const models::DriverId& d1 = t1.first;
    const models::DriverId& d2 = t2.first;

    if (!d1.dbid.empty() && !d2.dbid.empty()) {
      if (d1.dbid != d2.dbid) return false;
    } else if (!d1.clid.empty() && !d2.clid.empty()) {
      if (d1.clid != d2.clid) return false;
    }

    if (!(t1.second == t2.second)) return false;
  }

  return true;
}

TEST(GeobusAdjustTracks, One) {
  geobus::Tracks orig_tracks;
  orig_tracks.push_back(
      {models::DriverId("1", "1", "01234"),
       {geobus::Point{0.0, 1.0, 2, 3, 4,
                      utils::geometry::PointSource::Adjuster}}});
  orig_tracks.push_back(
      {models::DriverId("1", "1", "56789"),
       {geobus::Point{5.0, 6.0, 7, 8, 9,
                      utils::geometry::PointSource::Navigator}}});
  orig_tracks.push_back({models::DriverId("1", "1", "qwerty"),
                         {geobus::Point{1.4, 5}, geobus::Point{3, 1.3}}});

  const std::string& data = geobus::SerializeAdjustTrackEvent(orig_tracks);
  const auto& event = geobus::DeserializeAdjustTrackEvent(data);

  EXPECT_TRUE(TracksEquals(orig_tracks, event.adst_tracks));
}

TEST(GeobusAdjustTracks, Diff) {
  const geobus::Track track0({DummyPoint(12.0, 12.0, 102),
                              DummyPoint(11.0, 11.0, 101),
                              DummyPoint(10.0, 10.0, 100)});
  const geobus::Track track1(
      {DummyPoint(14.0, 14.0, 104), DummyPoint(13.0, 13.0, 103),
       DummyPoint(12.0, 12.0, 102), DummyPoint(11.0, 11.0, 101)});
  const geobus::Track track3({DummyPoint(13.0, 13.0, 103),
                              DummyPoint(12.0, 12.0, 102),
                              DummyPoint(9.0, 9.0, 90)});

  // case 0: ok
  const geobus::Track& diff0 = geobus::MakeAdjustTrackDiff(track0, track1);
  ASSERT_EQ(2u, diff0.size());
  EXPECT_EQ(track1[0], diff0[0]);
  EXPECT_EQ(track1[1], diff0[1]);

  const geobus::Track& undiff0 = geobus::ApplyAdjustTrackDiff(track0, diff0);
  // undiff is more long
  for (size_t i = 0; i < track1.size(); ++i) EXPECT_EQ(track1[i], undiff0[i]);

  // case 1: not full match
  const geobus::Track& diff1 = geobus::MakeAdjustTrackDiff(track0, track3);
  EXPECT_EQ(track3, diff1);

  const geobus::Track& undiff1 = geobus::ApplyAdjustTrackDiff(track0, diff1);
  EXPECT_EQ(track3, undiff1);

  // case 2: no match
  const geobus::Track& diff2 = geobus::MakeAdjustTrackDiff(track1, track3);
  EXPECT_EQ(track3, diff2);

  const geobus::Track& undiff2 = geobus::ApplyAdjustTrackDiff(track1, diff2);
  EXPECT_EQ(track3, undiff2);

  // case 3: equal
  const geobus::Track& diff3 = geobus::MakeAdjustTrackDiff(track1, track1);
  EXPECT_TRUE(diff3.empty());

  const geobus::Track& undiff3 = geobus::ApplyAdjustTrackDiff(track1, diff3);
  EXPECT_EQ(track1, undiff3);
}
