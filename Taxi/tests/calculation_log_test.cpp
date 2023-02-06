#include <grocery-discounts-calculator/apply.hpp>
#include <grocery-discounts-calculator/calculation_log.hpp>
#include "utils_test.hpp"

#include <userver/fs/blocking/read.hpp>

#include <userver/formats/json/serialize.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_discounts_calculator {

using ProductId = grocery_shared::ProductId;
using ComboId = grocery_shared::ComboId;
using grocery_pricing::Numeric;

BundleDiscountV2 MakeBundleDiscountV2(
    const std::unordered_map<ProductId, Numeric>& items,
    const PaymentRule& payment_rule) {
  std::vector<handlers::libraries::grocery_discounts_calculator::BundleItem>
      bundle_items;
  for (const auto& [id, quantity] : items) {
    bundle_items.push_back({id, quantity});
  }
  BundleDiscountV2 discount{
      ComboId{"combo-id"}, {{std::move(bundle_items)}}, payment_rule};
  discount.meta.hierarchy_name = handlers::libraries::
      grocery_discounts_calculator::HierarchyName::kBundleDiscounts;
  discount.bundles_count = Numeric{1};
  return discount;
}

TEST(calc_log, complex_discount_without_rounding) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1}),
       ProductPricing(ProductId{"product-2"}, Numeric{256}, Numeric{3})},
      Numeric{1}};

  const auto money_payment_absolute = MakeItemDiscount(
      ProductId{"product-1"}, RelativeMoneyPayment{Numeric{30}});
  const auto money_payment_relative = MakeItemDiscount(
      ProductId{"product-2"}, AbsoluteMoneyPayment{Numeric{65}});
  auto cart_discount = MakePlainCartDiscount(AbsoluteMoneyPayment{Numeric{50}});
  const auto cashback_absolute = MakeItemDiscount(
      ProductId{"product-1"}, AbsoluteCashbackGain{Numeric{30}});
  const auto cashback_relative = MakeItemDiscount(
      ProductId{"product-2"}, RelativeCashbackGain{Numeric{55}});
  const std::vector<Modifier> modifiers = {
      money_payment_absolute, money_payment_relative, cart_discount,
      cashback_absolute, cashback_relative};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "complex_discount_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, complex_discount_with_rounding) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1}),
       ProductPricing(ProductId{"product-2"}, Numeric{256}, Numeric{3})},
      Numeric{1}};

  DiscountMeta meta_1;
  meta_1.draft_id = "draft_1";
  const auto money_payment_absolute =
      MakeItemDiscount(ProductId{"product-1"},
                       RelativeMoneyPayment{Numeric{30}}, std::move(meta_1));
  const auto money_payment_relative = MakeItemDiscount(
      ProductId{"product-2"}, AbsoluteMoneyPayment{Numeric{65}});

  DiscountMeta meta_2;
  meta_2.draft_id = "draft_2";
  auto cart_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{0}, AbsoluteMoneyPayment{Numeric{50}}}},
      std::move(meta_2));
  const auto cashback_absolute = MakeItemDiscount(
      ProductId{"product-1"}, AbsoluteCashbackGain{Numeric{30}});
  const auto cashback_relative = MakeItemDiscount(
      ProductId{"product-2"}, RelativeCashbackGain{Numeric{55}});
  const auto rounding_modifier = MakeRoundingModifier(Numeric{1});
  const auto pack_union = MakePackUnionModifier();
  const std::vector<Modifier> modifiers = {money_payment_absolute,
                                           money_payment_relative,
                                           rounding_modifier,
                                           pack_union,
                                           cart_discount,
                                           rounding_modifier,
                                           pack_union,
                                           cashback_absolute,
                                           cashback_relative};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "complex_discount_with_round_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, product_payment) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{353}, Numeric{3})},
      Numeric{1}};

  const auto money_product_payment = MakeItemDiscount(
      ProductId{"product-1"}, ProductPayment{Numeric{2}, {Numeric{100}}});
  const std::vector<Modifier> modifiers = {money_product_payment};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "product_payment_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, payment_method_discount) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta;
  meta.draft_id = "draft_1";
  const auto money_payment_absolute = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta));
  const std::vector<Modifier> modifiers = {money_payment_absolute};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "payment_method_discount_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, complex_discount_with_rounding_union) {
  const auto initial_pricing =
      Pricing{{ProductPricing{ProductId{"product-1"},
                              Numeric::FromFloatInexact(13.9), Numeric{2}}},
              Numeric::FromFloatInexact(0.01)};

  const auto product_payment = MakeItemDiscount(
      ProductId{"product-1"}, ProductPayment{Numeric{2}, {Numeric{50}}});
  const auto rounding_modifier =
      MakeRoundingModifier(Numeric::FromFloatInexact(0.1));
  const std::vector<Modifier> modifiers = {product_payment, rounding_modifier};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "rounding_union_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, discount_not_applied_to_zero_quantity) {
  const auto initial_pricing =
      Pricing{{
                  ProductPricing(ProductId{"product-2"},
                                 Numeric::FromFloatInexact(10.45), Numeric{2}),
                  ProductPricing(ProductId{"product-1"},
                                 Numeric::FromFloatInexact(10.8), Numeric{0}),
              },
              Numeric::FromFloatInexact(0.01)};

  auto cart_discount =
      MakePlainCartDiscount(AbsoluteCashbackPayment{Numeric{20}});
  const std::vector<Modifier> modifiers = {cart_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "discount_with_zero_quantity.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, suppliers_and_dynamic_discounts) {
  const auto initial_pricing =
      Pricing{{
                  ProductPricing(ProductId{"product-1"},
                                 Numeric::FromFloatInexact(10.0), Numeric{1}),
              },
              Numeric::FromFloatInexact(1.0)};

  DiscountMeta suppliers_meta;
  suppliers_meta.hierarchy_name = handlers::libraries::
      grocery_discounts_calculator::HierarchyName::kSuppliersDiscounts;
  const auto suppliers_discount =
      MakeItemDiscount(ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{2}},
                       std::move(suppliers_meta));

  DiscountMeta dynamic_meta;
  dynamic_meta.hierarchy_name = handlers::libraries::
      grocery_discounts_calculator::HierarchyName::kDynamicDiscounts;
  const auto dynamic_discount =
      MakeItemDiscount(ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{2}},
                       std::move(dynamic_meta));

  const std::vector<Modifier> modifiers = {suppliers_discount,
                                           dynamic_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "suppliers_and_dynamic_discounts_log.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, cart_calculation) {
  const auto initial_pricing =
      Pricing{{ProductPricing(ProductId{"product-1"}, Numeric{205}, Numeric{1}),
               ProductPricing(ProductId{"product-2"}, Numeric{60}, Numeric{3})},
              Numeric{1}};

  DiscountMeta absolute_cashback_gain_meta;
  absolute_cashback_gain_meta.draft_id = "draft_1";

  const auto& absolute_cashback_gain = MakeCartDiscount(
      {CartDiscountStep{Numeric{0}, AbsoluteCashbackGain{Numeric{50}}}},
      absolute_cashback_gain_meta);

  const auto absolute_money_discount = MakeCartDiscount(
      {CartDiscountStep{Numeric{0}, AbsoluteMoneyPayment{Numeric{10}}}});

  const std::vector<Modifier> modifiers = {absolute_cashback_gain,
                                           absolute_money_discount};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "cart_calculation.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(calc_log, meta_new_fields) {
  const auto initial_pricing = Pricing{
      {ProductPricing(ProductId{"product-1"}, Numeric{354}, Numeric{1})},
      Numeric{1}};

  DiscountMeta meta;
  meta.discount_id = "123";
  meta.has_discount_usage_restrictions = false;
  const auto money_payment_absolute = MakePaymentMethodDiscount(
      ProductId{"product-1"}, AbsoluteMoneyPayment{Numeric{30}},
      std::move(meta));
  const std::vector<Modifier> modifiers = {money_payment_absolute};

  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});

  auto calc_log = MakeCalculationLog(resulting_pricing);
  ASSERT_EQ(
      calc_log["products_calculation"][0]["steps"][1]["discount"]["discount_id"]
          .As<std::string>(),
      "123");
  ASSERT_EQ(calc_log["products_calculation"][0]["steps"][1]["discount"]
                    ["has_discount_usage_restrictions"]
                        .As<bool>(),
            false);
}

TEST(Pricing_Apply_Bundle_V2, bundle_v2_calc_log) {
  ProductId product_1{"product-1"};
  ProductId product_2{"product-2"};
  Pricing initial_pricing{{ProductPricing{product_1, Numeric{100}, Numeric{1}},
                           ProductPricing{product_2, Numeric{100}, Numeric{1}}},
                          Numeric{1}};

  const auto bundle_discount =
      MakeBundleDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{1}}},
                           AbsoluteMoneyPayment{Numeric{10}});

  const auto modifiers = std::vector<Modifier>{bundle_discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});
  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "bundle_discount_calculation_v2.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

TEST(Pricing_Apply_Bundle_V2, simple_and_bundle_v2_calc_log) {
  ProductId product_1{"product-1"};
  ProductId product_2{"product-2"};
  Pricing initial_pricing{{ProductPricing{product_1, Numeric{100}, Numeric{1}},
                           ProductPricing{product_2, Numeric{100}, Numeric{1}}},
                          Numeric{1}};

  const auto money_payment_absolute_1 =
      MakeItemDiscount(product_1, AbsoluteMoneyPayment{Numeric{10}});
  const auto money_payment_absolute_2 =
      MakeItemDiscount(product_2, AbsoluteMoneyPayment{Numeric{15}});
  const auto bundle_discount =
      MakeBundleDiscountV2({{product_1, Numeric{1}}, {product_2, Numeric{1}}},
                           AbsoluteMoneyPayment{Numeric{10}});

  const auto modifiers = std::vector<Modifier>{
      money_payment_absolute_1, money_payment_absolute_2, bundle_discount};
  const auto resulting_pricing =
      Apply(modifiers, initial_pricing, Constraints{});
  auto calc_log = MakeCalculationLog(resulting_pricing);

  const std::string filename = "simple_and_bundle_discount_calculation_v2.json";
  auto expected = ReadFile(filename);
  ASSERT_EQ(calc_log, expected);
}

}  // namespace grocery_discounts_calculator
