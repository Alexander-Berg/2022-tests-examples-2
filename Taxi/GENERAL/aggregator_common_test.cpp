#include "aggregator_test_setup.hpp"

#include <userver/utest/utest.hpp>

namespace views::orders::utest {

UTEST(Aggregator, GetActiveOrdersRecentMasterWithTerminationPreference) {
  const auto config = CreateConfig(true, true, true);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  FillCaches(master_orders, client_orders, yandex_provider_idx);

  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());

  // incoming new active status, previous is absent,
  auto orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid8", "uuid8"}, models::orders::PrehashedAlias{"alias8"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Driving, orders[0].info.status);
  ASSERT_EQ(kTs100, orders[0].info.event_ts);

  // incoming new terminal status, previous is absent,
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid8", "uuid8"}, models::orders::PrehashedAlias{"alias8"}},
       {OrderStatus::Cancelled, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_TRUE(orders.empty());

  // incoming fresh terminal status, previous is active
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Cancelled, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  // incoming stale terminal status, previous is active
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Cancelled, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_TRUE(orders.empty());

  // incoming fresh active status, previous is an active status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Transporting, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Transporting, orders[0].info.status);
  ASSERT_EQ(kTs300, orders[0].info.event_ts);

  // incoming stale active status, previous is an active status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias0"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_FALSE(orders.empty());
  ASSERT_EQ(OrderStatus::Waiting, orders[0].info.status);
  ASSERT_EQ(kTs200, orders[0].info.event_ts);

  // incoming fresh active status, previous is a terminal status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  // incoming stale active status, previous is a terminal status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_TRUE(orders.empty());

  // incoming fresh terminal status, previous is a terminal status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Expired, yandex_provider_idx, kTs300, kTs300}});
  ASSERT_TRUE(orders.empty());

  // incoming stale terminal status, previous is a terminal status
  orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid1", "uuid1"}, models::orders::PrehashedAlias{"alias1"}},
       {OrderStatus::Expired, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_TRUE(orders.empty());
}

UTEST(Aggregator, OrderProviders) {
  const auto config = CreateConfig(true, false);
  const auto unknown_provider_idx =
      models::orders::FromStringToProviderIdx(kUnknownProvider);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  const auto park_provider_idx =
      models::orders::FromStringToProviderIdx(kParkProvider);
  const auto formula_provider_idx =
      models::orders::FromStringToProviderIdx(kFormulaProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();
  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());

  auto update_caches = [&master_orders, &client_orders](
                           std::uint16_t master_provider_idx,
                           std::uint16_t client_provider_idx) {
    master_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
        {OrderStatus::Complete, master_provider_idx, kTs100, kTs100});
    master_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias10"}},
        {OrderStatus::Waiting, master_provider_idx, kTs100, kTs100});
    master_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias20"}},
        {OrderStatus::Transporting, master_provider_idx, kTs100, kTs100});
    client_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
        {OrderStatus::Driving, client_provider_idx, kTs100, kTs100});
    client_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias10"}},
        {OrderStatus::Complete, client_provider_idx, kTs100, kTs100});
    client_orders->Update(
        {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias21"}},
        {OrderStatus::Driving, client_provider_idx, kTs100, kTs100});
  };

  auto compare = [](std::vector<models::orders::Order>&& active_orders,
                    std::vector<std::string> expected_aliases) {
    std::sort(active_orders.begin(), active_orders.end(),
              [](const auto& o1, const auto& o2) {
                return o1.key.alias_id.GetData() < o2.key.alias_id.GetData();
              });
    for (std::size_t i = 0; i < active_orders.size(); ++i) {
      ASSERT_EQ(active_orders[i].key.alias_id.GetData(), expected_aliases[i]);
    }
  };

  update_caches(yandex_provider_idx, yandex_provider_idx);
  auto orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 4);
  compare(std::move(orders), {"alias00", "alias10", "alias20", "alias21"});

  update_caches(park_provider_idx, park_provider_idx);
  orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 2);
  compare(std::move(orders), {"alias00", "alias21"});

  update_caches(yandex_provider_idx, park_provider_idx);
  orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 3);
  compare(std::move(orders), {"alias00", "alias20", "alias21"});

  update_caches(park_provider_idx, yandex_provider_idx);
  orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 2);
  compare(std::move(orders), {"alias00", "alias21"});

  // should be same as yandex, park
  update_caches(unknown_provider_idx, park_provider_idx);
  orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 3);
  compare(std::move(orders), {"alias00", "alias20", "alias21"});

  // should be same as park, yandex
  update_caches(formula_provider_idx, unknown_provider_idx);
  orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(orders.size(), 2);
  compare(std::move(orders), {"alias00", "alias21"});
}

UTEST(Aggregator, SeveralOrders) {
  const auto config = CreateConfig(true, false);
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx(kYandexProvider);
  const auto park_provider_idx =
      models::orders::FromStringToProviderIdx(kParkProvider);
  auto master_orders = std::make_shared<models::orders::Storage>();
  auto client_orders = std::make_shared<models::orders::Storage>();

  master_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
      {OrderStatus::Cancelled, yandex_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias01"}},
      {OrderStatus::Complete, yandex_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias02"}},
      {OrderStatus::Complete, yandex_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias03"}},
      {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100});
  client_orders->Update(
      {{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias01"}},
      {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias20"}},
      {OrderStatus::Cancelled, park_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias21"}},
      {OrderStatus::Complete, park_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias22"}},
      {OrderStatus::Complete, park_provider_idx, kTs100, kTs100});
  master_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias23"}},
      {OrderStatus::Driving, park_provider_idx, kTs100, kTs100});
  client_orders->Update(
      {{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias21"}},
      {OrderStatus::Driving, park_provider_idx, kTs100, kTs100});
  Aggregator aggregator({master_orders}, {client_orders}, config.GetSnapshot());

  ASSERT_TRUE(aggregator.HasActiveOrders({"dbid0", "uuid0"}));
  ASSERT_TRUE(aggregator.HasActiveOrders({"dbid2", "uuid2"}));

  auto active_orders = aggregator.GetActiveOrders({"dbid0", "uuid0"});
  ASSERT_EQ(2, active_orders.size());
  active_orders = aggregator.GetActiveOrders({"dbid2", "uuid2"});
  ASSERT_EQ(1, active_orders.size());

  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
       {OrderStatus::Waiting, yandex_provider_idx, kTs200, kTs200}});
  ASSERT_EQ(3, active_orders.size());
  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias20"}},
       {OrderStatus::Waiting, park_provider_idx, kTs200, kTs200}});
  ASSERT_EQ(1, active_orders.size());

  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
       {OrderStatus::Waiting, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(2, active_orders.size());
  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias20"}},
       {OrderStatus::Waiting, park_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(1, active_orders.size());

  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias03"}},
       {OrderStatus::Complete, yandex_provider_idx, kTs200, kTs200}});
  ASSERT_EQ(1, active_orders.size());
  active_orders = aggregator.GetActiveOrdersRecentMaster(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias23"}},
       {OrderStatus::Complete, park_provider_idx, kTs200, kTs200}});
  ASSERT_EQ(1, active_orders.size());

  // make alias00 active, but alias01 inactive from the client point of view
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias00"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(2, active_orders.size());

  // make alias20 active, but alias21 inactive
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias20"}},
       {OrderStatus::Driving, park_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(1, active_orders.size());

  // make all client orders inactive
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias01"}},
       {OrderStatus::Complete, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(1, active_orders.size());
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias21"}},
       {OrderStatus::Complete, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(0, active_orders.size());

  // make alias02 active, but alias01 inactive
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid0", "uuid0"}, models::orders::PrehashedAlias{"alias02"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(2, active_orders.size());

  // make alias22 active, but alias21 inactive
  active_orders = aggregator.GetActiveOrdersRecentClient(
      {{{"dbid2", "uuid2"}, models::orders::PrehashedAlias{"alias22"}},
       {OrderStatus::Driving, yandex_provider_idx, kTs100, kTs100}});
  ASSERT_EQ(1, active_orders.size());

  auto orders = aggregator.GetOrders();
  // 4 yandex (have records in ds.orders OR ds.master_orders)
  // 1 park (account only orders which have record in ds.orders)
  ASSERT_EQ(5, orders.size());
}

}  // namespace views::orders::utest
