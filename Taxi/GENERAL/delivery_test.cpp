#include <vector>

#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <client-geoareas-base/models/geoarea.hpp>
#include <geometry/position.hpp>

#include <dispatch/input/environment.hpp>
#include <dispatch/proposition-builders/delivery/route.hpp>
#include <experiments3/united_dispatch_generators_settings.hpp>
#include <models/united_dispatch/geoareas.hpp>
#include <models/united_dispatch/segment.hpp>
#include <utils/delivery.hpp>

using united_dispatch::delivery::FastRemoveElementsFromVector;
using namespace united_dispatch::waybill::delivery;
using namespace united_dispatch::models;
using namespace handlers;

namespace {

SegmentPtr GenerateSegment() {
  auto segment = std::make_shared<Segment>();
  segment->id = "segment_id_1";
  segment->corp_client_id = "corp_id_1";
  segment->zone_id = "moscow";
  segment->taxi_classes = {"courier"};

  std::vector<std::pair<handlers::SegmentPointType, int>> points = {
      {handlers::SegmentPointType::kPickup, 1},
      {handlers::SegmentPointType::kDropoff, 2},
      {handlers::SegmentPointType::kReturn, 3},
  };

  for (const auto& [point_type, visit_order] : points) {
    handlers::SegmentPoint point;
    point.id = "point-" + std::to_string(visit_order) + segment->id;
    point.coordinates = {visit_order * 1.0, visit_order * 2.0};
    point.segment_id = segment->id;
    point.type = point_type;
    point.visit_order = visit_order;
    point.time_intervals = {};
    segment->points.push_back(std::move(point));
  }

  return segment;
}

GeoareaPtr GenerateBigGeoarea() {
  std::vector<std::vector<geometry::Position>> polygon;
  std::vector<geometry::Position> points = {
      {0.0 * ::geometry::units::lon, 0.0 * ::geometry::units::lat},
      {0.0 * ::geometry::units::lon, 200.0 * ::geometry::units::lat},
      {200.0 * ::geometry::units::lon, 200.0 * ::geometry::units::lat},
      {200.0 * ::geometry::units::lon, 0.0 * ::geometry::units::lat},
      {0.0 * ::geometry::units::lon, 0.0 * ::geometry::units::lat}};
  polygon.push_back(std::move(points));

  Geoarea geoarea{"geoarea_id_1",
                  "ud-polygons-type",
                  "geoarea_name_1",
                  utils::datetime::Now(),
                  polygon,
                  {},
                  {},
                  0.0};

  return std::make_shared<Geoarea>(geoarea);
}

}  // namespace

UTEST(DeliveryUtils, FastRemoveElementsFromVector) {
  std::vector<int> v1;
  std::vector<int> v2;
  std::vector<std::vector<size_t>> idxs_to_removes = {
      {0},
      {9},
      {0, 9},
      {1},
      {8},
      {1, 8},
      {0, 1, 2},
      {7, 8, 9},
      {0, 2, 3},
      {6, 7, 9},
      {0, 1, 8, 9},
      {0, 1, 5, 8, 9},
      {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
      {1, 2, 3, 4, 5, 6, 7, 8, 9},
      {0, 1, 2, 3, 4, 5, 6, 7, 8},
      {0, 1, 2, 3, 5, 6, 7, 8, 9},
  };

  for (const auto& idxs_to_remove : idxs_to_removes) {
    std::vector<int> v1 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    std::vector<int> v2 = v1;
    for (auto it = v2.begin(); it != v2.end();) {
      if (std::find(idxs_to_remove.begin(), idxs_to_remove.end(), *it) !=
          idxs_to_remove.end()) {
        v2.erase(it);
      } else {
        ++it;
      }
    }
    FastRemoveElementsFromVector(v1, idxs_to_remove);
    ASSERT_EQ(v1, v2);
  }
}

UTEST(DeliveryUtils, TestGeoareasMatching) {
  auto segment = GenerateSegment();
  united_dispatch::waybill::Environment environment;
  SegmentGeoareasMap segment_to_geoareas;

  auto geoarea = GenerateBigGeoarea();
  segment_to_geoareas[segment->id] = {geoarea};
  environment.segment_to_geoareas =
      std::make_shared<SegmentGeoareasMap>(segment_to_geoareas);

  experiments3::united_dispatch_delivery_generators_settings::Common
      common_settings{};
  common_settings.min_performer_eta =
      dynamic_config::ValueDict<int>{{dynamic_config::kValueDictDefaultName, 0},
                                     {"moscow.corp_id_1", 5},
                                     {"geoarea_name_1.corp_id_1", 10}};

  const auto setting = united_dispatch::delivery::ExtractSettings(
      common_settings.min_performer_eta, segment, environment);
  ASSERT_EQ(setting, 10);
}
