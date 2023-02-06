#include <gtest/gtest.h>

#include <models/item_stock.hpp>
#include <models/place_menu_category.hpp>

#include <schedule/schedule.hpp>

#include <status/item_status_checker.hpp>

#include <utils/time/time.hpp>

namespace eats_rest_menu_storage::status {

erms_models::PlaceMenuCategory InitPlaceMenuCategory() {
  const erms_models::PlaceMenuCategory category = {
      erms_models::PlaceMenuCategoryId{1},  // id
      erms_models::Uuid{1},                 // brand_menu_category_id
      erms_models::CategoryOriginId{1},     // origin_id
      "",                                   // name
      {},                                   // sort
      {},                                   // legacy_id
      {},                                   // schedule
      std::nullopt,                         // deleted_at
      std::nullopt,                         // updated_at
      false,                                // is_synced_schedule
  };
  return category;
}

erms_models::CategoryStatus InitCategoryStatus() {
  const erms_models::CategoryStatus category_status = {
      erms_models::PlaceMenuCategoryId{1},  // category_id
      true,                                 // available
      {},                                   // deactivated_at
      {},                                   // reactivate_at
      std::nullopt,                         // deleted
      {}                                    // updated_at
  };
  return category_status;
}

TEST(CheckStatus, IsCategoryAvailableWithoutSchedule) {
  //Проверяем пока без расписания
  erms_models::PlaceMenuCategory place_menu_category = InitPlaceMenuCategory();
  erms_models::CategoryStatus category_status = InitCategoryStatus();

  auto time_point =
      ::utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000");

  ASSERT_TRUE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  // deleted статус не учитывается при подсчете доступности
  category_status.deleted_at = utils::time::ToTimePointTz(time_point);

  ASSERT_TRUE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  category_status.available = false;

  ASSERT_TRUE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  category_status.deleted_at = std::nullopt;
  ASSERT_FALSE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));
}

TEST(CheckStatus, IsCategoryAvailableWithSchedule_UTC) {
  erms_models::PlaceMenuCategory place_menu_category = InitPlaceMenuCategory();
  erms_models::CategoryStatus category_status = InitCategoryStatus();

  auto schedule_json = formats::json::FromString(R"(
  [
    {
    "day": 5,
    "from": 360,
    "to": 600
  }
  ]
  )");

  auto time_point =
      ::utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000");

  category_status.available = true;

  place_menu_category.schedule = std::make_optional<schedule::Schedule>(
      Parse(schedule_json, ::formats::parse::To<schedule::Schedule>()));

  ASSERT_FALSE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  time_point =
      ::utils::datetime::Stringtime("2021-11-19T06:00:01.854565956+0000");

  ASSERT_TRUE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  time_point =
      ::utils::datetime::Stringtime("2021-11-19T10:00:01.854565956+0000");

  ASSERT_FALSE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));

  time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.854565956+0000");

  ASSERT_FALSE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));
}

TEST(CheckStatus, IsCategoryAvailableWithSyncedSchedule) {
  erms_models::PlaceMenuCategory place_menu_category = InitPlaceMenuCategory();
  erms_models::CategoryStatus category_status = InitCategoryStatus();

  auto schedule_json = formats::json::FromString(R"(
  [
    {
    "day": 5,
    "from": 360,
    "to": 600
  }
  ]
  )");

  auto time_point =
      ::utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000");

  category_status.available = true;
  place_menu_category.is_synced_schedule = true;

  place_menu_category.schedule = std::make_optional<schedule::Schedule>(
      Parse(schedule_json, ::formats::parse::To<schedule::Schedule>()));

  ASSERT_TRUE(
      IsCategoryAvailable(category_status, place_menu_category, time_point));
}

TEST(IsItemAvailable, EmptyStock) {
  erms_models::ItemStock item_stock{
      erms_models::PlaceMenuItemId{1},  // id
      std::nullopt,                     // stock
      std::nullopt,                     // deleted_at
  };
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  ASSERT_FALSE(IsItemAvailable(std::nullopt, item_stock, true, time_point));
}

TEST(IsItemAvailable, ZeroStock) {
  erms_models::ItemStock item_stock{
      erms_models::PlaceMenuItemId{1},  // id
      erms_models::Stock{0},            // stock
      std::nullopt,                     // deleted_at
  };
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  ASSERT_FALSE(IsItemAvailable(std::nullopt, item_stock, true, time_point));
}

TEST(IsItemAvailable, ZeroButDeletedStock) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  erms_models::ItemStock item_stock{
      erms_models::PlaceMenuItemId{1},         // id
      erms_models::Stock{0},                   // stock
      utils::time::ToTimePointTz(time_point),  // deleted_at
  };

  ASSERT_TRUE(IsItemAvailable(std::nullopt, item_stock, true, time_point));
}

TEST(IsItemAvailable, DeletedStatus) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  erms_models::ItemStatus item_status{
      erms_models::PlaceMenuItemId{1},         // id
      false,                                   // available
      std::nullopt,                            // deactivated_at
      std::nullopt,                            // reactivate_at
      utils::time::ToTimePointTz(time_point),  // deleted_at
      std::nullopt                             // updated_at
  };

  ASSERT_TRUE(IsItemAvailable(item_status, std::nullopt, true, time_point));
}

TEST(IsItemAvailable, NullReactivate) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  erms_models::ItemStatus item_status{
      erms_models::PlaceMenuItemId{1},  // id
      false,                            // available
      std::nullopt,                     // deactivated_at
      std::nullopt,                     // reactivate_at
      std::nullopt,                     // deleted_at
      std::nullopt                      // updated_at
  };

  ASSERT_FALSE(IsItemAvailable(item_status, std::nullopt, true, time_point));
}

TEST(IsItemAvailable, ReactivateInPaste) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  auto reactivate_at =
      utils::time::ToTimePointTz(time_point - std::chrono::minutes{10});

  erms_models::ItemStatus item_status{
      erms_models::PlaceMenuItemId{1},  // id
      false,                            // available
      std::nullopt,                     // deactivated_at
      reactivate_at,                    // reactivate_at
      std::nullopt,                     // deleted_at
      std::nullopt                      // updated_at
  };

  ASSERT_TRUE(IsItemAvailable(item_status, std::nullopt, true, time_point));
}

TEST(IsItemAvailable, ReactivateInFuture) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  auto reactivate_at =
      utils::time::ToTimePointTz(time_point + std::chrono::minutes{10});

  erms_models::ItemStatus item_status{
      erms_models::PlaceMenuItemId{1},  // id
      false,                            // available
      std::nullopt,                     // deactivated_at
      reactivate_at,                    // reactivate_at
      std::nullopt,                     // deleted_at
      std::nullopt                      // updated_at
  };

  ASSERT_FALSE(IsItemAvailable(item_status, std::nullopt, true, time_point));
}

TEST(IsItemAvailable, ByCategoryAvailability) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  ASSERT_TRUE(IsItemAvailable(std::nullopt, std::nullopt, true, time_point));
  ASSERT_FALSE(IsItemAvailable(std::nullopt, std::nullopt, false, time_point));
}

TEST(IsOptionAvailable, DeletedStatus) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  erms_models::OptionStatus option_status{
      erms_models::PlaceItemOptionId{1},       // id
      false,                                   // available
      std::nullopt,                            // deactivated_at
      std::nullopt,                            // reactivate_at
      utils::time::ToTimePointTz(time_point),  // deleted
      std::nullopt                             // updated_at
  };

  ASSERT_TRUE(IsOptionAvailable(option_status, time_point));
}

TEST(IsOptionAvailable, NullReactivate) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  erms_models::OptionStatus option_status{
      erms_models::PlaceItemOptionId{1},  // id
      false,                              // available
      std::nullopt,                       // deactivated_at
      std::nullopt,                       // reactivate_at
      std::nullopt,                       // deleted
      std::nullopt                        // updated_at
  };

  ASSERT_FALSE(IsOptionAvailable(option_status, time_point));
}

TEST(IsOptionAvailable, ReactivateInPaste) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  auto reactivate_at =
      utils::time::ToTimePointTz(time_point - std::chrono::minutes{10});

  erms_models::OptionStatus option_status{
      erms_models::PlaceItemOptionId{1},  // id
      false,                              // available
      std::nullopt,                       // deactivated_at
      reactivate_at,                      // reactivate_at
      std::nullopt,                       // deleted
      std::nullopt                        // updated_at
  };

  ASSERT_TRUE(IsOptionAvailable(option_status, time_point));
}

TEST(IsOptionAvailable, ReactivateInFuture) {
  auto time_point =
      ::utils::datetime::Stringtime("2021-11-18T09:00:01.00+0000");

  auto reactivate_at =
      utils::time::ToTimePointTz(time_point + std::chrono::minutes{10});

  erms_models::OptionStatus option_status{
      erms_models::PlaceItemOptionId{1},  // id
      false,                              // available
      std::nullopt,                       // deactivated_at
      reactivate_at,                      // reactivate_at
      std::nullopt,                       // deleted
      std::nullopt                        // updated_at
  };

  ASSERT_FALSE(IsOptionAvailable(option_status, time_point));
}

}  // namespace eats_rest_menu_storage::status
