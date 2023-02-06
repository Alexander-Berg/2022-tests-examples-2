#include <gtest/gtest.h>

#include <validators.hpp>

namespace eats_discounts_applicator::validator::tests {

namespace {

struct TestParams {
  CartForDiscount cart;
  CartForDiscount exp_cart;
  std::unordered_map<int, int> exp_item_id_to_additional_item_id;
  std::string test_name;
};

class TestValidator : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {
        {{{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        {{{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt}}, kZeroMoney},
        {},
        "same_cart",
    },
    {
        {{
             {1, "1", Money(100), std::nullopt, 1, {}, std::nullopt},
             {2,
              "2",
              Money(100),
              std::nullopt,
              1,
              {},
              std::to_string(impl::kMoneyTypeId)

             },
         },
         kZeroMoney},
        {{{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt},
          {2,
           "2",
           Money(100),
           std::nullopt,
           1,
           {},
           std::to_string(impl::kMoneyTypeId)}},
         kZeroMoney},
        {},
        "same_cart_with_discounts",
    },
    {
        {{{1, "1", Money(100), std::nullopt, 1, {}, std::nullopt},
          {2,
           "1",
           Money(100),
           std::nullopt,
           1,
           {},
           std::to_string(impl::kProductTypeId)

          }},
         kZeroMoney},
        {{{1, "1", Money(100), std::nullopt, 2, {}, std::nullopt}}, kZeroMoney},
        {{1, 2}},
        "one_additional_item",
    },
};

}  // namespace

TEST_P(TestValidator, BasicTest) {
  const auto params = GetParam();
  auto validated_cart = params.cart;
  validated_cart.DeleteDiscountItems();

  EXPECT_EQ(params.exp_cart.items.size(), validated_cart.items.size());
  int i = 0;
  for (const auto& item : validated_cart.items) {
    const auto& it = params.exp_cart.items[i++];
    EXPECT_EQ(it.id, item.id);
    EXPECT_EQ(it.public_id, item.public_id);
    EXPECT_EQ(it.price, item.price);
    EXPECT_EQ(it.promo_price, item.promo_price);
    if (it.promo_price) {
      EXPECT_EQ(*it.promo_price, *item.promo_price);
    }
    EXPECT_EQ(it.quantity, item.quantity);
    EXPECT_EQ(it.options.size(), item.options.size());
    int j = 0;
    for (const auto& option : item.options) {
      const auto& cur_option = it.options[j++];
      EXPECT_EQ(cur_option.id, option.id);
      EXPECT_EQ(cur_option.price, option.price);
      EXPECT_EQ(cur_option.quantity, option.quantity);
    }
    EXPECT_EQ(it.promo_type_id.has_value(), item.promo_type_id.has_value());
    if (it.promo_type_id) {
      EXPECT_EQ(it.promo_type_id.value(), item.promo_type_id.value());
    }

    if (item.GetAdditionalItemId()) {
      EXPECT_EQ(params.exp_item_id_to_additional_item_id.count(it.id) != 0,
                true);
      EXPECT_EQ(params.exp_item_id_to_additional_item_id.at(it.id),
                item.GetAdditionalItemId().value());
    } else {
      EXPECT_EQ(params.exp_item_id_to_additional_item_id.count(it.id) != 0,
                false);
    }
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestValidator,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_discounts_applicator::validator::tests
