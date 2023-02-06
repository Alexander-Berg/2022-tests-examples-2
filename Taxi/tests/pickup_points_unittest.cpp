#include <gtest/gtest.h>
#include <fstream>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include "config/pickup_points_config.hpp"
#include "models/pickup_points/point.hpp"
#include "models/pickup_points/recommender.hpp"
#include "models/pickup_points/v2/ranker.hpp"

namespace {

using namespace config::pickup_points;
using namespace models::pickup_points;
using namespace utils::helpers;
using namespace utils::matrixnet;

class RankerMock : public v2::Ranker {
 public:
  RankerMock(const std::shared_ptr<MatrixnetWrapper>& model = nullptr)
      : Ranker(model) {}

  std::vector<float> ExtractFeaturesMock(
      const MLPoint& candidate,
      const utils::geometry::Point& pin_geopoint) const {
    return ExtractFeatures(candidate, pin_geopoint);
  }
};

class RecommenderMock : public Recommender {
 public:
  RecommenderMock(const PostprocessingConfig& config) : Recommender(config) {}

  Response ApplyMock(const std::vector<MLPoint>& points) const {
    return Apply(points, {}, {});
  }
};

MLPoint ParseMLPoint(const Json::Value& doc) {
  MLPoint point;
  FetchMemberDef(point.id, point.id, doc, "id");
  FetchMemberDef(point.geopoint, point.geopoint, doc, "geopoint");
  FetchMemberDef(point.projection, point.projection, doc, "projection");
  FetchMemberDef(point.score, point.score, doc, "score");
  FetchMemberDef(point.edge_id, point.edge_id, doc, "edge_id");
  FetchMemberDef(point.edge_geopoints, point.edge_geopoints, doc,
                 "edge_geopoints");
  FetchMemberDef(point.weights, point.weights, doc, "weights");
  FetchMemberDef(point.static_features, point.static_features, doc,
                 "static_features");
  Statistics stats;
  FetchMemberDef(stats.earth_distance, stats.earth_distance, doc,
                 "earth_distance");
  FetchMemberOptional(stats.route_distance, doc, "route_distance");
  FetchMemberOptional(stats.route_time, doc, "route_time");
  point.SetStatistics(stats);
  return point;
}

MLPoint GetMLPoint(const std::string& id = std::string(),
                   const std::string& edge_id = std::string(),
                   const utils::geometry::Point geopoint = {0, 0},
                   double earth_distance = 0) {
  MLPoint point;
  point.id = id;
  point.edge_id = edge_id;
  point.geopoint = geopoint;
  point.score = 1;
  Statistics stats;
  stats.earth_distance = earth_distance;
  stats.relevance = 1;
  point.SetStatistics(stats);
  return point;
}

PostprocessingConfig GetConfig(size_t max_points_count, size_t max_edge_count,
                               size_t max_line_count, double stick_radius) {
  PostprocessingConfig config;
  config.max_points_count = max_points_count;
  config.max_edge_count = max_edge_count;
  config.max_line_count = max_line_count;
  config.stick_radius = stick_radius;
  config.intersection_distance = 10;
  config.max_line_segment_distance = 100;
  config.max_line_projection_distance = 10;
  return config;
}

TEST(PickupPoints, ExtractFeatures) {
  std::ifstream in(std::string(SOURCE_DIR) +
                   "/tests/static/pickup_points_sample.json");
  Json::Value doc = utils::helpers::ParseJson(in);

  std::vector<MLPoint> candidates;
  for (const auto& point_doc : FetchArray(doc, "candidates")) {
    candidates.emplace_back(ParseMLPoint(point_doc));
  }
  utils::geometry::Point pin_position;
  FetchMember(pin_position, doc, "pin_position");
  std::vector<std::vector<float>> expected_features;
  for (const auto& row_doc : FetchArray(doc, "features")) {
    std::vector<float> row;
    for (auto it = row_doc.begin(); it != row_doc.end(); ++it) {
      row.push_back((*it).asFloat());
    }
    expected_features.emplace_back(std::move(row));
  }
  ASSERT_EQ(candidates.size(), expected_features.size());
  const auto ranker = RankerMock();
  for (size_t i = 0; i < candidates.size(); ++i) {
    const auto features =
        ranker.ExtractFeaturesMock(candidates[i], pin_position);
    ASSERT_EQ(features.size(), expected_features[i].size());
    for (size_t j = 0; j < features.size(); ++j) {
      ASSERT_FLOAT_EQ(features[j], expected_features[i][j]);
    }
  }
}

TEST(PickupPoints, Recommend) {
  const utils::geometry::Point pin_geopoint = {37.588750, 55.734555};
  std::vector<MLPoint> points;
  points.emplace_back(GetMLPoint("0", "a", {37.58925373, 55.73431540}, 20));
  points.emplace_back(GetMLPoint("1", "a", {37.58883251, 55.73458719}, 0));
  points.emplace_back(GetMLPoint("2", "b", {37.58776091, 55.73324854}, 10));
  points.emplace_back(GetMLPoint("3", "c", {37.58821078, 55.73297037}, 20));
  points.emplace_back(GetMLPoint("4", "c", {37.58697054, 55.73377891}, 20));
  {
    const auto recommender = RecommenderMock(GetConfig(4, 1, 2, 5));
    const auto response = recommender.ApplyMock(points);
    ASSERT_EQ(response.points.size(), 3u);
    ASSERT_EQ(response.points[0].id, "0");
    ASSERT_EQ(response.points[1].id, "2");
    ASSERT_EQ(response.points[2].id, "3");
    ASSERT_FALSE(response.sticky_point);
  }
  {
    const auto recommender = RecommenderMock(GetConfig(4, 3, 3, 15));
    const auto response = recommender.ApplyMock(points);
    ASSERT_EQ(response.points.size(), 4u);
    ASSERT_EQ(response.points[0].id, "0");
    ASSERT_EQ(response.points[1].id, "1");
    ASSERT_EQ(response.points[2].id, "2");
    ASSERT_EQ(response.points[3].id, "3");
    ASSERT_TRUE(response.sticky_point);
    ASSERT_EQ(response.sticky_point->id, "1");
  }
}

}  // namespace
