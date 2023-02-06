#include "projection.hpp"

#include <userver/utest/utest.hpp>
#include "models/delivery_zone.hpp"
#include "models/place.hpp"

namespace eats_catalog_storage::utils {

TEST(PlaceProjection, Id_RevisionId_UpdatedAt) {
  models::PlaceCacheItem place;
  place.id = 123;
  place.revision_id = 100;
  place.updated_at = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-05-05T15:46:00+03:00");
  place.real_updated_at = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-05-05T15:46:00+03:00");

  auto result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.id, place.id);
  ASSERT_EQ(result.revision_id, place.revision_id);
  ASSERT_EQ(result.updated_at, place.updated_at);
  ASSERT_EQ(result.real_updated_at, place.real_updated_at);
}

TEST(PlaceProjection, Slug) {
  models::PlaceCacheItem place;
  place.slug = "slug";

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kSlug},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.slug, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.slug, std::nullopt);
}

TEST(PlaceProjection, Enabled) {
  models::PlaceCacheItem place;
  place.enabled = true;

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kEnabled},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.enabled, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.enabled, std::nullopt);
}

TEST(PlaceProjection, Name) {
  models::PlaceCacheItem place;
  place.name = "name";

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kName},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.name, std::nullopt);
  ASSERT_EQ(result.name.value(), place.name);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.name, std::nullopt);
}

TEST(PlaceProjection, Type) {
  models::PlaceCacheItem place;
  place.type = models::PlaceType::kNative;

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kType},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.type, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.type, std::nullopt);
}

TEST(PlaceProjection, Business) {
  models::PlaceCacheItem place;
  place.business = "shop";

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kBusiness},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.business, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.business, std::nullopt);
}

TEST(PlaceProjection, LaunchedAt) {
  models::PlaceCacheItem place;
  place.launched_at = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-05-05T15:46:00+03:00");

  auto result = ConvertPlaceProjection(
      {handlers::PlacesProjection::kLaunchedAt}, models::PlaceCacheItem(place));
  ASSERT_NE(result.launched_at, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.launched_at, std::nullopt);
}

TEST(PlaceProjection, PaymentMethods) {
  models::PlaceCacheItem place;
  place.payment_methods = {models::PlacePaymentMethod::kPayture};

  auto result =
      ConvertPlaceProjection({handlers::PlacesProjection::kPaymentMethods},
                             models::PlaceCacheItem(place));
  ASSERT_NE(result.payment_methods, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.payment_methods, std::nullopt);
}

TEST(PlaceProjection, Gallery) {
  models::PlaceCacheItem place;
  place.gallery = {models::PlaceGallery{
      "picture",
      "https://avatars.mds.yandex.net/get-eda/1387779/"
      "f3819fadbe9b062b26a7df079c534e61/214x140",
      {"/images/1387779/f3819fadbe9b062b26a7df079c534e61-{w}x{h}.jpg"},
      100}};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kGallery},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.gallery, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.gallery, std::nullopt);
}

TEST(PlaceProjection, Brand) {
  models::PlaceCacheItem place;
  place.brand = models::PlaceBrand{20064, "bazar_mvsij", "Bazar"};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kBrand},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.brand, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.brand, std::nullopt);
}

TEST(PlaceProjection, Address) {
  models::PlaceCacheItem place;
  place.address = models::PlaceAddress{"Иваново", "Садовая улица, 3"};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kAddress},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.address, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.address, std::nullopt);
}

TEST(PlaceProjection, Country) {
  models::PlaceCacheItem place;
  place.country =
      models::PlaceCountry{35, "Российская Федерация", "RU", {"RUB", "₽"}};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kCountry},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.country, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.country, std::nullopt);
}

TEST(PlaceProjection, Categories) {
  models::PlaceCacheItem place;
  place.categories = {models::PlaceCategory{235, "Завтраки"},
                      {593, "Выпечка"},
                      {37, "Узбекская"}};

  auto result = ConvertPlaceProjection(
      {handlers::PlacesProjection::kCategories}, models::PlaceCacheItem(place));
  ASSERT_NE(result.categories, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.categories, std::nullopt);
}

TEST(PlaceProjection, QuickFilters) {
  models::PlaceCacheItem place;
  place.quick_filters = {models::PlaceQuickFilter{21, "slug21"}};
  place.wizard_quick_filters = {models::PlaceQuickFilter{22, "slug22"}};

  auto result =
      ConvertPlaceProjection({handlers::PlacesProjection::kQuickFilters},
                             models::PlaceCacheItem(place));
  ASSERT_NE(result.quick_filters, std::nullopt);

  ASSERT_FALSE(result.quick_filters->general.empty());
  ASSERT_FALSE(result.quick_filters->wizard.empty());

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.quick_filters, std::nullopt);
}

TEST(PlaceProjection, Region) {
  models::PlaceCacheItem place;
  place.region = models::PlaceRegion{57, {5}, "Europe/Moscow", "region_name"};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kRegion},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.region, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.region, std::nullopt);
}

TEST(PlaceProjection, Rating) {
  models::PlaceCacheItem place;
  place.rating = storages::postgres::PlainJson{
      models::ConvertPlaceRating(handlers::Rating{{4.6034}, 4.6034, 5.0, 116})};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kRating},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.rating, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.rating, std::nullopt);
}

TEST(PlaceProjection, NewRating) {
  models::PlaceCacheItem place;
  place.new_rating = storages::postgres::PlainJson{
      handlers::Serialize(handlers::NewRating{4.6034, true},
                          ::formats::serialize::To<formats::json::Value>{})};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kNewRating},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.new_rating, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.new_rating, std::nullopt);
}

TEST(PlaceProjection, Features) {
  handlers::Feature feature{};
  feature.ignore_surge = true;
  models::PlaceCacheItem place;
  place.features =
      storages::postgres::PlainJson{models::ConvertPlaceFeatures(feature)};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kFeatures},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.features, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.features, std::nullopt);
}

TEST(PlaceProjection, Timing) {
  models::PlaceCacheItem place;
  place.timing = storages::postgres::PlainJson{
      models::ConvertPlaceTiming(handlers::Timing{60, 600, 60})};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kTiming},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.timing, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.timing, std::nullopt);
}

TEST(PlaceProjection, Sorting) {
  models::PlaceCacheItem place;
  place.sorting = storages::postgres::PlainJson{
      models::ConvertPlaceSorting(handlers::Sorting{100, 1000, {12}})};

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kSorting},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.sorting, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.sorting, std::nullopt);
}

TEST(PlaceProjection, AssemblyCost) {
  models::PlaceCacheItem place;
  place.assembly_cost = 100;

  auto result =
      ConvertPlaceProjection({handlers::PlacesProjection::kAssemblyCost},
                             models::PlaceCacheItem(place));
  ASSERT_NE(result.assembly_cost, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.assembly_cost, std::nullopt);
}

TEST(PlaceProjection, Archived) {
  models::PlaceCacheItem place;
  place.archived = true;

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kArchived},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.archived, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.archived, std::nullopt);
}

TEST(PlaceProjection, WorkingIntervals) {
  models::PlaceCacheItem place;
  place.working_intervals = {};

  auto result =
      ConvertPlaceProjection({handlers::PlacesProjection::kWorkingIntervals},
                             models::PlaceCacheItem(place));
  ASSERT_NE(result.working_intervals, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.working_intervals, std::nullopt);
}

TEST(PlaceProjection, AllowedCouriersTypes) {
  models::PlaceCacheItem place;
  place.allowed_couriers_types = std::vector<models::CouriersType>{};

  auto result = ConvertPlaceProjection(
      {handlers::PlacesProjection::kAllowedCouriersTypes},
      models::PlaceCacheItem(place));
  ASSERT_NE(result.allowed_couriers_types, std::nullopt);

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.allowed_couriers_types, std::nullopt);
}

TEST(PlaceProjection, OriginId) {
  models::PlaceCacheItem place;
  place.origin_id = "id-1";

  auto result = ConvertPlaceProjection({handlers::PlacesProjection::kOriginId},
                                       models::PlaceCacheItem(place));
  ASSERT_NE(result.origin_id, std::nullopt);
  ASSERT_EQ(result.origin_id.value(), place.origin_id.value());

  result = ConvertPlaceProjection({}, models::PlaceCacheItem(place));
  ASSERT_EQ(result.origin_id, std::nullopt);
}

// DeliveryZone //

TEST(DeliveryZoneProjection, Id_RevisionId_UpdatedAt) {
  models::DeliveryZone zone;
  zone.id = 123;
  zone.revision_id = 100;
  zone.updated_at = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-05-05T15:46:00+03:00");
  zone.real_updated_at = ::utils::datetime::FromRfc3339StringSaturating(
      "2020-05-05T15:46:00+03:00");

  auto result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.id, zone.id);
  ASSERT_EQ(result.revision_id, zone.revision_id);
  ASSERT_EQ(result.updated_at, zone.updated_at);
  ASSERT_EQ(result.real_updated_at, zone.real_updated_at);
}

TEST(DeliveryZoneProjection, PlaceId) {
  models::DeliveryZone zone;
  zone.place_id = 123;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kPlaceId},
      models::DeliveryZone(zone));
  ASSERT_NE(result.place_id, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.place_id, std::nullopt);
}

TEST(DeliveryZoneProjection, CouriersZoneId) {
  models::DeliveryZone zone;
  zone.couriers_zone_id = 123;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kCouriersZoneId},
      models::DeliveryZone(zone));
  ASSERT_NE(result.couriers_zone_id, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.couriers_zone_id, std::nullopt);
}

TEST(DeliveryZoneProjection, Enabled) {
  models::DeliveryZone zone;
  zone.enabled = true;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kEnabled},
      models::DeliveryZone(zone));
  ASSERT_NE(result.enabled, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.enabled, std::nullopt);
}

TEST(DeliveryZoneProjection, Name) {
  models::DeliveryZone zone;
  zone.name = "name";

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kName}, models::DeliveryZone(zone));
  ASSERT_NE(result.name, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.name, std::nullopt);
}

TEST(DeliveryZoneProjection, CouriersType) {
  models::DeliveryZone zone;
  zone.couriers_type = models::CouriersType::kYandexTaxi;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kCouriersType},
      models::DeliveryZone(zone));
  ASSERT_NE(result.couriers_type, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.couriers_type, std::nullopt);
}

TEST(DeliveryZoneProjection, ShippingType) {
  models::DeliveryZone zone;
  zone.shipping_type = models::ShippingType::kDelivery;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kShippingType},
      models::DeliveryZone(zone));
  ASSERT_NE(result.shipping_type, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.shipping_type, std::nullopt);
}

TEST(DeliveryZoneProjection, DeliveryConditions) {
  models::DeliveryZone zone;
  zone.delivery_conditions = {models::DeliveryCondition{}};

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kDeliveryConditions},
      models::DeliveryZone(zone));
  ASSERT_NE(result.delivery_conditions, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.delivery_conditions, std::nullopt);
}

TEST(DeliveryZoneProjection, Timing) {
  models::DeliveryZone zone;
  zone.market_avg_time = 10.1;
  zone.time_of_arrival = 20.2;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kTiming}, models::DeliveryZone(zone));
  ASSERT_NE(result.timing, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.timing, std::nullopt);
}

TEST(DeliveryZoneProjection, WorkingIntervals) {
  models::DeliveryZone zone;
  zone.working_intervals = {};

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kWorkingIntervals},
      models::DeliveryZone(zone));
  ASSERT_NE(result.working_intervals, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.working_intervals, std::nullopt);
}

TEST(DeliveryZoneProjection, Polygon) {
  models::DeliveryZone zone;
  zone.polygons = {};

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kPolygon},
      models::DeliveryZone(zone));
  ASSERT_EQ(result.polygon, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.polygon, std::nullopt);

  zone.polygons = {
      storages::postgres::io::detail::Polygon{{{40.836667, 57.003798},
                                               {40.842155, 57.008107},
                                               {40.844298, 57.008653},
                                               {40.855585, 57.013111}}}};
  result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kPolygon},
      models::DeliveryZone(zone));
  ASSERT_NE(result.polygon, std::nullopt);
}

TEST(DeliveryZoneProjection, Archived) {
  models::DeliveryZone zone;
  zone.archived = true;

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kArchived},
      models::DeliveryZone(zone));
  ASSERT_NE(result.archived, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.archived, std::nullopt);
}

TEST(DeliveryZoneProjection, SourceInfo) {
  models::DeliveryZone zone;
  zone.source = models::Source::kEatsCore;
  zone.external_id = "id-123";

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kSourceInfo},
      models::DeliveryZone(zone));
  ASSERT_NE(result.source_info, std::nullopt);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.source_info, std::nullopt);
}

TEST(DeliveryZoneProjection, Features) {
  handlers::DeliveryZoneFeature feature{};
  feature.is_ultima = true;

  models::DeliveryZone zone;
  zone.features = storages::postgres::PlainJson{
      models::ConvertDeliveryZoneFeature(feature)};

  auto result = ConvertDeliveryZoneProjection(
      {handlers::DeliveryZonesProjection::kFeatures},
      models::DeliveryZone(zone));
  ASSERT_NE(result.features, std::nullopt);
  ASSERT_TRUE(result.features->is_ultima);

  result = ConvertDeliveryZoneProjection({}, models::DeliveryZone(zone));
  ASSERT_EQ(result.features, std::nullopt);
}

}  // namespace eats_catalog_storage::utils
