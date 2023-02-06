#include <userver/utest/utest.hpp>

#include "driver_orders.hpp"

using models::orders::Item;
using models::orders::Status;
using models::orders::Storage;

namespace {
bool Contains(const std::vector<models::orders::PrehashedAlias>& array,
              const models::orders::PrehashedAlias& key) {
  return std::find(array.begin(), array.end(), key) != array.end();
}
}  // namespace

UTEST(OrdersCache, Basic) {
  Storage stg;
  models::DriverId d0{"p0", "d0"};
  models::orders::PrehashedAlias order0{"order.0"};
  models::orders::PrehashedAlias order1{"order.1"};
  auto now = std::chrono::system_clock::now();
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx("yandex");

#define NOT_END(it) ASSERT_NE(it, stg.GetEnd())
  // Check if record can be found by both keys
  stg.Update({d0, order0}, {Status::Complete, yandex_provider_idx, now, now});

  NOT_END(stg.FindOrder({d0, order0}));
  ASSERT_EQ(stg.FindByContractorId(d0).size(), 1);
  ASSERT_EQ(stg.FindByContractorId(d0)[0], order0);

  // Check if new order is added and it is visible
  // from FindByDriver
  stg.Update({d0, order1}, {Status::Complete, yandex_provider_idx, now, now});
  NOT_END(stg.FindOrder({d0, order0}));
  NOT_END(stg.FindOrder({d0, order1}));
  ASSERT_EQ(stg.FindByContractorId(d0).size(), 2);
  ASSERT_TRUE(Contains(stg.FindByContractorId(d0), order0));
  ASSERT_TRUE(Contains(stg.FindByContractorId(d0), order1));

  // Check order update keeps driver orders the same
  stg.Update({d0, order1},
             {Status::Transporting, yandex_provider_idx, now, now});
  NOT_END(stg.FindOrder({d0, order0}));
  NOT_END(stg.FindOrder({d0, order1}));
  ASSERT_EQ(stg.FindByContractorId(d0).size(), 2);
  ASSERT_TRUE(Contains(stg.FindByContractorId(d0), order0));
  ASSERT_TRUE(Contains(stg.FindByContractorId(d0), order1));
#undef NOT_END
}

// TODO: we temporary allow non-unique orders, TAXIDRIVERORDER-247
// after unique order_id constraint restored, this test can be removed
UTEST(OrdersCache, NonUniqueOrder) {
  Storage stg;
  models::DriverId d0{"p0", "d0"};
  models::DriverId d1{"p1", "d1"};
  models::orders::PrehashedAlias order0{"order.0"};
  auto now = std::chrono::system_clock::now();
  const auto yandex_provider_idx =
      models::orders::FromStringToProviderIdx("yandex");

  stg.Update({d0, order0},
             {Status::Transporting, yandex_provider_idx, now, now});
  stg.Update({d1, order0},
             {Status::Transporting, yandex_provider_idx, now, now});

  auto orders = stg.FindByContractorId(d0);
  ASSERT_EQ(orders.size(), 1);
  ASSERT_TRUE(Contains(orders, order0));

  orders = stg.FindByContractorId(d1);
  ASSERT_EQ(orders.size(), 1);
  ASSERT_TRUE(Contains(orders, order0));

  auto it = stg.FindOrder({d0, order0});
  ASSERT_NE(it, stg.GetEnd());
  ASSERT_EQ(it->first.contractor_id, d0);
  ASSERT_EQ(it->first.alias_id, order0);

  it = stg.FindOrder({d1, order0});
  ASSERT_NE(it, stg.GetEnd());
  ASSERT_EQ(it->first.contractor_id, d1);
  ASSERT_EQ(it->first.alias_id, order0);
}
