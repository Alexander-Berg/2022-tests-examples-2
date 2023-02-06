#include "applier.hpp"

#include <iostream>

#include <gtest/gtest.h>

#include <fmt/format.h>

#include <models/delivery_condition.hpp>

namespace eats_places::models {

constexpr bool operator==(const DeliveryCondition& lhs,
                          const DeliveryCondition& rhs) {
  return lhs.delivery_cost == rhs.delivery_cost &&
         lhs.order_price == rhs.order_price;
}

std::ostream& operator<<(std::ostream& os, const DeliveryCondition& condition) {
  os << fmt::format("{{order_price: {}, delivery_cost: {}}}",
                    condition.order_price, condition.delivery_cost);
  return os;
}

}  // namespace eats_places::models

namespace eats_catalog::surge {

namespace {
using clients::eda_delivery_price::libraries::eats_surge::LavkaInfo;
using clients::eda_delivery_price::libraries::eats_surge::MarketPlaceInfo;
using clients::eda_delivery_price::libraries::eats_surge::NativeInfo;
using clients::eda_delivery_price::libraries::eats_surge::PlaceSurge;
using models::Business;
using models::DeliveryCondition;
using models::DeliveryType;
using models::EstimatedTime;
using models::Money;
using models::Place;
using models::PlaceInfo;

const bool kNotPreorder = false;
const auto kNoRadiusSurge = SurgeConfig{};

}  // namespace

TEST(SurgeApply, Native) {
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
      },
      std::nullopt,  // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kNative;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.delivery_conditions = {
      DeliveryCondition{
          Money(0),   // order_price
          Money(79),  // delivery_cost
      },
      DeliveryCondition{
          Money(100),  // order_price
          Money(49),   // delivery_cost
      },
  };

  Apply(place, surge, kNotPreorder, kNoRadiusSurge);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  ASSERT_TRUE(place.surge.delivery_fee.has_value());
  ASSERT_EQ(*place.surge.delivery_fee, Money(10 + 49));
}

TEST(SurgeApply, NativeNoConditions) {
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              20,  // deliveryfee
          },
      },
      std::nullopt,  // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kNative;
  place_info.business = Business::kRestaurant;
  Place place{place_info};
  place.delivery.info.is_available = true;

  Apply(place, surge, kNotPreorder, kNoRadiusSurge);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  ASSERT_TRUE(place.surge.delivery_fee.has_value());
  ASSERT_EQ(*place.surge.delivery_fee, Money(20));
}

TEST(SurgeApply, Marketplace) {
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
          MarketPlaceInfo{
              1,    // surgelevel
              1,    // loadlevel
              100,  // additionaltimepercents
          },
      },
      std::nullopt,  // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kMarketplace;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.timings.delivery = std::chrono::seconds{6 * 60};
  place.timings.avg_preparation = std::chrono::seconds{4 * 60};

  Apply(place, surge, kNotPreorder, kNoRadiusSurge);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  ASSERT_TRUE(place.surge.time_factor.has_value());
  ASSERT_EQ(*place.surge.time_factor, 100);
  EXPECT_EQ(place.timings.estimated.max, std::chrono::minutes{12})
      << "unexpected max delivery time: expected 12m, got "
      << place.timings.estimated.max.count();
}

TEST(SurgeApply, MarketplaceWithPreparationZetoPercent) {
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
          MarketPlaceInfo{
              1,  // surgelevel
              1,  // loadlevel
              0,  // additionaltimepercents
          },
      },
      std::nullopt,  // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kMarketplace;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.timings.delivery = std::chrono::seconds{6 * 60};
  place.timings.avg_preparation = std::chrono::seconds{4 * 60};

  Apply(place, surge, kNotPreorder, kNoRadiusSurge);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  ASSERT_TRUE(place.surge.time_factor.has_value());
  ASSERT_EQ(*place.surge.time_factor, 0);
  EXPECT_EQ(place.timings.estimated.max, std::chrono::minutes{6})
      << "unexpected max delivery time: expected 6m, got "
      << place.timings.estimated.max.count();
}

TEST(SurgeApply, Lavka) {
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
          MarketPlaceInfo{
              1,    // surgelevel
              1,    // loadlevel
              100,  // additionaltimepercents
          },
          LavkaInfo{
              1,    // surgelevel
              1,    // loadlevel
              300,  // minimumorder
          },
      },
      std::nullopt,  // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kNative;
  place_info.business = Business::kStore;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.delivery_conditions = {
      DeliveryCondition{
          Money(0),    // order_price
          Money(799),  // delivery_cost
      },
      DeliveryCondition{
          Money(100),  // order_price
          Money(200),  // delivery_cost
      },
  };

  Apply(place, surge, kNotPreorder, kNoRadiusSurge);

  std::vector<DeliveryCondition> expected_conditions{
      DeliveryCondition{
          Money(300),  // order_price
          Money(200),  // delivery_cost
      },
  };

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  EXPECT_EQ(place.delivery_conditions, expected_conditions);
  ASSERT_TRUE(place.surge.min_order_price.has_value());
  ASSERT_EQ(*place.surge.min_order_price, Money(300));
}

TEST(SurgeApply, SurgeFinalCost) {
  // Проверяет, что если в конфинге
  // стоит use_surge_final_cost, то
  // цена при сурже берется как есть из прайсинга

  const models::Money final_cost{100};
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
      },
      final_cost,    // surge_final_cost
      std::nullopt,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kNative;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.delivery_conditions = {
      DeliveryCondition{
          Money(0),   // order_price
          Money(79),  // delivery_cost
      },
      DeliveryCondition{
          Money(100),  // order_price
          Money(49),   // delivery_cost
      },
  };

  const SurgeConfig config{
      true,  // use_surge_final_cost
  };

  Apply(place, surge, kNotPreorder, config);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  ASSERT_TRUE(place.surge.delivery_fee.has_value());
  ASSERT_EQ(*place.surge.delivery_fee, final_cost);
}

TEST(SurgeApply, ContinuousSurgeRange) {
  // Проверяет, что ContinuousSurgeRange перекладывается
  // из ответа прайсига на плейс

  const models::ContinuousSurgeRange continuous_surge_range{
      models::Money{100},  // min
      models::Money{200},  // max
  };
  const SurgeInfo surge{
      PlaceSurge{
          1,  // placeid
          NativeInfo{
              1,   // surgelevel
              1,   // loadlevel
              10,  // deliveryfee
          },
      },
      std::nullopt,            // surge_final_cost
      continuous_surge_range,  // continuous_surge_range
  };

  PlaceInfo place_info;
  place_info.id = models::PlaceId(1);
  place_info.delivery_type = DeliveryType::kNative;
  Place place{place_info};
  place.delivery.info.is_available = true;
  place.delivery_conditions = {};

  const SurgeConfig config{};

  Apply(place, surge, kNotPreorder, config);

  EXPECT_EQ(place.surge.level, 1) << "unexpected surge level";
  const auto [min, max] = place.surge.continuous_surge_range.value();
  ASSERT_EQ(min, continuous_surge_range.min);
  ASSERT_EQ(max, continuous_surge_range.max);
}

}  // namespace eats_catalog::surge
