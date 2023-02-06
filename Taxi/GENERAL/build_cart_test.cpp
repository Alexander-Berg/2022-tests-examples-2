#include <iterator>
#include <utility>

#include <userver/utest/utest.hpp>

#include <l10n/l10n.hpp>

#include <clients/eats-catalog/client.hpp>
#include <clients/eats-catalog/definitions.hpp>
#include <defs/all_definitions.hpp>
#include <handlers/dependencies.hpp>
#include <models/common.hpp>
#include <models/extra_fees.hpp>
#include <utils/localizations.hpp>

#include "cart.hpp"

namespace eats_cart::builders {
namespace {

namespace mc = models;
namespace l10n = eats_cart::utils::localizations;

using Decimal = decimal64::Decimal<2>;
using Threshold = clients::eats_catalog::Threshold;

l10n::TestLocalizer MakeLocalizer() { return l10n::TestLocalizer{}; }

clients::eats_catalog::PlaceInfoConstraints MakeConstraints(
    std::optional<Decimal> min_price, std::optional<Decimal> max_price,
    std::optional<mc::Weight> max_weight) {
  clients::eats_catalog::PlaceInfoConstraints result;
  if (min_price.has_value()) {
    result.minimum_order_price = {Decimal{min_price.value()}, ""};
  }
  if (max_price.has_value()) {
    result.maximum_order_price = {Decimal{max_price.value()}, ""};
  }
  if (max_weight.has_value()) {
    result.maximum_order_weight = {max_weight->ToDoubleInexact(), ""};
  }
  return result;
}

models::ExtraFees MakeExtraFees() {
  models::ExtraFees extra_fees;
  models::ExtraFee extra_fee;
  defs::internal::extra_fee_payload::ExtraFeePayload payload;
  defs::internal::extra_fee_payload::DeliveryPricing pricing;
  defs::internal::extra_fee_payload::DeliveryPricingNextdeliverythreshold
      threshold;
  payload.delivery_time = ::utils::datetime::Now();
  payload.location = {{55.35, 37.12}};
  payload.delivery_class = models::DeliveryClass::kRegular;
  threshold.amount_need = Decimal{150};
  threshold.next_cost = Decimal{550};
  pricing.next_delivery_threshold = std::move(threshold);
  pricing.sum_to_free_delivery = {Decimal{80}};
  pricing.min_cart = {Decimal{30}};
  payload.delivery_pricing = std::move(pricing);

  extra_fee.money = models::PriceMoney{200};
  extra_fee.payload = {std::move(payload)};
  extra_fees.SetFee(models::kDeliveryFee, std::move(extra_fee));
  return extra_fees;
}

requesters::DeliveryPrice MakeDeliveryPrice() {
  requesters::DeliveryPrice result;
  auto& cart_delivery_price = result.cart_delivery_price.emplace();
  cart_delivery_price.delivery_fee = Decimal{100};
  auto& next_threshold = cart_delivery_price.next_delivery_threshold.emplace();
  next_threshold.next_cost = Decimal{500};
  next_threshold.amount_need = Decimal{100};
  cart_delivery_price.min_cart = Decimal{10};
  cart_delivery_price.sum_to_free_delivery = Decimal{50};
  return result;
}

}  // namespace

TEST(MakeRequirements, Simple) {
  const models::PriceMoney cart_subtotal = utils::ToPrice(Decimal{250});
  const std::string currency_sign = "$";
  std::vector<Threshold> order_delivery{{Decimal{3}, Decimal{10}},
                                        {Decimal{7}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{"10.8"}, Decimal{0}}};

  auto localizer = MakeLocalizer();

  // next threshold has cost
  mc::PriceMoney order_price{8};
  mc::Weight order_weight{1};
  mc::Weight max_weight{10};

  auto constraints = MakeConstraints(/*min_price*/ Decimal{"2.9"},
                                     /*max_price*/ Decimal{20}, max_weight);
  std::unique_ptr<models::DeliveryDiscountCalculator> delivery_discount =
      nullptr;
  auto delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );

  auto result =
      MakeRequirements(localizer, constraints, order_price, order_weight, false,
                       delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, 3);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, Decimal{"2.8"});
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, "message.delivery_cost,$,3,1");

  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            true, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);

  // next threshold is free
  order_price = 9;
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, 2);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, Decimal{"1.8"});
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, "message.free_delivery,$,2")
      << result.next_delivery_threshold.value();
  EXPECT_TRUE(result.violated_constraints.empty());

  // order_price is less than min_price
  order_price = 1;
  auto min_price = utils::ToDecimal(order_price) + Decimal{"0.9"};
  constraints = MakeConstraints(min_price,
                                /*max_price*/ Decimal{20}, max_weight);
  order_delivery[0].order_price = min_price;
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, 1);
  EXPECT_EQ(result.decimal_sum_to_min_order, Decimal{"0.9"});
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);
  EXPECT_TRUE(result.violated_constraints.empty());

  // order_price is greater or equal than maximal threshold
  order_price = utils::ToPrice(order_delivery.back().order_price);
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);
  EXPECT_TRUE(result.violated_constraints.empty());

  // maximal weight constraint is violated
  order_price = utils::ToPrice(min_price);
  order_delivery[0].order_price = min_price;
  order_weight = max_weight + mc::Weight{"0.1"};
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);
  EXPECT_EQ(result.violated_constraints.size(), 1);
  auto violation = handlers::Constraint{handlers::ConstraintType::kMaxWeight,
                                        "message.max_weight_title,10",
                                        "error.max_weight_exceeded,0.1"};
  EXPECT_EQ(result.violated_constraints[0], violation);

  // maximal weight and maximal price constraints are violated
  Decimal max_price{20};
  order_price = utils::ToPrice(max_price) + 1;
  order_weight = max_weight + mc::Weight{"0.1"};
  constraints = MakeConstraints(min_price, max_price, max_weight);

  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);
  EXPECT_EQ(result.violated_constraints.size(), 2);
  violation =
      handlers::Constraint{handlers::ConstraintType::kMaxSubtotalCost,
                           "message.max_cost_title,$CURRENCY$,$SIGN$,20",
                           "error.max_cost_exceeded,$CURRENCY$,$SIGN$,1"};
  EXPECT_EQ(result.violated_constraints[0], violation);
  violation = handlers::Constraint{handlers::ConstraintType::kMaxWeight,
                                   "message.max_weight_title,10",
                                   "error.max_weight_exceeded,0.1"};
  EXPECT_EQ(result.violated_constraints[1], violation);

  auto extra_fees = MakeExtraFees();
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    std::nullopt,      // delivery_price
                                    order_weight,      // order_weight
                                    extra_fees,        // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);

  EXPECT_EQ(result.sum_to_min_order, 9);
  EXPECT_EQ(result.decimal_sum_to_min_order, Decimal{9});
}

TEST(MakeRequirements, DirectPricing) {
  // Проверяем, что если указан delivery_price
  // он переопределяет поля "как есть"
  const std::string currency_sign = "$";
  const models::PriceMoney cart_subtotal = utils::ToPrice(Decimal{250});
  std::vector<Threshold> order_delivery{{Decimal{3}, Decimal{10}},
                                        {Decimal{7}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{"10.8"}, Decimal{0}}};

  auto localizer = MakeLocalizer();

  // // next threshold has cost
  mc::PriceMoney order_price{8};
  mc::Weight order_weight{1};
  mc::Weight max_weight{10};
  auto delivery_price = MakeDeliveryPrice();
  auto& cart_delivery_price = delivery_price.cart_delivery_price.value();
  cart_delivery_price.min_cart = Decimal{0};
  auto constraints = MakeConstraints(/*min_price*/ Decimal{"2.9"},
                                     /*max_price*/ Decimal{20}, max_weight);
  std::unique_ptr<models::DeliveryDiscountCalculator> delivery_discount =
      nullptr;

  auto delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    delivery_price,    // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  auto result =
      MakeRequirements(localizer, constraints, order_price, order_weight, false,
                       delivery_price_requirements, cart_subtotal);

  EXPECT_EQ(result.sum_to_free_delivery,
            cart_delivery_price.sum_to_free_delivery.value().ToInteger());
  EXPECT_EQ(result.decimal_sum_to_free_delivery,
            cart_delivery_price.sum_to_free_delivery);

  EXPECT_EQ(result.sum_to_min_order, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_min_order, std::nullopt);

  // next delivery is free
  auto& next_threshold = cart_delivery_price.next_delivery_threshold.value();
  next_threshold.next_cost = Decimal{0};
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    delivery_price,    // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);
  EXPECT_EQ(result.next_delivery_threshold, "message.free_delivery,$,100");

  // min order
  cart_delivery_price.min_cart = Decimal{10};
  delivery_price_requirements =
      MakeDeliveryPriceRequirements(localizer,         // localizer
                                    order_delivery,    // thresholds
                                    constraints,       // constraints
                                    order_price,       // order_price
                                    false,             // actual_has_surge
                                    currency_sign,     // currency_sign
                                    delivery_price,    // delivery_price
                                    order_weight,      // order_weight
                                    {},                // extra_fees
                                    delivery_discount  // delivery_discount
      );
  result = MakeRequirements(localizer, constraints, order_price, order_weight,
                            false, delivery_price_requirements, cart_subtotal);

  EXPECT_EQ(result.sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.decimal_sum_to_free_delivery, std::nullopt);
  EXPECT_EQ(result.sum_to_min_order, 2);
  EXPECT_EQ(result.decimal_sum_to_min_order,
            Decimal{2});  // min_cart(10) - order_price(8)
  EXPECT_EQ(result.next_delivery_threshold, std::nullopt);
  EXPECT_TRUE(result.violated_constraints.empty());
}

}  // namespace eats_cart::builders
