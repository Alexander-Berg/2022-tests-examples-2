#include "retail.hpp"

#include <gtest/gtest.h>

#include <utils/test_param.hpp>

namespace handlers::eats_upsell_v1_upsell::post::impl {

namespace {

using ItemInfo = RetailResponseBuilder::ItemInfo;
using PublicId = RetailResponseBuilder::PublicId;
using RetailCartItem = RetailResponseBuilder::RetailCartItem;
using RetailPromoItem = RetailResponseBuilder::RetailPromoItem;
using ShippingType = eats_upsell::models::ShippingType;
using PromoSettings = eats_upsell::models::PromoSettings;
using CategoryId = RetailResponseBuilder::CategoryId;

template <typename... Apply>
PromoSettings MakePromoSettings(Apply... apply) {
  PromoSettings result;

  (apply(result), ...);

  return result;
}

auto ApplyPositions(std::unordered_set<size_t>&& positions) {
  return [positions = std::move(positions)](PromoSettings& settings) {
    settings.positions = std::move(positions);
  };
}

auto ApplyUnlimitedAds(bool unlimited) {
  return
      [unlimited](PromoSettings& settings) { settings.unlimited = unlimited; };
}

struct ResponseBuilderBuildCaseItem {
  PublicId public_id{};
  bool is_promoted{};
};

struct ResponseBuilderBuildCase {
  std::string name{};
  RequestParams request_params{};
  std::vector<PublicId> menu_items{};
  std::vector<RetailCartItem> cart_items{};
  std::vector<ItemInfo> items_info{};
  std::vector<RetailPromoItem> promotions{};
  std::vector<PublicId> recommendations{};
  PromoSettings promo_settings{};
  std::vector<ResponseBuilderBuildCaseItem> expected{};
};

void AssertPartiallyEq(const ResponseBuilderBuildCaseItem& lhs,
                       const handlers::UpsellItem& rhs) {
  ASSERT_TRUE(rhs.public_id.has_value());
  const PublicId public_id{rhs.public_id.value()};

  ASSERT_EQ(lhs.public_id, public_id);
  if (lhs.is_promoted) {
    ASSERT_TRUE(rhs.promoted.has_value());
  } else {
    ASSERT_FALSE(rhs.promoted.has_value());
  }
}

RequestParams MakeRequestParams(
    ShippingType shipping_type = ShippingType::kDelivery) {
  RequestParams result;
  result.shipping_type = shipping_type;

  return result;
}

const static std::vector<PublicId> kEmptyPublicIds{};
const static std::vector<RetailCartItem> kEmptyCartItems{};
const static std::vector<ItemInfo> kEmptyItemsInfo{};
const static std::unordered_set<size_t> kEmptyPromoPositions{};
const static std::vector<RetailPromoItem> kEmptyPromotions{};
const static std::vector<ResponseBuilderBuildCaseItem>
    kEmptyResponseBuilderBuildCaseItems{};

ItemInfo MakeItemInfo(PublicId&& public_id, bool available = true,
                      std::optional<int> in_stock = 1,
                      std::vector<CategoryId> categories_ = {}) {
  ItemInfo items_info{};

  items_info.core_item_id = eats_upsell::models::CoreItemId{1};
  items_info.public_item_id = std::move(public_id);
  items_info.available = available;
  items_info.in_stock = in_stock;
  items_info.categories = categories_;

  return items_info;
}

RetailCartItem MakeRetailCartItem(PublicId&& public_id, size_t quantity = 1) {
  return {
      std::move(public_id),  // public_id
      quantity,              // quantity
  };
}

RetailPromoItem MakeRetailPromoItem(PublicId&& public_id,
                                    std::unordered_set<CategoryId> categories =
                                        std::unordered_set<CategoryId>{}) {
  return {
      std::move(public_id),  // public_id
      std::nullopt,          // core_id
      categories,            // suitable_categories
  };
}

}  // namespace

class ResponseBuilderBuild
    : public ::testing::TestWithParam<ResponseBuilderBuildCase> {};

TEST_P(ResponseBuilderBuild, Test) {
  const auto param = GetParam();

  RetailResponseBuilder builder(param.request_params, param.menu_items,
                                param.cart_items,
                                std::vector<ItemInfo>(param.items_info));

  builder.AddPromotions(std::vector<RetailPromoItem>(param.promotions));
  builder.AddRecommendations(std::vector<PublicId>(param.recommendations));

  const auto actual = builder.Build(param.promo_settings);
  const auto& expected = param.expected;

  ASSERT_EQ(expected.size(), actual.size());

  auto expected_it = expected.begin();
  auto actual_it = actual.begin();
  while (expected_it != expected.end() && actual_it != actual.end()) {
    const auto want = *expected_it++;
    const auto got = *actual_it++;
    AssertPartiallyEq(want, got);
  }
}

std::vector<ResponseBuilderBuildCase> MakeResponseBuilderBuildCases();

INSTANTIATE_TEST_SUITE_P(ResponseBuilderBuild, ResponseBuilderBuild,
                         ::testing::ValuesIn(MakeResponseBuilderBuildCases()),
                         [](const auto& test_case) -> std::string {
                           return eats_upsell::utils::GetTestName(test_case);
                         });

std::vector<ResponseBuilderBuildCase> MakeResponseBuilderBuildCases() {
  return std::vector<ResponseBuilderBuildCase>{
      {
          "nothing to recommend",               // name
          MakeRequestParams(),                  // request_params
          kEmptyPublicIds,                      // menu_items
          kEmptyCartItems,                      // cart_items
          kEmptyItemsInfo,                      // items_info
          kEmptyPromotions,                     // promotions
          kEmptyPublicIds,                      // recommendations
          MakePromoSettings(),                  // promo_settings
          kEmptyResponseBuilderBuildCaseItems,  // expected
      },
      {
          "recommend nothing due to no info",  // name
          MakeRequestParams(),                 // request_params
          kEmptyPublicIds,                     // menu_items
          kEmptyCartItems,                     // cart_items
          kEmptyItemsInfo,                     // items_info
          kEmptyPromotions,                    // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
          },                                    // recommendations
          MakePromoSettings(),                  // promo_settings
          kEmptyResponseBuilderBuildCaseItems,  // expected
      },
      {
          "recommend all unfiltered",  // name
          MakeRequestParams(),         // request_params
          kEmptyPublicIds,             // menu_items
          kEmptyCartItems,             // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"2"}),
              MakeItemInfo(PublicId{"3"}),
          },                 // items_info
          kEmptyPromotions,  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              {PublicId{"1"}, /*is_promoted*/ false},
              {PublicId{"2"}, /*is_promoted*/ false},
              {PublicId{"3"}, /*is_promoted*/ false},
          },  // expected
      },
      {
          "recommend part because no info for 2",  // name
          MakeRequestParams(),                     // request_params
          kEmptyPublicIds,                         // menu_items
          kEmptyCartItems,                         // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"3"}),
          },                 // items_info
          kEmptyPromotions,  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              {PublicId{"1"}, /*is_promoted*/ false},
              {PublicId{"3"}, /*is_promoted*/ false},
          },  // expected
      },
      {
          "filtering categories for promotions",  // name
          MakeRequestParams(),                    // request_params
          kEmptyPublicIds,                        // menu_items
          {MakeRetailCartItem(PublicId{"1"})},    // cart_items
          {
              MakeItemInfo(PublicId{"1"}, true, 1, {CategoryId{"1"}}),
              MakeItemInfo(PublicId{"2"}, true, 1, {CategoryId{"1"}}),
              MakeItemInfo(PublicId{"3"}, true, 1, {CategoryId{"2"}}),
              MakeItemInfo(PublicId{"4"}, true, 1,
                           {CategoryId{"1"}, CategoryId{"2"}}),
              MakeItemInfo(PublicId{"42"}),
          },  // items_info
          {
              MakeRetailPromoItem(PublicId{"2"}, {CategoryId{"1"}}),
              MakeRetailPromoItem(PublicId{"3"}, {CategoryId{"2"}}),
              MakeRetailPromoItem(PublicId{"4"},
                                  {CategoryId{"1"}, CategoryId{"2"}}),
              MakeRetailPromoItem(PublicId{"42"}),
          },                                           // promotions
          kEmptyPublicIds,                             // recommendations
          MakePromoSettings(ApplyUnlimitedAds(true)),  // promo_settings
          {
              {PublicId{"2"}, /*is_promoted*/ true},
              {PublicId{"4"}, /*is_promoted*/ true},
              {PublicId{"42"}, /*is_promoted*/ true},
          },  // expected
      },
      {
          "recommend part because we have items in cart and menu",  // name
          MakeRequestParams(),  // request_params
          {
              PublicId{"1"},
          },  // menu_items
          {
              MakeRetailCartItem(PublicId{"2"}),
          },  // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"2"}),
              MakeItemInfo(PublicId{"3"}),
          },                 // items_info
          kEmptyPromotions,  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              {PublicId{"3"}, /*is_promoted*/ false},
          },  // expected
      },
      {
          "recommend and promote",  // name
          MakeRequestParams(),      // request_params
          kEmptyPublicIds,          // menu_items
          kEmptyCartItems,          // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"2"}),
              MakeItemInfo(PublicId{"3"}),
          },  // items_info
          {
              MakeRetailPromoItem(PublicId{"1"}),
              MakeRetailPromoItem(PublicId{"3"}),
          },  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
          },                                          // recommendations
          MakePromoSettings(ApplyPositions({0, 1})),  // promo_settings
          {
              {PublicId{"1"}, /*is_promoted*/ true},
              {PublicId{"3"}, /*is_promoted*/ true},
              {PublicId{"2"}, /*is_promoted*/ false},
          },  // expected
      },
      {
          "test unlimited ads",  // name
          MakeRequestParams(),   // request_params
          kEmptyPublicIds,       // menu_items
          kEmptyCartItems,       // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"2"}),
              MakeItemInfo(PublicId{"3"}),
              MakeItemInfo(PublicId{"4"}),
              MakeItemInfo(PublicId{"5"}),
              MakeItemInfo(PublicId{"6"}),
              MakeItemInfo(PublicId{"7"}),
              MakeItemInfo(PublicId{"8"}),
          },  // items_info
          {
              MakeRetailPromoItem(PublicId{"1"}),
              MakeRetailPromoItem(PublicId{"3"}),
              MakeRetailPromoItem(PublicId{"6"}),
              MakeRetailPromoItem(PublicId{"7"}),
              MakeRetailPromoItem(PublicId{"8"}),
          },  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
              PublicId{"4"},
              PublicId{"5"},
          },  // recommendations
          MakePromoSettings(ApplyPositions({0, 1}),
                            ApplyUnlimitedAds(true)),  // promo_settings
          {
              {PublicId{"1"}, /*is_promoted*/ true},
              {PublicId{"3"}, /*is_promoted*/ true},
              {PublicId{"2"}, /*is_promoted*/ false},
              {PublicId{"4"}, /*is_promoted*/ false},
              {PublicId{"5"}, /*is_promoted*/ false},
              {PublicId{"6"}, /*is_promoted*/ true},
              {PublicId{"7"}, /*is_promoted*/ true},
              {PublicId{"8"}, /*is_promoted*/ true},
          },  // expected
      },
      {
          "test non-unlimited ads",  // name
          MakeRequestParams(),       // request_params
          kEmptyPublicIds,           // menu_items
          kEmptyCartItems,           // cart_items
          {
              MakeItemInfo(PublicId{"1"}),
              MakeItemInfo(PublicId{"2"}),
              MakeItemInfo(PublicId{"3"}),
              MakeItemInfo(PublicId{"4"}),
              MakeItemInfo(PublicId{"5"}),
              MakeItemInfo(PublicId{"6"}),
              MakeItemInfo(PublicId{"7"}),
              MakeItemInfo(PublicId{"8"}),
          },  // items_info
          {
              MakeRetailPromoItem(PublicId{"1"}),
              MakeRetailPromoItem(PublicId{"3"}),
              MakeRetailPromoItem(PublicId{"6"}),
              MakeRetailPromoItem(PublicId{"7"}),
              MakeRetailPromoItem(PublicId{"8"}),
          },  // promotions
          {
              PublicId{"1"},
              PublicId{"2"},
              PublicId{"3"},
              PublicId{"4"},
              PublicId{"5"},
          },  // recommendations
          MakePromoSettings(ApplyPositions({0, 1}),
                            ApplyUnlimitedAds(false)),  // promo_settings
          {
              {PublicId{"1"}, /*is_promoted*/ true},
              {PublicId{"3"}, /*is_promoted*/ true},
              {PublicId{"2"}, /*is_promoted*/ false},
              {PublicId{"4"}, /*is_promoted*/ false},
              {PublicId{"5"}, /*is_promoted*/ false},
          },  // expected
      },
  };
}

}  // namespace handlers::eats_upsell_v1_upsell::post::impl
