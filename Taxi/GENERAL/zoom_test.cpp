#include "zoom.hpp"

#include <array>
#include <cmath>
#include <iterator>
#include <utility>

#include <gtest/gtest.h>
#include <geometry/bounding_box.hpp>
#include <geometry/position.hpp>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <defs/all_definitions.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/EATS_CATALOG_ZOOM_CONSTRAINT.hpp>
#include "test_utils.hpp"

namespace eats_catalog::algo {

namespace {

using ::geometry::BoundingBox;
using ::geometry::Latitude;
using ::geometry::Position;
using ::handlers::ZoomRange;

taxi_config::TaxiConfig PatchConfig(double precent_extra_size) {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  config.eats_catalog_zoom_constraint =
      taxi_config::eats_catalog_zoom_constraint::EatsCatalogZoomConstraint{
          precent_extra_size,  // percent_extra_size
          0,                   // min_zoom_level
          19                   // max_zoom_level
      };
  return config;
}

struct RangeTestCase {
  double percent_extra_size;
  Position lower_left, upper_right;
  double zoom_bbox;
  std::vector<Position> points;
  ZoomRange expected;
};

struct BoxTestCase {
  double percent_extra_size;
  double sw_lon, sw_lat, ne_lon, ne_lat;
  BoundingBox expected;
};

void TestZoomRange(const RangeTestCase& tc) {
  const auto& config = PatchConfig(tc.percent_extra_size);

  ZoomRangeKeeper zoom_keeper(config, {tc.lower_left, tc.upper_right},
                              tc.zoom_bbox);
  zoom_keeper.UpdateZoomRange(tc.points);

  const auto& zrange = zoom_keeper.GetZoomRange();
  ExpectDoubleEqual(zrange.min, tc.expected.min);
  ExpectDoubleEqual(zrange.max, tc.expected.max);
}

void TestOuterBox(const BoxTestCase& tc) {
  const auto& config = PatchConfig(tc.percent_extra_size);

  ZoomRangeKeeper zoom_keeper(
      config,
      {MakePosition(tc.sw_lon, tc.sw_lat), MakePosition(tc.ne_lon, tc.ne_lat)},
      /*not used*/ 1);
  const auto& outer = zoom_keeper.GetOuterBoundingBox();

  ExpectPositionEqual(tc.expected.south_west, outer.south_west);
  ExpectPositionEqual(tc.expected.north_east, outer.north_east);
}

}  // namespace

// Empty points cause ZoomRangeKeeper to use maximum zoom range from config
UTEST(ZoomRange, EmptyPoints) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {},
      {9, 19}  // expected
  };
  TestZoomRange(tc);
}

// Decreasing side 2-fold leaves point (2, 2) inside
UTEST(ZoomRange, DecreaseTwoFold) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {MakePosition(2, 2), MakePosition(1.5, 1.5)},
      {9, 11}  // expected
  };
  TestZoomRange(tc);
}

// If all points lie in between bounding box and outer box return zoom_bbox as
// maximum possible
UTEST(ZoomRange, OutsideBoundingBox) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {MakePosition(0.5, 1), MakePosition(3, 4)},
      {9, 10}  // expected
  };
  TestZoomRange(tc);
}

// Not increasing size of the bounding box (if percent_extra_size = 0) implies
// zoom_min == zoom_bbox
UTEST(ZoomRange, DoNotIncreaseBox) {
  RangeTestCase tc{
      0,                   // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {},
      {10, 19}  // expected
  };
  TestZoomRange(tc);
}

// Single one point is OK
UTEST(ZoomRange, OnePoint) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {MakePosition(2, 2)},
      {9, 11}  // expected
  };
  TestZoomRange(tc);
}

// Points lying on the boundary of the box are the same as outside of box
UTEST(ZoomRange, BoxBoundary) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(1, 1),  // lower_left
      MakePosition(3, 3),  // upper_right
      10,                  // zoom_bbox
      {MakePosition(1, 1), MakePosition(1, 3), MakePosition(3, 1),
       MakePosition(2, 3), MakePosition(1, 1.5)},
      {9, 10}  // expected
  };
  TestZoomRange(tc);
}

// Select median margin as a maximum offset
UTEST(ZoomRange, MedianMargin) {
  RangeTestCase tc{
      100,                 // percent_extra_size
      MakePosition(5, 5),  // lower_left
      MakePosition(9, 9),  // upper_right
      10,                  // zoom_bbox
      {MakePosition(6, 5.5), MakePosition(6, 8), MakePosition(7, 7),
       MakePosition(7, 7), MakePosition(7, 7)},
      {9, 11}  // expected
  };
  TestZoomRange(tc);
}

// Real data
UTEST(ZoomRange, RealData) {
  RangeTestCase tc{
      35,                          // percent_extra_size
      MakePosition(36.55, 55.01),  // lower_left
      MakePosition(37.65, 57.20),  // upper_right
      12.18,                       // zoom_bbox
      {MakePosition(36.41, 55.00), MakePosition(36.80, 55.80),
       MakePosition(37.07, 56.46), MakePosition(37.55, 58.40),
       MakePosition(36.99, 56.99), MakePosition(37.64, 57.19),
       MakePosition(36.57, 57.19)},
      {11.747, 12.325}  // expected
  };
  TestZoomRange(tc);
}

UTEST(OuterBoundingBox, ScaleSidesTwoFold) {
  BoxTestCase tc{
      100,   // percent_extra_size
      37,    // south_west_lon
      55,    // south_west_lat
      37.5,  // north_east_lon
      56.0,  // north_east_lat
      {MakePosition(36.75, 54.5), MakePosition(37.75, 56.5)}  // expected
  };
  TestOuterBox(tc);
}

UTEST(OuterBoundingBox, ScaleSidesByThirtyPercent) {
  BoxTestCase tc{
      30,    // percent_extra_size
      37,    // south_west_lon
      55,    // south_west_lat
      37.5,  // north_east_lon
      56.0,  // north_east_lat
      {MakePosition(36.925, 54.85), MakePosition(37.575, 56.150)}  // expected
  };
  TestOuterBox(tc);
}

// Relative order of latitudes and longitudes in input bounding box does not
// matter
UTEST(OuterBoundingBox, LonLatOrder) {
  std::array<double, 2> longitudes{37, 38};
  std::array<double, 2> latitudes{55, 56};

  for (const auto first_lon : {0, 1}) {
    for (const auto first_lat : {0, 1}) {
      BoxTestCase tc{
          50,                         // percent_extra_size
          longitudes[first_lon],      // south_west_lon
          latitudes[first_lat],       // south_west_lat
          longitudes[1 - first_lon],  // north_east_lon
          latitudes[1 - first_lat],   // north_east_lat
          {MakePosition(36.75, 54.75),
           MakePosition(38.250, 56.250)}  // expected
      };
      TestOuterBox(tc);
    }
  }
}

}  // namespace eats_catalog::algo
