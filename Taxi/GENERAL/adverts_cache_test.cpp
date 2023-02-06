#include <eats-adverts-goods/models/adverts_cache.hpp>

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_adverts_goods::models {

template <typename T>
bool operator==(const PlacePromotions<T>& lhs, const PlacePromotions<T>& rhs) {
  return std::tie(lhs.table_key, lhs.place_promotions, lhs.revision) ==
         std::tie(rhs.table_key, rhs.place_promotions, rhs.revision);
}

}  // namespace eats_adverts_goods::models

namespace eats_adverts_goods::models {

TEST(Dishes, IsDumpable) {
  const Dishes dishes{
      TableKey{"testsuite"},  // table_key
      {
          {PlaceId{1}, {}},
          {PlaceId{2}, {CoreItemId{1}}},
          {PlaceId{3}, {CoreItemId{2}, CoreItemId{3}}},
      },    // place_promotions
      123,  // revision
  };

  dump::TestWriteReadCycle(dishes);
}

TEST(Products, IsDumpable) {
  const Products products{
      TableKey{"testsuite"},  // table_key
      {
          {PlaceId{1}, {}},
          {
              PlaceId{2},
              {
                  Product{
                      ProductId{"1"},     // product_id
                      {CategoryId{"2"}},  // suitable_categories
                      {CategoryId{"3"}},  // non_suitable_categories
                  },
              },
          },
          {
              PlaceId{3},
              {
                  Product{
                      ProductId{"1"},     // product_id
                      {CategoryId{"2"}},  // suitable_categories
                      {CategoryId{"3"}},  // non_suitable_categories
                  },
                  Product{
                      ProductId{"2"},     // product_id
                      {CategoryId{"3"}},  // suitable_categories
                      {CategoryId{"4"}},  // non_suitable_categories
                  },
              },
          },
      },    // place_promotions
      123,  // revision
  };

  dump::TestWriteReadCycle(products);
}

}  // namespace eats_adverts_goods::models
