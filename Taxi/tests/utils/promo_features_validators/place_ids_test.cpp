#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <caches/places_catalog_storage.hpp>
#include <defs/api/promo.hpp>
#include <defs/definitions.hpp>
#include <experiments3/eats_restapp_promo_settings.hpp>
#include <utils/promo_features_validators/place_ids.hpp>

namespace eats_restapp_promo::utils {

using namespace testing;

struct PlaceCatalogMock {
  MOCK_METHOD(std::optional<::caches::PlaceFromCatalogStorage>, GetValue,
              (int64_t), (const));
};

struct ValivatationPlaceIds : public Test {
  StrictMock<PlaceCatalogMock> place_catalog_mock;

  static ::caches::PlaceFromCatalogStorage MakePlaceInfo(
      const std::string& currency_sign) {
    ::caches::Currency currency;
    currency.sign = currency_sign;
    ::caches::Country country;
    country.currency = currency;
    ::caches::PlaceFromCatalogStorage place_info;
    place_info.country = country;
    return place_info;
  }
};

TEST_F(ValivatationPlaceIds, ThrowExceptionForEmptyValue) {
  types::Places places;
  ASSERT_THROW(
      ValidatePlaceIds(&place_catalog_mock, models::PromoInfo(), places),
      models::ValidationError);
}

TEST_F(ValivatationPlaceIds,
       DontThrowExceptionForValueWith1SizeAndMultiplyPlaceTrue) {
  types::Places places{{1}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  EXPECT_CALL(place_catalog_mock, GetValue(1)).WillOnce(Return(std::nullopt));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
}

TEST_F(ValivatationPlaceIds,
       DontThrowExceptionForValueWith1SizeAndMultiplyPlaceFalse) {
  types::Places places{{1}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = false;
  EXPECT_CALL(place_catalog_mock, GetValue(1)).WillOnce(Return(std::nullopt));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
}

TEST_F(ValivatationPlaceIds,
       DontThrowExceptionForValueWith2SizeAndMultiplyPlaceTrue) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  EXPECT_CALL(place_catalog_mock, GetValue(1)).WillOnce(Return(std::nullopt));
  EXPECT_CALL(place_catalog_mock, GetValue(2)).WillOnce(Return(std::nullopt));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
}

TEST_F(ValivatationPlaceIds,
       ThrowExceptionForValueWith2SizeAndMultiplyPlaceFalse) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = false;
  ASSERT_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places),
               models::ValidationError);
}

TEST_F(ValivatationPlaceIds, DoesNotSetCurrencyForUnknownPlace) {
  types::Places places{{1}, {}};
  EXPECT_CALL(place_catalog_mock, GetValue(1)).WillOnce(Return(std::nullopt));
  ASSERT_NO_THROW(
      ValidatePlaceIds(&place_catalog_mock, models::PromoInfo(), places));
  ASSERT_FALSE(places.currency_sign.has_value());
}

TEST_F(ValivatationPlaceIds, DoesNotSetCurrencyForUnknownCountry) {
  types::Places places{{1}, {}};
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(::caches::PlaceFromCatalogStorage()));
  ASSERT_NO_THROW(
      ValidatePlaceIds(&place_catalog_mock, models::PromoInfo(), places));
  ASSERT_FALSE(places.currency_sign.has_value());
}

TEST_F(ValivatationPlaceIds, SetCurrencyForKnownCountry) {
  types::Places places{{1}, {}};
  ::caches::PlaceFromCatalogStorage place_info;
  ::caches::Country place_country;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  ASSERT_NO_THROW(
      ValidatePlaceIds(&place_catalog_mock, models::PromoInfo(), places));
  ASSERT_TRUE(places.currency_sign.has_value());
  ASSERT_EQ(*places.currency_sign, "₽");
}

TEST_F(ValivatationPlaceIds, SkipUnknownPlacesForCurrency) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2)).WillOnce(Return(std::nullopt));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
  ASSERT_TRUE(places.currency_sign.has_value());
  ASSERT_EQ(*places.currency_sign, "₽");
}

TEST_F(ValivatationPlaceIds, SkipUnknownCountriesForCurrency) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2))
      .WillOnce(Return(::caches::PlaceFromCatalogStorage()));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
  ASSERT_TRUE(places.currency_sign.has_value());
  ASSERT_EQ(*places.currency_sign, "₽");
}

TEST_F(ValivatationPlaceIds, DoesNotSetCurrencyForDifferentPlacesNoConfig) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2))
      .WillOnce(Return(MakePlaceInfo("$")));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
  ASSERT_FALSE(places.currency_sign.has_value());
}

TEST_F(ValivatationPlaceIds,
       DoesNotSetCurrencyForDifferentPlacesNoCheckConfig) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  ::experiments3::eats_restapp_promo_settings::PlaceIdsConfiguration conf;
  conf.need_same_currency = false;
  settings.configuration.place_ids = conf;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2))
      .WillOnce(Return(MakePlaceInfo("$")));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
  ASSERT_FALSE(places.currency_sign.has_value());
}

TEST_F(ValivatationPlaceIds, ThrowForDifferentPlacesWithCheckConfig) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  ::experiments3::eats_restapp_promo_settings::PlaceIdsConfiguration conf;
  conf.need_same_currency = true;
  settings.configuration.place_ids = conf;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2))
      .WillOnce(Return(MakePlaceInfo("$")));
  ASSERT_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places),
               models::ValidationError);
}

TEST_F(ValivatationPlaceIds, SetCurrencyForSamePlaces) {
  types::Places places{{1, 2}, {}};
  models::PromoInfo settings;
  settings.is_multiple_places_allowed = true;
  ::experiments3::eats_restapp_promo_settings::PlaceIdsConfiguration conf;
  conf.need_same_currency = true;
  settings.configuration.place_ids = conf;
  EXPECT_CALL(place_catalog_mock, GetValue(1))
      .WillOnce(Return(MakePlaceInfo("₽")));
  EXPECT_CALL(place_catalog_mock, GetValue(2))
      .WillOnce(Return(MakePlaceInfo("₽")));
  ASSERT_NO_THROW(ValidatePlaceIds(&place_catalog_mock, settings, places));
  ASSERT_TRUE(places.currency_sign.has_value());
  ASSERT_EQ(*places.currency_sign, "₽");
}

}  // namespace eats_restapp_promo::utils
