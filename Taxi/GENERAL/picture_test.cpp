#include <gtest/gtest.h>

#include <eats-full-text-search-models/picture.hpp>
#include "userver/formats/json/value_builder.hpp"

TEST(PictureModel, Serialization) {
  eats_full_text_search_models::PictureModel picture{};
  picture.url = "http://avatars.mds.yandex.net/my/picture";
  picture.scale = eats_full_text_search_models::PictureScale::kAspectFit;

  auto value = formats::json::ValueBuilder{picture}.ExtractValue();
  auto restored_picture =
      value.As<eats_full_text_search_models::PictureModel>();

  ASSERT_EQ(picture.url, restored_picture.url);
  ASSERT_EQ(picture.scale, restored_picture.scale);
}

TEST(PictureModel, OptionalScale) {
  eats_full_text_search_models::PictureModel picture{};
  picture.url = "http://avatars.mds.yandex.net/my/picture";

  auto value = formats::json::ValueBuilder{picture}.ExtractValue();
  auto restored_picture =
      value.As<eats_full_text_search_models::PictureModel>();

  ASSERT_EQ(picture.url, restored_picture.url);
  ASSERT_EQ(picture.scale, restored_picture.scale);
  ASSERT_FALSE(picture.scale.has_value());
  ASSERT_FALSE(restored_picture.scale.has_value());
}
