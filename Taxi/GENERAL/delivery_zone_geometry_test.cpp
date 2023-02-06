#include <userver/utest/utest.hpp>

#include <geometry/position_as_object.hpp>

#include <grocery-depots-internal/models/delivery_zone_geometry.hpp>
#include <grocery-depots-internal/utils/delivery_zone_geometry_convertors.hpp>

using grocery_depots::models::DeliveryZoneGeometry;

geometry::PositionAsObject AsPosition(double lon, double lat) {
  return geometry::PositionAsObject{
      geometry::Position(lat * geometry::lat, lon * geometry::lon)};
}

TEST(DeliveryZoneGeometry, LavkaProspectMira) {
  grocery_depots::utils::GeoMultiPolygon coordinates = {
      {{AsPosition(37.852672, 55.779078), AsPosition(37.861792, 55.780819),
        AsPosition(37.870154, 55.769703), AsPosition(37.874535, 55.763165),
        AsPosition(37.87634, 55.75924), AsPosition(37.873615, 55.756506),
        AsPosition(37.8678, 55.754545), AsPosition(37.854469, 55.751833),
        AsPosition(37.84736, 55.750525), AsPosition(37.846446, 55.756186),
        AsPosition(37.843159, 55.755504), AsPosition(37.843623, 55.76169),
        AsPosition(37.843736, 55.766947), AsPosition(37.846488, 55.768072),
        AsPosition(37.843612, 55.773545), AsPosition(37.844094, 55.775123),
        AsPosition(37.845656, 55.77678), AsPosition(37.852672, 55.779078)}}};

  auto geozone = grocery_depots::utils::Convert(
      coordinates, grocery_shared::utils::To<DeliveryZoneGeometry>());

  EXPECT_FALSE(geozone.Contains(geometry::Position{}));

  const auto inside =
      geometry::Position(55.76069 * geometry::lat, 37.86147 * geometry::lon);
  EXPECT_TRUE(geozone.Contains(inside));

  const auto outside =
      geometry::Position(55.74994 * geometry::lat, 37.86872 * geometry::lon);
  EXPECT_FALSE(geozone.Contains(outside));
}

TEST(DeliveryZoneGeometry, LavkaKamenshiky) {
  grocery_depots::utils::GeoMultiPolygon coordinates = {
      {{AsPosition(37.640106, 55.736991), AsPosition(37.64178, 55.737675),
        AsPosition(37.642429, 55.736234), AsPosition(37.643936, 55.736374),
        AsPosition(37.64487, 55.735532), AsPosition(37.642016, 55.733668),
        AsPosition(37.641038, 55.735366), AsPosition(37.640106, 55.736991)}}};

  auto geozone = grocery_depots::utils::Convert(
      coordinates, grocery_shared::utils::To<DeliveryZoneGeometry>());

  EXPECT_FALSE(geozone.Contains(geometry::Position{}));

  const auto inside = geometry::Position(55.73450198879418 * geometry::lat,
                                         37.6415095537858 * geometry::lon);
  EXPECT_FALSE(geozone.Contains(inside));
}
