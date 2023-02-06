#include <unordered_set>

#include <geo-index/geo-index.hpp>
#include <geometry/boost_geometry.hpp>
#include <geometry/position.hpp>

#include <gtest/gtest.h>

namespace {

using Point = geometry::Position;
using RegularPolygon = boost::geometry::model::polygon<Point>;

template <typename Polygon = RegularPolygon>
struct GeoArea {
  using polygon_t = Polygon;

  std::string name;
  polygon_t geometry;

  GeoArea() = default;
  GeoArea(std::string name, polygon_t polygon)
      : name(std::move(name)), geometry(std::move(polygon)) {}
};

template <typename Polygon>
struct PolygonAccessor {
  const Polygon& operator()(const GeoArea<Polygon>& area) const {
    return area.geometry;
  }
};

template <typename Polygon = RegularPolygon>
using Index =
    geo_index::Index<GeoArea<Polygon>, Polygon, PolygonAccessor<Polygon>>;

Point GetPoint(std::pair<double, double> lon_lat) {
  return geometry::Position{lon_lat.first * geometry::units::lon,
                            lon_lat.second * geometry::units::lat};
}

RegularPolygon MakePolygon(
    std::vector<std::pair<double, double>> outer_points,
    std::vector<std::pair<double, double>> inner_points = {}) {
  RegularPolygon ret;

  for (auto lon_lat : outer_points) {
    boost::geometry::append(ret.outer(), GetPoint(lon_lat));
  }

  if (!inner_points.empty()) {
    ret.inners().resize(1);
    for (auto lon_lat : inner_points) {
      boost::geometry::append(ret.inners().front(), GetPoint(lon_lat));
    }
  }

  return ret;
}

std::unordered_set<std::string> GetAreasNames(
    const std::vector<std::reference_wrapper<const ::GeoArea<>>>&
        query_result) {
  std::unordered_set<std::string> areas_names_set;
  for (const auto& geoarea : query_result)
    areas_names_set.insert(geoarea.get().name);
  return areas_names_set;
}

}  // namespace

TEST(GeoIndexTest, TestSquaredRegularPolygons) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back(
      "id1",
      MakePolygon({{-10, -10}, {-10, 10}, {10, 10}, {10, -10}, {-10, -10}}));
  geoareas.emplace_back(
      "id2", MakePolygon({{10, 10}, {10, 12}, {12, 12}, {12, 10}, {10, 10}}));
  geoareas.emplace_back(
      "id3", MakePolygon({{9, 9}, {9, 13}, {13, 13}, {13, 9}, {9, 9}}));
  geoareas.emplace_back(
      "id4", MakePolygon({{-1, -1}, {-1, 1}, {1, 1}, {1, -1}, {-1, -1}}));
  geoareas.emplace_back(
      "id5", MakePolygon({{-2, -2}, {-2, 2}, {0, 2}, {0, -2}, {-2, -2}}));
  geoareas.emplace_back(
      "id6", MakePolygon({{-1, -3}, {-1, 3}, {3, 3}, {3, -3}, {-1, -3}}));
  geoareas.emplace_back(
      "id7", MakePolygon({{-2, -2}, {-2, 2}, {2, 2}, {2, -2}, {-2, -2}}));
  geoareas.emplace_back(
      "id8", MakePolygon({{-3, -3}, {-3, 3}, {1, 3}, {1, -3}, {-3, -3}}));
  geoareas.emplace_back(
      "id9", MakePolygon({{-2, -4}, {-2, 4}, {4, 4}, {4, -4}, {-2, -4}}));

  Index<> index(geoareas);

  auto query_result = index.Find(GetPoint({1, 0}));
  EXPECT_EQ(6, query_result.size());

  const auto areas_names_set = GetAreasNames(query_result);
  EXPECT_EQ(areas_names_set, (std::unordered_set<std::string>{
                                 "id1", "id4", "id6", "id7", "id8", "id9"}));

  auto any_area = index.FindAny(GetPoint({1, 0}));
  EXPECT_TRUE(any_area);
  EXPECT_TRUE(areas_names_set.count(any_area->name) > 0);
}

TEST(GeoIndexTest, TestNonSquaredRegularPolygons) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back("id1", MakePolygon({{-10, -10},
                                            {-7, -8},
                                            {-15, 3},
                                            {-10, 10},
                                            {1, 5},
                                            {10, 12},
                                            {10, -10},
                                            {-10, -10}}));
  geoareas.emplace_back("id2", MakePolygon({{10, 10},
                                            {9, 11},
                                            {10, 12},
                                            {12, 12},
                                            {15, 13},
                                            {12, 10},
                                            {10, 10}}));
  geoareas.emplace_back(
      "id3", MakePolygon({{9, 7}, {17, 13}, {8, 14}, {6, 10}, {9, 7}}));
  geoareas.emplace_back(
      "id4", MakePolygon({{-1, -2}, {-2, 3}, {1, 1}, {1, -1}, {-1, -2}}));

  Index<> index(geoareas);

  auto query_result = index.Find(GetPoint({0, 0}));
  EXPECT_EQ(2, query_result.size());

  const auto areas_names_set = GetAreasNames(query_result);
  EXPECT_EQ(areas_names_set, (std::unordered_set<std::string>{"id1", "id4"}));

  auto any_area = index.FindAny(GetPoint({0, 0}));
  EXPECT_TRUE(any_area);
  EXPECT_TRUE(areas_names_set.count(any_area->name) > 0);

  query_result = index.Find(GetPoint({16, 13}));
  EXPECT_EQ(1, query_result.size());
  EXPECT_EQ(&query_result.front().get(), &geoareas[2]);
}

TEST(GeoIndexTest, TestNonConvexPolygon) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back("id1", MakePolygon({{-10, -10},
                                            {-15, 0},
                                            {-10, 10},
                                            {0, 15},
                                            {10, 10},
                                            {12, 5},
                                            {10, 7},
                                            {0, 10},
                                            {-7, 0},
                                            {0, -10},
                                            {10, -7},
                                            {12, -5},
                                            {10, -10},
                                            {0, -15},
                                            {-10, -10}}));
  Index<> index(geoareas);

  EXPECT_TRUE(index.Find(GetPoint({0, 0})).empty());

  auto query_result = index.Find(GetPoint({-7, 5}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(&query_result.front().get(), geoareas.data());
}

TEST(GeoIndexTest, TestHoledPolygon) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back(
      "id1",
      MakePolygon({{-10, -10}, {-10, 10}, {10, 10}, {10, -10}, {-10, -10}},
                  {{-5, -5}, {-5, 5}, {5, 5}, {5, -5}, {-5, -5}}));

  Index<> index(geoareas);

  auto query_result = index.Find(GetPoint({0, 0}));
  EXPECT_TRUE(query_result.empty());

  query_result = index.Find(GetPoint({7, 8}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(&query_result.front().get(), geoareas.data());

  query_result = index.Find(GetPoint({20, 20}));
  EXPECT_TRUE(query_result.empty());
}

TEST(GeoIndexTest, TestBorders) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back(
      "id1", MakePolygon({{-1, -1}, {-1, 1}, {0, 1}, {0, -1}, {-1, -1}}));

  Index<> index(geoareas);
  auto query_result = index.Find(GetPoint({0, 0}));
  EXPECT_EQ(query_result.size(), 1u);

  geoareas.emplace_back(
      "id2", MakePolygon({{1, -1}, {1, 1}, {0, 1}, {0, -1}, {1, -1}}));
  index.Rebuild(geoareas);
  query_result = index.Find(GetPoint({0, 0}));
  EXPECT_EQ(query_result.size(), 2u);
}

TEST(GeoIndexTest, TestIntersectCandidates) {
  std::vector<GeoArea<>> geoareas;
  geoareas.emplace_back(
      "id1", MakePolygon({{-10, 0}, {0, 10}, {10, 0}, {0, -10}, {-10, 0}}));
  geoareas.emplace_back(
      "id2", MakePolygon({{-1, 0}, {0, 1}, {1, 0}, {0, -1}, {-1, -1}}));
  Index<> index(geoareas);

  std::unordered_set<std::string> expected_set{"id1", "id2"};
  // no intersect
  auto query_result = index.IntersectCandidates(
      MakePolygon({{20, 20}, {20, 21}, {21, 21}, {21, 20}, {20, 20}}));
  EXPECT_EQ(query_result.size(), 0u);
  // intersect id1
  query_result = index.IntersectCandidates(
      MakePolygon({{5, 5}, {5, 15}, {15, 15}, {15, 5}, {5, 5}}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(query_result[0].get().name, "id1");
  // inside id1 and contains id2
  query_result = index.IntersectCandidates(
      MakePolygon({{-5, -5}, {-5, 5}, {5, 5}, {5, -5}, {-5, -5}}));
  EXPECT_EQ(query_result.size(), 2u);
  EXPECT_EQ(GetAreasNames(query_result), expected_set);
  // touch vertex with id1
  query_result = index.IntersectCandidates(
      MakePolygon({{10, 10}, {10, 11}, {11, 11}, {11, 10}, {10, 10}}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(query_result[0].get().name, "id1");
  // touch side with id1
  query_result = index.IntersectCandidates(
      MakePolygon({{9, 10}, {9, 11}, {11, 11}, {11, 10}, {9, 10}}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(query_result[0].get().name, "id1");
  // equal to id1
  query_result = index.IntersectCandidates(
      MakePolygon({{-10, -10}, {-10, 10}, {10, 10}, {10, -10}, {-10, -10}}));
  EXPECT_EQ(query_result.size(), 2u);
  EXPECT_EQ(GetAreasNames(query_result), expected_set);
  // id2 is inside polygons hole
  query_result = index.IntersectCandidates(
      MakePolygon({{-5, -5}, {-5, 5}, {5, 5}, {5, -5}, {-5, -5}},
                  {{-3, -3}, {-3, 3}, {3, 3}, {3, -3}, {-3, -3}}));
  EXPECT_EQ(query_result.size(), 1u);
  EXPECT_EQ(query_result[0].get().name, "id1");
  // id2 interesects polygon hole
  query_result = index.IntersectCandidates(
      MakePolygon({{-5, -5}, {-5, 5}, {5, 5}, {5, -5}, {-5, -5}},
                  {{-1.5, 0}, {0, 1.5}, {1.5, 0}, {0, -1.5}, {-1.5, -0}}));
  EXPECT_EQ(query_result.size(), 2u);
  EXPECT_EQ(GetAreasNames(query_result), expected_set);
}
