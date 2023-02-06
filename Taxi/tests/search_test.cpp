#include <gtest/gtest.h>
#include <grocery-depots-client/models/depots_cache.hpp>
#include <grocery-depots-internal/utils/search.hpp>
#include <memory>

std::vector<grocery_depots::models::Depot> MakeTestDepotCache() {
  return {
      {grocery_shared::DepotId{"wms123"},
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
       std::nullopt, /* company_actual_address */
       std::optional{std::vector<grocery_shared::datetime::TimeOfDayInterval>{
           grocery_shared::datetime::TimeOfDayInterval{
               grocery_shared::datetime::TimeOfDayInterval::DayType::kEveryday,
               grocery_shared::datetime::TimeOfDayInterval::Range{
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{10}},
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{20}}}}}} /* timetable */},
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
       std::nullopt, /* company_actual_address */
       std::optional{std::vector<grocery_shared::datetime::TimeOfDayInterval>{
           grocery_shared::datetime::TimeOfDayInterval{
               grocery_shared::datetime::TimeOfDayInterval::DayType::kEveryday,
               grocery_shared::datetime::TimeOfDayInterval::Range{
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{10}},
                   grocery_shared::datetime::TimeOfDayInterval::Time{
                       std::chrono::minutes{20}}}}}} /* timetable */}};
}

TEST(SearchTests, Base) {
  using grocery_depots::utils::FilterDepotsBySearchQuery;
  grocery_depots_client::models::DepotsCache cache(MakeTestDepotCache());
  auto depots =
      FilterDepotsBySearchQuery(cache.GetDepotsByRegionId(123), "Super");
  ASSERT_EQ(depots.size(), 1);
  ASSERT_EQ(depots[0].get().id, grocery_shared::DepotId{"wms123"});
  depots = FilterDepotsBySearchQuery(cache.GetDepots(), "Super");
  ASSERT_EQ(depots.size(), 1);
  ASSERT_EQ(depots[0].get().id, grocery_shared::DepotId{"wms123"});
  depots = FilterDepotsBySearchQuery(
      cache.GetDepots(grocery_shared::CountryIso3{"USA"}), "Under");
  ASSERT_EQ(depots.size(), 1);
  ASSERT_EQ(depots[0].get().id, grocery_shared::DepotId{"wms321"});
  depots = FilterDepotsBySearchQuery(
      cache.GetDepots(grocery_shared::CountryIso3{"USA"}), std::nullopt);
  ASSERT_EQ(depots.size(), 1);
  ASSERT_EQ(depots[0].get().id, grocery_shared::DepotId{"wms321"});
  ASSERT_TRUE(
      FilterDepotsBySearchQuery(
          cache.GetDepots(grocery_shared::CountryIso3{"USA"}), "NoSuchString")
          .empty());
  depots = FilterDepotsBySearchQuery(cache.GetDepots(), std::nullopt);
  ASSERT_EQ(depots.size(), 2);
  // ToDo: Make search case insensitive
  //  depots = grocery_depots::utils::FilterDepotsBySearchQuery(
  //      cache.GetDepotsByRegionId(123), "super");
  //  ASSERT_EQ(depots.size(), 1);
  //  ASSERT_EQ(depots[0]->id, "wms123");
}

TEST(SearchTests, EmptyCases) {
  using grocery_depots::utils::FilterDepotsBySearchQuery;
  const grocery_depots_client::models::DepotsCache::Depots none{};
  ASSERT_TRUE(FilterDepotsBySearchQuery(none, "NoSuchString").empty());
  ASSERT_TRUE(FilterDepotsBySearchQuery(none, std::nullopt).empty());
}

TEST(SearchTests, MoveDepotsCache) {
  using grocery_depots::utils::FilterDepotsBySearchQuery;
  auto ptr = std::make_unique<grocery_depots_client::models::DepotsCache>(
      MakeTestDepotCache());
  grocery_depots_client::models::DepotsCache local(std::move(*ptr));
  ASSERT_TRUE(
      FilterDepotsBySearchQuery(local.GetDepots(), "ScanAllFileds").empty());
}
