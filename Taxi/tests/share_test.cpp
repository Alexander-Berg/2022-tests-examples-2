#include <grocery-discounts-calculator/share.hpp>

#include <grocery-discounts-calculator/modifier.hpp>
#include <grocery-discounts-calculator/pricing.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_discounts_calculator {

using ProductId = grocery_shared::ProductId;
using grocery_pricing::Numeric;

const ProductId product_one{"product-one"};
const ProductId product_two{"product-two"};
const ProductId product_three{"product-three"};

const Numeric kRUB = Numeric::FromFloatInexact(1.0);
const Numeric kILS = Numeric::FromFloatInexact(0.1);

auto GetMinimalPriceEveryProductConstraint(Numeric value) {
  return Constraints{EveryProductConstraint{MinimalPrice{value}}};
}

// Значения никак не используются, нужно только для интерфейса
auto GetDummyDiscount() {
  return CartDiscount{{{Numeric{50}, AbsoluteMoneyPayment{Numeric{100}}}}};
}

void AddBag(Pricing& pricing, const ProductId& product_id, Bag bag) {
  auto it = std::find_if(
      pricing.product_pricings.begin(), pricing.product_pricings.end(),
      [&product_id](const auto& value) { return value.id == product_id; });
  ASSERT_TRUE(it != pricing.product_pricings.end());
  it->Update(std::move(bag), GetDummyDiscount(), {});
}

TEST(Pricing_Share_RUB, discount_is_shared_non_uniform) {
  // 1 товар - 100 руб. 2 товара - 200 руб. скидка 100 руб., ограничение на
  // каждый 90 руб. на первый скидка 10, на оставшиеся (100-10) / 2 = 45
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1}),
               ProductPricing(product_two, Numeric{200}, Numeric{2})},
              kRUB};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{90});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{100}, initial_pricing, constraints, cart_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{90}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{155}, Numeric{2}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

TEST(Pricing_Share_RUB, fair_shair_no_constraints) {
  // 1 товар - 50 руб. 1 товар - 200 руб. скидка 100 руб., ограничение на
  // каждый 1 руб. на первый скидка 20, на второй 80. 20/50 == 80/200
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{50}, Numeric{1}),
               ProductPricing(product_two, Numeric{200}, Numeric{1})},
              kRUB};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{1});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{100}, initial_pricing, constraints, cart_discount, {},
      SharePolicyFair{});
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{30}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{120}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

TEST(Pricing_Share_RUB, discount_is_shared_different_constraints) {
  // Ограничения влияют на распределение, но не записываются в историю, если
  // удаётся полностью распределить скидку по товарам.
  // 220 - распределяется полностью, 221 - нет.
  const auto cart_discount = GetDummyDiscount();
  const auto constraints = Constraints{
      SingleProductConstraint{product_one, MinimalPrice{Numeric{80}}},
      SingleProductConstraint{product_two, MinimalPrice{Numeric{100}}}};

  for (auto constraints_applied : {false, true}) {
    auto initial_pricing =
        Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1}),
                 ProductPricing(product_two, Numeric{200}, Numeric{2})},
                kRUB};

    auto discount = constraints_applied ? Numeric{221} : Numeric{220};
    const auto resulting_pricing = grocery_discounts_calculator::Share(
        discount, initial_pricing, constraints, cart_discount);
    const auto constraints_1 =
        constraints_applied ? Constraints{constraints[0]} : Constraints{};
    const auto expected_product_one_history =
        Step{Bag{Pack{Numeric{80}, Numeric{1}}}, cart_discount, constraints_1};
    ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
              expected_product_one_history);

    const auto constraints_2 =
        constraints_applied ? Constraints{constraints[1]} : Constraints{};
    const auto expected_product_two_history =
        Step{Bag{Pack{Numeric{100}, Numeric{2}}}, cart_discount, constraints_2};
    ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
              expected_product_two_history);
  }
}

TEST(Pricing_Share_RUB, all_packs_are_united) {
  // скидка полностью размазывается по всем товарам, 2 пачки объеденяются в одну
  // [{150,1},{100,2}] -> [{90,3}]. Ограничение сработало.
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1})}, kRUB};

  AddBag(initial_pricing, product_one,
         {Pack{Numeric{150}, Numeric{1}}, Pack{Numeric{100}, Numeric{2}}});

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{90});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{120}, initial_pricing, constraints, dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{90}, Numeric{3}}}, dummy_discount, constraints};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_RUB, pack_is_split_1) {
  // Скидка по возможности распределяется без округления, с учётом минимальной
  // цены. Расщепление предпочтительнее округления. Пачка распадается на 2
  // [{20,10}] -> [{11,5},{12,5}]
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{20}, Numeric{10})}, kRUB};

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{10});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{85}, initial_pricing, constraints, dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{11}, Numeric{5}}, Pack{Numeric{12}, Numeric{5}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_RUB, pack_is_split_2) {
  // 2 пачки, к одной скидку нельзя применить, вторая распадается на 2
  // [{10,2},{20,7}] -> [{10,2},{14,2},{15,5}]
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{20}, Numeric{10})}, kRUB};
  AddBag(initial_pricing, product_one,
         {Pack{Numeric{10}, Numeric{2}}, Pack{Numeric{20}, Numeric{7}}});

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{10});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{37}, initial_pricing, constraints, dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{10}, Numeric{2}}, Pack{Numeric{15}, Numeric{5}},
               Pack{Numeric{14}, Numeric{2}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_RUB, pack_is_split_3) {
  // 3 продукта, на 2 скидка применяется полностью, 3ий  расщепляется
  // [{100,1},{90,2},{80,3}] -> [{90,1},{70,2},{57,2},{56,1}]
  // Скидка 10+20*2+23*2+24=120
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1}),
               ProductPricing(product_two, Numeric{90}, Numeric{2}),
               ProductPricing(product_three, Numeric{80}, Numeric{3})},
              kRUB};

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = Constraints{
      SingleProductConstraint{product_one, MinimalPrice{Numeric{90}}},
      SingleProductConstraint{product_two, MinimalPrice{Numeric{70}}},
      SingleProductConstraint{product_three, MinimalPrice{Numeric{50}}}};

  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{120}, initial_pricing, constraints, dummy_discount);

  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{90}, Numeric{1}}}, dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{70}, Numeric{2}}}, dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);

  const auto expected_product_three_history =
      Step{Bag{Pack{Numeric{57}, Numeric{2}}, Pack{Numeric{56}, Numeric{1}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_three)->steps.back(),
            expected_product_three_history);
}

TEST(Pricing_Share_RUB, spread_min_value) {
  // Количество товаров(100) больше чем общая скидка(70)
  // На первые 70 товаров применяется скидка 1 руб.
  Pricing initial_pricing{kRUB};
  auto generate_id = [](int i) {
    return ProductId{(i < 10 ? "product_0" : "product_") + std::to_string(i)};
  };
  for (int i = 0; i < 100; ++i) {
    initial_pricing.product_pricings.push_back(
        ProductPricing{generate_id(i), Numeric{20}, Numeric{1}});
  }

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{0});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{70}, initial_pricing, constraints, dummy_discount);
  const auto applied_discount =
      Step{Bag{Pack{Numeric{19}, Numeric{1}}}, dummy_discount};
  const auto not_applied_discount =
      Step{Bag{Pack{Numeric{20}, Numeric{1}}}, dummy_discount};
  for (int i = 0; i < 100; ++i) {
    ASSERT_EQ(History(resulting_pricing, generate_id(i))->steps.back(),
              i < 70 ? applied_discount : not_applied_discount);
  }
}

TEST(Pricing_Share_ILS, uniform_discount_is_shared_greedily) {
  // 2.5 - 1, 4.3 - 2, скидка 1.7
  auto initial_pricing = Pricing{
      {ProductPricing(product_one, Numeric::FromFloatInexact(2.5), Numeric{1}),
       ProductPricing(product_two, Numeric::FromFloatInexact(4.3), Numeric{2})},
      kILS};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{2});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric::FromFloatInexact(1.7), initial_pricing, constraints,
      cart_discount);
  const auto expected_product_one_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(2.0), Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(3.7), Numeric{2}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

TEST(Pricing_Share_ILS, discount_is_shared_different_constraints) {
  // Ограничения влияют на распределение, но не записываются в историю, если
  // удаётся полностью распределить скидку по товарам.

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = Constraints{
      SingleProductConstraint{product_one, MinimalPrice{Numeric{2}}},
      SingleProductConstraint{product_two, MinimalPrice{Numeric{3}}}};

  for (auto constraints_applied : {false, true}) {
    auto initial_pricing =
        Pricing{{ProductPricing(product_one, Numeric::FromFloatInexact(2.5),
                                Numeric{1}),
                 ProductPricing(product_two, Numeric::FromFloatInexact(4.3),
                                Numeric{2})},
                kILS};

    const auto discount = constraints_applied ? Numeric::FromFloatInexact(3.2)
                                              : Numeric::FromFloatInexact(3.1);
    const auto resulting_pricing = grocery_discounts_calculator::Share(
        discount, initial_pricing, constraints, cart_discount);

    const auto constraints_1 =
        constraints_applied ? Constraints{constraints[0]} : Constraints{};
    const auto expected_product_one_history =
        Step{Bag{Pack{Numeric{2}, Numeric{1}}}, cart_discount, constraints_1};
    ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
              expected_product_one_history);

    const auto constraints_2 =
        constraints_applied ? Constraints{constraints[1]} : Constraints{};
    const auto expected_product_two_history =
        Step{Bag{Pack{Numeric{3}, Numeric{2}}}, cart_discount, constraints_2};
    ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
              expected_product_two_history);
  }
}

TEST(Pricing_Share_ILS, all_packs_are_united) {
  // скидка полностью размазывается по всем товарам, 2 пачки объеденяются в одну
  // [{2.5,1},{4.7,2}] -> [{1.8,3}]. Ограничение сработало.
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{10}, Numeric{1})}, kILS};

  AddBag(initial_pricing, product_one,
         {Pack{Numeric::FromFloatInexact(2.5), Numeric{1}},
          Pack{Numeric::FromFloatInexact(4.7), Numeric{2}}});

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints =
      GetMinimalPriceEveryProductConstraint(Numeric::FromFloatInexact(1.8));
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{10}, initial_pricing, constraints, dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric::FromFloatInexact(1.8), Numeric{3}}},
           dummy_discount, constraints};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_ILS, pack_is_split_1) {
  // Пачка распадается на 2 [{5.7,7}] -> [{5.1,3},{5.2,4}]
  auto initial_pricing = Pricing{
      {ProductPricing(product_one, Numeric::FromFloatInexact(5.7), Numeric{7})},
      kILS};

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints =
      GetMinimalPriceEveryProductConstraint(Numeric::FromFloatInexact(4.9));
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric::FromFloatInexact(3.8), initial_pricing, constraints,
      dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric::FromFloatInexact(5.2), Numeric{4}},
               Pack{Numeric::FromFloatInexact(5.1), Numeric{3}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_ILS, pack_is_split_2) {
  // 2 пачки, к одной скидку нельзя применить, вторая распадается на 2
  // [{4.9,2},{5.7,7}] -> [{4.9,2},{5.1,3},{5.2,4}]
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{10}, Numeric{10})}, kILS};

  AddBag(initial_pricing, product_one,
         {Pack{Numeric::FromFloatInexact(4.9), Numeric{2}},
          Pack{Numeric::FromFloatInexact(5.7), Numeric{7}}});

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints =
      GetMinimalPriceEveryProductConstraint(Numeric::FromFloatInexact(4.9));
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric::FromFloatInexact(3.8), initial_pricing, constraints,
      dummy_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric::FromFloatInexact(4.9), Numeric{2}},
               Pack{Numeric::FromFloatInexact(5.2), Numeric{4}},
               Pack{Numeric::FromFloatInexact(5.1), Numeric{3}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);
}

TEST(Pricing_Share_ILS, spread_min_value) {
  // Количество товаров(100) больше чем общая скидка(7)
  // На первые 70 товаров применяется скидка 0.1 ILS
  Pricing initial_pricing{kILS};
  auto generate_id = [](int i) {
    return ProductId{(i < 10 ? "product_0" : "product_") + std::to_string(i)};
  };
  for (int i = 0; i < 100; ++i) {
    initial_pricing.product_pricings.push_back(
        ProductPricing{generate_id(i), Numeric{20}, Numeric{1}});
  }

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{0});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{7}, initial_pricing, constraints, dummy_discount);
  const auto applied_discount = Step{
      Bag{Pack{Numeric::FromFloatInexact(19.9), Numeric{1}}}, dummy_discount};
  const auto not_applied_discount =
      Step{Bag{Pack{Numeric{20}, Numeric{1}}}, dummy_discount};
  for (int i = 0; i < 100; ++i) {
    ASSERT_EQ(History(resulting_pricing, generate_id(i))->steps.back(),
              i < 70 ? applied_discount : not_applied_discount);
  }
}

TEST(Pricing_Share_ILS, pack_is_split_3) {
  // 3 товара, на 2 скидка применяется полностью, 3ий расщепляется
  // [{15.9,1},{14.8,2},{11.2,3}] -> [{14.8,1},{12.5,2},{8.4,2},{8.5,1}]
  // Скидка 1.1+2.3*2+2.8*2+2.7=14
  auto initial_pricing = Pricing{
      {ProductPricing(product_one, Numeric::FromFloatInexact(15.9), Numeric{1}),
       ProductPricing(product_two, Numeric::FromFloatInexact(14.8), Numeric{2}),
       ProductPricing(product_three, Numeric::FromFloatInexact(11.2),
                      Numeric{3})},
      kILS};

  const auto dummy_discount = GetDummyDiscount();
  const auto constraints = Constraints{
      SingleProductConstraint{product_one,
                              MinimalPrice{Numeric::FromFloatInexact(14.8)}},
      SingleProductConstraint{product_two,
                              MinimalPrice{Numeric::FromFloatInexact(12.5)}},
      SingleProductConstraint{product_three,
                              MinimalPrice{Numeric::FromFloatInexact(5.5)}}};

  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{14}, initial_pricing, constraints, dummy_discount);

  const auto expected_product_one_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(14.8), Numeric{1}}}, dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(12.5), Numeric{2}}}, dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);

  const auto expected_product_three_history =
      Step{Bag{Pack{Numeric::FromFloatInexact(8.4), Numeric{2}},
               Pack{Numeric::FromFloatInexact(8.5), Numeric{1}}},
           dummy_discount};
  ASSERT_EQ(History(resulting_pricing, product_three)->steps.back(),
            expected_product_three_history);
}

TEST(Pricing_Share, without_constraints) {
  // Ограничения отсутсвуют, на каждый товар применилась скидка 600/3=200
  // Стоимость первого товара стала отрицательной.
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1}),
               ProductPricing(product_two, Numeric{200}, Numeric{2})},
              kRUB};

  const auto cart_discount = GetDummyDiscount();
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{600}, initial_pricing, Constraints{}, cart_discount);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{-100}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{0}, Numeric{2}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

TEST(Pricing_Share, priorited_share_uniform) {
  // 1 товар - 100 руб. 2 товара - 200 руб. скидка 100 руб., ограничение на
  // каждый 90 руб. приоритет размазывания равномерный. на первый скидка 10, на
  // оставшиеся (100-10) / 2 = 45
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{100}, Numeric{1}),
               ProductPricing(product_two, Numeric{200}, Numeric{2})},
              kRUB};

  const auto share_policy =
      SharePolicyPriority{[](const ProductId&) { return Numeric{}; }};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{90});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{100}, initial_pricing, constraints, cart_discount, {},
      share_policy);
  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{90}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{155}, Numeric{2}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

TEST(Pricing_Share, priorited_share_by_price) {
  // 1 товар - 50 руб. 2 товара - 100 руб. 1 товар - 150 руб. скидка 201 руб.
  // приоритет размазывания по стоимости. ограничение на товар - 10 руб.
  // на второй товар скидка 140 руб, на третий 31 + 30.
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{50}, Numeric{3}),
               ProductPricing(product_two, Numeric{150}, Numeric{1}),
               ProductPricing(product_three, Numeric{100}, Numeric{2})},
              kRUB};

  std::unordered_map<ProductId, Numeric> priorities;
  for (const auto& product_pricing : initial_pricing.product_pricings) {
    const auto& pack = *product_pricing.CurrentBag().begin();
    priorities[product_pricing.id] = pack.price;
  }

  const auto share_policy = SharePolicyPriority{
      [&priorities](const ProductId& id) { return priorities[id]; }};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{10});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{201}, initial_pricing, constraints, cart_discount, {},
      share_policy);

  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{50}, Numeric{3}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{10}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);

  const auto expected_product_three_history =
      Step{Bag{Pack{Numeric{69}, Numeric{1}}, Pack{Numeric{70}, Numeric{1}}},
           cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_three)->steps.back(),
            expected_product_three_history);
}

TEST(Pricing_Share, priorited_share_fair) {
  // 1 товар - 50 руб. 1 товар - 200 руб. 3 товара - 50руб. скидка 100 руб.
  // приоритет размазывания по стоимости.
  // на первый скидка 20, на второй 80, на третий - не осталось. 20/50 == 80/200
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{50}, Numeric{1}),
               ProductPricing(product_two, Numeric{200}, Numeric{1}),
               ProductPricing(product_three, Numeric{50}, Numeric{3})},
              kRUB};

  std::unordered_map<ProductId, Numeric> priorities;
  priorities[product_one] = Numeric{1};
  priorities[product_two] = Numeric{1};
  priorities[product_three] = Numeric{0};

  const auto share_policy = SharePolicyPriority{
      [&priorities](const ProductId& id) { return priorities[id]; },
      SharePolicyFair{},
  };

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{0});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric{100}, initial_pricing, constraints, cart_discount, {},
      share_policy);

  const auto expected_product_one_history =
      Step{Bag{Pack{Numeric{30}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history =
      Step{Bag{Pack{Numeric{120}, Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);

  const auto expected_product_three_history =
      Step{Bag{Pack{Numeric{50}, Numeric{3}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_three)->steps.back(),
            expected_product_three_history);
}

TEST(Pricing_Share, fair_with_large_sum) {
  // тест пропорционального размазывания маленькой скидки на большую стоимоcть
  // товаров. алгоритм fair не сможет отработать, скидка доразмажется через
  // uniform + greedy алгоритмы
  auto initial_pricing =
      Pricing{{ProductPricing(product_one, Numeric{900}, Numeric{1}),
               ProductPricing(product_two, Numeric{100}, Numeric{1})},
              Numeric::FromFloatInexact(0.01)};

  const auto cart_discount = GetDummyDiscount();
  const auto constraints = GetMinimalPriceEveryProductConstraint(Numeric{0});
  const auto resulting_pricing = grocery_discounts_calculator::Share(
      Numeric::FromFloatInexact(0.06), initial_pricing, constraints,
      cart_discount, {}, SharePolicyFair{});
  const auto expected_product_one_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(899.97), Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_history);

  const auto expected_product_two_history = Step{
      Bag{Pack{Numeric::FromFloatInexact(99.97), Numeric{1}}}, cart_discount};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_history);
}

}  // namespace grocery_discounts_calculator
