#include <random>
#include <string>
#include <vector>

#include <gtest/gtest.h>
#include <defs/definitions/cargo_dispatch.hpp>
#include <dispatch/proposition-builders/delivery/route.hpp>
#include <dispatch/proposition-builders/delivery/route_generator/route_finder.hpp>
#include <infraver-geometry/point_serialization.hpp>
#include <models/geometry/point.hpp>
#include <models/united_dispatch/segment.hpp>
#include <userver/utest/utest.hpp>
#include <utils/delivery.hpp>

using Waypoint = united_dispatch::waybill::delivery::Waypoint;
using united_dispatch::models::Segment;
using SegmentPtr = std::shared_ptr<united_dispatch::models::Segment>;
using ConstSegmentPtr = std::shared_ptr<const united_dispatch::models::Segment>;
using SegmentPoint = handlers::SegmentPoint;
using united_dispatch::waybill::delivery::route_generator::CanSwap;
using united_dispatch::waybill::delivery::route_generator::EdgesAnnealing;
using united_dispatch::waybill::delivery::route_generator::
    GetRouteDistanceDiffAfterSwap;
using united_dispatch::waybill::delivery::route_generator::GetSegmentPointsMap;
using united_dispatch::waybill::delivery::route_generator::
    GetSegmentThatMaximizesDistance;
using united_dispatch::waybill::delivery::route_generator::RouteFinderSettings;
using united_dispatch::waybill::delivery::route_generator::SegmentsPointsMap;

std::vector<std::shared_ptr<united_dispatch::models::Segment>> segments;
std::vector<handlers::SegmentPoint> segment_points;

RouteFinderSettings GetRouteFinderSettings() {
  RouteFinderSettings settings;
  settings.num_best_routes = 5;
  settings.edges_swap_annealing_it_num = 20;
  settings.segments_swap_annealing_it_mult = 5;
  settings.init_annealing_probability = 0.7;
  settings.extra_segments_handling_num = 1;
  settings.max_num_of_swap_edges_attempts = 10;
  return settings;
}

std::vector<Waypoint> GetPath(
    const std::vector<std::tuple<double, double, handlers::SegmentPointType>>&
        route_points) {
  segment_points.clear();
  segments.clear();
  int idx = 1;
  for (const auto& [pickup_point, dropoff_point, point_type] : route_points) {
    segment_points.emplace_back();
    segment_points.back().coordinates =
        ::models::geometry::Point(pickup_point, dropoff_point);
    segment_points.back().type = point_type;
    segment_points.back().id = std::to_string(idx);
    segment_points.back().visit_order = idx;
    segments.emplace_back(std::make_shared<united_dispatch::models::Segment>());
    segments.back()->id = std::to_string(idx % (route_points.size() / 3));
    ++idx;
  }
  std::vector<Waypoint> path;
  for (size_t i = 0; i < segment_points.size(); ++i) {
    path.emplace_back(segment_points[i],
                      segments[i % (route_points.size() / 3)]);
  }
  return path;
}

bool CheckPathValid(const std::vector<Waypoint>& path) {
  std::unordered_map<std::string_view, int> visit_order;
  for (size_t i = 0; i < path.size(); ++i) {
    if (visit_order[path[i].segment->id] >= path[i].point.get().visit_order) {
      return false;
    }
    visit_order[path[i].segment->id] = path[i].point.get().visit_order;
  }
  return true;
}

bool CheckPathsValid(const std::vector<std::vector<Waypoint>>& paths) {
  for (const auto& path : paths) {
    if (!CheckPathValid(path)) {
      return false;
    }
  }
  return true;
}

UTEST(RouteFinderTest, EdgesAnnealing) {
  const std::vector<std::tuple<double, double, handlers::SegmentPointType>>
      route_points = {
          {37.613896, 55.7482269, handlers::SegmentPointType::kPickup},
          {37.613896, 55.7482269, handlers::SegmentPointType::kPickup},
          {37.613896, 55.7482269, handlers::SegmentPointType::kPickup},
          {37.613896, 55.7482269, handlers::SegmentPointType::kPickup},

          {37.613896, 55.7482269, handlers::SegmentPointType::kDropoff},
          {37.623061, 55.7497660, handlers::SegmentPointType::kDropoff},
          {37.619998, 55.7522880, handlers::SegmentPointType::kDropoff},
          {37.616745, 55.7549538, handlers::SegmentPointType::kDropoff},

          {37.613896, 55.7482269, handlers::SegmentPointType::kReturn},
          {37.613896, 55.7482269, handlers::SegmentPointType::kReturn},
          {37.613896, 55.7482269, handlers::SegmentPointType::kReturn},
          {37.613896, 55.7482269, handlers::SegmentPointType::kReturn},
      };
  std::vector<Waypoint> path = GetPath(route_points);
  ASSERT_TRUE(CheckPathsValid({path}));
  auto long_path = path;
  int segments_num = route_points.size() / 3;
  ASSERT_EQ(path.size(), segments_num * 3);
  std::swap(long_path[5], long_path[6]);
  SegmentsPointsMap segments_points = GetSegmentPointsMap(long_path);
  auto annealed_paths =
      EdgesAnnealing(long_path, segments_points, GetRouteFinderSettings());
  ASSERT_TRUE(CheckPathsValid(annealed_paths));
  return;
  for (size_t i = 0; i < path.size(); ++i) {
    ASSERT_FLOAT_EQ(path[i].point.get().coordinates,
                    long_path[i].point.get().coordinates);
  }

  united_dispatch::delivery::FastRemoveElementsFromVector(path, {2, 6, 10});
  ASSERT_EQ(path.size(), (segments_num - 1) * 3);
  long_path = path;
  std::swap(long_path[4], long_path[5]);
  segments_points = GetSegmentPointsMap(long_path);
  annealed_paths =
      EdgesAnnealing(long_path, segments_points, GetRouteFinderSettings());
  ASSERT_TRUE(CheckPathsValid(annealed_paths));
  for (size_t i = 0; i < path.size(); ++i) {
    ASSERT_FLOAT_EQ(path[i].point.get().coordinates,
                    long_path[i].point.get().coordinates);
  }
}

UTEST(RouteFinderTest, EdgesAnnealingPathInvalid) {
  const std::vector<std::tuple<double, double, handlers::SegmentPointType>>
      route_points = {
          {37.444629, 55.719156, handlers::SegmentPointType::kPickup},  // 0
          {37.477965, 55.706939, handlers::SegmentPointType::kPickup},  // 1

          {37.436553, 55.717822, handlers::SegmentPointType::kDropoff},  // 2
          {37.535763, 55.732945, handlers::SegmentPointType::kDropoff},  // 3

          {37.444629, 55.719156, handlers::SegmentPointType::kReturn},  // 4
          {37.477965, 55.706939, handlers::SegmentPointType::kReturn},  // 5
      };
  std::vector<Waypoint> path = GetPath(route_points);
  ASSERT_TRUE(CheckPathsValid({path}));

  std::swap(path[0], path[2]);
  ASSERT_FALSE(CheckPathValid(path));
  std::swap(path[0], path[2]);

  std::swap(path[0], path[4]);
  ASSERT_FALSE(CheckPathValid(path));
  std::swap(path[0], path[4]);

  std::swap(path[2], path[4]);
  ASSERT_FALSE(CheckPathValid(path));
  std::swap(path[2], path[4]);
}

UTEST(RouteFinderTest, EdgesAnnealingPathValid) {
  const std::vector<std::tuple<double, double, handlers::SegmentPointType>>
      route_points = {
          {37.444629, 55.719156, handlers::SegmentPointType::kPickup},  // 0
          {37.477965, 55.706939, handlers::SegmentPointType::kPickup},  // 1

          {37.436553, 55.717822, handlers::SegmentPointType::kDropoff},  // 2
          {37.535763, 55.732945, handlers::SegmentPointType::kDropoff},  // 3

          {37.444629, 55.719156, handlers::SegmentPointType::kReturn},  // 4
          {37.477965, 55.706939, handlers::SegmentPointType::kReturn},  // 5
      };
  std::vector<Waypoint> path = GetPath(route_points);

  std::vector<std::vector<std::pair<int, int>>> points_to_swaps = {
      {},
      {
          {0, 1},
      },
      {
          {1, 2},
      },
      {
          {2, 3},
      },
      {
          {0, 1},
          {2, 3},
      },
  };
  for (const auto& points_to_swap : points_to_swaps) {
    for (const auto& [u, v] : points_to_swap) {
      std::swap(path[u], path[v]);
    }
    ASSERT_TRUE(CheckPathValid(path));

    SegmentsPointsMap segments_points = GetSegmentPointsMap(path);
    auto tmp_path = path;
    auto annealed_paths =
        EdgesAnnealing(tmp_path, segments_points, GetRouteFinderSettings());
    ASSERT_TRUE(CheckPathValid(tmp_path));
    ASSERT_TRUE(CheckPathsValid(annealed_paths));

    for (const auto& [u, v] : points_to_swap) {
      std::swap(path[u], path[v]);
    }
  }
}

bool WaypoitComparator(const Waypoint& self, const Waypoint& other) {
  return self.point.get().id < other.point.get().id;
}

void BruteForceAnnealing(std::vector<Waypoint>& brute_force_path) {
  if (brute_force_path.empty()) {
    return;
  }
  std::sort(brute_force_path.begin(), brute_force_path.end(),
            WaypoitComparator);
  int max_distance =
      united_dispatch::waybill::delivery::GetRouteDistance(brute_force_path);
  std::vector<Waypoint> best_path = brute_force_path;
  do {
    int new_distance =
        united_dispatch::waybill::delivery::GetRouteDistance(brute_force_path);
    if (new_distance < max_distance) {
      max_distance = new_distance;
      best_path = brute_force_path;
    }
  } while (std::next_permutation(brute_force_path.begin(),
                                 brute_force_path.end(), WaypoitComparator));
  brute_force_path = std::move(best_path);
}

UTEST(RouteFinderTest, BruteForceCheckEdgesAnnealing) {
  std::random_device rd;
  std::mt19937 gen(rd());
  gen.seed(42);
  std::uniform_real_distribution<> lon_dist(37.0, 38.0);
  std::uniform_real_distribution<> lat_dist(55.0, 56.0);
  for (int batch_size = 0; batch_size <= 3; ++batch_size) {
    for (int j = 0; j < 3; ++j) {
      std::vector<std::tuple<double, double, handlers::SegmentPointType>>
          route_points;
      for (int i = 0; i < batch_size; ++i) {
        route_points.emplace_back(lon_dist(gen), lat_dist(gen),
                                  handlers::SegmentPointType::kPickup);
      }
      for (int i = 0; i < batch_size; ++i) {
        route_points.emplace_back(lon_dist(gen), lat_dist(gen),
                                  handlers::SegmentPointType::kDropoff);
      }
      for (int i = 0; i < batch_size; ++i) {
        route_points.emplace_back(lon_dist(gen), lat_dist(gen),
                                  handlers::SegmentPointType::kReturn);
      }
      std::vector<Waypoint> annealing_path = GetPath(route_points);
      std::vector<Waypoint> brute_force_path = annealing_path;

      SegmentsPointsMap segments_points = GetSegmentPointsMap(annealing_path);
      EdgesAnnealing(annealing_path, segments_points, GetRouteFinderSettings());
      BruteForceAnnealing(brute_force_path);

      for (size_t i = 0; i < annealing_path.size(); ++i) {
        ASSERT_FLOAT_EQ(annealing_path[i].point.get().coordinates,
                        brute_force_path[i].point.get().coordinates);
      }
    }
  }
}

UTEST(RouteFinderTest, GetSegmentIdThatMaximizesDistance) {
  std::vector<Waypoint> path;

  std::vector<SegmentPoint> segment_points;
  std::vector<std::pair<double, double>> segment_points_init_list = {
      {10.0, 10.0},
      {20.0, 10.0},
      {20.0, 100.0},
      {30.0, 10.0},
  };
  for (const auto& [lon, lat] : segment_points_init_list) {
    SegmentPoint point;
    point.coordinates = infraver_geometry::Point(lon, lat);
    point.type = handlers::SegmentPointType::kPickup;
    segment_points.emplace_back(std::move(point));
  }

  int segment_index = 1;
  for (const auto& segment_point : segment_points) {
    SegmentPtr segment = std::make_shared<Segment>();
    segment->id = std::to_string(segment_index++);
    path.emplace_back(segment_point, segment);
  }

  {
    std::vector<Waypoint> path_to_test;
    path_to_test = path;
    ConstSegmentPtr max_segment = GetSegmentThatMaximizesDistance(path_to_test);
    ASSERT_EQ(max_segment->id, "3");
  }

  {
    std::vector<Waypoint> path_to_test;
    path_to_test = path;
    std::reverse(path_to_test.begin(), path_to_test.end());
    ConstSegmentPtr max_segment = GetSegmentThatMaximizesDistance(path_to_test);
    ASSERT_EQ(max_segment->id, "3");
  }

  {
    std::vector<Waypoint> path_to_test;
    path_to_test = path;
    path_to_test.pop_back();
    ConstSegmentPtr max_segment = GetSegmentThatMaximizesDistance(path_to_test);
    ASSERT_EQ(max_segment->id, "3");
  }

  {
    std::vector<Waypoint> path_to_test;
    path_to_test = path;
    path_to_test.pop_back();
    std::reverse(path_to_test.begin(), path_to_test.end());
    ConstSegmentPtr max_segment = GetSegmentThatMaximizesDistance(path_to_test);
    ASSERT_EQ(max_segment->id, "3");
  }
}

UTEST(RouteFinderTest, GetRouteDistanceDiffAfterSwapIncrease) {
  const int dist_unit = 111'226;
  const int error = 10;
  std::vector<Waypoint> path;
  std::vector<SegmentPoint> segment_points;
  std::vector<std::pair<double, double>> segment_points_init_list = {
      {0, 0}, {0, 1}, {0, 2}, {0, 3}, {0, 4}, {0, 5},
  };
  for (const auto& [lon, lat] : segment_points_init_list) {
    SegmentPoint point;
    point.coordinates = infraver_geometry::Point(lon, lat);
    point.type = handlers::SegmentPointType::kPickup;
    segment_points.emplace_back(std::move(point));
  }

  int segment_index = 1;
  for (const auto& segment_point : segment_points) {
    SegmentPtr segment = std::make_shared<Segment>();
    segment->id = std::to_string(segment_index++);
    path.emplace_back(segment_point, segment);
  }

  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 0, 1),
              1 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 0, 2),
              2 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 0, 3),
              5 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 0, 5),
              6 * dist_unit, error);

  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 1, 2),
              2 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 1, 3),
              4 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 1, 4),
              8 * dist_unit, error);
  ASSERT_NEAR(GetRouteDistanceDiffAfterSwap(path, path.size(), 1, 5),
              8 * dist_unit, error);
}

UTEST(RouteFinderTest, CanSwap) {
  std::vector<Waypoint> path;
  std::vector<SegmentPoint> segment_points;
  std::vector<
      std::tuple<double, double, handlers::SegmentPointType, std::string>>
      route_points = {
          {37, 55, handlers::SegmentPointType::kPickup, "1"},
          {37, 55, handlers::SegmentPointType::kPickup, "2"},
          {37, 55, handlers::SegmentPointType::kPickup, "3"},
          {37.0003, 55.0004, handlers::SegmentPointType::kDropoff, "1"},
          {37.0002, 55.0003, handlers::SegmentPointType::kDropoff, "2"},
          {37.0001, 55.0002, handlers::SegmentPointType::kDropoff, "3"},
          {37, 55, handlers::SegmentPointType::kReturn, "1"},
          {37, 55, handlers::SegmentPointType::kReturn, "2"},
          {37, 55, handlers::SegmentPointType::kReturn, "3"},
      };
  for (const auto& [lon, lat, type, id] : route_points) {
    SegmentPoint point;
    point.coordinates = infraver_geometry::Point(lon, lat);
    point.type = type;
    point.id = id;
    segment_points.emplace_back(std::move(point));
  }

  for (const auto& segment_point : segment_points) {
    SegmentPtr segment = std::make_shared<Segment>();
    segment->id = segment_point.id;
    path.emplace_back(segment_point, segment);
  }

  SegmentsPointsMap segments_points = GetSegmentPointsMap(path);

  ASSERT_FALSE(CanSwap(path, segments_points, 0, 6));
  ASSERT_FALSE(CanSwap(path, segments_points, 0, 1));
  ASSERT_FALSE(CanSwap(path, segments_points, 0, 3));

  ASSERT_TRUE(CanSwap(path, segments_points, 3, 4));
  ASSERT_TRUE(CanSwap(path, segments_points, 3, 5));
}

UTEST(RouteFinderTest, GetRouteDistanceDiffAfterSwapDecrease) {
  std::vector<Waypoint> path;
  std::vector<SegmentPoint> segment_points;
  std::vector<std::tuple<double, double, handlers::SegmentPointType>>
      route_points = {
          {37, 55, handlers::SegmentPointType::kPickup},
          {37, 55, handlers::SegmentPointType::kPickup},
          {37, 55, handlers::SegmentPointType::kPickup},
          {37.0003, 55.0004, handlers::SegmentPointType::kDropoff},
          {37.0002, 55.0003, handlers::SegmentPointType::kDropoff},
          {37.0001, 55.0002, handlers::SegmentPointType::kDropoff},
          {37, 55, handlers::SegmentPointType::kReturn},
          {37, 55, handlers::SegmentPointType::kReturn},
          {37, 55, handlers::SegmentPointType::kReturn},
      };
  for (const auto& [lon, lat, type] : route_points) {
    SegmentPoint point;
    point.coordinates = infraver_geometry::Point(lon, lat);
    point.type = type;
    segment_points.emplace_back(std::move(point));
  }

  int segment_index = 1;
  for (const auto& segment_point : segment_points) {
    SegmentPtr segment = std::make_shared<Segment>();
    segment->id = std::to_string(segment_index++);
    path.emplace_back(segment_point, segment);
  }

  ASSERT_TRUE(GetRouteDistanceDiffAfterSwap(path, path.size() - 3, 3, 5) < 0);
}
