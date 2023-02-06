#include <eats-places/utils/dedup/places.hpp>

#include <gtest/gtest.h>

namespace eats_places::utils::dedup {

namespace {

using eats_places::models::BrandId;
using eats_places::models::Place;
using eats_places::models::PlaceId;
using eats_places::models::PlaceInfo;

std::vector<const Place*> CreatePointers(const std::vector<Place>& places) {
  std::vector<const Place*> ptrs{};
  ptrs.reserve(places.size());

  for (const auto& place : places) {
    ptrs.push_back(&place);
  }

  return ptrs;
}

}  // namespace

TEST(DeduplicatePlacesSorted, Simple) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(5);
  std::vector<Place> places{};
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(1);
    place_info.brand.id = BrandId(1);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(2);
    place_info.brand.id = BrandId(1);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(8);
    place_info.brand.id = BrandId(4);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(16);
    place_info.brand.id = BrandId(7);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(3);
    place_info.brand.id = BrandId(1);
    places.emplace_back(place_info);
  }

  auto ptrs = CreatePointers(places);
  PlacesSorted(ptrs);

  ASSERT_EQ(3, ptrs.size())
      << "unexpected number of places after deduplication";

  std::vector<int64_t> expected_order{1, 8, 16};
  for (size_t i = 0; i < expected_order.size(); i++) {
    EXPECT_EQ(expected_order[i], ptrs[i]->id) << "unexpected place at " << i;
  }
}

TEST(DeduplicatePlacesSorted, AllUnique) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(5);
  std::vector<Place> places{};
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(1);
    place_info.brand.id = BrandId(1);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(2);
    place_info.brand.id = BrandId(2);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(8);
    place_info.brand.id = BrandId(3);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(16);
    place_info.brand.id = BrandId(4);
    places.emplace_back(place_info);
  }
  {
    auto& place_info = place_infos.emplace_back();
    place_info.id = PlaceId(3);
    place_info.brand.id = BrandId(5);
    places.emplace_back(place_info);
  }

  auto ptrs = CreatePointers(places);
  PlacesSorted(ptrs);

  ASSERT_EQ(5, ptrs.size())
      << "unexpected number of places after deduplication";

  std::vector<int64_t> expected_order{1, 2, 8, 16, 3};
  for (size_t i = 0; i < expected_order.size(); i++) {
    EXPECT_EQ(expected_order[i], ptrs[i]->id) << "unexpected place at " << i;
  }
}

TEST(DeduplicatePlacesSorted, Empty) {
  std::vector<const Place*> ptrs{};

  ASSERT_NO_THROW(PlacesSorted(ptrs));

  ASSERT_EQ(0, ptrs.size())
      << "unexpected number of places after deduplication";
}

}  // namespace eats_places::utils::dedup
