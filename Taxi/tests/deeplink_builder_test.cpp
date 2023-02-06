#include <gtest/gtest.h>

#include <eats-deeplink/deeplink_builder.hpp>

namespace eats_deeplink {

TEST(Builder, Collection) {
  const auto result = DeeplinkBuilder().Collection("my_collection").Build();
  ASSERT_EQ(result, "eda.yandex://collections/my_collection");
}

TEST(Builder, CollectionWeb) {
  const auto result = WebLinkBuilder().Collection("my_collection").Build();
  ASSERT_EQ(result, "https://eda.yandex.ru/collections/my_collection");
}

TEST(Builder, Restaurant) {
  const auto result = DeeplinkBuilder().Restaurant("my_rest").Build();
  ASSERT_EQ(result, "eda.yandex://restaurant/my_rest");
}

TEST(Builder, Shop) {
  const auto result = DeeplinkBuilder().Shop("my_shop").Build();
  ASSERT_EQ(result, "eda.yandex://shop/my_shop");
}

TEST(Builder, RestaurantWeb) {
  const auto result = WebLinkBuilder().Restaurant("my_rest").Build();
  ASSERT_EQ(result, "https://eda.yandex.ru/restaurant/my_rest");
}

TEST(Builder, ShopWeb) {
  const auto result = WebLinkBuilder().Shop("my_shop").Build();
  ASSERT_EQ(result, "https://eda.yandex.ru/shop/my_shop");
}

TEST(Builder, ShopCategory) {
  const auto result =
      DeeplinkBuilder().Shop("my_shop").Category("my_category").Build();
  ASSERT_EQ(result, "eda.yandex://shop/my_shop?category=my_category");
}

TEST(Builder, Grocery) {
  const auto result = DeeplinkBuilder().Grocery().Build();
  ASSERT_EQ(result, "eda.yandex://lavka");
}

TEST(Builder, GroceryCategory) {
  const auto result =
      DeeplinkBuilder().Grocery().Category("lavka_category").Build();
  ASSERT_EQ(result, "eda.yandex://lavka?link=?category=lavka_category");
}

}  // namespace eats_deeplink
