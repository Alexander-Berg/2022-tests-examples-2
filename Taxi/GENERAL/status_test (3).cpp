#include <gtest/gtest.h>

#include <unordered_map>

#include <clients/grocery-orders/responses.hpp>
#include <models/status.hpp>

using GroceryStatus = clients::grocery_orders::libraries::
    grocery_orders_shared::GroceryOrderStatus;
using GroceryResolution = clients::grocery_orders::libraries::
    grocery_orders_shared::GroceryOrderResolution;
using CourierInfo =
    clients::grocery_orders::libraries::grocery_orders_shared::StateCourierInfo;
using TrackingStatus = std::string;

CourierInfo empty_courier_info{};

const std::string kRover = "rover";

CourierInfo rover_courier_info{
    std::nullopt /*name*/,       kRover /*transport_type*/,
    std::nullopt /*position*/,   std::nullopt /*cargo_dispatch_info*/,
    std::nullopt /*car_number*/, std::nullopt /*driver_id*/
};

struct StatusEntry {
  StatusEntry(
      TrackingStatus tracking_status, GroceryStatus grocery_status,
      CourierInfo courier_info,
      std::optional<GroceryResolution> grocery_resolution = std::nullopt)
      : tracking_status(tracking_status),
        grocery_status(grocery_status),
        courier_info(courier_info),
        grocery_resolution(grocery_resolution) {}
  TrackingStatus tracking_status;
  GroceryStatus grocery_status;
  CourierInfo courier_info;
  std::optional<GroceryResolution> grocery_resolution;
};

struct DescriptionKeysEntry {
  DescriptionKeysEntry(
      std::string title, std::string description, GroceryStatus grocery_status,
      CourierInfo courier_info,
      std::optional<GroceryResolution> grocery_resolution = std::nullopt)
      : title(title),
        description(description),
        grocery_status(grocery_status),
        courier_info(courier_info),
        grocery_resolution(grocery_resolution) {}

  std::string title;
  std::string description;
  GroceryStatus grocery_status;
  CourierInfo courier_info;
  std::optional<GroceryResolution> grocery_resolution;
};

TEST(TestStatus, EatsTrackingTest) {
  static const std::vector<StatusEntry> testing_entries = {
      {"order.created", GroceryStatus::kCreated, empty_courier_info},
      {"order.cooking", GroceryStatus::kAssembling, empty_courier_info},
      {"order.cooking", GroceryStatus::kAssembled, empty_courier_info},
      {"order.cooking", GroceryStatus::kPerformerFound, empty_courier_info},
      {"order.delivering", GroceryStatus::kDelivering, empty_courier_info},
      {"order.delivering", GroceryStatus::kDeliveryArrived, empty_courier_info},
      {"order.delivered", GroceryStatus::kClosed, empty_courier_info,
       GroceryResolution::kSucceeded},
      {"order.cancel", GroceryStatus::kClosed, empty_courier_info,
       GroceryResolution::kCanceled},
      {"order.cancel", GroceryStatus::kClosed, empty_courier_info,
       GroceryResolution::kFailed},
  };

  for (const auto& entry : testing_entries) {
    const models::Status status{entry.grocery_status, entry.grocery_resolution,
                                entry.courier_info};
    EXPECT_EQ(status.TrackingStatus(), entry.tracking_status);
  }

  ASSERT_THROW(
      models::Status(GroceryStatus::kClosed, std::nullopt, empty_courier_info),
      std::runtime_error);
}

TEST(TestStatus, DescriptionKeysTest) {
  static const std::vector<DescriptionKeysEntry> testing_entries = {
      {"foodtech.order_status.order_created_title",
       "foodtech.order_status.order_created_description",
       GroceryStatus::kCreated, empty_courier_info},
      {"foodtech.order_status.order_collecting_title",
       "foodtech.order_status.order_collecting_description",
       GroceryStatus::kAssembling, empty_courier_info},
      {"foodtech.order_status.order_collected_title",
       "foodtech.order_status.order_collected_description",
       GroceryStatus::kAssembled, empty_courier_info},
      {"foodtech.order_status.order_rover_arrived_title",
       "foodtech.order_status.order_rover_arrived_description",
       GroceryStatus::kDeliveryArrived, rover_courier_info},
      {"foodtech.order_status.order_delivered_title",
       "foodtech.order_status.order_delivered_description",
       GroceryStatus::kClosed, empty_courier_info,
       GroceryResolution::kSucceeded},
      {"foodtech.order_status.order_cancel_title",
       "foodtech.order_status.order_cancel_description", GroceryStatus::kClosed,
       empty_courier_info, GroceryResolution::kCanceled},
      {"foodtech.order_status.order_cancel_title",
       "foodtech.order_status.order_cancel_description", GroceryStatus::kClosed,
       empty_courier_info, GroceryResolution::kFailed},
  };

  for (const auto& entry : testing_entries) {
    const models::Status status{entry.grocery_status, entry.grocery_resolution,
                                entry.courier_info};
    const auto description = status.MakeDescriptionKeys();
    EXPECT_EQ(description.title_tanker_key, entry.title);
    EXPECT_EQ(description.description_tanker_key, entry.description);
  }
}
