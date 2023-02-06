#include "price_category_meta.hpp"

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

namespace {

using eats_catalog::models::Currency;
using eats_catalog::models::Place;
using eats_catalog::models::PlaceInfo;
using handlers::internal_v1_catalog_for_layout::post::render::PriceCategoryMeta;

Place CreatePlaceWithCurrency(PlaceInfo& place_info, const Currency& currency,
                              const double value = 1.0) {
  const eats_catalog::models::PriceCategory kDefaultPriceCategory = {
      1,       // id
      "name",  // name
      value    // value
  };

  place_info.currency = currency;
  place_info.price_category = kDefaultPriceCategory;
  Place place{place_info};
  return place;
}

}  // namespace

TEST(PriceCategory, CommonCurrency) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();
  const handlers::internal_v1_catalog_for_layout::post::render::Context context{
      eats_catalog::models::ShippingType::kDelivery,  // shipping_type
      eats_catalog::models::CustomFilterType::kAny,   // block_type
  };
  PriceCategoryMeta modifier(config, std::nullopt);

  const std::vector<Currency> currencies = {
      {"₽", "RUB"},
      {"$", "USD"},
      {"Br", "BYN"},
      {"₸", "KZT"},
  };

  for (const auto& currency : currencies) {
    handlers::PlaceListItem listItem{};
    PlaceInfo place_info{};
    const auto place = CreatePlaceWithCurrency(place_info, currency);
    modifier.Modify(listItem, place, context);

    const auto& payload = listItem.payload.data.meta.at(0).payload;
    const auto price_category = std::get<handlers::PriceCategoryMeta>(payload);
    EXPECT_EQ(price_category.currency_sign, currency.sign);
  }
}

TEST(PriceCategory, CurrencyOverride) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();
  const handlers::internal_v1_catalog_for_layout::post::render::Context context{
      eats_catalog::models::ShippingType::kDelivery,  // shipping_type
      eats_catalog::models::CustomFilterType::kAny,   // block_type
  };
  PriceCategoryMeta modifier(config, "override");

  const std::vector<Currency> currencies = {
      {"₽", "RUB"},
      {"$", "USD"},
      {"Br", "BYN"},
      {"₸", "KZT"},
  };

  const std::string expected_currency_sign = "override";

  for (const auto& currency : currencies) {
    handlers::PlaceListItem listItem{};
    PlaceInfo place_info{};
    const auto place = CreatePlaceWithCurrency(place_info, currency);
    modifier.Modify(listItem, place, context);

    const auto& payload = listItem.payload.data.meta.at(0).payload;
    const auto price_category = std::get<handlers::PriceCategoryMeta>(payload);
    EXPECT_EQ(price_category.currency_sign, expected_currency_sign);
  }
}

TEST(PriceCategory, Value) {
  const auto& config_ptr = dynamic_config::GetDefaultSnapshot();
  const auto& config = config_ptr.Get<::taxi_config::TaxiConfig>();
  const handlers::internal_v1_catalog_for_layout::post::render::Context context{
      eats_catalog::models::ShippingType::kDelivery,  // shipping_type
      eats_catalog::models::CustomFilterType::kAny,   // block_type
  };
  PriceCategoryMeta modifier(config, std::nullopt);

  const int config_total_symbols =
      config.eats_catalog_price_category_meta.total_symbols;
  const std::vector<std::pair<double, int>> value_expected{
      {1.0, config_total_symbols},
      {2.0, config_total_symbols},
      {1.2, config_total_symbols},
      {0.5, 2},
      {0, 1},
      {0.3, 1},
  };

  for (const auto& [value, expected] : value_expected) {
    handlers::PlaceListItem listItem{};
    PlaceInfo place_info{};
    auto place = CreatePlaceWithCurrency(place_info, {"$", "USD"}, value);
    modifier.Modify(listItem, place, context);

    const auto& payload = listItem.payload.data.meta.at(0).payload;
    const auto price_category = std::get<handlers::PriceCategoryMeta>(payload);
    EXPECT_EQ(price_category.currency_sign, "$");
    EXPECT_EQ(price_category.highlighted_symbols, expected);
  }
}
