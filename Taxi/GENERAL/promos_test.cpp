#include "promos.hpp"

#include <optional>
#include <vector>

#include <gtest/gtest.h>

#include <eats-discounts-applicator/discounts_threshold.hpp>

#include <models/place.hpp>

namespace eats_catalog::utils {

namespace {

using eats_catalog::models::DeliveryCondition;
using eats_catalog::models::Money;
using eats_catalog::models::Promo;

namespace edapp = eats_discounts_applicator;

Promo MakePromo(const edapp::DiscountTypeForThreshold& discount_type,
                edapp::ValueType value_type, const Money& from_cost,
                const Money& amount, const std::optional<Money>& max_amount) {
  return Promo{
      1,             // id
      "test1",       // title
      std::nullopt,  // description
      {
          1,             // id
          "test promo",  // title
          std::nullopt,  // picture
          std::nullopt,  // detailed_picture
      },                 // type
      false,             // disabled_by_surge
      500,               // score
      edapp::DiscountThreshold{
          from_cost,      // from_cost
          discount_type,  // discount_type
          value_type,     // value
          amount,         // amount
          max_amount,     // max_amount
          1,              // promo_type_id
      }                   // discount_threshold
  };
}

bool IsEqual(const std::vector<DeliveryCondition>& result,
             const std::vector<DeliveryCondition>& result_expected) {
  return std::equal(
      std::begin(result), std::end(result), std::begin(result_expected),
      [](const DeliveryCondition& lhs, const DeliveryCondition& rhs) {
        return lhs.order_price == rhs.order_price &&
               lhs.delivery_cost == rhs.delivery_cost;
      });
}

}  // namespace

TEST(ApplyDeliveryConditionsPromo, Empty) {
  std::vector<DeliveryCondition> delivery_conditions;
  std::optional<Promo> promo;

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_EQ(result, std::nullopt);
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromo) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{3000},  // order_price
      Money{100},   // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{0},                                    // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {{
      Money{3000},  // order_price
      Money{0},     // delivery_cost
  }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoInsertEnd) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{3000},  // order_price
      Money{100},   // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{4000},                                 // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{3000},  // order_price
          Money{100},   // delivery_cost
      },
      {
          Money{4000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoInsertMiddle) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{2000},                                 // from_cost
                Money{50},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{2000},  // order_price
          Money{50},    // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoInsertDelete) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{1000},  // order_price
          Money{50},    // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{500},                                  // from_cost
                Money{50},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{500},  // order_price
          Money{50},   // delivery_cost
      },
      {
          Money{1000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, FractionPromo) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{3000},  // order_price
      Money{100},   // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kFraction,                 // value_type
                Money{0},                                    // from_cost
                Money{10},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {{
      Money{3000},  // order_price
      Money{90},    // delivery_cost
  }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, FractionPromoInsertEnd) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{3000},  // order_price
      Money{100},   // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kFraction,                 // value_type
                Money{4000},                                 // from_cost
                Money{10},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{3000},  // order_price
          Money{100},   // delivery_cost
      },
      {
          Money{4000},  // order_price
          Money{90},    // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, FractionPromoInsertMiddle) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kFraction,                 // value_type
                Money{2000},                                 // from_cost
                Money{10},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{2000},  // order_price
          Money{90},    // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, FractionPromoFree) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{3000},  // order_price
      Money{100},   // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kFraction,                 // value_type
                Money{0},                                    // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {{
      Money{3000},  // order_price
      Money{0},     // delivery_cost
  }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, FractionPromoFreeDelete) {
  std::vector<DeliveryCondition> delivery_conditions = {{
      Money{0},    // order_price
      Money{100},  // delivery_cost
  }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kFraction,                 // value_type
                Money{0},                                    // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, false);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(result.value().empty());
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoContinuousNoInsertMiddle) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{2000},                                 // from_cost
                Money{50},                                   // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, true);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoContinuousNoDelete) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{100},  // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{0},                                    // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );
  std::vector<DeliveryCondition> result_expected = {
      {
          Money{100},  // order_price
          Money{0},    // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, true);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(IsEqual(result.value(), result_expected));
}

TEST(ApplyDeliveryConditionsPromo, AbsolutePromoContinuousFreeDelete) {
  std::vector<DeliveryCondition> delivery_conditions = {
      {
          Money{0},    // order_price
          Money{100},  // delivery_cost
      },
      {
          Money{3000},  // order_price
          Money{0},     // delivery_cost
      }};
  const auto promo =
      MakePromo(edapp::DiscountTypeForThreshold::kDelivery,  // discount_type
                edapp::ValueType::kAbsolute,                 // value_type
                Money{0},                                    // from_cost
                Money{100},                                  // amount
                std::nullopt                                 // max_amount
      );

  const auto result =
      ApplyDeliveryConditionsPromo(delivery_conditions, promo, true);

  ASSERT_NE(result, std::nullopt);
  ASSERT_TRUE(result.value().empty());
}

}  // namespace eats_catalog::utils
