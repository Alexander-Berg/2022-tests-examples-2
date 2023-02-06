#include <grocery-discounts-calculator/apply.hpp>
#include <grocery-discounts-calculator/modifier/item_discount.hpp>

#include <grocery-discounts-calculator/modifier.hpp>
#include <grocery-discounts-calculator/pricing.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_discounts_calculator {

namespace {

using ProductId = grocery_shared::ProductId;
using ComboId = grocery_shared::ComboId;
using grocery_pricing::Numeric;

const ProductId product_1{"product-1"};
const ProductId product_2{"product-2"};
const ProductId product_3{"product-3"};
const ProductId product_4{"product-4"};
const ProductId product_5{"product-5"};

const ProductId combo_id{"combo_id"};

Pricing GetPricing(ProductPricings pricings) {
  return Pricing{std::move(pricings), Numeric{1}};
}

BundleDiscountV2 MakeDiscountV2(
    const std::unordered_map<ProductId, Numeric>& items,
    const PaymentRule& payment_rule, Numeric bundle_count = Numeric{1},
    ComboId id = ComboId{"bundle_id"}) {
  std::vector<handlers::libraries::grocery_discounts_calculator::BundleItem>
      bundle_items;
  for (const auto& [id, quantity] : items) {
    bundle_items.push_back({id, quantity});
  }
  return BundleDiscountV2{
      id, {{std::move(bundle_items)}}, payment_rule, {}, bundle_count};
}

void AssertNotChanged(const std::vector<ProductId>& non_changed_products,
                      const Pricing& pricing) {
  for (const auto& product_id : non_changed_products) {
    auto hist = History(pricing, product_id);
    ASSERT_EQ(hist->steps.size(), 1);
  }
}

}  // namespace

// проверяем скидку на набор в размере 10 у.е.
// скидка размазывается только на товары набора
// product-1 4 единицы product-2 3 единицы product-3 3 единицы
TEST(Pricing_Apply_Bundle_V2, absolute_discount) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{1}},
                  ProductPricing{product_2, Numeric{100}, Numeric{1}},
                  ProductPricing{product_3, Numeric{100}, Numeric{1}},
                  ProductPricing{product_4, Numeric{100}, Numeric{1}},
                  ProductPricing{product_5, Numeric{100}, Numeric{1}}});

  const auto discount = MakeDiscountV2({{product_1, Numeric{1}},
                                        {product_2, Numeric{1}},
                                        {product_3, Numeric{1}}},
                                       AbsoluteMoneyPayment{Numeric{10}});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  AssertNotChanged({product_4, product_5}, resulting_pricing);
  auto kek = History(resulting_pricing, product_1)->steps.back();
  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{96}, Numeric{1}}}, discount}));
  ASSERT_EQ(History(resulting_pricing, product_2)->steps.back(),
            (Step{Bag{Pack{Numeric{97}, Numeric{1}}}, discount}));
  ASSERT_EQ(History(resulting_pricing, product_3)->steps.back(),
            (Step{Bag{Pack{Numeric{97}, Numeric{1}}}, discount}));
}

// проверяем скидку на набор в размере 10 процентов. Скидка высчитвается на
// основе цен товаров в наборе. (100 + 200 * 2 + 100) * 0,1 = 40 и равномерно
// размазывается на товары набора - каждому продукту по 25 у.е.
TEST(Pricing_Apply_Bundle_V2, fraction_discount) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{1}},
                  ProductPricing{product_2, Numeric{200}, Numeric{2}},
                  ProductPricing{product_3, Numeric{100}, Numeric{1}},
                  ProductPricing{product_4, Numeric{100}, Numeric{1}}});

  const auto discount = MakeDiscountV2({{product_1, Numeric{1}},
                                        {product_2, Numeric{2}},
                                        {product_3, Numeric{1}}},
                                       RelativeMoneyPayment{Numeric{10}});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  AssertNotChanged({product_4}, resulting_pricing);
  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{85}, Numeric{1}}}, discount}));
  ASSERT_EQ(History(resulting_pricing, product_2)->steps.back(),
            (Step{Bag{Pack{Numeric{185}, Numeric{2}}}, discount}));
  ASSERT_EQ(History(resulting_pricing, product_3)->steps.back(),
            (Step{Bag{Pack{Numeric{85}, Numeric{1}}}, discount}));
}

// скидка на набор может расщипить товар на пачки. Изначально
// product-1 [{p: 100 q: 3}]
// product-2 [{p: 100 q: 2}]
// после применения скидки на набор [product-1 q: 1, product-2 q : 1]
// product-1 расщепляется на несколько пачек
// product-1 [{p: 97 q: 2}, {p: 98 q: 1}]
// product-1 [{p: 98 q: 2}]
TEST(Pricing_Apply_Bundle_V2, discount_split_items) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{3}},
                  ProductPricing{product_2, Numeric{100}, Numeric{2}}});

  const auto discount =
      MakeDiscountV2({{product_1, Numeric{2}}, {product_2, Numeric{2}}},
                     AbsoluteMoneyPayment{Numeric{12}});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  ASSERT_EQ(
      History(resulting_pricing, product_1)->steps.back(),
      (Step{Bag{Pack{Numeric{97}, Numeric{2}}, Pack{Numeric{98}, Numeric{1}}},
            discount}));
  ASSERT_EQ(History(resulting_pricing, product_2)->steps.back(),
            (Step{Bag{Pack{Numeric{98}, Numeric{2}}}, discount}));
}

// Проверяем что скидка на набор корректно применяется, если в корзине один и
// тот же бандл представлен несколько раз. Изначально:
// product-1 [{p: 100 q: 3}]
// product-2 [{p: 100 q: 2}]
// после применения скидки на набор [product-1 q: 1, product-2 q : 1],
// размере 12*2=24 у.е (набор встречается 2 раза) product-2 расщепляется на
// несколько пачек:
// product-1 [{p: 95 q: 3}]
// product-2 [{p: 95 q: 1}, {p: 96 q: 1}]
TEST(Pricing_Apply_Bundle_V2, discount_several_bundles_absolute) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{3}},
                  ProductPricing{product_2, Numeric{100}, Numeric{2}}});

  const auto discount =
      MakeDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{1}}},
                     AbsoluteMoneyPayment{Numeric{12}}, Numeric{2});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{95}, Numeric{3}}}, discount}));
  ASSERT_EQ(
      History(resulting_pricing, product_2)->steps.back(),
      (Step{Bag{Pack{Numeric{95}, Numeric{1}}, Pack{Numeric{96}, Numeric{1}}},
            discount}));
}

// Проверяем скидку на набор в размере 6 процентов. Изначально:
// product-1 [{p: 100 q: 3}]
// product-2 [{p: 100 q: 2}]
// после применения скидки на набор [product-1 q: 1, product-2 q : 1],
// размере (100+100)*0,06*2=24 у.е (набор встречается 2 раза) product-2
// расщепляется на несколько пачек:
// product-1 [{p: 95 q: 3}]
// product-2 [{p: 95 q: 1}, {p: 96 q: 1}]
TEST(Pricing_Apply_Bundle_V2, discount_several_bundles_relative) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{3}},
                  ProductPricing{product_2, Numeric{100}, Numeric{2}}});

  const auto discount =
      MakeDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{1}}},
                     RelativeMoneyPayment{Numeric{6}}, Numeric{2});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{95}, Numeric{3}}}, discount}));
  ASSERT_EQ(
      History(resulting_pricing, product_2)->steps.back(),
      (Step{Bag{Pack{Numeric{95}, Numeric{1}}, Pack{Numeric{96}, Numeric{1}}},
            discount}));
}

// скидка на набор не применяется, если какого либо товаров меньше чем требуется
// для набора product-1 1 в pricing, 2 требуется для набора
TEST(Pricing_Apply_Bundle_V2, not_enough_product) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{1}},
                  ProductPricing{product_2, Numeric{100}, Numeric{1}}});

  const auto discount =
      MakeDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{2}}},
                     AbsoluteMoneyPayment{Numeric{12}});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});
  AssertNotChanged({product_1, product_2}, resulting_pricing);
}

// скидка на набор не применяется, если какого либо товаров меньше чем требуется
// для набора product-1 1 в pricing, 2 требуется для набора
TEST(Pricing_Apply_Bundle_V2, product_is_missing) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{1}}});

  const auto discount =
      MakeDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{2}}},
                     AbsoluteMoneyPayment{Numeric{12}});

  const auto modifiers = std::vector{discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});
  AssertNotChanged({product_1}, resulting_pricing);
}

// Проверяем скидку на наборы в размере 10 процентов. Изначально:
// product-1 [{p: 100 q: 1}]
// product-2 [{p: 100 q: 2}]
// product-2 [{p: 100 q: 1}]
// после первой применения скидки на набор:
// product-1 [{p: 93 q: 1}]
// product-2 [{p: 93 q: 1}, {p: 94 q: 1}]
// product-2 [{p: 100 q: 1}]
// после второй применения скидки на набор:
// product-1 [{p: 93 q: 1}]
// product-2 [{p: 86 q: 1}, {p: 87 q: 1}]
// product-2 [{p: 94 q: 1}]
TEST(Pricing_Apply_Bundle_V2, discount_two_bundle_modifiers) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{100}, Numeric{1}},
                  ProductPricing{product_2, Numeric{100}, Numeric{2}},
                  ProductPricing{product_3, Numeric{100}, Numeric{1}}});

  const auto discount_1 = MakeDiscountV2(
      {{product_1, Numeric{1}}, {product_2, Numeric{1}}},
      RelativeMoneyPayment{Numeric{10}}, Numeric{1}, ComboId{"bundle_1"});
  const auto discount_2 = MakeDiscountV2(
      {{product_2, Numeric{1}}, {product_3, Numeric{1}}},
      RelativeMoneyPayment{Numeric{10}}, Numeric{1}, ComboId{"bundle_2"});

  auto resulting_pricing =
      Apply(std::vector{discount_1}, initial_pricing, Constraints{});

  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{93}, Numeric{1}}}, discount_1}));
  ASSERT_EQ(
      History(resulting_pricing, product_2)->steps.back(),
      (Step{Bag{Pack{Numeric{93}, Numeric{1}}, Pack{Numeric{94}, Numeric{1}}},
            discount_1}));
  resulting_pricing =
      Apply(std::vector{discount_2}, resulting_pricing, Constraints{});
  ASSERT_EQ(
      History(resulting_pricing, product_2)->steps.back(),
      (Step{Bag{Pack{Numeric{86}, Numeric{1}}, Pack{Numeric{87}, Numeric{1}}},
            discount_2}));
  ASSERT_EQ(History(resulting_pricing, product_3)->steps.back(),
            (Step{Bag{Pack{Numeric{94}, Numeric{1}}}, discount_2}));
}

// Проверяем скидку на наборы в размере 10 процентов вместе с другими скидками.
// Изначально:
// product-1 [{p: 110 q: 1}]
// product-2 [{p: 110 q: 1}]
// после скидок на товары:
// product-1 [{p: 100 q: 1}]
// product-2 [{p: 100 q: 1}]
// после применения скидки на набор:
// product-1 [{p: 90 q: 1}]
// product-2 [{p: 90 q: 1}]
TEST(Pricing_Apply_Bundle_V2, discount_modifiers_with_other_discounts) {
  auto initial_pricing =
      GetPricing({ProductPricing{product_1, Numeric{110}, Numeric{1}},
                  ProductPricing{product_2, Numeric{110}, Numeric{1}}});
  const auto product_1_discount =
      MakeItemDiscount(product_1, AbsoluteMoneyPayment{Numeric{10}});
  const auto product_2_discount =
      MakeItemDiscount(product_2, AbsoluteMoneyPayment{Numeric{10}});
  auto resulting_pricing =
      Apply(std::vector{product_1_discount, product_2_discount},
            initial_pricing, Constraints{});

  const auto discount = MakeDiscountV2(
      {{product_1, Numeric{1}}, {product_2, Numeric{1}}},
      RelativeMoneyPayment{Numeric{10}}, Numeric{1}, ComboId{"bundle_1"});

  resulting_pricing =
      Apply(std::vector{discount}, resulting_pricing, Constraints{});

  ASSERT_EQ(History(resulting_pricing, product_1)->steps.back(),
            (Step{Bag{Pack{Numeric{90}, Numeric{1}}}, discount}));
  ASSERT_EQ(History(resulting_pricing, product_2)->steps.back(),
            (Step{Bag{Pack{Numeric{90}, Numeric{1}}}, discount}));
}

}  // namespace grocery_discounts_calculator
