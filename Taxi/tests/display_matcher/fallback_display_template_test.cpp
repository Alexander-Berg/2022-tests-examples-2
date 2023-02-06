#include <gmock/gmock.h>

#include "dependencies.hpp"

#include <display_matcher/fallback_display_template.hpp>

namespace {

namespace dm = eats_orders_tracking::display_matcher;

namespace dm_impl = eats_orders_tracking::display_matcher::impl;

using RequestData = eats_orders_tracking::utils::RequestData;
using TrackedOrderPayload = eats_orders_tracking::utils::TrackedOrderPayload;
using defs::internal::exp3_order_status::ButtonContactType;
using defs::internal::exp3_order_status::ButtonType;
using defs::internal::exp3_order_status::IconStatus;
using defs::internal::pg_order::OrderStatus;
using defs::internal::pg_waybill::CourierType;
using eats_orders_tracking::models::CourierStaticWithPayload;

using eats_orders_tracking::tests::display_matcher::DependenciesForTest;
using eats_orders_tracking::tests::display_matcher::DependenciesForTestFallback;
using eats_orders_tracking::tests::display_matcher::DependenciesForTestNotNull;

static constexpr const char* kDisplayTemplateCodeDefault =
    "eats_orders_tracking_dm_layer_order_status_native.default";
static constexpr const char* kDisplayTemplateCodeRover =
    "eats_orders_tracking_dm_layer_order_status_native.rover";
static constexpr const char* kDisplayTemplateCodeOnCar =
    "eats_orders_tracking_dm_layer_order_status_native.car";
static constexpr const char* kDisplayTemplateCodeHardOfHearing =
    "eats_orders_tracking_dm_layer_order_status_native.hard_of_hearing";

}  // namespace

TEST(DisplayMatcherFallback, CancelledAfterCreation) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CancelledDuringCookingDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CancelledDuringCookingRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, CancelledDuringCookingOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, CancelledDuringDelivery) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CancelledAfterDeliveryDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.delivered_at =
      ::utils::datetime::Now();

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CancelledAfterDeliveryRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.delivered_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, CancelledAfterDeliveryOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kCancelled;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.status_history.delivered_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kFailed);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kExclamationIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_cancelled.close");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.cancel_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.cancel_title_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, DeliveredDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kDelivered;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_delivered.thanks");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_delivered_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(*display_template.payload.description_key,
            "status_messages.uft.native.order_delivered_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.order_delivered_title_short");
  EXPECT_EQ(*display_template.payload.short_description_key,
            "status_messages.default.order_delivered_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, DeliveredRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kDelivered;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_delivered.thanks");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.yandex_rover.order_delivered_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(*display_template.payload.description_key,
            "status_messages.yandex_rover.order_delivered_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.yandex_rover.order_delivered_title_short");
  EXPECT_EQ(*display_template.payload.short_description_key,
            "status_messages.yandex_rover.order_delivered_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, DeliveredOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kDelivered;
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_delivered.thanks");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.shop.order_delivered_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(*display_template.payload.description_key,
            "status_messages.shop.order_delivered_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.shop.order_delivered_title_short");
  EXPECT_EQ(*display_template.payload.short_description_key,
            "status_messages.shop.order_delivered_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, ChangedWithoutCCDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status =
      OrderStatus::kAwaitingCardPayment;
  tracked_order_payload.order.payload.changes_state.emplace();
  tracked_order_payload.order.payload.changes_state->applicable_until =
      ::utils::datetime::Now() + std::chrono::seconds(100);

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type,
            ButtonType::kShowOrderChanges);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.what_changed");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.order_on_hold_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.order_on_hold_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_on_hold_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_on_hold_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, ChangedWithoutCCRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status =
      OrderStatus::kAwaitingCardPayment;
  tracked_order_payload.order.payload.changes_state.emplace();
  tracked_order_payload.order.payload.changes_state->applicable_until =
      ::utils::datetime::Now() + std::chrono::seconds(100);
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type,
            ButtonType::kShowOrderChanges);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.what_changed");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.order_on_hold_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.order_on_hold_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_on_hold_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_on_hold_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, ChangedWithoutCCOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kDelivered;
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kClose);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.order_delivered.thanks");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.shop.order_delivered_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(*display_template.payload.description_key,
            "status_messages.shop.order_delivered_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.shop.order_delivered_title_short");
  EXPECT_EQ(*display_template.payload.short_description_key,
            "status_messages.shop.order_delivered_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, LowLateGradationDuringCookingDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(10);

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.low_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.low_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.low_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.low_late_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, LowLateGradationDuringCookingRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(10);
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.low_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.low_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.low_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.low_late_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, LowLateGradationDuringCookingOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(10);
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.low_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.low_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.low_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.low_late_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, HighLateGradationDuringCookingDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(100);

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.high_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.high_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.high_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.high_late_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, HighLateGradationDuringCookingRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(100);
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.high_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.high_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.high_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.high_late_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, HighLateGradationDuringCookingOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kPlaceConfirmed;
  tracked_order_payload.order.payload.status_history.place_confirmed_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.promise =
      ::utils::datetime::Now() - std::chrono::seconds(100);
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.high_late_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.high_late_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.high_late_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.high_late_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, AwaitingCardPayment) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status =
      OrderStatus::kAwaitingCardPayment;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCancelOrder);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.cancel_order");

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.order_awaiting_payment_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.order_awaiting_payment_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_awaiting_payment_title");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CreatedNotAsap) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kUnconfirmed;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCancelOrder);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.cancel_order");

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.pre_order_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.pre_order_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.pre_order_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.pre_order_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CreatedAsap) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kUnconfirmed;
  tracked_order_payload.order.payload.is_asap = true;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCancelOrder);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.cancel_order");

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_created_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.uft.native.order_created_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.order_created_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.native.order_created_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, ArrivedToCustomerDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kArrivedToCustomer;
  tracked_order_payload.order.payload.status_history.arrived_to_customer_at =
      ::utils::datetime::Now();

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.call_to_courier");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.uft.native.order_delivering_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, ArrivedToCustomerRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kArrivedToCustomer;
  tracked_order_payload.order.payload.status_history.arrived_to_customer_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.rover.contact_us");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kOpenRover);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.rover.open_rover");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.yandex_rover.courier_arrived_to_customer_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(
      display_template.payload.description_key,
      "status_messages.yandex_rover.courier_arrived_to_customer_description");
  EXPECT_EQ(
      display_template.payload.short_title_key,
      "status_messages.yandex_rover.courier_arrived_to_customer_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.yandex_rover.courier_arrived_to_customer_"
            "description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, ArrivedToCustomerOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kArrivedToCustomer;
  tracked_order_payload.order.payload.status_history.arrived_to_customer_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.call_to_courier");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.order_taxi_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, true);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.order_taxi_delivering_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_taxi_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_taxi_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, ArrivedToCustomerHardOfHearing) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kArrivedToCustomer;
  tracked_order_payload.order.payload.status_history.arrived_to_customer_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kPedestrian;
  tracked_order_payload.order_courier_assignment->performer_info
      .is_hard_of_hearing = true;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(
      display_template.payload.description_key,
      "status_messages.uft.native.order_delivering_description_hard_hearing");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeHardOfHearing);
}

TEST(DisplayMatcherFallback, DeliveryDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.call_to_courier");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.uft.native.order_delivering_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, DeliveryRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.rover.contact_us");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.yandex_rover.order_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.yandex_rover.order_delivering_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.yandex_rover.order_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.yandex_rover.order_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, DeliveryOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kCall);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.call_to_courier");
  EXPECT_EQ(display_template.payload.buttons[0].contact_type,
            ButtonContactType::kCourier);

  EXPECT_EQ(display_template.payload.buttons[1].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[1].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.default.order_taxi_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, true);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.default.order_taxi_delivering_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_taxi_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_taxi_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}

TEST(DisplayMatcherFallback, DeliveryHardOfHearing) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order.payload.status_history.moved_to_delivery_at =
      ::utils::datetime::Now();
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kPedestrian;
  tracked_order_payload.order_courier_assignment->performer_info
      .is_hard_of_hearing = true;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_delivering_title");
  EXPECT_EQ(display_template.payload.show_courier, true);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(
      display_template.payload.description_key,
      "status_messages.uft.native.order_delivering_description_hard_hearing");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.default.order_delivering_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.default.order_delivering_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeHardOfHearing);
}

TEST(DisplayMatcherFallback, CookingDefault) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kCyclistIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_cooking_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.uft.native.order_cooking_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.order_cooking_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.native.order_cooking_description_short");

  EXPECT_EQ(display_template.display_template_code,
            kDisplayTemplateCodeDefault);
}

TEST(DisplayMatcherFallback, CookingRover) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kRover;

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kRoverIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.native.order_cooking_description_short");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.yandex_rover.order_cooking_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.yandex_rover.order_cooking_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.yandex_rover.order_cooking_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeRover);
}

TEST(DisplayMatcherFallback, CookingOnCar) {
  const RequestData request_data;
  TrackedOrderPayload tracked_order_payload;
  const DependenciesForTestFallback dependencies;

  tracked_order_payload.order.payload.status = OrderStatus::kReadyForDelivery;
  tracked_order_payload.order.payload.region.country_code = "RU";
  tracked_order_payload.order_courier_assignment.emplace();
  tracked_order_payload.order_courier_assignment->waybill_info.courier_type =
      CourierType::kVehicle;
  tracked_order_payload.order_courier_assignment->waybill_info.car_model =
      "CarModel";
  tracked_order_payload.order_courier_assignment->waybill_info.car_number =
      "x123xx999";

  const auto display_template = dm::BuildFallbackDisplayTemplate(
      request_data, tracked_order_payload, dependencies);

  EXPECT_EQ(display_template.payload.icons[0].status, IconStatus::kFinished);
  EXPECT_EQ(display_template.payload.icons[0].uri, dm_impl::kCheckIcon);
  EXPECT_EQ(display_template.payload.icons[0].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[0].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[1].status, IconStatus::kInProgress);
  EXPECT_EQ(display_template.payload.icons[1].uri, dm_impl::kChiefhatIcon);
  EXPECT_EQ(display_template.payload.icons[1].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[1].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[2].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[2].uri, dm_impl::kTaxiCarIcon);
  EXPECT_EQ(display_template.payload.icons[2].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[2].show_eta, false);

  EXPECT_EQ(display_template.payload.icons[3].status, IconStatus::kPending);
  EXPECT_EQ(display_template.payload.icons[3].uri, dm_impl::kFlagIcon);
  EXPECT_EQ(display_template.payload.icons[3].show_animation, false);
  EXPECT_EQ(display_template.payload.icons[3].show_eta, false);

  EXPECT_EQ(display_template.payload.buttons[0].type, ButtonType::kContactUs);
  EXPECT_EQ(display_template.payload.buttons[0].title_key,
            "buttons.default.contact_us");

  EXPECT_EQ(display_template.payload.title_key,
            "status_messages.uft.native.order_cooking_title");
  EXPECT_EQ(display_template.payload.show_courier, false);
  EXPECT_EQ(display_template.payload.show_car_info, false);
  EXPECT_EQ(display_template.payload.description_key,
            "status_messages.uft.native.order_cooking_description");
  EXPECT_EQ(display_template.payload.short_title_key,
            "status_messages.native.order_cooking_title_short");
  EXPECT_EQ(display_template.payload.short_description_key,
            "status_messages.native.order_cooking_description_short");

  EXPECT_EQ(display_template.display_template_code, kDisplayTemplateCodeOnCar);
}
