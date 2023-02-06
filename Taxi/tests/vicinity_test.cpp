#include <userver/utest/utest.hpp>

#include <string>
#include <utility>
#include <vector>

#include <geometry/position.hpp>

#include <driver-scoring-preprocessing/logic/vicinity/explorer.hpp>
#include <driver-scoring-preprocessing/models/vicinity/common.hpp>

namespace driver_scoring_preprocessing::tests {

namespace {

models::vicinity::Type ToType(size_t idx) {
  return static_cast<models::vicinity::Type>(idx);
}

auto GetGeopoint(std::string_view name) {
  ::geometry::Position pos;
  if (name == "center") {
    return ::geometry::Position::FromGeojsonArray({37.63, 55.75});
  } else if (name == "city") {
    return ::geometry::Position::FromGeojsonArray({37.53, 55.76});
  } else if (name == "north") {
    return ::geometry::Position::FromGeojsonArray({37.7, 55.87});
  }
  return ::geometry::Position{};
}

struct TestCase {
  int max_depth;
  double max_radius;
  size_t vertex_count;
  std::vector<std::pair<size_t, size_t>> edges;
  std::vector<size_t> colors;
  std::vector<::geometry::Position> positions;
  std::vector<bool> repositions;
  std::vector<models::vicinity::Result> expected;
};

class TestRunner : public logic::vicinity::ExplorerBuilder {
 public:
  TestRunner(TestCase test)
      : logic::vicinity::ExplorerBuilder(), ids_(), test_(std::move(test)) {
    ids_.resize(test_.vertex_count);
    for (size_t idx = 0; idx < test_.vertex_count; ++idx) {
      ids_[idx] = std::to_string(idx);
    }
    for (const auto& [source, target] : test_.edges) {
      AddVertex({ids_[source], test_.positions[source],
                 ToType(test_.colors[source]), std::nullopt});
      AddVertex({ids_[target], test_.positions[target],
                 ToType(test_.colors[target]), test_.repositions[target]});
      AddEdge(ids_[source], ids_[target]);
    }
  }

  void RunTest() {
    auto explorer = Build();
    for (size_t idx = 0; idx < test_.expected.size(); ++idx) {
      ASSERT_EQ(test_.expected[idx],
                explorer.CountNearbyOrdersAndCandidates(
                    test_.max_depth, test_.max_radius, ids_[idx]));
    }
  }

 private:
  std::vector<std::string> ids_;
  TestCase test_;
};

}  // namespace

TEST(DriverScoringPreprocessing, DistanceCheck) {
  auto test_two_with_radius = [](double radius, int exp) {
    TestCase test;
    test.max_depth = 1;
    test.max_radius = radius;
    test.vertex_count = 2;
    test.positions = {GetGeopoint("city"), GetGeopoint("center")};
    test.colors = {0, 1};
    test.repositions = {0, 0};
    test.edges = {{0, 1}};
    test.expected = {{test.max_depth, test.max_radius, 1, exp, 0},
                     {test.max_depth, test.max_radius, exp, 1, 0}};
    TestRunner builder(std::move(test));
    builder.RunTest();
  };
  // real distance is 6355
  test_two_with_radius(6356, 1);
  test_two_with_radius(6354, 0);
}

TEST(DriverScoringPreprocessing, DepthCheck) {
  TestCase test;
  test.vertex_count = 6;
  test.max_depth = 2;
  test.max_radius = 1;
  test.positions = std::vector(test.vertex_count, GetGeopoint("city"));
  test.colors = {0, 0, 0, 1, 1, 1};
  test.repositions = {0, 0, 0, 1, 0, 1};
  test.edges = {{0, 3}, {0, 4}, {1, 3}, {1, 4}, {1, 5}, {2, 5}};
  test.expected = {{test.max_depth, test.max_radius, 2, 2, 1},
                   {test.max_depth, test.max_radius, 3, 3, 2},
                   {test.max_depth, test.max_radius, 2, 1, 1},
                   {test.max_depth, test.max_radius, 2, 3, 2},
                   {test.max_depth, test.max_radius, 2, 3, 2},
                   {test.max_depth, test.max_radius, 2, 3, 2}};
  TestRunner builder(std::move(test));
  builder.RunTest();
}

}  // namespace driver_scoring_preprocessing::tests
