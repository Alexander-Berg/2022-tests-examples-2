#include "aggregator_test_setup.hpp"

#include <userver/utest/utest.hpp>

namespace views::orders::utest {

UTEST(Aggregator, EmptyCachesDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid", "uuid"}));

  auto orders = aggregator.GetActiveOrders({"dbid", "uuid"});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid", "uuid"}, models::orders::PrehashedAlias{"alias"}},
       {OrderStatus::Driving, yandex_provider_idx, {}, {}}});
  ASSERT_FALSE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid", "uuid"}, models::orders::PrehashedAlias{"alias"}},
       {OrderStatus::Driving, yandex_provider_idx, {}, {}}});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetOrders();
  ASSERT_TRUE(orders.empty());
}

UTEST(Aggregator, HasActiveOrdersDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  ASSERT_TRUE(aggregator.HasActiveOrders({"dbid0", "uuid0"}));
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid1", "uuid1"}));
  ASSERT_TRUE(aggregator.HasActiveOrders({"dbid2", "uuid2"}));
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid3", "uuid3"}));
  ASSERT_TRUE(aggregator.HasActiveOrders({"dbid4", "uuid4"}));
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid5", "uuid5"}));
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid6", "uuid6"}));
  ASSERT_FALSE(aggregator.HasActiveOrders({"dbid7", "uuid7"}));
}

UTEST(Aggregator, GetActiveOrdersDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  auto orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);

  orders = aggregator.GetActiveOrders({"dbid1", "uuid1"});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrders({"dbid2", "uuid2"});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);

  orders = aggregator.GetActiveOrders({"dbid3", "uuid3"});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrders({"dbid4", "uuid4"});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);

  orders = aggregator.GetActiveOrders({"dbid5", "uuid5"});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrders({"dbid6", "uuid6"});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrders({"dbid7", "uuid7"});
  ASSERT_TRUE(orders.empty());
}

UTEST(Aggregator, GetActiveOrdersRecentMasterDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  auto orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias2"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid3", "uuid3"}, models::orders::PrehashedAlias{"alias3"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid4", "uuid4"}, models::orders::PrehashedAlias{"alias4"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid5", "uuid5"}, models::orders::PrehashedAlias{"alias5"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid6", "uuid6"}, models::orders::PrehashedAlias{"alias6"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid7", "uuid7"}, models::orders::PrehashedAlias{"alias7"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  // recent order has earlier TS
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias2"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);
  ASSERT_EQ(kTs200, orders[0].info.event_ts);
}

UTEST(Aggregator, GetActiveOrdersRecentClientDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  auto orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);
  ASSERT_EQ(kTs200, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias2"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);
  ASSERT_EQ(kTs200, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid3", "uuid3"}, models::orders::PrehashedAlias{"alias3"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid4", "uuid4"}, models::orders::PrehashedAlias{"alias4"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);
  ASSERT_EQ(kTs200, orders[0].info.event_ts);

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid5", "uuid5"}, models::orders::PrehashedAlias{"alias5"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid6", "uuid6"}, models::orders::PrehashedAlias{"alias6"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid7", "uuid7"}, models::orders::PrehashedAlias{"alias7"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());
}

UTEST(Aggregator, GetOrdersDontUseClient) {
  const auto config = CreateConfig(false, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());
  auto orders = aggregator.GetOrders();
  ASSERT_EQ(6, orders.size());
}

}  // namespace views::orders::utest
