#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "catalog_search_layout_builder.hpp"

namespace {

struct Item {
  std::string id;
  std::optional<std::string> sku_id;
};

using eats_full_text_search::models::CatalogSearchLayoutBuilder;
using PlaceItems = std::vector<Item>;
using PlaceItemsSortOrder = std::vector<std::vector<std::string>>;

std::vector<eats_full_text_search::models::PlaceLayout> BuildPlacesLayout(
    const std::vector<PlaceItems>& places) {
  std::vector<eats_full_text_search::models::PlaceLayout> places_layout;
  places_layout.reserve(places.size());
  for (size_t i = 0; i < places.size(); ++i) {
    const auto& place = places[i];
    eats_full_text_search::models::PlaceLayout new_place;
    new_place.catalog_place.id = eats_full_text_search::models::PlaceId{i};
    new_place.items.reserve(place.size());
    for (const auto& item : place) {
      eats_full_text_search::models::ItemPreviewLayout new_item;
      new_item.id = item.id;
      new_item.sku_id = item.sku_id;
      new_place.items.emplace_back(std::move(new_item));
    }
    places_layout.emplace_back(std::move(new_place));
  }
  return places_layout;
}

void AssertSortOrder(
    const std::vector<eats_full_text_search::models::PlaceLayout>&
        result_places_items,
    const std::vector<std::vector<std::string>>& expected_places_items) {
  ASSERT_EQ(result_places_items.size(), expected_places_items.size());
  for (size_t place_ind = 0; place_ind < result_places_items.size();
       ++place_ind) {
    const auto& result_items = result_places_items[place_ind].items;
    const auto& expected_items = expected_places_items[place_ind];
    ASSERT_EQ(result_items.size(), expected_items.size());
    for (size_t item_ind = 0; item_ind < result_items.size(); ++item_ind) {
      ASSERT_EQ(result_items[item_ind].id, expected_items[item_ind]);
    }
  }
}

}  // namespace

UTEST(SortPlacesAndItemsBySku, NoSku) {
  const size_t sku_items_count = 3;
  auto places = BuildPlacesLayout({{{"1", std::nullopt},
                                    {"2", std::nullopt},
                                    {"3", std::nullopt},
                                    {"4", std::nullopt},
                                    {"5", std::nullopt},
                                    {"6", std::nullopt}},
                                   {{"7", std::nullopt},
                                    {"1", std::nullopt},
                                    {"8", std::nullopt},
                                    {"3", std::nullopt}}});
  const PlaceItemsSortOrder expected_places_items = {
      {"1", "2", "3", "4", "5", "6"}, {"7", "1", "8", "3"}};
  CatalogSearchLayoutBuilder::SortPlacesAndItemsBySku(places, sku_items_count);
  AssertSortOrder(places, expected_places_items);
}

UTEST(SortPlacesAndItemsBySku, TooManyMainItems) {
  const size_t sku_items_count = 3;
  auto places = BuildPlacesLayout({
      {{"1", "1"},
       {"2", std::nullopt},
       {"3", "3"},
       {"4", "4"},
       {"5", std::nullopt},
       {"6", std::nullopt}},
      {{"3", "3"}},
      {{"4", "4"}, {"1", "1"}},
  });
  const PlaceItemsSortOrder expected_places_items = {
      {"1", "3", "4", "2", "5", "6"}, {"1", "4"}, {"3"}};
  CatalogSearchLayoutBuilder::SortPlacesAndItemsBySku(places, sku_items_count);
  AssertSortOrder(places, expected_places_items);
}

UTEST(SortPlacesAndItemsBySku, SkuItemsCount) {
  const auto places = BuildPlacesLayout(
      {{{"1", "1"},
        {"2", std::nullopt},
        {"3", "3"},
        {"4", "4"},
        {"5", std::nullopt},
        {"6", std::nullopt}},
       {{"7", "7"}, {"1", "1"}, {"8", std::nullopt}, {"3", "3"}}});
  std::vector<size_t> sku_items_counts = {1, 2, 3, 4};
  std::unordered_map<size_t, PlaceItemsSortOrder> expected_places_items;
  expected_places_items[1] = {{"1", "2", "3", "4", "5", "6"},
                              {"1", "7", "8", "3"}};
  expected_places_items[2] = {{"1", "3", "2", "4", "5", "6"},
                              {"1", "3", "7", "8"}};
  expected_places_items[3] = {{"1", "3", "4", "2", "5", "6"},
                              {"1", "3", "7", "8"}};
  expected_places_items[4] = {{"1", "3", "4", "2", "5", "6"},
                              {"1", "3", "7", "8"}};
  for (const auto& sku_items_count : sku_items_counts) {
    auto current_places = places;
    CatalogSearchLayoutBuilder::SortPlacesAndItemsBySku(current_places,
                                                        sku_items_count);
    AssertSortOrder(current_places, expected_places_items.at(sku_items_count));
  }
}

UTEST(SortPlacesAndItemsBySku, EqualPlaces) {
  const size_t sku_items_count = 3;
  auto places =
      BuildPlacesLayout({{{"1", "1"}},
                         {{"1", "1"},
                          {"2", std::nullopt},
                          {"3", "3"},
                          {"4", "4"},
                          {"5", std::nullopt},
                          {"6", std::nullopt}},
                         {{"1", "1"}, {"4", "4"}, {"5", std::nullopt}},
                         {{"3", "3"}, {"5", std::nullopt}, {"4", "4"}},
                         {{"5", std::nullopt}, {"3", "3"}, {"1", "1"}},
                         {{"4", "4"}},
                         {{"3", "3"}},
                         {{"1", "1"}}});
  const PlaceItemsSortOrder expected_places_items = {
      {"1", "3", "4", "2", "5", "6"},
      {"1", "3", "5"},
      {"1", "5", "4"},
      {"5", "3", "4"},
      {"1"},
      {"1"},
      {"3"},
      {"4"}};
  CatalogSearchLayoutBuilder::SortPlacesAndItemsBySku(places, sku_items_count);
  AssertSortOrder(places, expected_places_items);
}
