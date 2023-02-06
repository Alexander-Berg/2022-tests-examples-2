#include <gmock/gmock.h>
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <models/order.hpp>
#include <tracked_order/filter.hpp>

namespace {

namespace models = eats_orders_tracking::models;

using defs::internal::pg_order::CancelReason;
using defs::internal::pg_order::kPaymentMethodValues;
using defs::internal::pg_order::OrderStatus;
using defs::internal::pg_order::PaymentMethod;
using eats_orders_tracking::tracked_order::CanShowOrder;
using models::OrderWithPayload;

constexpr std::chrono::seconds kDelta(1);

const char* kClientSelfDidNotPayRawCancelReason = "client.self.did_not_pay";
const char* kDefaultConfigKey = "__default__";
const char* kDuplicateRawCancelReason = "duplicate";
const char* kPaymentFailedRawCancelReason = "payment_failed";

constexpr PaymentMethod kValidPaymentMethods[] = {PaymentMethod::kTaxi,
                                                  PaymentMethod::kEatsPayments,
                                                  PaymentMethod::kGrocery};

taxi_config::TaxiConfig GetConfig() {
  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  std::unordered_map<std::string, std::chrono::seconds> cancel_reasons;
  cancel_reasons[kDefaultConfigKey] = std::chrono::seconds(200);
  cancel_reasons[kClientSelfDidNotPayRawCancelReason] = std::chrono::seconds(0);
  cancel_reasons[kDuplicateRawCancelReason] = std::chrono::seconds(0);
  cancel_reasons[kPaymentFailedRawCancelReason] = std::chrono::seconds(300);
  dynamic_config::ValueDict<std::chrono::seconds> cancelled_config{
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue()
          .cancelled.GetName(),
      cancel_reasons};

  std::unordered_map<
      std::string,
      taxi_config::eats_orders_tracking_timeouts_for_orders_show_2::
          TimeoutForOrderShow>
      timeouts;
  taxi_config::eats_orders_tracking_timeouts_for_orders_show_2::
      TimeoutForOrderShow timeout;
  timeout.delivered = std::chrono::seconds(100);
  timeout.cancelled = cancelled_config;
  timeout.all = std::chrono::seconds(400);
  timeouts[kDefaultConfigKey] = timeout;
  config.eats_orders_tracking_timeouts_for_orders_show_2 =
      dynamic_config::ValueDict<
          taxi_config::eats_orders_tracking_timeouts_for_orders_show_2::
              TimeoutForOrderShow>(
          config.eats_orders_tracking_timeouts_for_orders_show_2.GetName(),
          timeouts);

  return config;
}

}  // namespace

TEST(OrdersFilter, Market) {
  const auto config = GetConfig();

  OrderWithPayload order;
  order.payload.client_app = models::kOrderClientAppMarket;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, TimeoutForAllOrders) {
  const auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now - timeouts.all - kDelta;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, EmptyDelivered) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kDelivered;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, TimeoutForDelivered) {
  const auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kDelivered;
  order.payload.status_history.delivered_at = now - timeouts.delivered - kDelta;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, GreenFlowForDelivered) {
  const auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kDelivered;
  order.payload.status_history.delivered_at = now - timeouts.delivered;

  ASSERT_EQ(CanShowOrder(order, config), true);
}

TEST(OrdersFilter, EmptyCancelled) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kCancelled;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, CancelledDuplicate) {
  const auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kCancelled;
  order.payload.status_history.call_center_confirmed_at = now;
  order.payload.status_history.cancelled_at = now - timeouts.all;
  order.payload.cancel_reason = CancelReason::kDuplicate;
  order.payload.raw_cancel_reason = kDuplicateRawCancelReason;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, CancelledClientSelfDidNotPay) {
  const auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kCancelled;
  order.payload.status_history.call_center_confirmed_at = now;
  order.payload.status_history.cancelled_at = now - timeouts.all;
  order.payload.cancel_reason = CancelReason::kClientSelfDidNotPay;
  order.payload.raw_cancel_reason = kClientSelfDidNotPayRawCancelReason;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, EmptyPaymentMethod) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kAwaitingCardPayment;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, InvalidPaymentMethod) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kAwaitingCardPayment;

  for (const auto& payment_method : kPaymentMethodValues) {
    if (std::count(std::begin(kValidPaymentMethods),
                   std::end(kValidPaymentMethods), payment_method) > 0) {
      continue;
    }

    order.payload.payment_method = payment_method;
    ASSERT_EQ(CanShowOrder(order, config), false);
  }
}

TEST(OrdersFilter, GreenFlowForAwaitingCardPayment) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status = OrderStatus::kAwaitingCardPayment;

  for (const auto& payment_method : kValidPaymentMethods) {
    order.payload.payment_method = payment_method;
    ASSERT_EQ(CanShowOrder(order, config), true);
  }
}

TEST(OrdersFilter, GreenFlowOtherStatuses) {
  const auto config = GetConfig();

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;

  for (const auto status : defs::internal::pg_order::kOrderStatusValues) {
    switch (status) {
      case OrderStatus::kDelivered:
      case OrderStatus::kCancelled:
      case OrderStatus::kAwaitingCardPayment:
        continue;  // already tested in other tests
      default:
        break;
    }

    order.payload.status = status;
    ASSERT_EQ(CanShowOrder(order, config), true);
  }
}

TEST(OrdersFilter, GreenFlowForCancelReasonValueInConfig) {
  auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue()
          .cancelled;

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status_history.cancelled_at =
      now - timeouts[kPaymentFailedRawCancelReason];
  order.payload.status = OrderStatus::kCancelled;
  order.payload.raw_cancel_reason = kPaymentFailedRawCancelReason;
  order.payload.cancel_reason = CancelReason::kPaymentFailed;

  ASSERT_EQ(CanShowOrder(order, config), true);
}

TEST(OrdersFilter, TimeoutForCancelReasonValueInConfig) {
  auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue()
          .cancelled;

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status_history.cancelled_at =
      now - timeouts[kPaymentFailedRawCancelReason] - kDelta;
  order.payload.status = OrderStatus::kCancelled;
  order.payload.raw_cancel_reason = kPaymentFailedRawCancelReason;
  order.payload.cancel_reason = CancelReason::kPaymentFailed;

  ASSERT_EQ(CanShowOrder(order, config), false);
}

TEST(OrdersFilter, GreenFlowForCancelReasonDefaultValue) {
  auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue()
          .cancelled;

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status_history.cancelled_at = now - timeouts.GetDefaultValue();
  order.payload.status = OrderStatus::kCancelled;
  order.payload.raw_cancel_reason = "some_reason";
  order.payload.cancel_reason = CancelReason::kOther;

  ASSERT_EQ(CanShowOrder(order, config), true);
}

TEST(OrdersFilter, TimeoutForCancelReasonDefaultValue) {
  auto config = GetConfig();
  const auto& timeouts =
      config.eats_orders_tracking_timeouts_for_orders_show_2.GetDefaultValue()
          .cancelled;

  auto now = utils::datetime::Stringtime("2020-01-01T00:00:00.00Z", "UTC");
  utils::datetime::MockNowSet(now);

  OrderWithPayload order;
  order.payload.updated_at = now;
  order.payload.status_history.cancelled_at =
      now - timeouts.GetDefaultValue() - kDelta;
  order.payload.status = OrderStatus::kCancelled;
  order.payload.raw_cancel_reason = "some_reason";
  order.payload.cancel_reason = CancelReason::kOther;

  ASSERT_EQ(CanShowOrder(order, config), false);
}
