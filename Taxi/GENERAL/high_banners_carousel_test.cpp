#include <gtest/gtest.h>

#include "high_banners_carousel.hpp"

namespace handlers::eats_communications_v1_layout_banners::post::blocks {

namespace high_banners_carousel {

namespace {

namespace models = eats_communications::models;

const std::string kExp = "exp";
const std::string kBlockId = "block_id";
constexpr BlockType kBlockType = BlockType::kHighBannersCarousel;

struct Images {
  std::vector<models::BannerImage> images{};
  std::vector<models::BannerImage> shortcuts{};
  std::vector<models::BannerImage> wide_and_short{};
};

models::BannerImage MakeImage() {
  models::BannerImage result{};
  result.platform = "mobile";
  result.theme = "light";
  result.url = "image.url";
  return result;
}

Images MakeImages() {
  Images result;
  result.images.push_back(MakeImage());
  return result;
}

models::Banner MakeBanner(const int id) {
  models::Banner result{};

  result.id = models::BannerId{id};
  result.url = models::BannerUrl(fmt::format("url_{}", id));
  result.app_url = models::BannerAppUrl(fmt::format("app_url_{}", id));

  auto images = MakeImages();
  result.images = std::move(images.images);

  auto& meta_info = result.meta_info.emplace();
  meta_info.experiment = kExp;

  return result;
}

HighBannersCarousel MakeCarousel() {
  return HighBannersCarousel{kBlockId, kBlockType, {kExp}};
}

}  // namespace

TEST(HighBannersCarousel, IsMatch) {
  // Проверяем, что IsMatch возвращает true
  // только на те баннера, которые пришли
  // с экспериментами из конструктора

  static const std::string kMatchExp = "exp1";
  static const std::string kDoNotMatchExp = "exp2";

  HighBannersCarousel carousel{kBlockId, kBlockType, {kMatchExp}};
  auto banner = MakeBanner(1);

  banner.meta_info.value().experiment = kDoNotMatchExp;
  ASSERT_FALSE(carousel.Add(banner));

  banner.meta_info.value().experiment = kMatchExp;
  ASSERT_TRUE(carousel.Add(banner));
}

TEST(HighBannersCarousel, AddBanners) {
  // Проверяем, что баннеры корректно добавляются

  auto carousel = MakeCarousel();
  carousel.Add(MakeBanner(1));
  carousel.Add(MakeBanner(2));
  carousel.Add(MakeBanner(3));
  carousel.Add(MakeBanner(4));

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());

  const auto& payload = result.value().payload.As<HighBannersCarouselPayload>();
  ASSERT_EQ(payload.banners.size(), 4);
}

TEST(HighBannersCarousel, AddInvalid) {
  // Проверяем, что Add не падает,
  // если передать в него невалидный баннер

  auto banner = MakeBanner(1);
  banner.url.GetUnderlying() = std::nullopt;
  auto carousel = MakeCarousel();
  carousel.Add(banner);

  const auto result = carousel.Serialize();
  ASSERT_FALSE(result.has_value());
}

}  // namespace high_banners_carousel

}  // namespace handlers::eats_communications_v1_layout_banners::post::blocks
