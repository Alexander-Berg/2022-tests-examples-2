#include "route_info.hpp"

#include <gtest/gtest.h>

namespace shuttle_control::tests::helpers::interlayers {

TEST(RouteInfo, ParseFull) {
  const auto& route_info_json = R"(
    {
      "meta": {
        "id": 10,
        "name": "route_1",
        "is_cyclic": true,
        "is_dynamic": true,
        "is_deleted": true,
        "version": 2
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
          "ya_transport_id": "stop__1"
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

  const auto& actual_route_info =
      ::formats::json::FromString(route_info_json).As<RouteInfo>();

  models::Route route{
      models::Route::Meta{models::RouteIdT{10}, "route_1", true, true, true, 2},
  };
  route.AddViaPoint(models::Route::ViaPoint{
      models::PointIdT{10},
      ::geometry::Position{::geometry::Latitude{33.33},
                           ::geometry::Longitude{55.55}},
      true,
  });
  route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{11},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{1},
      "stop_1",
      false,
      {}});
  const RouteInfo expected_route_info{
      std::move(route),
      ::geometry::Distance::from_value(200.0),
      models::GeoData{"MSC", "moscow", "central"},
      {{models::StopIdT{1}, "stop__1"}},
  };

  EXPECT_EQ(expected_route_info, actual_route_info);
}

TEST(RouteInfo, ParseDefults) {
  const auto& route_info_json = R"(
    {
      "meta": {
        "id": 10,
        "name": "route_1"
      },
      "points": [
        {
          "point_id": 10,
          "position": [33.33, 55.55]
        },
        {
          "point_id": 11,
          "position": [33.33, 55.55],
          "stop_id": 1,
          "name": "stop_1"
        }
      ]
    }
  )";

  const auto& actual_route_info =
      ::formats::json::FromString(route_info_json).As<RouteInfo>();

  models::Route route{
      models::Route::Meta{
          models::RouteIdT{10},
          "route_1",
          false,
          false,
          false,
          1,
      },
  };
  route.AddViaPoint(models::Route::ViaPoint{
      models::PointIdT{10},
      ::geometry::Position{::geometry::Latitude{33.33},
                           ::geometry::Longitude{55.55}},
      false,
  });
  route.AddStopPoint(models::Route::StopPoint{
      models::Route::ViaPoint{
          models::PointIdT{11},
          ::geometry::Position{::geometry::Latitude{33.33},
                               ::geometry::Longitude{55.55}},
          false,
      },
      models::StopIdT{1},
      "stop_1",
      false,
      {}});
  const RouteInfo expected_route_info{
      std::move(route),
      ::geometry::Distance::from_value(0.0),
      models::GeoData{},
      {},
  };

  EXPECT_EQ(expected_route_info, actual_route_info);
}

}  // namespace shuttle_control::tests::helpers::interlayers
