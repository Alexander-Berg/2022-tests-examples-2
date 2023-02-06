#include <grocery-discounts-calculator/apply.hpp>

#include <grocery-discounts-calculator/modifier.hpp>
#include <grocery-discounts-calculator/pricing.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_discounts_calculator {

using ProductId = grocery_shared::ProductId;
using grocery_pricing::Numeric;

namespace {
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

}  // namespace

// История сохраняется в порядке применения модификаторов.
TEST(Pricing_Apply, history_is_chronological) {
  auto initial_pricing =
      Pricing{{ProductPricing(ProductId{"asdf"}, Numeric{100}, Numeric{1})},
              Numeric{1}};

  const auto asdf_discount_first =
      MakeItemDiscount(ProductId{"asdf"}, AbsoluteMoneyPayment{Numeric{20}});
  const auto asdf_discount_second =
      MakeItemDiscount(ProductId{"asdf"}, RelativeMoneyPayment{Numeric{10}});
  const auto modifiers = std::vector{asdf_discount_first, asdf_discount_second};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_asdf_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{1}}}},
      Step{Bag{Pack{Numeric{80}, Numeric{1}}}, asdf_discount_first},
      Step{Bag{Pack{Numeric{72}, Numeric{1}}}, asdf_discount_second}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"asdf"})->steps,
            expected_asdf_history);
}

// На применение модификаторов могут быть наложены ограничения.
TEST(Pricing_Apply, constraints) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{2})},
      Numeric{1}};

  const auto discount_one = MakeItemDiscount(ProductId{"product-one"},
                                             AbsoluteMoneyPayment{Numeric{50}});
  const auto discount_two = MakeItemDiscount(
      ProductId{"product-two"}, AbsoluteMoneyPayment{Numeric{100}});
  const auto modifiers = std::vector{discount_one, discount_two};

  const auto constraint = SingleProductConstraint{ProductId{"product-one"},
                                                  MinimalPrice{Numeric{60}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{1}}}},
      Step{Bag{Pack{Numeric{60}, Numeric{1}}}, discount_one, {constraint}}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{2}}}},
                  Step{Bag{Pack{Numeric{100}, Numeric{2}}}, discount_two}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// Ограничение может быть наложено сразу на все товары.
TEST(Pricing_Apply, every_product_constraint) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{9})},
      Numeric{1}};

  const auto discount_one = MakeItemDiscount(ProductId{"product-one"},
                                             AbsoluteMoneyPayment{Numeric{50}});
  const auto discount_two = MakeItemDiscount(
      ProductId{"product-two"}, AbsoluteMoneyPayment{Numeric{150}});
  const auto modifiers = std::vector{discount_one, discount_two};

  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{79}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{1}}}},
      Step{Bag{Pack{Numeric{79}, Numeric{1}}}, discount_one, {constraint}}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history = std::vector{
      Step{Bag{Pack{Numeric{200}, Numeric{9}}}},
      Step{Bag{Pack{Numeric{79}, Numeric{9}}}, discount_two, {constraint}}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// Скидка на корзину размазывается по товарам.
// Ограничения сработали на всех товарах
TEST(Pricing_Apply, cart_discount_is_shared) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, RelativeMoneyPayment{Numeric{50}}}});
  const auto modifiers = std::vector{cart_discount};

  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{99}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);
  const auto apply_result = CartApplyMoneyResult{Numeric{850}, Numeric{710}, 0};

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
                  Step{Bag{Pack{Numeric{99}, Numeric{3}}}, cart_discount,
                       constraints, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{99}, Numeric{7}}}, cart_discount,
                       constraints, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// порог на корзину большой, скидка не применяется
TEST(Pricing_Apply, cart_discount_not_applied) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{5000}, RelativeMoneyPayment{Numeric{50}}}});
  const auto modifiers = std::vector{cart_discount};

  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{99}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);
  const auto apply_result = CartApplyMoneyResult{Numeric{0}, Numeric{0}, {}};

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
                  Step{Bag{Pack{Numeric{100}, Numeric{3}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{200}, Numeric{7}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// несколько порогов на корзину выбирается подходящий
// корзина 1700 -> скидка от 1000, 100 р.
TEST(Pricing_Apply, cart_discount_correct_step_1) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{1000}, AbsoluteMoneyPayment{Numeric{100}}},
       CartDiscountStep{Numeric{2000}, AbsoluteMoneyPayment{Numeric{500}}}});
  const auto modifiers = std::vector{cart_discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto apply_result = CartApplyMoneyResult{Numeric{100}, Numeric{100}, 0};

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
      Step{
          Bag{Pack{Numeric{90}, Numeric{3}}}, cart_discount, {}, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{190}, Numeric{7}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// несколько порогов на корзину выбирается подходящий
// корзина 1700 -> скидка от 1700, 200 р.
TEST(Pricing_Apply, cart_discount_correct_step_2) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{1000}, AbsoluteMoneyPayment{Numeric{100}}},
       CartDiscountStep{Numeric{1700}, AbsoluteMoneyPayment{Numeric{200}}},
       CartDiscountStep{Numeric{2000}, AbsoluteMoneyPayment{Numeric{500}}}});
  const auto modifiers = std::vector{cart_discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto apply_result = CartApplyMoneyResult{Numeric{200}, Numeric{200}, 1};
  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
      Step{
          Bag{Pack{Numeric{80}, Numeric{3}}}, cart_discount, {}, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{180}, Numeric{7}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// Скидка на корзину применяется по порогу.
TEST(Pricing_Apply, cart_discount_threshold) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto this_is_too_much = Numeric{100500};
  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{this_is_too_much, AbsoluteMoneyPayment{Numeric{50}}}});
  const auto modifiers = std::vector{cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto apply_result = CartApplyMoneyResult{Numeric{0}, Numeric{0}, {}};

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
                  Step{Bag{Pack{Numeric{100}, Numeric{3}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{200}, Numeric{7}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

// Применение скидки зависит от количества единиц товара.
TEST(Pricing_Apply, quantity_matters) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-two"}, Numeric{100}, Numeric{2}),
       ProductPricing(ProductId{"product-three"}, Numeric{100}, Numeric{3})},
      Numeric{1}};

  const auto product_two_discount = MakeItemDiscount(
      ProductId{"product-two"}, ProductPayment{Numeric{2}, {Numeric{30}}});
  const auto product_three_discount = MakeItemDiscount(
      ProductId{"product-three"}, ProductPayment{Numeric{2}, {Numeric{70}}});
  const auto modifiers =
      std::vector{product_two_discount, product_three_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_two_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{2}}}},
      Step{Bag{Pack{Numeric{85}, Numeric{2}}}, product_two_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);

  const auto expected_product_three_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
      Step{Bag{Pack{Numeric{77}, Numeric{2}}, Pack{Numeric{76}, Numeric{1}}},
           product_three_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-three"})->steps,
            expected_product_three_history);
}

//скидка 150% от 3 товаров, в пачке 3 товара
TEST(Pricing_Apply, one_free) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3})},
      Numeric{1}};

  const auto product_discount = MakeItemDiscount(
      ProductId{"product-one"}, ProductPayment{Numeric{3}, {Numeric{150}}});
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
                  Step{Bag{Pack{Numeric{50}, Numeric{3}}}, product_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_history);
}

//скидка 150% от 3 товаров, в пачке 5 товаров. Скидка размызывается на все.
TEST(Pricing_Apply, item_discount_shared) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{5})},
      Numeric{1}};

  const auto product_discount = MakeItemDiscount(
      ProductId{"product-one"}, ProductPayment{Numeric{3}, {Numeric{150}}});
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{5}}}},
                  Step{Bag{Pack{Numeric{70}, Numeric{5}}}, product_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_history);
}

// Неприменённая скидка сохраняется в истории.
TEST(Pricing_Apply, non_applied_discount) {
  auto initial_pricing =
      Pricing{{ProductPricing(ProductId{"asdf"}, Numeric{100}, Numeric{1})},
              Numeric{1}};

  const auto product_discount = MakeItemDiscount(
      ProductId{"asdf"}, ProductPayment{Numeric{2}, {Numeric{20}}});
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{1}}}},
                  Step{Bag{Pack{Numeric{100}, Numeric{1}}}, product_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"asdf"})->steps,
            expected_history);
}

// Метаданные скидки сохраняются при применении.
TEST(Pricing_Apply, meta_is_forwarded) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"my-product"}, Numeric{111}, Numeric{3})},
      Numeric{1}};

  const auto meta =
      DiscountMeta{true, std::nullopt, "title", "subtitle", "color"};
  const auto product_discount = MakeItemDiscount(
      ProductId{"my-product"}, AbsoluteMoneyPayment{Numeric{11}}, meta);
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto& last_step =
      History(resulting_pricing, ProductId{"my-product"})->steps.back();
  ASSERT_TRUE(last_step.modifier.has_value());

  const auto& modifier = std::get<ItemDiscount>(*last_step.modifier);
  ASSERT_EQ(modifier.meta, meta);
}

// Кэшбек начисляется только на цену товара. Предыдущие начисления кэшбека не
// влияют на последующие начисления.
TEST(Pricing_Apply, cashback_is_gained_depending_on_price_only) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"cashback-product"}, Numeric{120}, Numeric{3})},
      Numeric{1}};

  const auto absolute_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, AbsoluteCashbackGain{Numeric{80}});
  const auto relative_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, RelativeCashbackGain{Numeric{10}});
  const auto modifiers = std::vector{absolute_gain, relative_gain};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_history = std::vector{
      Step{Bag{Pack{Numeric{120}, Numeric{3}}}},
      // Начислили 80 рублей.
      Step{Bag{Pack{Numeric{120}, Numeric{3}, Numeric{80}}}, absolute_gain},
      // Начислили ещё 120 * 10% = 12 рублей.
      Step{Bag{Pack{Numeric{120}, Numeric{3}, Numeric{92}}}, relative_gain}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"cashback-product"})->steps,
            expected_history);
}

// Существует глобальное ограничение на кэшбек.
TEST(Pricing_Apply, max_cashback_constraint) {
  auto initial_pricing = Pricing{{ProductPricing(ProductId{"cashback-product"},
                                                 Numeric{2000}, Numeric{3})},
                                 Numeric{1}};

  const auto absolute_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, AbsoluteCashbackGain{Numeric{1000}});
  const auto relative_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, RelativeCashbackGain{Numeric{10}});
  const auto modifiers = std::vector{absolute_gain, relative_gain};

  const auto constraint = EveryProductConstraint{MaximalCashback{Numeric{100}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);

  const auto expected_history =
      std::vector{Step{Bag{Pack{Numeric{2000}, Numeric{3}}}},
                  // Попытались начислить 1000 рублей.
                  Step{Bag{Pack{Numeric{2000}, Numeric{3}, Numeric{100}}},
                       absolute_gain,
                       {constraint}},
                  // Попытались начислить 2000 * 10% = 200 рублей.
                  Step{Bag{Pack{Numeric{2000}, Numeric{3}, Numeric{100}}},
                       relative_gain,
                       {constraint}}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"cashback-product"})->steps,
            expected_history);
}

// Скидка кэшбеком размазывается по всем товарам.
// Ограничения сработали на всех товарах
TEST(Pricing_Apply, cashback_discount_is_shared) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{3}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{7})},
      Numeric{1}};

  const auto cashback_discount =
      MakePlainCartDiscount(AbsoluteCashbackPayment{Numeric{2000}});
  const auto modifiers = std::vector{cashback_discount};

  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{99}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);

  // 1700 - суммарная цена корзины, мы не мжем применить скидку большую цены
  // корзины
  const auto apply_result =
      CartApplyMoneyResult{Numeric{1700}, Numeric{710}, 0};

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric{100}, Numeric{3}}}},
                  Step{Bag{Pack{Numeric{99}, Numeric{3}}}, cashback_discount,
                       constraints, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{7}}}},
                  Step{Bag{Pack{Numeric{99}, Numeric{7}}}, cashback_discount,
                       constraints, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);
}

//Скидка кэшбеком расщипляет пачку товаров
TEST(Pricing_Apply, cashback_discount_split_pack) {
  auto initial_pricing = Pricing{
      {ProductPricing{ProductId{"product-one"}, Numeric{70}, Numeric{5}}},
      Numeric{1}};

  const auto cashback_discount =
      MakePlainCartDiscount(AbsoluteCashbackPayment{Numeric{58}});
  const auto modifiers = std::vector{cashback_discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto apply_result = CartApplyMoneyResult{Numeric{58}, Numeric{58}, 0};

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{70}, Numeric{5}}}},
      Step{Bag{Pack{Numeric{58}, Numeric{3}}, Pack{Numeric{59}, Numeric{2}}},
           cashback_discount,
           {},
           apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// Скидка кэшбеком расщипляет пачку товаров на две
// из за минимальной цены на корзину
TEST(Pricing_Apply, cashback_discount_split_pack_for_min_price) {
  auto initial_pricing = Pricing{
      {ProductPricing{ProductId{"product-one"}, Numeric{70}, Numeric{5}}},
      Numeric{1}};

  const auto cashback_discount =
      MakePlainCartDiscount(AbsoluteCashbackPayment{Numeric{1000}}, Numeric{1});
  const auto modifiers = std::vector{cashback_discount};
  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{0}}};
  const auto constraints = Constraints{constraint};
  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);

  // Размазывается значение равное цена корзины(70*5) - минимальная цена
  // корзины(1)
  const auto apply_result = CartApplyMoneyResult{Numeric{349}, Numeric{349}, 0};
  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{70}, Numeric{5}}}},
      Step{Bag{Pack{Numeric{0}, Numeric{4}}, Pack{Numeric{1}, Numeric{1}}},
           cashback_discount,
           {},
           apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// Проверяем округление. Товары для которых округление не сработало, не хранят в
// истории модификатор.
TEST(Pricing_Apply, round_modifier_floor) {
  auto initial_pricing =
      Pricing{{ProductPricing{ProductId{"product-one"},
                              Numeric::FromFloatInexact(70.25), Numeric{5}},
               ProductPricing{ProductId{"product-two"},
                              Numeric::FromFloatInexact(50.1), Numeric{5}}},
              Numeric::FromFloatInexact(0.1)};

  const auto modifier =
      MakeRoundingModifier(initial_pricing.currency_min_value);
  const auto modifiers = std::vector{modifier};
  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric::FromFloatInexact(70.25), Numeric{5}}}},
      Step{Bag{Pack{Numeric::FromFloatInexact(70.2), Numeric{5}}}, modifier}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric::FromFloatInexact(50.1), Numeric{5}}}}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// Проверяем округление вверх
TEST(Pricing_Apply, round_modifier_ceil) {
  auto initial_pricing =
      Pricing{{ProductPricing{ProductId{"product-one"},
                              Numeric::FromFloatInexact(70.25), Numeric{5}}},
              Numeric::FromFloatInexact(0.1)};

  const auto modifier =
      MakeRoundingModifier(initial_pricing.currency_min_value, false);
  const auto modifiers = std::vector{modifier};
  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric::FromFloatInexact(70.25), Numeric{5}}}},
      Step{Bag{Pack{Numeric::FromFloatInexact(70.3), Numeric{5}}}, modifier}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// Проверяем что пачки объединяются в одну новую пачку
// цена - минимальная среди всех пачек,
// количество - сумма по всем пачкам
// кэшбек - максимальный среди всех пачек
TEST(Pricing_Apply, union_modifier) {
  auto initial_pricing = Pricing{
      {ProductPricing{ProductId{"product-one"}, Numeric{120}, Numeric{7}}},
      Numeric{1}};
  Bag bag = {Pack{Numeric{100}, Numeric{5}, Numeric{20}},
             Pack{Numeric{80}, Numeric{2}, Numeric{30}}};
  initial_pricing.product_pricings.begin()->Update(std::move(bag), {}, {});
  const auto modifier = MakePackUnionModifier();
  const auto modifiers = std::vector{modifier};
  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  auto product_history =
      History(resulting_pricing, ProductId{"product-one"})->steps;
  ASSERT_TRUE(product_history.size() == 3);
  const auto expected_last_step =
      Step{Bag{Pack{Numeric{80}, Numeric{7}, Numeric{30}}}, modifier};
  ASSERT_EQ(product_history.back(), expected_last_step);
}

// Проверяем что модификатор округления схлопывает пачки с одинаковой ценой.
TEST(Pricing_Apply, round_modifier_union) {
  ProductId product_one{"product-one"};
  ProductId product_two{"product-two"};
  auto initial_pricing =
      Pricing{{ProductPricing{product_one, Numeric::FromFloatInexact(100.0),
                              Numeric{3}},
               ProductPricing{product_two, Numeric::FromFloatInexact(100.0),
                              Numeric{3}}},
              Numeric::FromFloatInexact(0.1)};

  AddBag(initial_pricing, product_one,
         {Pack{Numeric::FromFloatInexact(90.97), Numeric{1}},
          Pack{Numeric::FromFloatInexact(90.96), Numeric{1}},
          Pack{Numeric::FromFloatInexact(90.95), Numeric{1}}});

  AddBag(initial_pricing, product_two,
         {Pack{Numeric::FromFloatInexact(90.97), Numeric{1}, Numeric{1}},
          Pack{Numeric::FromFloatInexact(90.96), Numeric{1}, Numeric{1}},
          Pack{Numeric::FromFloatInexact(90.95), Numeric{1}, Numeric{2}}});

  const auto modifier =
      MakeRoundingModifier(initial_pricing.currency_min_value);
  const auto modifiers = std::vector{modifier};
  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  const auto expected_product_one_last_step =
      Step{Bag{Pack{Numeric::FromFloatInexact(90.9), Numeric{3}}}, modifier};
  ASSERT_EQ(History(resulting_pricing, product_one)->steps.back(),
            expected_product_one_last_step);

  // Товары с разным количеством кэшбека не объединяются
  const auto expected_product_two_last_step =
      Step{Bag{Pack{Numeric::FromFloatInexact(90.9), Numeric{2}, Numeric{1}},
               Pack{Numeric::FromFloatInexact(90.9), Numeric{1}, Numeric{2}}},
           modifier};
  ASSERT_EQ(History(resulting_pricing, product_two)->steps.back(),
            expected_product_two_last_step);
}

// проверяем что скидка по товару не превышает заданный порог
TEST(Pricing_Apply, max_discount_constraint) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{10})},
      Numeric{1}};

  const auto discount_one = MakeItemDiscount(
      ProductId{"product-one"}, RelativeMoneyPayment{Numeric{10}, Numeric{5}});

  const auto modifiers = std::vector{discount_one};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric(100), Numeric{10}}}},
                  Step{Bag{Pack{Numeric(95), Numeric{10}}}, modifiers[0]}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// проверяем что скидка кэшбеком по товару не превышает заданный порог
TEST(Pricing_Apply, max_discount_cashback_constraint) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{10})},
      Numeric{1}};

  const auto discount_one =
      MakeItemDiscount(ProductId{"product-one"},
                       RelativeCashbackPayment{Numeric{10}, Numeric{5}});

  const auto modifiers = std::vector{discount_one};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_one_history =
      std::vector{Step{Bag{Pack{Numeric(100), Numeric{10}}}},
                  Step{Bag{Pack{Numeric(95), Numeric{10}}}, modifiers[0]}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);
}

// проверяем что кэшбек по товару не превышает заданный порог
TEST(Pricing_Apply, maximal_cashback_constraint) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{10})},
      Numeric{1}};

  const auto cashback_one = MakeItemDiscount(
      ProductId{"product-one"}, RelativeCashbackGain{Numeric{10}, Numeric{5}});

  const auto modifiers = std::vector{cashback_one};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{10}}}},
      Step{Bag{Pack{Numeric{100}, Numeric{10}, Numeric{5}}}, cashback_one}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_history);
}

// Проверяем, что начисление кешбека и скидка по корзине
// записываются в историю корзины
TEST(Pricing_Apply, cart_history) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1})},
      Numeric{1}};

  const auto cashback_gain = Numeric{10};
  const auto money_discount = Numeric{10};

  const auto cart_cashback_gain_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, AbsoluteCashbackGain{cashback_gain}}});

  const auto cart_money_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, AbsoluteMoneyPayment{money_discount}}});

  const auto modifiers =
      std::vector{cart_cashback_gain_discount, cart_money_discount};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  const auto cashback_gain_apply_result =
      CartApplyCashbackResult{cashback_gain, 0};

  const auto money_apply_result =
      CartApplyMoneyResult{Numeric{money_discount}, Numeric{money_discount}, 0};

  const auto expected_cart_history = std::vector{
      CartHistoryStep{
          cart_cashback_gain_discount, {}, cashback_gain_apply_result},
      CartHistoryStep{cart_money_discount, {}, money_apply_result}};
  ASSERT_EQ(resulting_pricing.cart_history, expected_cart_history);
}

// Проверяем что ограничения записываются в историю корзины
TEST(Pricing_Apply, cart_discount_constaints) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1})},
      Numeric{1}};

  const auto money_payment_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{100}, AbsoluteMoneyPayment{Numeric{50}}}});
  const auto modifiers = std::vector{money_payment_discount};

  const auto constraint = SingleProductConstraint{ProductId{"product-one"},
                                                  MinimalPrice{Numeric{90}}};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{constraint});

  const auto apply_result = CartApplyMoneyResult{Numeric{50}, Numeric{10}, 0};

  const auto expected_cart_history = std::vector{CartHistoryStep{
      money_payment_discount, Constraints{constraint}, apply_result}};
  ASSERT_EQ(resulting_pricing.cart_history, expected_cart_history);
}

// Проверяем, что кешбек корзины высчитывается
// в зависимости от цены корзины на данный момент
TEST(Pricing_Apply, cart_history_cashback_evaluation) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{1})},
      Numeric{1}};

  const auto absolute_gain = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, AbsoluteCashbackGain{Numeric{30}}}});

  const auto relative_gain = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, RelativeCashbackGain{Numeric{5}}}});

  const auto money_payment = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, AbsoluteMoneyPayment{Numeric{100}}}});

  const auto modifiers = {absolute_gain, money_payment, relative_gain,
                          absolute_gain};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  ASSERT_EQ(resulting_pricing.GetCartCashback(), Numeric{70});
}

// Проверяем что относительный кешбек по корзине не превышает заданный порог
TEST(Pricing_Apply, relative_cart_cashback_gain_max_constraint) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1})},
      Numeric{1}};

  const auto cashback_discount = MakeCartDiscount({CartDiscountStep{
      Numeric{50}, RelativeCashbackGain{Numeric{50}, Numeric{10}}}});
  const auto modifiers = std::vector{cashback_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  ASSERT_EQ(resulting_pricing.GetCartCashback(), Numeric{10});
}

// Проверяем что если ни один порог для скидки не пройден, то размазывается
// нужный apply result: для денег - деньги, кешбека - кешбек.
TEST(Pricing_Apply, cart_no_step_reached_scenario) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1})},
      Numeric{1}};

  const auto money_cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{1000}, AbsoluteMoneyPayment{Numeric{100}}}});
  const auto modifiers = std::vector{money_cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  CartApplyMoneyResult result = {Numeric{0}, Numeric{0}, std::nullopt};

  auto expected_cart_history =
      std::vector{CartHistoryStep{money_cart_discount, Constraints{}, result}};
  ASSERT_EQ(resulting_pricing.cart_history, expected_cart_history);

  const auto cashback_gain_cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{1000}, AbsoluteCashbackGain{Numeric{100}}}});

  const auto cashback_discount_resulting_pricing = Apply(
      std::vector{cashback_gain_cart_discount}, initial_pricing, Constraints{});

  CartApplyCashbackResult new_result = {std::nullopt, std::nullopt};

  auto cashback_discount_expected_cart_history = std::vector{
      CartHistoryStep{cashback_gain_cart_discount, Constraints{}, new_result}};

  ASSERT_EQ(cashback_discount_resulting_pricing.cart_history,
            cashback_discount_expected_cart_history);
}

// Проверяем, что ограничения на максимальный кешбек с корзины работает
TEST(Pricing_Apply, cart_cashback_gain_max_discount) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{1000}, Numeric{1})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{10}, RelativeCashbackGain{Numeric{100}}}}, {},
      {}, Numeric{5});
  const auto modifiers = std::vector{cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  CartApplyCashbackResult result = {Numeric{5}, 0};

  auto expected_cart_history =
      std::vector{CartHistoryStep{cart_discount, Constraints{}, result}};
  ASSERT_EQ(resulting_pricing.cart_history, expected_cart_history);
}

// Проверяем, что если не было скидки кешбеком на корзину, то
// вернется пустой optional
TEST(Pricing_Apply, cart_cashback_value_opt) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{1000}, Numeric{1})},
      Numeric{1}};

  const auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{10}, AbsoluteMoneyPayment{Numeric{100}}}});

  const auto modifiers = std::vector{cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  ASSERT_EQ(resulting_pricing.GetCartCashback(), std::nullopt);
}

// 8.3 * 0.1927 = 1.59941, округляем до 0.1 у.е 1.6
TEST(Pricing_Apply, item_discount_round_v1) {
  auto initial_pricing =
      Pricing{{ProductPricing(ProductId{"product-one"},
                              Numeric::FromFloatInexact(8.3), Numeric{2})},
              Numeric::FromFloatInexact(0.1)};

  const auto product_discount = MakeItemDiscount(
      ProductId{"product-one"},
      ProductPayment{Numeric{2}, {Numeric::FromFloatInexact(19.27)}});
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{}, 2);

  const auto expected_product_history =
      std::vector{Step{Bag{Pack{Numeric::FromFloatInexact(8.3), Numeric{2}}}},
                  Step{Bag{Pack{Numeric::FromFloatInexact(7.5), Numeric{2}}},
                       product_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_history);
}

// 345*0.32 = 110.4 -> округляем до 1 у.е. получаем 111
// 11 размазываем по товарам, первому 55 второму 56
TEST(Pricing_Apply, item_discount_round_v2) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{345}, Numeric{2})},
      Numeric{1}};

  const auto product_discount = MakeItemDiscount(
      ProductId{"product-one"}, ProductPayment{Numeric{2}, {Numeric{32}}});
  const auto modifiers = std::vector{product_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{}, 2);

  const auto expected_product_history = std::vector{
      Step{Bag{Pack{Numeric{345}, Numeric{2}}}},
      Step{Bag{Pack{Numeric{290}, Numeric{1}}, Pack{Numeric{289}, Numeric{1}}},
           product_discount}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_history);
}

// Тест размазывания нулевой скидки на корзину, которая меньше min_cart_price
TEST(Pricing_Apply, zero_discount) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{0}, Numeric{1})},
      Numeric{1}};

  const auto discount =
      MakePlainCartDiscount(AbsolutePromocodePayment{Numeric{0}}, Numeric{10});
  const auto modifiers = std::vector{discount};

  const auto apply_result = CartApplyMoneyResult{Numeric{0}, Numeric{0}, 0};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_product_history = std::vector{
      Step{Bag{Pack{Numeric{0}, Numeric{1}}}},
      Step{Bag{Pack{Numeric{0}, Numeric{1}}}, discount, {}, apply_result},
  };
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_history);
}

// скидка на корзину с исключениями. Значение скидки вычисляется с учетом
// исключений, но при этом скидка так же размызывтся на товары из исключений.
// Скидка на корзину 10% за исключением product-three, итоговая скидка =
// (100+200)*0,1=30. распредляется по каждому товару по 10
TEST(Pricing_Apply, cart_discount_with_exceptions) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{1}),
       ProductPricing(ProductId{"product-three"}, Numeric{300}, Numeric{1})},
      Numeric{1}};

  auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, RelativeMoneyPayment{Numeric{10}}}});
  cart_discount.exclusions =
      std::unordered_set<ProductId>{ProductId{"product-three"}};

  const auto modifiers = std::vector{cart_discount};

  const auto constraint = EveryProductConstraint{MinimalPrice{Numeric{0}}};
  const auto constraints = Constraints{constraint};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, constraints);
  const auto apply_result = CartApplyMoneyResult{Numeric{30}, Numeric{30}, 0};

  const auto expected_product_one_history = std::vector{
      Step{Bag{Pack{Numeric{100}, Numeric{1}}}},
      Step{
          Bag{Pack{Numeric{90}, Numeric{1}}}, cart_discount, {}, apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-one"})->steps,
            expected_product_one_history);

  const auto expected_product_two_history =
      std::vector{Step{Bag{Pack{Numeric{200}, Numeric{1}}}},
                  Step{Bag{Pack{Numeric{190}, Numeric{1}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-two"})->steps,
            expected_product_two_history);

  const auto expected_product_three_history =
      std::vector{Step{Bag{Pack{Numeric{300}, Numeric{1}}}},
                  Step{Bag{Pack{Numeric{290}, Numeric{1}}},
                       cart_discount,
                       {},
                       apply_result}};
  ASSERT_EQ(History(resulting_pricing, ProductId{"product-three"})->steps,
            expected_product_three_history);
}

// скидка на корзину кешбеком с исключениями. Скидка 10% на корзину за
// исключением product-three и равна (100+200)*0,1=30 баллов кешбека.
TEST(Pricing_Apply, cart_cashback_with_exceptions) {
  auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-one"}, Numeric{100}, Numeric{1}),
       ProductPricing(ProductId{"product-two"}, Numeric{200}, Numeric{1}),
       ProductPricing(ProductId{"product-three"}, Numeric{300}, Numeric{1})},
      Numeric{1}};

  auto cart_cashback_gain_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{50}, RelativeCashbackGain{Numeric{10}}}});
  cart_cashback_gain_discount.exclusions =
      std::unordered_set<ProductId>{ProductId{"product-three"}};
  const auto modifiers = std::vector{cart_cashback_gain_discount};

  const auto resulting_pricing = Apply(modifiers, initial_pricing, {});

  const auto cashback_gain_apply_result =
      CartApplyCashbackResult{Numeric{30}, 0};
  const auto expected_cart_history = std::vector{CartHistoryStep{
      cart_cashback_gain_discount, {}, cashback_gain_apply_result}};
  ASSERT_EQ(resulting_pricing.cart_history, expected_cart_history);
}

// Кэшбек округляется в соответствии с min_currency_value.
TEST(Pricing_Apply, cashback_is_rounded_correctly) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"cashback-product"}, Numeric{123}, Numeric{1})},
      Numeric{"0.1"}};

  const auto absolute_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, AbsoluteCashbackGain{Numeric{"12.34"}});
  const auto relative_gain = MakeItemDiscount(
      ProductId{"cashback-product"}, RelativeCashbackGain{Numeric{"12.34"}});
  const auto modifiers = std::vector{absolute_gain, relative_gain};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  const auto expected_history = std::vector{
      Step{Bag{Pack{Numeric{123}, Numeric{1}}}},
      // Ceil(12.34, 0.1) -> 12.4
      Step{Bag{Pack{Numeric{123}, Numeric{1}, Numeric{"12.4"}}}, absolute_gain},
      // 12.4 + Ceil(123 * 12.34%, 0.1) -> 27.6
      Step{Bag{Pack{Numeric{123}, Numeric{1}, Numeric{"27.6"}}},
           relative_gain}};

  ASSERT_EQ(History(resulting_pricing, ProductId{"cashback-product"})->steps,
            expected_history);
}

}  // namespace grocery_discounts_calculator
