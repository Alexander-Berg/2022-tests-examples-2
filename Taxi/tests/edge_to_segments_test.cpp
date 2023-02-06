#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <caches/surge_points.hpp>
#include <graph/tests/graph_fixture.hpp>

#include <models/graph_surge_points.hpp>
#include <models/nearest_edges.hpp>
#include <utils/arrange_surge_points.hpp>
#include <views/common.hpp>

namespace tests {
using graph::test::GraphTestFixture;

class EdgeToSegmentsTest : public GraphTestFixture {
 protected:
  EdgeToSegmentsTest() {}
  void SetUp() override { GraphTestFixture::SetUp(); }
};

UTEST_F(EdgeToSegmentsTest, EdgeToSegments) {
  using ::models::Point;

  models::GraphSurgePoints gsp{GetGraph()};

  std::vector<models::NearestEdge> expected = {
      {/*id=*/0,
       {37.6253330 * geometry::lon, 55.7497300 * geometry::lat},
       {37.627109333333323 * geometry::lon, 55.749817 * geometry::lat},
       0,
       {}},
      {/*id=*/1,
       {37.627109333333323 * geometry::lon, 55.749817 * geometry::lat},
       {37.628052222222209 * geometry::lon, 55.749808333333334 * geometry::lat},
       0,
       {}},
      {/*id=*/2,
       {37.628052222222209 * geometry::lon, 55.749808333333334 * geometry::lat},
       {37.632446999999985 * geometry::lon, 55.749493000000001 * geometry::lat},
       0,
       {}}};

  int road_class = 0;
  std::vector<models::NearestFixedPoint> nearest_points = {};
  std::vector<models::NearestEdge> all_edges = {};
  models::EdgeToSegments(all_edges, 203823, 0.999, *GetGraph(), road_class,
                         nearest_points);

  ASSERT_EQ(all_edges.size(), 3);

  for (auto x = all_edges.begin(), y = expected.begin();
       x != all_edges.end() && y != expected.end(); ++x, ++y) {
    EXPECT_DOUBLE_EQ(x->start.GetLongitudeAsDouble(),
                     y->start.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->start.GetLatitudeAsDouble(),
                     y->start.GetLatitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLongitudeAsDouble(),
                     y->end.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLatitudeAsDouble(),
                     y->end.GetLatitudeAsDouble());
  }
}

UTEST_F(EdgeToSegmentsTest, EdgeToSegmentsFactorZero) {
  using ::models::Point;

  models::GraphSurgePoints gsp{GetGraph()};

  std::vector<models::NearestEdge> expected = {
      {/*id=*/0,
       {37.6253330 * geometry::lon, 55.7497300 * geometry::lat},
       {37.6324470 * geometry::lon, 55.7494930 * geometry::lat},
       0,
       {}}};

  int road_class = 0;
  std::vector<models::NearestFixedPoint> nearest_points = {};
  std::vector<models::NearestEdge> all_edges = {};
  models::EdgeToSegments(all_edges, 203823, 0, *GetGraph(), road_class,
                         nearest_points);

  ASSERT_EQ(all_edges.size(), 1);

  for (auto x = all_edges.begin(), y = expected.begin();
       x != all_edges.end() && y != expected.end(); ++x, ++y) {
    EXPECT_DOUBLE_EQ(x->start.GetLongitudeAsDouble(),
                     y->start.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->start.GetLatitudeAsDouble(),
                     y->start.GetLatitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLongitudeAsDouble(),
                     y->end.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLatitudeAsDouble(),
                     y->end.GetLatitudeAsDouble());
  }
}

UTEST_F(EdgeToSegmentsTest, EdgeToSegmentsFactorOne) {
  using ::models::Point;

  models::GraphSurgePoints gsp{GetGraph()};

  std::vector<models::NearestEdge> expected = {
      {/*id=*/0,
       {37.6253330 * geometry::lon, 55.7497300 * geometry::lat},
       {37.625393444444434 * geometry::lon, 55.749735666666666 * geometry::lat},
       0,
       {}},
      {/*id=*/1,
       {37.625393444444434 * geometry::lon, 55.749735666666666 * geometry::lat},
       {37.626279888888874 * geometry::lon, 55.74979033333333 * geometry::lat},
       0,
       {}},
      {/*id=*/2,
       {37.626279888888874 * geometry::lon, 55.74979033333333 * geometry::lat},
       {37.627109333333323 * geometry::lon, 55.749817 * geometry::lat},
       0,
       {}},
      {/*id=*/3,
       {37.627109333333323 * geometry::lon, 55.749817 * geometry::lat},
       {37.627689777777761 * geometry::lon, 55.74981866666667 * geometry::lat},
       0,
       {}},
      {/*id=*/4,
       {37.627689777777761 * geometry::lon, 55.74981866666667 * geometry::lat},
       {37.628052222222209 * geometry::lon, 55.749808333333334 * geometry::lat},
       0,
       {}},
      {/*id=*/5,
       {37.628052222222209 * geometry::lon, 55.749808333333334 * geometry::lat},
       {37.628539666666647 * geometry::lon, 55.749780999999999 * geometry::lat},
       0,
       {}},
      {/*id=*/6,
       {37.628539666666647 * geometry::lon, 55.749780999999999 * geometry::lat},
       {37.630660111111098 * geometry::lon, 55.74963566666667 * geometry::lat},
       0,
       {}},
      {/*id=*/7,
       {37.630660111111098 * geometry::lon, 55.74963566666667 * geometry::lat},
       {37.632186555555535 * geometry::lon, 55.749522333333331 * geometry::lat},
       0,
       {}},
      {/*id=*/8,
       {37.632186555555535 * geometry::lon, 55.749522333333331 * geometry::lat},
       {37.6324470 * geometry::lon, 55.7494930 * geometry::lat},
       0,
       {}}};
  int road_class = 0;
  std::vector<models::NearestFixedPoint> nearest_points = {};
  std::vector<models::NearestEdge> all_edges = {};
  models::EdgeToSegments(all_edges, 203823, 1, *GetGraph(), road_class,
                         nearest_points);

  ASSERT_EQ(all_edges.size(), 9);

  for (auto x = all_edges.begin(), y = expected.begin();
       x != all_edges.end() && y != expected.end(); ++x, ++y) {
    EXPECT_DOUBLE_EQ(x->start.GetLongitudeAsDouble(),
                     y->start.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->start.GetLatitudeAsDouble(),
                     y->start.GetLatitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLongitudeAsDouble(),
                     y->end.GetLongitudeAsDouble());
    EXPECT_DOUBLE_EQ(x->end.GetLatitudeAsDouble(),
                     y->end.GetLatitudeAsDouble());
  }
}

}  // namespace tests
