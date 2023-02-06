#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <clients/transactions-eda/client_gmock.hpp>
#include <clients/trust-eda/client_gmock.hpp>
#include <experiments3/models/cache_manager.hpp>
#include <helpers/order_tracking.hpp>
#include <taxi_config/taxi_config.hpp>
#include <testing/taxi_config.hpp>
#include <tests/db/storage_mock_test.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>

TEST(OrderTracking, TrivialCase) {
  db::MockStorage storage;

  EXPECT_CALL(storage, FetchOrder("123123-321321"))
      .Times(testing::AtLeast(1))
      .WillOnce(testing::Return(std::nullopt));

  EXPECT_CALL(storage, FetchOrderPayment("123123-321321"))
      .Times(testing::AtLeast(0))
      .WillOnce(testing::Return(std::nullopt));

  clients::transactions_eda::ClientGMock transactions_eda_client;
  clients::trust_eda::ClientGMock trust_eda_client;

  auto config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();

  try {
    const auto response = helpers::order_tracking::BuildResponse(
        "123123-321321", "12345678", "ru",
        utils::FeatureFlagsResolver{dynamic_config::ValueDict<
            taxi_config::eats_payments_feature_flags::FeatureFlag>{}},
        storage, trust_eda_client, transactions_eda_client, config,
        {nullptr} /* translations */,
        (const std::optional<experiments3::models::CacheManager>&)std::nullopt);
    ASSERT_TRUE(false);
  } catch (handlers::eats_v1_eats_payments_v1_order_tracking::post::Response404
               exception) {
    ASSERT_TRUE(true);
  }
}
