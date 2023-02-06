#include <gtest/gtest.h>

#include "banners_carousel.hpp"

namespace handlers::eats_communications_v1_layout_banners::post::blocks {

namespace banners_carousel {

namespace {

namespace models = eats_communications::models;

const std::string kExp = "exp";

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
  result.wide_and_short.push_back(MakeImage());
  result.shortcuts.push_back(MakeImage());
  return result;
}

models::Banner MakeBanner(const int id, const models::BannerWidth width =
                                            models::BannerWidth::kSingle) {
  models::Banner result{};

  result.id = models::BannerId{id};
  result.url = models::BannerUrl(fmt::format("url_{}", id));
  result.app_url = models::BannerAppUrl(fmt::format("app_url_{}", id));

  auto images = MakeImages();
  result.images = std::move(images.images);
  result.wide_and_short = std::move(images.wide_and_short);
  result.shortcuts = std::move(images.shortcuts);

  auto& meta_info = result.meta_info.emplace();
  meta_info.width = width;
  meta_info.experiment = kExp;

  return result;
}

BannersCarousel MakeCarousel() {
  static const std::string kBlockId{"block_id"};
  static const auto kBlockType{BlockType::kBannersCarousel};
  const std::unordered_set<std::string> kExps{kExp};

  return BannersCarousel{kBlockId, kBlockType, kExps};
}

struct BannerAssertion {
  std::string id;
  BannersCarouselItemWidth width;
  std::optional<std::string> image_url{std::nullopt};
};

using PageAssertions = std::vector<std::vector<BannerAssertion>>;

void Assert(const BannersCarouselPayload& payload,
            const PageAssertions& assertion) {
  ASSERT_EQ(payload.pages.size(), assertion.size());
  for (size_t i = 0; i < assertion.size(); i++) {
    const auto& page = payload.pages[i];
    const auto& page_assertion = assertion[i];
    ASSERT_EQ(page.banners.size(), page_assertion.size());

    for (size_t j = 0; j < page_assertion.size(); j++) {
      const auto& banner = page.banners[j];
      const auto& banner_assertion = page_assertion[j];
      ASSERT_EQ(banner.id, banner_assertion.id);
      ASSERT_EQ(banner.width, banner_assertion.width);
      ASSERT_FALSE(banner.images.empty());
      if (banner_assertion.image_url.has_value()) {
        ASSERT_EQ(banner.images.front().url, banner_assertion.image_url);
      }
    }
  }
}

}  // namespace

TEST(BannersCarousel, IsMatch) {
  // Проверяем, что IsMatch возвращает true
  // только на те баннера, которые пришли
  // с экспериментами из конструктора

  const std::string kMatchExp{"exp1"};
  const std::string kDoNotMatchExp{"exp2"};

  const std::unordered_set<std::string> kExps{kMatchExp};
  BannersCarousel carousel{"block_id", BlockType::kBannersCarousel, kExps};
  auto banner = MakeBanner(1);

  banner.meta_info.value().experiment = kDoNotMatchExp;
  ASSERT_FALSE(carousel.Add(banner));

  banner.meta_info.value().experiment = kMatchExp;
  ASSERT_TRUE(carousel.Add(banner));
}

TEST(BannersCarousel, AddDouble) {
  // Проверяем
  // Если приходит одинарный баннер, потом двойной
  // потом еще 4 одинарных
  // Все баннеры должны быть отрисованы одинарными
  // суммурно будет 2 страницы

  const std::string kBlockId{"block_id"};
  const auto kBlockType{BlockType::kBannersCarousel};
  const std::unordered_set<std::string> kExps{kExp};

  BannersCarousel carousel{kBlockId, kBlockType, kExps};
  carousel.Add(MakeBanner(1, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(2, models::BannerWidth::kDouble));
  carousel.Add(MakeBanner(3, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(4, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(5, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(6, models::BannerWidth::kSingle));

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().block_id, kBlockId);
  ASSERT_EQ(result.value().type, kBlockType);

  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {{
                                  {"1", BannersCarouselItemWidth::kSingle},
                                  {"2", BannersCarouselItemWidth::kSingle},
                                  {"3", BannersCarouselItemWidth::kSingle},
                              },
                              {
                                  {"4", BannersCarouselItemWidth::kSingle},
                                  {"5", BannersCarouselItemWidth::kSingle},
                                  {"6", BannersCarouselItemWidth::kSingle},
                              }};
  Assert(payload, assertion);
}

TEST(BannersCarousel, AddTriple) {
  // Проверяем, что если приходит
  // несколько одинарных баннеров,
  // а потом тройной, тройной
  // он нарисуется как одинарный

  auto carousel = MakeCarousel();
  carousel.Add(MakeBanner(1, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(2, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(3, models::BannerWidth::kTriple));

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {{
      {"1", BannersCarouselItemWidth::kSingle},
      {"2", BannersCarouselItemWidth::kSingle},
      {"3", BannersCarouselItemWidth::kSingle},
  }};
  Assert(payload, assertion);
}

TEST(BannersCarousel, AddInvalid) {
  // Проверяем, что Add не падает,
  // если передать в него невалидный баннер

  auto carousel = MakeCarousel();
  auto banner = MakeBanner(1);
  banner.app_url.GetUnderlying() = std::nullopt;

  carousel.Add(banner);

  auto result = carousel.Serialize();
  ASSERT_FALSE(result.has_value());
}

TEST(BannersCarousel, AddOnlyTriple) {
  // Проверяем, что если пришло несколько
  // тройных, в выдаче будет только один как тройной,
  // а все остальные будут нарисованы одинарнымии
  auto carousel = MakeCarousel();
  carousel.Add(MakeBanner(1, models::BannerWidth::kTriple));
  carousel.Add(MakeBanner(2, models::BannerWidth::kTriple));
  carousel.Add(MakeBanner(3, models::BannerWidth::kTriple));
  carousel.Add(MakeBanner(4, models::BannerWidth::kTriple));

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {
      {
          {"1", BannersCarouselItemWidth::kTriple},
      },
      {
          {"2", BannersCarouselItemWidth::kSingle},
          {"3", BannersCarouselItemWidth::kSingle},
          {"4", BannersCarouselItemWidth::kSingle},
      },
  };
  Assert(payload, assertion);
}

TEST(BannersCarousel, SingleResize) {
  // Проверяем, что если пришел
  // 1 баннер шириной 1,
  // он будет отрисован с шириной 3

  static const std::string kTripleImageUrl{"triple.image.url"};
  static const std::string kSingleImageUrl{"single.image.url"};

  auto banner = MakeBanner(1, models::BannerWidth::kSingle);
  banner.images.begin()->url = kTripleImageUrl;
  banner.shortcuts.begin()->url = kSingleImageUrl;

  auto carousel = MakeCarousel();
  carousel.Add(banner);

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {
      {
          {"1", BannersCarouselItemWidth::kTriple, kTripleImageUrl},
      },
  };
  Assert(payload, assertion);
}

TEST(BannersCarousel, TwoSingleResize) {
  // Проверяем, что если пришло
  // 2 баннера шириной 1,
  // они будут отрисованы как 2 + 1

  static const std::string kTripleImageUrl{"triple.image.url"};
  static const std::string kDoubleImageUrl{"double.image.url"};
  static const std::string kSingleImageUrl{"single.image.url"};

  auto one_banner = MakeBanner(1, models::BannerWidth::kSingle);
  one_banner.images.begin()->url = kTripleImageUrl;
  one_banner.wide_and_short.begin()->url = kDoubleImageUrl;
  one_banner.shortcuts.begin()->url = kSingleImageUrl;

  auto two_banner = MakeBanner(2, models::BannerWidth::kSingle);
  two_banner.images.begin()->url = kTripleImageUrl;
  two_banner.wide_and_short.begin()->url = kDoubleImageUrl;
  two_banner.shortcuts.begin()->url = kSingleImageUrl;

  auto carousel = MakeCarousel();
  carousel.Add(one_banner);
  carousel.Add(two_banner);

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {
      {
          {"1", BannersCarouselItemWidth::kDouble, kDoubleImageUrl},
          {"2", BannersCarouselItemWidth::kSingle, kSingleImageUrl},
      },
  };
  Assert(payload, assertion);
}

TEST(BannersCarousel, AddOnlySinle) {
  // Проверяем, что если пришло несколько
  // одинарных, в выдаче будут все из них
  auto carousel = MakeCarousel();
  carousel.Add(MakeBanner(1, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(2, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(3, models::BannerWidth::kSingle));
  carousel.Add(MakeBanner(4, models::BannerWidth::kSingle));

  auto result = carousel.Serialize();
  ASSERT_TRUE(result.has_value());
  const auto& payload = result.value().payload.As<BannersCarouselPayload>();

  PageAssertions assertion = {{
                                  {"1", BannersCarouselItemWidth::kSingle},
                                  {"2", BannersCarouselItemWidth::kSingle},
                                  {"3", BannersCarouselItemWidth::kSingle},
                              },
                              {
                                  {"4", BannersCarouselItemWidth::kTriple},
                              }};
  Assert(payload, assertion);
}

}  // namespace banners_carousel

}  // namespace handlers::eats_communications_v1_layout_banners::post::blocks
