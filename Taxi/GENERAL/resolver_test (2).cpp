#include "resolver.hpp"

#include <gtest/gtest.h>
#include <algorithm>

#include <userver/decimal64/decimal64.hpp>

namespace eats_places::resolve {
namespace {

struct ZoneMock : eats_places::resolve::Zone {
  int id;
};

}  // namespace

TEST(Resolve, Delivery) {
  std::vector<ZoneMock> zones;

  {
    ZoneMock zone;

    zone.id = 2;
    zone.shipping_type = ShippingType::kDelivery;
    zone.couriers_type = CouriersType::kYandexTaxi;
    zone.delivery_duration = std::chrono::seconds{10 * 60};
    zone.delivery_cost = decimal64::Decimal<4>(100);
    zone.minimum_order_cost = decimal64::Decimal<4>(23);

    zones.push_back(zone);
  }

  {
    ZoneMock zone;

    zone.id = 1;
    zone.shipping_type = ShippingType::kDelivery;
    zone.couriers_type = CouriersType::kYandexTaxi;
    zone.delivery_duration = std::chrono::seconds{2 * 60};
    zone.delivery_cost = decimal64::Decimal<4>(59);
    zone.minimum_order_cost = decimal64::Decimal<4>(292);

    zones.push_back(zone);
  }

  {
    ZoneMock zone;

    zone.id = 3;
    zone.shipping_type = ShippingType::kDelivery;
    zone.couriers_type = CouriersType::kYandexTaxi;
    zone.delivery_duration = std::chrono::seconds{42 * 60};
    zone.delivery_cost = decimal64::Decimal<4>(29);
    zone.minimum_order_cost = decimal64::Decimal<4>(3);

    zones.push_back(zone);
  }

  const auto best =
      std::min_element(zones.begin(), zones.end(), CompareDeliveryZones);

  EXPECT_TRUE(best != zones.end());
  EXPECT_EQ(best->id, 1);
}

TEST(Resolve, CourierWeight) {
  struct TestCase {
    std::vector<CouriersType> types;
    int expected_id;
  };

  std::vector<TestCase> cases{
      {
          {CouriersType::kYandexTaxi, CouriersType::kVehicle},  // types
          2,                                                    // expected_id
      },
      {
          {CouriersType::kPedestrian, CouriersType::kVehicle},  // types
          1,                                                    // expected_id
      },
      {
          {CouriersType::kYandexTaxi, CouriersType::kVehicle,
           CouriersType::kBicycle},  // types
          3,                         // expected_id
      },
      {
          {CouriersType::kVehicle, CouriersType::kBicycle,
           CouriersType::kPedestrian},  // types
          2,                            // expected_id
      },
  };

  for (const auto& test_case : cases) {
    std::vector<ZoneMock> zones;
    for (size_t i = 0; i < test_case.types.size(); ++i) {
      ZoneMock zone;

      zone.id = i + 1;
      zone.shipping_type = ShippingType::kDelivery;
      zone.couriers_type = test_case.types[i];
      zones.push_back(zone);
    }

    auto best = std::min_element(zones.begin(), zones.end(),
                                 eats_places::resolve::CompareDeliveryZones);

    EXPECT_TRUE(best != zones.end());
    EXPECT_EQ(best->id, test_case.expected_id);
  }
}

TEST(Resolve, Pickup) {
  std::vector<ZoneMock> zones;

  {
    ZoneMock zone;

    zone.id = 2;
    zone.shipping_type = ShippingType::kDelivery;
    zone.couriers_type = CouriersType::kYandexTaxi;
    zone.delivery_duration = std::chrono::seconds{1 * 60};
    zone.delivery_cost = decimal64::Decimal<4>(29);
    zone.minimum_order_cost = decimal64::Decimal<4>(3);

    zones.push_back(zone);
  }

  {
    ZoneMock zone;

    zone.id = 178;
    zone.shipping_type = ShippingType::kPickup;
    zone.minimum_order_cost = decimal64::Decimal<4>(23);

    zones.push_back(zone);
  }

  {
    ZoneMock zone;

    zone.id = 29;
    zone.shipping_type = ShippingType::kPickup;
    zone.minimum_order_cost = decimal64::Decimal<4>(292);

    zones.push_back(zone);
  }

  const auto best =
      std::min_element(zones.begin(), zones.end(), ComparePickupZones);

  EXPECT_TRUE(best != zones.end());
  EXPECT_EQ(best->id, 178);
}

}  // namespace eats_places::resolve
