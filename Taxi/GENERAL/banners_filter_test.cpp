#include <gtest/gtest.h>

#include "banners_filter.hpp"

TEST(BannersFilter, EmptySettings) {
  auto settings = formats::json::Value();
  auto filter =
      settings.As<eats_layout_constructor::utils::filters::BannersFilter>();
  auto banner = eats_layout_constructor::sources::banners::Banner();
  ASSERT_TRUE(filter.Filter(banner));
}

TEST(BannersFilter, Filter) {
  auto settings = formats::json::FromString(R"=(
{
  "place_ids": [1, 3],
  "brand_ids": [3, 4],
  "banner_ids": [2, 5]
})=");
  auto filter =
      settings.As<eats_layout_constructor::utils::filters::BannersFilter>();
  auto banner = eats_layout_constructor::sources::banners::Banner();
  banner.meta.place_id = eats_layout_constructor::sources::PlaceId(1);
  ASSERT_FALSE(filter.Filter(banner));
  banner.meta.place_id = eats_layout_constructor::sources::PlaceId(2);
  banner.meta.brand_id = eats_layout_constructor::sources::BrandId(3);
  ASSERT_FALSE(filter.Filter(banner));
  banner.meta.brand_id = eats_layout_constructor::sources::BrandId(2);
  banner.meta.banner_id = eats_layout_constructor::sources::BannerId(5);
  ASSERT_FALSE(filter.Filter(banner));
  banner.meta.banner_id = eats_layout_constructor::sources::BannerId(3);
  ASSERT_TRUE(filter.Filter(banner));
}
