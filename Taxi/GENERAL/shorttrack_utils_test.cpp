#include "shorttrack_utils.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>

namespace {

using utils::geometry::TrackPoint;

config::ShortTrackConfig GetShorttrackConfig() {
  Json::Value v;
  v["TRACK_MAX_COUNT"] = 1;
  v["TAXIROUTE_FALLBACK_TO_RAW_TRACK"] = true;
  v["TRACK_MAX_AGE"] = 1;
  v["TRACK_MAX_AGE_INDEX"] = 1;
  v["TRACK_UPDATE_MODE"] = 1;
  v["TRACK_EVENT_REDIS_CC"] = {};
  v["TRACK_USE_ACCURACY_ON"] = false;
  v["SHORTTRACK_LOW_DISTANCE_FILTER_ENABLE"] = true;
  v["SHORTTRACK_LOW_DISTANCE_FILTER_DISTANCE"] = 10;
  v["SHORTTRACK_LOW_DISTANCE_FILTER_TIME"] = 60;
  v["SHORTTRACK_ADJUSTED_OBSOLESCENCE"] = 5;
  v["SHORTTRACK_MAX_MESSAGES_SIZE"] = 256;
  v["USE_DRIVER_TRACKSTORY_PERCENT"] = 0;
  v["USE_DRIVER_TRACKSTORY_DP_PERCENT"] = 0;

  config::DocsMap docs_map;
  docs_map.Parse(v.toStyledString());
  return config::ShortTrackConfig(docs_map);
}

bool IsSorted(const utils::geometry::Track& track) {
  for (size_t i = 1; i < track.size(); ++i) {
    if (track[i - 1].timestamp < track[i].timestamp) return false;
  }
  return true;
}

}  // namespace

TEST(IsPreviusPointNeedModify, TooFarFirstPoint) {
  const auto timestamp = std::chrono::system_clock::from_time_t(1533731553);
  TrackPoint point0(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point1(55.1, 35.0, 0, 0, timestamp);
  TrackPoint point2(55.0, 35.0, 0, 0, timestamp);
  ASSERT_FALSE(shorttrack::IsPreviusPointNeedModify(point0, point1, point2,
                                                    GetShorttrackConfig()));
}

TEST(IsPreviusPointNeedModify, TooFarSecondPoint) {
  const auto timestamp = std::chrono::system_clock::from_time_t(1533731553);
  TrackPoint point0(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point1(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point2(55.1, 35.1, 0, 0, timestamp);
  ASSERT_FALSE(shorttrack::IsPreviusPointNeedModify(point0, point1, point2,
                                                    GetShorttrackConfig()));
}

TEST(IsPreviusPointNeedModify, TooOldSecondPoint) {
  const auto timestamp = std::chrono::system_clock::from_time_t(1533731553);
  TrackPoint point0(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point1(55.0, 35.0, 0, 0, timestamp - std::chrono::seconds(90));
  TrackPoint point2(55.0, 35.0, 0, 0, timestamp - std::chrono::seconds(99));
  ASSERT_FALSE(shorttrack::IsPreviusPointNeedModify(point0, point1, point2,
                                                    GetShorttrackConfig()));
}

TEST(IsPreviusPointNeedModify, Modify) {
  const auto timestamp = std::chrono::system_clock::from_time_t(1533731553);
  TrackPoint point0(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point1(55.0, 35.0, 0, 0, timestamp);
  TrackPoint point2(55.0, 35.0, 0, 0, timestamp - std::chrono::seconds(1));
  ASSERT_TRUE(shorttrack::IsPreviusPointNeedModify(point0, point1, point2,
                                                   GetShorttrackConfig()));
}

TEST(InsertOriginPoint, Simple) {
  auto timestamp = std::chrono::system_clock::from_time_t(1533731553);
  utils::geometry::Track track;
  config::ShortTrackConfig shorttrack_config = GetShorttrackConfig();

  shorttrack::InsertOriginPoint(track, TrackPoint(55.0, 35.0, 0, 0, timestamp),
                                shorttrack_config);
  timestamp += std::chrono::seconds(3);
  shorttrack::InsertOriginPoint(track, TrackPoint(55.0, 35.0, 0, 0, timestamp),
                                shorttrack_config);
  timestamp += std::chrono::seconds(1);
  shorttrack::InsertOriginPoint(track, TrackPoint(55.0, 35.0, 0, 0, timestamp),
                                shorttrack_config);
  ASSERT_EQ(2u, track.size());
  EXPECT_EQ(timestamp, track.front().timestamp);
  EXPECT_TRUE(IsSorted(track));

  timestamp -= std::chrono::seconds(2);
  shorttrack::InsertOriginPoint(track, TrackPoint(55.0, 35.0, 0, 0, timestamp),
                                shorttrack_config);
  ASSERT_EQ(2u, track.size());
  EXPECT_EQ(timestamp + std::chrono::seconds(2), track.front().timestamp);
  EXPECT_TRUE(IsSorted(track));

  timestamp += std::chrono::seconds(1);
  shorttrack::InsertOriginPoint(track, TrackPoint(55.0, 35.0, 0, 0, timestamp),
                                shorttrack_config);
  ASSERT_EQ(2u, track.size());
  EXPECT_EQ(timestamp + std::chrono::seconds(1), track.front().timestamp);
  EXPECT_TRUE(IsSorted(track));

  timestamp += std::chrono::seconds(5);
  shorttrack::InsertOriginPoint(track, TrackPoint(55.1, 35.1, 0, 0, timestamp),
                                shorttrack_config);
  ASSERT_EQ(3u, track.size());
  EXPECT_EQ(timestamp, track.front().timestamp);
  EXPECT_TRUE(IsSorted(track));
}
