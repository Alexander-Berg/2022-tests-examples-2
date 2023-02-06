#include <userver/utest/utest.hpp>

#include "components/eats_zone_mapping_component.hpp"

namespace {
namespace cmp = eats_market_dsbs::components;
}

TEST(ConvertDataZone, EmptyFields) {
  const cmp::EatsZoneItem eats_zone;
  ASSERT_FALSE(cmp::impl::ConvertEatsToMarketZone(eats_zone).has_value());
}

TEST(ConvertDataZone, PartEmptyField) {
  cmp::EatsZoneItem eats_zone;
  clients::eats_catalog_storage::Polygon test_polygon;
  eats_zone.polygon = test_polygon;  // don't have internal vector, must failed

  ASSERT_FALSE(cmp::impl::ConvertEatsToMarketZone(eats_zone).has_value());
}

TEST(ConvertDataZone, NotEmptyField) {
  cmp::EatsZoneItem eats_zone;
  eats_zone.name = "ZoneName";
  eats_zone.enabled = true;
  std::vector<geometry::Position> test_positions;
  clients::eats_catalog_storage::Polygon test_polygon;
  test_polygon.coordinates.push_back(test_positions);
  eats_zone.polygon = test_polygon;
  eats_zone.id = 123;

  cmp::MarketZoneItem exp_market_zone;
  auto& exp_polygondata = exp_market_zone.geo;
  exp_polygondata.type = clients::market_nesu::MarketZoneItemGeoType::kPolygon;
  exp_polygondata.name = eats_zone.name.value();
  exp_polygondata.enabled = eats_zone.enabled.value();
  exp_polygondata.id = eats_zone.id;
  exp_polygondata.coordinates = eats_zone.polygon->coordinates;

  std::optional<cmp::MarketZoneItem> market_zone_opt =
      cmp::impl::ConvertEatsToMarketZone(eats_zone);
  ASSERT_TRUE(market_zone_opt.has_value());
  ASSERT_EQ(exp_market_zone.geo.type, market_zone_opt.value().geo.type);
}
