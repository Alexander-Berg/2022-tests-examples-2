#include "utils.hpp"

#include <gtest/gtest.h>

namespace eats_catalog_storage::utils {

namespace {

void AssertEqual(const std::unordered_set<int64_t>& expected,
                 const std::unordered_set<int64_t>& actual) {
  ASSERT_EQ(expected.size(), actual.size()) << " size of sets does not match";

  for (const auto& expected_item : expected) {
    if (actual.count(expected_item) == 0) {
      FAIL() << "missing value: " << expected_item;
    }
  }
}

void AssertContainsOnly(
    const std::vector<int64_t>& expected,
    const std::unordered_map<int64_t, std::vector<int64_t>>& actual) {
  ASSERT_EQ(expected.size(), actual.size()) << " size of sets does not match";

  for (const auto& expected_item : expected) {
    if (actual.count(expected_item) == 0) {
      FAIL() << "missing value: " << expected_item;
    }
  }
}

std::unordered_map<int64_t, std::vector<int64_t>> MakeMapWithKeys(
    const std::vector<int64_t> keys) {
  std::unordered_map<int64_t, std::vector<int64_t>> result;
  result.reserve(keys.size());

  for (const auto key : keys) {
    result[key];
  }

  return result;
}

}  // namespace

TEST(Intersect, Simple) {
  std::unordered_set<int64_t> result{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  std::unordered_set<int64_t> set{2, 4, 6, 8, 16, 32, 64, 128, 256, 512};

  Intersect(result, std::move(set));

  AssertEqual({2, 4, 6, 8}, result);
}

TEST(Intersect, ResultEmpty) {
  std::unordered_set<int64_t> result{};
  std::unordered_set<int64_t> set{2, 4, 6, 8, 16, 32, 64, 128, 256, 512};

  Intersect(result, std::move(set));

  AssertEqual({}, result);
}

TEST(Intersect, SetEmpty) {
  std::unordered_set<int64_t> result{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  std::unordered_set<int64_t> set{};

  Intersect(result, std::move(set));

  AssertEqual({}, result);
}

TEST(Intersect, NoItersection) {
  std::unordered_set<int64_t> result{0, 2, 4, 6, 8};
  std::unordered_set<int64_t> set{1, 3, 5, 7, 9};

  Intersect(result, std::move(set));

  AssertEqual({}, result);
}

TEST(IntersectOrSet, Simple) {
  std::unordered_set<int64_t> result{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  std::unordered_set<int64_t> set{2, 4, 6, 8, 16, 32, 64, 128, 256, 512};

  const bool has_intersections = IntersectOrSet(result, std::move(set));
  ASSERT_TRUE(has_intersections);

  AssertEqual({2, 4, 6, 8}, result);
}

TEST(IntersectOrSet, ResultEmpty) {
  std::unordered_set<int64_t> result{};
  std::unordered_set<int64_t> set{2, 4, 6, 8, 16, 32, 64, 128, 256, 512};

  const bool has_intersections = IntersectOrSet(result, std::move(set));
  ASSERT_TRUE(has_intersections);

  AssertEqual({2, 4, 6, 8, 16, 32, 64, 128, 256, 512}, result);
}

TEST(IntersectOrSet, SetEmpty) {
  std::unordered_set<int64_t> result{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  std::unordered_set<int64_t> set{};

  const bool has_intersections = IntersectOrSet(result, std::move(set));
  ASSERT_FALSE(has_intersections);

  AssertEqual({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, result);
}

TEST(IntersectOrSet, NoItersection) {
  std::unordered_set<int64_t> result{0, 2, 4, 6, 8};
  std::unordered_set<int64_t> set{1, 3, 5, 7, 9};

  const bool has_intersections = IntersectOrSet(result, std::move(set));
  ASSERT_FALSE(has_intersections);

  AssertEqual({}, result);
}

TEST(FilterPlaces, Simple) {
  std::unordered_set<int64_t> place_ids{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  auto place_id_zone_ids =
      MakeMapWithKeys({2, 4, 6, 8, 16, 32, 64, 128, 256, 512});

  FilterPlaces(place_ids, place_id_zone_ids);

  AssertContainsOnly({2, 4, 6, 8}, place_id_zone_ids);
}

TEST(FilterPlaces, EmptyPlaceIds) {
  std::unordered_set<int64_t> place_ids{};
  auto place_id_zone_ids =
      MakeMapWithKeys({2, 4, 6, 8, 16, 32, 64, 128, 256, 512});

  FilterPlaces(place_ids, place_id_zone_ids);

  AssertContainsOnly({}, place_id_zone_ids);
}

TEST(FilterPlaces, EmptyMap) {
  std::unordered_set<int64_t> place_ids{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  auto place_id_zone_ids = MakeMapWithKeys({});

  FilterPlaces(place_ids, place_id_zone_ids);

  AssertContainsOnly({}, place_id_zone_ids);
}

TEST(FilterPlaces, NoItersection) {
  std::unordered_set<int64_t> place_ids{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
  auto place_id_zone_ids =
      MakeMapWithKeys({-1, -2, -3, -4, -5, -6, -7, -8, -9});

  FilterPlaces(place_ids, place_id_zone_ids);

  AssertContainsOnly({}, place_id_zone_ids);
}

}  // namespace eats_catalog_storage::utils
