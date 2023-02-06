#include "fetch_discounts.hpp"

#include <random>

#include <gtest/gtest.h>

namespace {

std::vector<handlers::RegionConditions> GetRegions(
    const size_t regions_count, const size_t brands_in_region_count,
    const size_t places_in_brand_count) {
  std::vector<handlers::RegionConditions> regions;
  regions.reserve(regions_count);
  size_t region_id = 0;
  size_t brand_id = 0;
  size_t place_id = 0;
  while (regions.size() != regions_count) {
    handlers::RegionConditions region;
    region.id = region_id++;
    region.brands.reserve(brands_in_region_count);
    while (region.brands.size() != brands_in_region_count) {
      handlers::BrandConditions brand;
      brand.id = brand_id++;
      brand.places.reserve(places_in_brand_count);
      while (brand.places.size() != places_in_brand_count) {
        handlers::PlaceConditions place;
        place.id = place_id++;
        brand.places.push_back(place);
      }
      region.brands.push_back(brand);
    }
    regions.push_back(region);
  }
  return regions;
}

}  // namespace

TEST(FetchDiscounts, GetTasksCount) {
  EXPECT_EQ(utils::GetTasksCount(100, 10, 1000), 100);
  EXPECT_EQ(utils::GetTasksCount(10, 10, 1000), 10);
  EXPECT_EQ(utils::GetTasksCount(1, 10, 1000), 1);
  EXPECT_EQ(utils::GetTasksCount(100, 10, 100), 10);
  EXPECT_EQ(utils::GetTasksCount(10, 5000, 12345), 3);
  EXPECT_EQ(utils::GetTasksCount(10, 5000, 1), 1);
  EXPECT_EQ(utils::GetTasksCount(10, 50, 10), 1);
  EXPECT_EQ(utils::GetTasksCount(10, 10, 10), 1);
  EXPECT_EQ(utils::GetTasksCount(10, 11, 10), 1);
  EXPECT_EQ(utils::GetTasksCount(10, 9, 10), 2);
  EXPECT_EQ(utils::GetTasksCount(10, 1, 10), 10);
}

TEST(FetchDiscounts, GetPlacesInTask) {
  EXPECT_EQ(utils::GetPlacesInTask(1, 10), 10);
  EXPECT_EQ(utils::GetPlacesInTask(2, 10), 5);
  EXPECT_EQ(utils::GetPlacesInTask(3, 10), 4);
  EXPECT_EQ(utils::GetPlacesInTask(100, 1), 1);
  EXPECT_EQ(utils::GetPlacesInTask(100, 2), 1);
  EXPECT_EQ(utils::GetPlacesInTask(100, 99), 1);
  EXPECT_EQ(utils::GetPlacesInTask(100, 100), 1);
  EXPECT_EQ(utils::GetPlacesInTask(100, 101), 2);
  EXPECT_EQ(utils::GetPlacesInTask(100, 199), 2);
  EXPECT_EQ(utils::GetPlacesInTask(100, 200), 2);
  EXPECT_EQ(utils::GetPlacesInTask(100, 201), 3);
}

TEST(FetchDiscounts, GetTasksCursorsSingleTask) {
  const auto regions = GetRegions(2, 5, 3);
  const auto places_count = utils::GetPlacesCount(regions);
  const auto cursors = utils::GetTasksCursors(1, places_count, regions);
  EXPECT_EQ(cursors.size(), 1);
  const auto& cursor = cursors.front();
  EXPECT_EQ(cursor.region_offset->id, 0);
  EXPECT_EQ(cursor.brand_offset->id, 0);
  EXPECT_EQ(cursor.place_offset->id, 0);
  EXPECT_EQ(cursor.limit, places_count);
}

TEST(FetchDiscounts, GetTasksCursors) {
  std::random_device dev;
  std::mt19937 gen{dev()};
  [[maybe_unused]] std::uniform_int_distribution<> distrib{1, 10};
  const size_t regions_count = distrib(gen);
  const size_t brands_in_region_count = distrib(gen);
  const size_t places_in_brand_count = distrib(gen);
  const size_t tasks_count = distrib(gen);
  const auto regions =
      GetRegions(regions_count, brands_in_region_count, places_in_brand_count);
  const auto places_count = utils::GetPlacesCount(regions);
  const auto cursors =
      utils::GetTasksCursors(tasks_count, places_count, regions);
  ASSERT_FALSE(cursors.empty());
  ASSERT_LE(cursors.size(), tasks_count) << fmt::format(
      "regions {}, brands {}, places {}, tasks {}", regions_count,
      brands_in_region_count, places_in_brand_count, tasks_count);
  const auto places_in_task = utils::GetPlacesInTask(tasks_count, places_count);
  size_t places_in_task_counter = 0;
  size_t cursor_idx = 0;
  size_t places_counter = 0;
  for (const auto& region : regions) {
    for (const auto& brand : region.brands) {
      for (const auto& place : brand.places) {
        if (places_in_task_counter == 0) {
          auto error_message = fmt::format(
              "regions {}, brands {}, places {}, tasks {}, cursor_idx {}",
              regions_count, brands_in_region_count, places_in_brand_count,
              tasks_count, cursor_idx);
          places_in_task_counter = places_in_task;
          const auto& cursor = cursors[cursor_idx];
          ASSERT_EQ(cursor.region_offset->id, region.id) << error_message;
          ASSERT_EQ(cursor.brand_offset->id, brand.id) << error_message;
          ASSERT_EQ(cursor.place_offset->id, place.id) << error_message;
          places_counter += cursor.limit;
          if (++cursor_idx != cursors.size()) {
            ASSERT_EQ(cursor.limit, places_in_task);
          } else {
            EXPECT_LE(cursor.limit, places_in_task);
            EXPECT_EQ(places_counter, places_count);
          }
        }
        --places_in_task_counter;
      }
    }
  }
}
