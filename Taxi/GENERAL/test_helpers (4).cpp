#include "test_helpers.hpp"

namespace united_dispatch::test_helpers {

std::shared_ptr<united_dispatch::models::Segment> GenerateSegment(
    GenerateSegmentKwargs kwargs) {
  auto segment = std::make_shared<united_dispatch::models::Segment>();
  segment->id = kwargs.segment_id;
  segment->corp_client_id = kwargs.corp_id;
  segment->zone_id = kwargs.zone_id;
  segment->created_ts = kwargs.created_ts;
  segment->allow_batch = kwargs.allow_batch;
  segment->taxi_classes = {"courier"};
  segment->claim_origin = kwargs.claim_origin;
  segment->claim_features_set = kwargs.claim_features_set;

  std::vector<std::pair<handlers::SegmentPointType, int>> points = {
      {handlers::SegmentPointType::kPickup, 1},
      {handlers::SegmentPointType::kDropoff, 2},
      {handlers::SegmentPointType::kReturn, 3},
  };
  if (!kwargs.is_valid) {
    std::swap(points[0], points[2]);
  }

  if (kwargs.multipoint) {
    std::vector<std::pair<handlers::SegmentPointType, int>> temp(points);
    for (auto& point : temp) {
      point.second = point.second + temp.size();
      points.push_back(std::move(point));
    }
  }

  for (const auto& [point_type, visit_order] : points) {
    handlers::SegmentPoint point;
    point.id = "point-" + std::to_string(visit_order) + kwargs.segment_id;
    point.coordinates = {visit_order * 1.0, visit_order * 2.0};
    point.segment_id = kwargs.segment_id;
    point.type = point_type;
    point.visit_order = visit_order;
    point.time_intervals = kwargs.intervals;
    segment->points.push_back(std::move(point));
  }
  segment->points[0].due = kwargs.due;

  return segment;
}

std::vector<Waypoint> GetPath(std::shared_ptr<Segment> segment) {
  std::vector<Waypoint> path;
  for (const auto& segment_point : segment->points) {
    path.emplace_back(segment_point, segment);
  }
  return path;
}

std::vector<Waypoint> GetPath(
    const std::vector<std::shared_ptr<Segment>>& segments) {
  std::vector<Waypoint> path;
  for (const auto& segment : segments) {
    for (const auto& segment_point : segment->points) {
      path.emplace_back(segment_point, segment);
    }
  }
  return path;
}

Route GetRouteWithSegments(const std::string& generator_name,
                           const std::vector<std::string>& segments_ids,
                           bool is_valid) {
  std::vector<Waypoint> path;

  for (const auto& segment_id : segments_ids) {
    GenerateSegmentKwargs segment_kwargs;
    segment_kwargs.segment_id = segment_id;
    auto segment_ptr = GenerateSegment(segment_kwargs);

    std::vector<Waypoint> wps = GetPath(segment_ptr);
    // reserve на stackoverflow бенчмарком отвергнут
    std::move(wps.begin(), wps.end(), std::back_inserter(path));
  }

  return Route(generator_name, path, is_valid);
}

Route GetRouteFromSegment(std::shared_ptr<Segment> segment_ptr,
                          const std::string& generator_name, bool is_valid) {
  std::vector<Waypoint> path = GetPath(segment_ptr);
  return Route(generator_name, path, is_valid);
}

Route GetRouteFromSegments(std::vector<std::shared_ptr<Segment>> segments,
                           const std::string& generator_name, bool is_valid) {
  std::vector<Waypoint> path = GetPath(segments);
  return Route(generator_name, path, is_valid);
}

}  // namespace united_dispatch::test_helpers
