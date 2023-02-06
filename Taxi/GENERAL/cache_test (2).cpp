#include <eats-restapp-marketing-cache/models/cache.hpp>

#include <optional>
#include <unordered_map>

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace eats_restapp_marketing_cache::models {

bool operator==(const PlacesBanners& lhs, const PlacesBanners& rhs) {
  return lhs.banners_by_places_ == rhs.banners_by_places_;
}

}  // namespace eats_restapp_marketing_cache::models

namespace eats_restapp_marketing_cache::models {

TEST(PlacesBanners, IsDumpable) {
  std::unordered_map<PlaceId, std::vector<AdvertBanner>> banners_by_places{
      {PlaceId{1}, {{BannerId{1}, AdvertType::kCPC, std::nullopt}}},
      {PlaceId{2},
       {{BannerId{2}, AdvertType::kCPC, std::nullopt},
        {BannerId{22}, AdvertType::kCPA, std::nullopt}}},
      {PlaceId{3},
       {{BannerId{3}, AdvertType::kCPC, std::nullopt},
        {BannerId{33}, AdvertType::kCPC, std::make_optional("foo_exp_name")}}},
  };

  const PlacesBanners places_banners(std::move(banners_by_places));

  dump::TestWriteReadCycle(places_banners);
}

}  // namespace eats_restapp_marketing_cache::models
