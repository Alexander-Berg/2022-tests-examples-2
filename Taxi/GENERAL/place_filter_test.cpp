#include <gtest/gtest.h>

#include "place_filter.hpp"

TEST(PlacesFilter, EmptySettings) {
  auto settings = formats::json::Value();
  auto filter =
      settings.As<eats_layout_constructor::utils::filters::PlaceFilter>();
  auto place = eats_layout_constructor::sources::catalog::Place();
  ASSERT_TRUE(filter.Filter(place));
}

TEST(PlacesFilter, Filter) {
  auto settings = formats::json::FromString(R"=(
{
  "place_ids": [1, 3],
  "brand_ids": [3, 4]
})=");
  auto filter =
      settings.As<eats_layout_constructor::utils::filters::PlaceFilter>();
  auto place = eats_layout_constructor::sources::catalog::Place();
  place.meta.place_id = eats_layout_constructor::sources::PlaceId(1);
  ASSERT_FALSE(filter.Filter(place));
  place.meta.place_id = eats_layout_constructor::sources::PlaceId(2);
  place.meta.brand_id = eats_layout_constructor::sources::BrandId(3);
  ASSERT_FALSE(filter.Filter(place));
  place.meta.brand_id = eats_layout_constructor::sources::BrandId(2);
  ASSERT_TRUE(filter.Filter(place));
}
