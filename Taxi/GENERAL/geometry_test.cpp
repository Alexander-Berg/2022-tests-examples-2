#include "geometry.hpp"

#include <gtest/gtest.h>

using namespace utils::geometry;

struct SimplePoint {
  double lat;
  double lon;

  bool operator==(const SimplePoint& obj) const {
    return lat == obj.lat && lon == obj.lon;
  }
};

struct TimePoint {
  double lat;
  double lon;
  double timestamp;

  bool operator==(const TimePoint& obj) const {
    return lat == obj.lat && lon == obj.lon && timestamp == obj.timestamp;
  }
};

TEST(DropSamePoints, One) {
  std::vector<SimplePoint> track(
      {{1., 1.}, {2., 2.}, {2., 2.}, {3., 3.}, {3., 3.}, {3., 3.}});
  DropSamePoints(track);
  ASSERT_EQ(3u, track.size());
  EXPECT_EQ((SimplePoint{1., 1.}), track[0]);
  EXPECT_EQ((SimplePoint{2., 2.}), track[1]);
  EXPECT_EQ((SimplePoint{3., 3.}), track[2]);
}

TEST(DropSameTimePoints, One) {
  std::vector<TimePoint> track({{1., 1., 100.},
                                {2., 2., 99.},
                                {2., 2., 98.},
                                {3., 3., 97.},
                                {3., 3., 96.},
                                {3., 3., 95.}});
  DropSameTimePoints(track);
  ASSERT_EQ(5u, track.size());
  EXPECT_EQ((TimePoint{1., 1., 100.}), track[0]);
  EXPECT_EQ((TimePoint{2., 2., 99.}), track[1]);
  EXPECT_EQ((TimePoint{2., 2., 98.}), track[2]);
  EXPECT_EQ((TimePoint{3., 3., 97.}), track[3]);
  EXPECT_EQ((TimePoint{3., 3., 95.}), track[4]);
}

TEST(DropSameTimePoints, Two) {
  std::vector<TimePoint> track({{1., 1., 0.},
                                {2., 2., 0.},
                                {2., 2., 0.},
                                {3., 3., 0.},
                                {3., 3., 0.},
                                {3., 3., 0.}});
  DropSameTimePoints(track);
  ASSERT_EQ(3u, track.size());
  EXPECT_EQ((TimePoint{1., 1., 0.}), track[0]);
  EXPECT_EQ((TimePoint{2., 2., 0.}), track[1]);
  EXPECT_EQ((TimePoint{3., 3., 0.}), track[2]);
}
