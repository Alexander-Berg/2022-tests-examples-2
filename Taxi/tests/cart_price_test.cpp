#include <gtest/gtest.h>

#include <grocery-cart-client/cart_price.hpp>

namespace grocery_cart_client {

namespace cart = clients::grocery_cart;

using SubItem = cart::SubItem;
using Item = cart::RetrieveRawItemV2;
using ItemInfo = cart::RetrieveRawItemInfoV2;

SubItem MakeSubItem(std::string item_id, Numeric price,
                    Numeric quantity = Numeric{1}) {
  SubItem result;
  result.item_id = std::move(item_id);
  result.price = price;
  result.quantity = quantity;

  return result;
}

ItemInfo MakeItemInfo(std::string item_id,
                      std::optional<Numeric> vat = std::nullopt) {
  ItemInfo result;
  result.item_id = std::move(item_id);
  result.vat = vat;

  return result;
}

TEST(CalculatePrice, kTotalProducts) {
  CartInfo cart;
  cart.items_v2 = {
      Item{
          MakeItemInfo("item1"),
          {
              MakeSubItem("item1:0", Numeric{100}),
          },
      },
      Item{
          MakeItemInfo("item2"),
          {
              MakeSubItem("item2:0", Numeric{50}, Numeric{2}),
              MakeSubItem("item2:1", Numeric{100}, Numeric{1}),
          },
      },
  };

  auto price = CalculatePrice(cart, PriceFlag::kTotalProducts);

  EXPECT_EQ(price, Numeric{300});
}

TEST(CalculatePrice, kTotalPaidWithCashback) {
  auto sub_item1_0 = MakeSubItem("item1:0", Numeric{100});
  auto sub_item1_1 = MakeSubItem("item1:1", Numeric{100});

  sub_item1_1.paid_with_cashback = Numeric{50};

  CartInfo cart;
  cart.items_v2 = {
      Item{
          MakeItemInfo("item1"),
          {sub_item1_0, sub_item1_1},
      },
  };

  auto price = CalculatePrice(cart, PriceFlag::kTotalPaidWithCashback);

  EXPECT_EQ(price, Numeric{50});
}

TEST(CalculatePrice, kTotalVatFree) {
  auto item2_info = MakeItemInfo("item2");
  item2_info.vat = Numeric{20};

  CartInfo cart;
  cart.items_v2 = {
      Item{
          MakeItemInfo("item1"),
          {
              MakeSubItem("item1:0", Numeric{100}),
          },
      },
      Item{
          item2_info,
          {
              MakeSubItem("item2:0", Numeric{50}, Numeric{2}),
              MakeSubItem("item2:1", Numeric{100}, Numeric{1}),
          },
      },
  };

  auto price = CalculatePrice(cart, PriceFlag::kTotalVatFree);

  EXPECT_EQ(price, Numeric{100});
}

TEST(CalculatePrice, kDelivery) {
  CartInfo cart;
  cart.delivery = cart::DeliveryInfo{};
  cart.delivery->cost = Numeric{150};

  auto price = CalculatePrice(cart, PriceFlag::kDelivery);

  EXPECT_EQ(price, Numeric{150});
}

TEST(CalculatePrice, kTips_Absolute) {
  CartInfo cart;
  cart.tips = cart::TipsInfo{};
  cart.tips->amount = Numeric{50};
  cart.tips->amount_type = cart::TipsAmountType::kAbsolute;

  auto price = CalculatePrice(cart, PriceFlag::kTips);

  EXPECT_EQ(price, Numeric{50});
}

TEST(CalculatePrice, kTips_Percent) {
  CartInfo cart;
  cart.tips = cart::TipsInfo{};
  cart.tips->amount = Numeric{20};
  cart.tips->amount_type = cart::TipsAmountType::kPercent;
  cart.items_v2 = {
      Item{
          MakeItemInfo("item1"),
          {
              MakeSubItem("item1:0", Numeric{200}),
          },
      },
  };

  auto price = CalculatePrice(cart, PriceFlag::kTips);

  EXPECT_EQ(price, Numeric{40});
}

TEST(CalculatePrice, kTipsWithOrder) {
  CartInfo cart;
  cart.tips = cart::TipsInfo{};
  cart.tips->amount = Numeric{50};
  cart.tips->amount_type = cart::TipsAmountType::kAbsolute;
  cart.tips->payment_flow = cart::TipsPaymentFlow::kWithOrder;

  auto price = CalculatePrice(cart, PriceFlag::kTipsWithOrder);

  EXPECT_EQ(price, Numeric{50});
}

TEST(CalculatePrice, kTipsWithOrder_No) {
  CartInfo cart;
  cart.tips = cart::TipsInfo{};
  cart.tips->amount = Numeric{50};
  cart.tips->amount_type = cart::TipsAmountType::kAbsolute;
  cart.tips->payment_flow = cart::TipsPaymentFlow::kSeparate;

  auto price = CalculatePrice(cart, PriceFlag::kTipsWithOrder);

  EXPECT_EQ(price, Numeric{0});
}

TEST(CalculatePrice, kServiceFee) {
  CartInfo cart;
  cart.service_fee = Numeric{75};

  auto price = CalculatePrice(cart, PriceFlag::kServiceFee);

  EXPECT_EQ(price, Numeric{75});
}

TEST(CalculatePrice, Agregate) {
  CartInfo cart;
  cart.delivery = cart::DeliveryInfo{};
  cart.delivery->cost = Numeric{15};
  cart.service_fee = Numeric{35};
  cart.items_v2 = {
      Item{
          MakeItemInfo("item1"),
          {
              MakeSubItem("item1:0", Numeric{150}),
          },
      },
  };

  auto price =
      CalculatePrice(cart, PriceFlag::kTotalProducts | PriceFlag::kDelivery);

  EXPECT_EQ(price, Numeric{165});
}

}  // namespace grocery_cart_client
