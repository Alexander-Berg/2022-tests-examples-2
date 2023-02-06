#include <gtest/gtest.h>
#include <grocery-depots-client/models/depots_cache.hpp>
#include <vector>

namespace {
std::vector<grocery_depots::models::Depot> MakeTestDepotCache() {
  return {
      {
          grocery_shared::DepotId{"wms123"},
          grocery_shared::LegacyDepotId{"123"},
          grocery_shared::CountryIso3{"RUS"},
          grocery_shared::CountryIso2{"RU"},
          123,
          "Europe/Moscow",
          geometry::PositionAsObject{
              geometry::Position::FromGeojsonArray({12.0, 21.0})},
          "Long address",
          "INN123123",
          grocery_shared::PhoneNumber{},
          std::nullopt,
          std::nullopt,
          "RUB",
          std::nullopt,
          grocery_shared::CompanyType::kYandex,
          "OOO Yandex.Lavka",
          true,
          "SuperLavka",
          "short_address",
          grocery_depots::models::Depot::Status::kActive,
          false,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          std::nullopt, /* oebs_depot_id */
          std::nullopt /* company_actual_address */,
          std::optional{
              std::vector<grocery_shared::datetime::TimeOfDayInterval>{
                  grocery_shared::datetime::TimeOfDayInterval{
                      grocery_shared::datetime::TimeOfDayInterval::DayType::
                          kEveryday,
                      grocery_shared::datetime::TimeOfDayInterval::Range{
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{10}},
                          grocery_shared::datetime::TimeOfDayInterval::Time{
                              std::chrono::minutes{20}}}}}} /* timetable */
      },
      {grocery_shared::DepotId{"wms321"},
       grocery_shared::LegacyDepotId{"321"},
       grocery_shared::CountryIso3{"USA"},
       grocery_shared::CountryIso2{"US"},
       321,
       "USA/NewYork",
       geometry::PositionAsObject{
           geometry::Position::FromGeojsonArray({21.0, 12.0})},
       "Long address",
       "TIN123123",
       grocery_shared::PhoneNumber{},
       std::nullopt,
       std::nullopt,
       "RUB",
       std::nullopt,
       grocery_shared::CompanyType::kYandex,
       "OOO Yandex.Lavka",
       true,
       "UnderLavka",
       "short_address",
       grocery_depots::models::Depot::Status::kActive,
       false,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt, /* oebs_depot_id */
       std::nullopt /* company_actual_address */,
       std::optional{std::vector<grocery_shared::datetime::TimeOfDayInterval>{
           grocery_shared::datetime::TimeOfDayInterval{
               grocery_shared::datetime::TimeOfDayInterval::DayType::kEveryday,
               grocery_shared::datetime::TimeOfDayInterval::Range{
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{10}},
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{20}}}}}} /* timetable */}};
}
}  // namespace

TEST(GroceryDepotsCacheTests, Base) {
  grocery_depots_client::models::DepotsCache cache(MakeTestDepotCache());
  ASSERT_TRUE(cache.GetDepot(grocery_shared::DepotId{"wms123"}));
  ASSERT_TRUE(!cache.GetDepot(grocery_shared::DepotId{"NoSuchDepot"}));
}
