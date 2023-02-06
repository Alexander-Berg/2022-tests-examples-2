#include "aggregator.hpp"

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/utils/underlying_value.hpp>

#include <models/provider.hpp>
#include <taxi_config/variables/DRIVER_STATUS_ORDERS_FEATURES.hpp>

namespace views::orders::utest {

using driver_status::models::v2::OrderStatus;

inline const auto& kUnknownProvider = driver_status::ToProviderName(
    utils::UnderlyingValue(driver_status::Provider::kUnknown));
inline const auto& kYandexProvider = driver_status::ToProviderName(
    utils::UnderlyingValue(driver_status::Provider::kYandex));
inline const auto& kParkProvider = driver_status::ToProviderName(
    utils::UnderlyingValue(driver_status::Provider::kPark));
inline const auto& kFormulaProvider = driver_status::ToProviderName(
    utils::UnderlyingValue(driver_status::Provider::kFormula));

inline const auto kTs100 = std::chrono::system_clock::from_time_t(100);
inline const auto kTs200 = std::chrono::system_clock::from_time_t(200);
inline const auto kTs300 = std::chrono::system_clock::from_time_t(300);

inline dynamic_config::StorageMock CreateConfig(
    bool finish_by_client, bool use_timeout,
    bool terminal_status_preference = false) {
  taxi_config::driver_status_orders_features::DriverStatusOrdersFeatures
      order_features;
  order_features.finish_by_client = finish_by_client;
  order_features.finish_by_client_use_timeout = use_timeout;
  order_features.enable_terminal_status_preference = terminal_status_preference;

  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::DRIVER_STATUS_ORDERS_FEATURES, order_features}});
}

inline void FillCaches(std::shared_ptr<models::orders::Storage>& master_orders,
                       std::shared_ptr<models::orders::Storage>& client_orders,
                       std::uint16_t provider_idx) {
  // available only in master_orders
  master_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
      {OrderStatus::Waiting, provider_idx, kTs200, kTs200});
  master_orders->Update(
      {{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});

  // available in both caches
  master_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias2"}},
      {OrderStatus::Waiting, provider_idx, kTs200, kTs200});
  master_orders->Update(
      {{"dbid3", "uuid3"}, models::orders::PrehashedAlias{"alias3"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});
  master_orders->Update(
      {{"dbid4", "uuid4"}, models::orders::PrehashedAlias{"alias4"}},
      {OrderStatus::Waiting, provider_idx, kTs200, kTs200});
  master_orders->Update(
      {{"dbid5", "uuid5"}, models::orders::PrehashedAlias{"alias5"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});

  client_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias2"}},
      {OrderStatus::Driving, provider_idx, kTs200, kTs200});
  client_orders->Update(
      {{"dbid3", "uuid3"}, models::orders::PrehashedAlias{"alias3"}},
      {OrderStatus::Driving, provider_idx, kTs200, kTs200});
  client_orders->Update(
      {{"dbid4", "uuid4"}, models::orders::PrehashedAlias{"alias4"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});
  client_orders->Update(
      {{"dbid5", "uuid5"}, models::orders::PrehashedAlias{"alias5"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});

  // available only in client_orders
  client_orders->Update(
      {{"dbid6", "uuid6"}, models::orders::PrehashedAlias{"alias6"}},
      {OrderStatus::Driving, provider_idx, kTs200, kTs200});
  client_orders->Update(
      {{"dbid7", "uuid7"}, models::orders::PrehashedAlias{"alias7"}},
      {OrderStatus::Complete, provider_idx, kTs200, kTs200});
}

}  // namespace views::orders::utest
