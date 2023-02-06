#include <gtest/gtest.h>

#include "deeplink.hpp"

namespace eats_layout_constructor::deeplink {

TEST(Deeplink, MakeCollectionDeeplink) {
  const auto deeplink = MakeCollectionDeeplink("my_collection");
  ASSERT_EQ(deeplink.GetUnderlying(), "eda.yandex://collections/my_collection");
}

TEST(Deeplink, MakeGroceryDeeplink) {
  const auto deeplink = MakeGroceryDeeplink();
  ASSERT_EQ(deeplink.GetUnderlying(), "eda.yandex://lavka");
}

TEST(Deeplink, MakeShopDeeplink) {
  const auto deeplink = MakeShopDeeplink(sources::PlaceSlug{"my_shop"});
  ASSERT_EQ(deeplink.GetUnderlying(), "eda.yandex://shop/my_shop");
}

TEST(Deeplink, MakeRestaurantDeeplink) {
  const auto deeplink = MakeRestaurantDeeplink(sources::PlaceSlug{"my_rest"});
  ASSERT_EQ(deeplink.GetUnderlying(), "eda.yandex://restaurant/my_rest");
}

}  // namespace eats_layout_constructor::deeplink
