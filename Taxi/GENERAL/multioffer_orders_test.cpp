#include "multioffer_orders.hpp"

#include <gtest/gtest.h>
#include <testing/taxi_config.hpp>

using candidates::GeoMember;
using candidates::filters::Context;
using candidates::filters::Result;

const candidates::filters::FilterInfo kEmptyInfo;

namespace cfp = candidates::filters::partners;

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

TEST(MultiofferOrdersFilter, ResultDisallow) {
  models::MultiofferOrdersData data{};
  models::MultiofferDriversData order_drivers;
  order_drivers.emplace("park_id_driver_id", 0);
  data["order_id"] = order_drivers;

  cfp::MultiofferFilter filter(kEmptyInfo, order_drivers);
  GeoMember member{{0, 0}, "park_id_driver_id"};
  {
    Context context;
    EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
  }
}

TEST(MultiofferOrdersFilter, ResultAllow) {
  models::MultiofferOrdersData data{};
  models::MultiofferDriversData order_drivers;
  order_drivers.emplace("park_id_not_driver_id", 0);
  data["order_id"] = order_drivers;

  cfp::MultiofferFilter filter(kEmptyInfo, order_drivers);
  GeoMember member{{0, 0}, "park_id_driver_id"};
  {
    Context context;
    EXPECT_EQ(filter.Process(member, context), Result::kAllow);
  }
}

TEST(MultiofferOrdersFilter, AuctionResultDisallow) {
  models::MultiofferOrdersData data{};
  models::MultiofferDriversData order_drivers;
  order_drivers.emplace("park_id_driver_id", 4);
  data["order_id"] = order_drivers;

  cfp::MultiofferFilter filter(kEmptyInfo, order_drivers, 4);
  GeoMember member{{0, 0}, "park_id_driver_id"};
  {
    Context context;
    EXPECT_EQ(filter.Process(member, context), Result::kDisallow);
  }
}

TEST(MultiofferOrdersFilter, AuctionResultAllow) {
  models::MultiofferOrdersData data{};
  models::MultiofferDriversData order_drivers;
  order_drivers.emplace("park_id_driver_id", 3);
  data["order_id"] = order_drivers;

  cfp::MultiofferFilter filter(kEmptyInfo, order_drivers, 4);
  GeoMember member{{0, 0}, "park_id_driver_id"};
  {
    Context context;
    EXPECT_EQ(filter.Process(member, context), Result::kAllow);
  }
}
