#include "route_cache_test_helper.hpp"

#include <gtest/gtest.h>

namespace shuttle_control::tests::helpers {

TEST(RouteCacheTestHelper, SingleRoute) {
  const auto& route_json = R"(
    {
      "meta": {
        "id": 10,
        "name": "route_1"
      },
      "points": [
        {
          "point_id": 10,
          "position": [33.33, 55.55],
          "is_anchor": true
        },
        {
          "point_id": 11,
          "position": [33.33, 55.55],
          "stop_id": 1,
          "name": "stop_1",
          "is_terminal": true,
          "ya_transport_id": "stop__1"
        },
        {
          "point_id": 12,
          "position": [33.33, 55.55],
          "stop_id": 2,
          "name": "stop_2",
          "ya_transport_id": "stop__2"
        }
      ],
      "length": 200.0,
      "geo_data": {
        "timezone": "MSC",
        "city": "moscow",
        "tariff_zone": "central"
      }
    }
  )";
  const auto& route =
      ::formats::json::FromString(route_json).As<interlayers::RouteInfo>();
  const auto& [actual_cache] =
      RouteCacheTestHelper::Build({{models::RouteIdT{10}, route}});
  const auto& expected_cache = models::RoutesCacheIndex{
      {{
          models::RouteIdT{10},
          models::RouteData{
              "route_1",
              {models::PointIdT{10}, models::PointIdT{11},
               models::PointIdT{12}},
              {models::StopIdT{1}, models::StopIdT{2}},
              {models::StopIdT{1}},
              false,
              false,
              false,
              ::geometry::Distance ::from_value(200.0),
              models::GeoData{"MSC", "moscow", "central"},
              1,
          },
      }},
      {
          {
              models::PointIdT{10},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  std::nullopt,
                  {{models::RouteIdT{10}, models::RoutePointData{0, true}}},
              },
          },
          {
              models::PointIdT{11},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  models::StopIdT{1},
                  {{models::RouteIdT{10}, models::RoutePointData{1, false}}},
              },
          },
          {
              models::PointIdT{12},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  models::StopIdT{2},
                  {{models::RouteIdT{10}, models::RoutePointData{2, false}}},
              },
          },
      },
      {{
           models::StopIdT{1},
           models::StopData{
               models::PointIdT{11}, "stop_1", "stop__1", {}, true, true},
       },
       {
           models::StopIdT{2},
           models::StopData{
               models::PointIdT{12}, "stop_2", "stop__2", {}, true, false},
       }},
      {{"route_1", models::RouteIdT{10}}},
  };

  EXPECT_EQ(expected_cache.routes, actual_cache.routes);
  EXPECT_EQ(expected_cache.points, actual_cache.points);
  EXPECT_EQ(expected_cache.stops, actual_cache.stops);
  EXPECT_EQ(expected_cache.route_name_to_id, actual_cache.route_name_to_id);
}

TEST(RouteCacheTestHelper, DisabledRoute) {
  const auto& route_json = R"(
    {
      "meta": {
        "id": 10,
        "name": "route_1",
        "is_deleted": true
      },
      "points": [
        {
          "point_id": 11,
          "position": [33.33, 55.55],
          "stop_id": 1,
          "name": "stop_1"
        }
      ]
    }
  )";
  const auto& route =
      ::formats::json::FromString(route_json).As<interlayers::RouteInfo>();
  const auto& [actual_cache] =
      RouteCacheTestHelper::Build({{models::RouteIdT{10}, route}});
  const auto& expected_cache = models::RoutesCacheIndex{
      {{
          models::RouteIdT{10},
          models::RouteData{
              "route_1",
              {models::PointIdT{11}},
              {models::StopIdT{1}},
              {},
              false,
              false,
              true,
              ::geometry::Distance::from_value(0.0),
              models::GeoData{},
              1,
          },
      }},
      {{
          models::PointIdT{11},
          models::PointData{
              ::geometry::Position{::geometry::Latitude{33.33},
                                   ::geometry::Longitude{55.55}},
              models::StopIdT{1},
              {{models::RouteIdT{10}, models::RoutePointData{0, false}}},
          },
      }},
      {{
          models::StopIdT{1},
          models::StopData{
              models::PointIdT{11},
              "stop_1",
              std::nullopt,
              {},
              false,
              false,
          },
      }},
      {{"route_1", models::RouteIdT{10}}},
  };

  EXPECT_EQ(expected_cache.routes, actual_cache.routes);
  EXPECT_EQ(expected_cache.points, actual_cache.points);
  EXPECT_EQ(expected_cache.stops, actual_cache.stops);
  EXPECT_EQ(expected_cache.route_name_to_id, actual_cache.route_name_to_id);
}

TEST(RouteCacheTestHelper, CrossRoutes) {
  const auto& route1_json = R"(
    {
      "meta": {
        "id": 1,
        "name": "route_1"
      },
      "points": [
        {
          "point_id": 1,
          "position": [33.33, 55.55]
        },
        {
          "point_id": 2,
          "position": [33.33, 55.55],
          "stop_id": 2,
          "name": "stop_2"
        }
      ]
    }
  )";
  const auto& route2_json = R"(
    {
      "meta": {
        "id": 2,
        "name": "route_2"
      },
      "points": [
        {
          "point_id": 2,
          "position": [33.33, 55.55],
          "stop_id": 2,
          "name": "stop_2"
        },
        {
          "point_id": 3,
          "position": [33.33, 55.55]
        }
      ]
    }
  )";
  const auto& route1 =
      ::formats::json::FromString(route1_json).As<interlayers::RouteInfo>();
  const auto& route2 =
      ::formats::json::FromString(route2_json).As<interlayers::RouteInfo>();
  const auto& [actual_cache] = RouteCacheTestHelper::Build({
      {models::RouteIdT{1}, route1},
      {models::RouteIdT{2}, route2},
  });
  const auto& expected_cache = models::RoutesCacheIndex{
      {
          {
              models::RouteIdT{1},
              models::RouteData{
                  "route_1",
                  {models::PointIdT{1}, models::PointIdT{2}},
                  {models::StopIdT{2}},
                  {},
                  false,
                  false,
                  false,
                  ::geometry::Distance::from_value(0.0),
                  models::GeoData{},
                  1,
              },
          },
          {
              models::RouteIdT{2},
              models::RouteData{
                  "route_2",
                  {models::PointIdT{2}, models::PointIdT{3}},
                  {models::StopIdT{2}},
                  {},
                  false,
                  false,
                  false,
                  ::geometry::Distance::from_value(0.0),
                  models::GeoData{},
                  1,
              },
          },
      },
      {
          {
              models::PointIdT{1},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  std::nullopt,
                  {{models::RouteIdT{1}, models::RoutePointData{0, false}}},
              },
          },
          {
              models::PointIdT{2},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  models::StopIdT{2},
                  {
                      {models::RouteIdT{1}, models::RoutePointData{1, false}},
                      {models::RouteIdT{2}, models::RoutePointData{0, false}},
                  },
              },
          },
          {
              models::PointIdT{3},
              models::PointData{
                  ::geometry::Position{::geometry::Latitude{33.33},
                                       ::geometry::Longitude{55.55}},
                  std::nullopt,
                  {{models::RouteIdT{2}, models::RoutePointData{1, false}}},
              },
          },
      },
      {{
          models::StopIdT{2},
          models::StopData{
              models::PointIdT{2},
              "stop_2",
              std::nullopt,
              {},
              true,
              false,
          },
      }},
      {
          {"route_1", models::RouteIdT{1}},
          {"route_2", models::RouteIdT{2}},
      },
  };

  EXPECT_EQ(expected_cache.routes, actual_cache.routes);
  EXPECT_EQ(expected_cache.points, actual_cache.points);
  EXPECT_EQ(expected_cache.stops, actual_cache.stops);
  EXPECT_EQ(expected_cache.route_name_to_id, actual_cache.route_name_to_id);
}

}  // namespace shuttle_control::tests::helpers
