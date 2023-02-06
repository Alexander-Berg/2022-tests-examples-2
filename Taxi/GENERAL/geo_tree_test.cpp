#include <userver/utest/utest.hpp>

#include <geo-search/models/geo_tree.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/rand.hpp>

namespace geo_tree_test {

struct Point {
  double lon;
  double lat;
};

using Points = geo_search::models::geo_tree::Tree<Point>;

geometry::Position GetPosition(const Point& point) {
  return {point.lon * geometry::units::lon, point.lat * geometry::units::lat};
}

std::vector<Point> GetNormalPoints(const geometry::BoundingBox& bbox) {
  std::vector<Point> points;
  for (double lon = -179; lon < 0; ++lon) {
    for (double lat = -89; lat < 0; ++lat) {
      points.push_back({lon, lat});
    }
  }
  Points tree(points);
  geo_search::models::geo_tree::TreeView<Point> tree_view(tree, bbox);
  return std::vector<Point>(tree_view.begin(), tree_view.end());
}

TEST(TestGeoTree, SimpleTests) {
  geometry::BoundingBox bbox(GetPosition({-30.5, -25.5}),
                             GetPosition({-10.5, -15.5}));
  const auto in_bbox = GetNormalPoints(bbox);
  const size_t length = in_bbox.size();
  EXPECT_EQ(length, 200);
  for (const auto& position : in_bbox) {
    EXPECT_TRUE(bbox.Contains(GetPosition(position)));
  }
}

TEST(TestGeoTree, BboxOver180Tests) {
  geometry::BoundingBox bbox(GetPosition({30.5, -25.5}),
                             GetPosition({10.5, -15.5}));
  const auto in_bbox = GetNormalPoints(bbox);
  const size_t length = in_bbox.size();
  EXPECT_NE(length, 0);
  for (const auto& position : in_bbox) {
    EXPECT_TRUE(bbox.Contains(GetPosition(position)));
  }
}

TEST(TestGeoTree, EmptyTests) {
  geometry::BoundingBox bbox(GetPosition({10.5, -15.5}),
                             GetPosition({30.5, -25.5}));
  const auto in_bbox = GetNormalPoints(bbox);
  const size_t length = in_bbox.size();
  EXPECT_EQ(length, 0);
}

TEST(TestGeoTree, HugeData) {
  std::vector<Point> points;
  for (double lon = -0.0001; lon < 0.0001; lon += 0.0000001) {
    for (double lat = -0.0001; lat < 0.0001; lat += 0.0000001) {
      points.push_back({lon, lat});
    }
  }
  EXPECT_EQ(points.size(), 4000000);
  auto time_now = utils::datetime::Now();
  Points tree(std::move(points));
  auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                      utils::datetime::Now() - time_now)
                      .count();
  EXPECT_LT(duration, 10000);
  geometry::BoundingBox bbox(GetPosition({-1.0, -1.0}),
                             GetPosition({0.0, 0.0}));
  EXPECT_TRUE(bbox.Contains(GetPosition(Point{-0.0001, -0.0001})));
  geo_search::models::geo_tree::TreeView<Point> tree_view(tree, bbox);
  std::vector<Point> answer;
  answer.reserve(points.size() / 4);
  auto point_it = tree_view.begin();
  time_now = utils::datetime::Now();
  for (; !point_it.Terminated(); ++point_it) {
    answer.push_back(*point_it);
  }
  duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                 utils::datetime::Now() - time_now)
                 .count();
  EXPECT_EQ(answer.size(), 1000000);
  // it took longer with sanitizers. wout sanitizers it is very fast
  EXPECT_LT(duration, 100);
  time_now = utils::datetime::Now();
  answer = tree.Get(bbox);
  duration = std::chrono::duration_cast<std::chrono::milliseconds>(
                 utils::datetime::Now() - time_now)
                 .count();
  EXPECT_EQ(answer.size(), 1000000);
  // it took 11 ms with sanitizers. wout sanitizers it is very fast
  EXPECT_LT(duration, 30);
}

Point GeneratePoint(const geometry::BoundingBox& bbox) {
  int precision = 1000000;
  double lon = (utils::Rand() % precision) / static_cast<double>(precision);
  double lat = (utils::Rand() % precision) / static_cast<double>(precision);
  auto delta = bbox.north_east - bbox.south_west;
  delta.longitude_delta *= lon;
  delta.latitude_delta *= lat;
  auto position = bbox.south_west + delta;
  return {position.GetLongitudeAsDouble(), position.GetLatitudeAsDouble()};
}

TEST(TestGeoTree, RandomTests) {
  int test_iteartions = 100;
  geometry::BoundingBox gen_bbox(GetPosition({39.1, 51.5}),
                                 GetPosition({39.4, 51.8}));
  geometry::BoundingBox testing_bbox(GetPosition({39.2, 51.6}),
                                     GetPosition({39.3, 51.7}));
  while (--test_iteartions) {
    int points_num = 1000;
    std::vector<Point> points;
    while (--points_num) {
      points.push_back(GeneratePoint(gen_bbox));
    }
    Points tree(std::move(points));
    geo_search::models::geo_tree::TreeView<Point> tree_view(tree, testing_bbox);
    std::vector<Point> answer_1(tree_view.begin(), tree_view.end());
    auto answer_2 = tree.Get(testing_bbox);
    EXPECT_EQ(answer_1.size(), answer_2.size());
    for (const auto& answer_1_el : answer_1) {
      auto answer_2_it = std::find_if(answer_2.begin(), answer_2.end(),
                                      [&answer_1_el](const auto& answer_2_el) {
                                        return geometry::AreClosePositions(
                                            GetPosition(answer_1_el),
                                            GetPosition(answer_2_el));
                                      });
      EXPECT_NE(answer_2_it, answer_2.end());
    }
  }
}

}  // namespace geo_tree_test
