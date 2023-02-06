#include "build_default_test.hpp"

namespace routestats::fallback::main {

MinimalPrice BuildDefaultMinimalPrice() {
  MinimalPrice price{};
  price.category_name = "econom";
  price.category_type = MinimalPrice::CategoryType::kApplication;
  // 9:00 - 18:00
  price.time_from = std::chrono::minutes(540);
  price.time_to = std::chrono::minutes(1080);
  price.day_type = MinimalPrice::DayType::kEveryday;
  price.minimal = Decimal("145");
  return price;
}

models::Country BuildDefaultCountry() {
  models::Country country{};
  country.weekends = std::unordered_set<cctz::weekday>{cctz::weekday::saturday,
                                                       cctz::weekday::sunday};
  return country;
}

core::Zone BuildDefaultZone() {
  core::Zone zone{};

  zone.country = BuildDefaultCountry();

  zone.tariff.minimal_prices.push_back(BuildDefaultMinimalPrice());

  zone.tariff_settings.timezone = "Europe/Moscow";

  return zone;
}

}  // namespace routestats::fallback::main
