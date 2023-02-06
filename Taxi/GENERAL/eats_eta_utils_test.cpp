#include <gtest/gtest.h>

#include <clients/eats-eta/client_gmock.hpp>
#include <clients/eats-picker-orders/client_gmock.hpp>
#include <clients/eats-picking-time-estimator/client_gmock.hpp>
#include <experiments3/models/cache_manager.hpp>
#include <userver/dynamic_config/storage_mock.hpp>

#include "utils/common.hpp"
#include "utils/eats_eta_utils.hpp"

using namespace eats_picker_dispatch::utils;

namespace {

formats::json::Value MakeEtaConfig(int batch_size = 1) {
  formats::json::ValueBuilder builder;
  builder["batch_size"] = batch_size;
  return builder.ExtractValue();
}

formats::json::Value MakePickingDurationsFallbackConfig(
    int time_estimator_batch_size = 1, int time_estimator_tasks_count = 1,
    int estimation_orders_tasks_count = 1,
    int estimation_orders_batch_size = 1) {
  formats::json::ValueBuilder builder;
  builder["time_estimator_tasks_count"] = time_estimator_tasks_count;
  builder["time_estimator_batch_size"] = time_estimator_batch_size;
  builder["estimation_orders_tasks_count"] = estimation_orders_tasks_count;
  builder["estimation_orders_batch_size"] = estimation_orders_batch_size;
  return builder.ExtractValue();
}

OrderEstimationContext MakeOrderEstimationContext(
    const std::string& order_nr, bool use_initial_picking_duration,
    const std::optional<std::chrono::seconds>& estimated_picking_time =
        std::nullopt) {
  EtaSettings eta_settings{false, false, use_initial_picking_duration,
                           std::chrono::seconds(300)};
  auto now = std::chrono::system_clock::from_time_t(3600);
  auto status_updated_at = now - std::chrono::seconds(1800);
  bool picking_has_started = false;
  bool is_picked_up = false;

  return {
      order_nr,
      true,
      eta_settings,
      now,
      picking_has_started,
      is_picked_up,
      status_updated_at,
      estimated_picking_time,
  };
}

clients::eats_picker_orders::EstimationOrder MakeEstimationOrder(
    const std::string& eats_id) {
  return {eats_id,
          1,
          "1",
          std::nullopt,
          clients::eats_picker_orders::FlowType::kPickingPacking,
          std::nullopt,
          std::nullopt,
          clients::eats_picker_orders::OrderState::kNew,
          {{"1", false}},
          {}};
}

clients::eats_picker_orders::api_v1_estimation_orders::post::Request
MakeOrderRequest(const std::string& eats_id) {
  clients::eats_picker_orders::api_v1_estimation_orders::post::Request
      order_request;
  order_request.body.eats_ids.push_back(eats_id);
  return order_request;
}

clients::eats_picker_orders::api_v1_estimation_orders::post::Response
MakeOrderResponse(const std::string& eats_id) {
  clients::eats_picker_orders::api_v1_estimation_orders::post::Response
      order_response;
  order_response.estimation_orders.push_back(MakeEstimationOrder(eats_id));
  return order_response;
}

clients::eats_picking_time_estimator::api_v1_orders_estimate::post::Request
MakeEstimatorRequest(const std::string& eats_id) {
  clients::eats_picking_time_estimator::OrderV1 estimator_order;
  estimator_order.eats_id = eats_id;

  clients::eats_picking_time_estimator::api_v1_orders_estimate::post::Request
      estimator_request;
  estimator_request.body.orders.push_back(std::move(estimator_order));

  return estimator_request;
}

clients::eats_picking_time_estimator::api_v1_orders_estimate::post::Response
MakeEstimatorResponse(const std::string& eats_id) {
  clients::eats_picking_time_estimator::OrdersResponseEstimationsA estimation;
  estimation.eats_id = eats_id;
  estimation.estimation.eta_seconds = std::chrono::seconds(300).count();
  ;
  clients::eats_picking_time_estimator::api_v1_orders_estimate::post::Response
      estimator_response;
  estimator_response.estimations.push_back(std::move(estimation));

  return estimator_response;
}

}  // namespace

namespace clients::eats_picker_orders::api_v1_estimation_orders::post {
bool operator==(
    const clients::eats_picker_orders::api_v1_estimation_orders::post::Request&
        lhs,
    const clients::eats_picker_orders::api_v1_estimation_orders::post::Request&
        rhs) {
  return lhs.body.eats_ids == rhs.body.eats_ids;
}
}  // namespace clients::eats_picker_orders::api_v1_estimation_orders::post

// clang-format off
namespace clients::eats_picking_time_estimator::api_v1_orders_estimate::post {
bool operator==(const clients::eats_picking_time_estimator::
                    api_v1_orders_estimate::post::Request& lhs,
                const clients::eats_picking_time_estimator::
                    api_v1_orders_estimate::post::Request& rhs) {
  if (lhs.body.orders.size() != rhs.body.orders.size()) {
    return false;
  }
  size_t i = 0;
  while (i < lhs.body.orders.size()) {
    if (lhs.body.orders[i].eats_id != rhs.body.orders[i].eats_id) {
      return false;
    }
    ++i;
  }
  return true;
}
}  // namespace
   // clients::eats_picking_time_estimator::api_v1_orders_estimate::post
   // clang-format on

TEST(GetDeliveryDurationTest, UseEstimatedDeliveryDuration) {
  Order order;
  const std::chrono::seconds estimated_delivery_duration{1000};
  EtaSettings eta_settings{false, false};
  order.estimated_delivery_duration = estimated_delivery_duration;

  ::testing::StrictMock<clients::eats_eta::ClientGMock> eta_client;

  const auto result = GetDeliveryDuration(
      eta_settings, std::shared_ptr<const experiments3::models::CacheManager>{},
      eta_client, order);

  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), estimated_delivery_duration);
}

UTEST(GetPickingDurationsTest, FallbackPickingDurationCast) {
  const dynamic_config::StorageMock config_storage{
      {taxi_config::EATS_PICKER_DISPATCH_ETA_SETTINGS, MakeEtaConfig()},
      {taxi_config::EATS_PICKER_DISPATCH_PICKING_DURATION_FALLBACK_SETTINGS,
       MakePickingDurationsFallbackConfig()}};
  const auto config = config_storage.GetSnapshot();
  EtaSettings eta_settings{false, false, true, std::chrono::seconds(300)};

  ::testing::StrictMock<clients::eats_eta::ClientGMock> eta_client;
  ::testing::StrictMock<clients::eats_picking_time_estimator::ClientGMock>
      time_estimator_mock;
  ::testing::StrictMock<clients::eats_picker_orders::ClientGMock>
      picker_orders_mock;

  auto now = std::chrono::system_clock::from_time_t(3600);
  auto status_updated_at = now - std::chrono::seconds(1800);
  auto estimated_picking_time = std::chrono::seconds(600);
  bool picking_has_started = true;
  bool is_picked_up = false;

  OrderEstimationContext order_estimation_context{
      "eats_id",           true,
      eta_settings,        now,
      picking_has_started, is_picked_up,
      status_updated_at,   estimated_picking_time,
  };

  // negative
  auto result =
      GetPickingDurations(config, time_estimator_mock, picker_orders_mock,
                          eta_client, {order_estimation_context});
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.at(order_estimation_context.order_nr),
            eta_settings.initial_picking_duration_after_picked_up);

  // positive
  order_estimation_context.estimated_picking_time = std::chrono::seconds{2400};
  result = GetPickingDurations(config, time_estimator_mock, picker_orders_mock,
                               eta_client, {order_estimation_context});
  ASSERT_EQ(result.size(), 1);
  ASSERT_EQ(result.at(order_estimation_context.order_nr).count(), 600);
}

UTEST(GetPickingDurationsTest, FallbackWithPartlyUsingEstimator) {
  const dynamic_config::StorageMock config_storage{
      {taxi_config::EATS_PICKER_DISPATCH_ETA_SETTINGS, MakeEtaConfig()},
      {taxi_config::EATS_PICKER_DISPATCH_PICKING_DURATION_FALLBACK_SETTINGS,
       MakePickingDurationsFallbackConfig()}};
  const auto config = config_storage.GetSnapshot();

  ::testing::StrictMock<clients::eats_eta::ClientGMock> eta_client;
  ::testing::StrictMock<clients::eats_picking_time_estimator::ClientGMock>
      time_estimator_mock;
  ::testing::StrictMock<clients::eats_picker_orders::ClientGMock>
      picker_orders_mock;

  const std::string eats_id1 = "eats_id1";
  const std::string eats_id2 = "eats_id2";

  const auto order_estimation_context1 =
      MakeOrderEstimationContext(eats_id1, true, std::chrono::seconds(600));

  const auto order_estimation_context2 =
      MakeOrderEstimationContext(eats_id2, false);

  const auto order_request = MakeOrderRequest(eats_id2);
  const auto order_response = MakeOrderResponse(eats_id2);

  const auto estimator_request = MakeEstimatorRequest(eats_id2);
  const auto estimator_response = MakeEstimatorResponse(eats_id2);

  ::testing::InSequence s;
  EXPECT_CALL(picker_orders_mock, EstimationOrders(order_request, ::testing::_))
      .Times(1)
      .WillOnce(::testing::Return(order_response));

  EXPECT_CALL(time_estimator_mock,
              OrdersPickingTimeEstimate(estimator_request, ::testing::_))
      .Times(1)
      .WillOnce(::testing::Return(estimator_response));

  std::vector<OrderEstimationContext> orders_context = {
      order_estimation_context1, order_estimation_context2};
  auto result =
      GetPickingDurations(config, time_estimator_mock, picker_orders_mock,
                          eta_client, orders_context);

  EXPECT_EQ(result.size(), orders_context.size());
}
