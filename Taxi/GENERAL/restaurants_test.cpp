#include "restaurants.hpp"

#include <gtest/gtest.h>

#include <utils/test_param.hpp>

namespace handlers::eats_upsell_v1_upsell::post::impl {

namespace {

namespace models = eats_upsell::models;

RequestParams MakeRequestParams(
    models::ShippingType shipping_type = models::ShippingType::kDelivery) {
  RequestParams result;
  result.shipping_type = shipping_type;

  return result;
}

models::ItemInfo MakeItemInfo(models::CoreItemId core_id, bool available = true,
                              std::optional<int> in_stock = 1) {
  models::ItemInfo items_info{};

  items_info.core_item_id = core_id;
  items_info.available = available;
  items_info.in_stock = in_stock;

  return items_info;
}

handlers::UpsellItem MakeUpsellItem(models::CoreItemId core_id,
                                    bool is_promoted = false) {
  handlers::UpsellItem result{};
  result.id = core_id.GetUnderlying();
  if (is_promoted) {
    result.promoted.emplace();
  }

  return result;
}

template <typename... Apply>
models::PromoSettings MakePromoSettings(Apply... apply) {
  models::PromoSettings result;

  (apply(result), ...);

  return result;
}

auto ApplyPositions(std::unordered_set<size_t>&& positions) {
  return [positions = std::move(positions)](models::PromoSettings& settings) {
    settings.positions = std::move(positions);
  };
}

auto ApplyUnlimitedAds(bool unlimited) {
  return [unlimited](models::PromoSettings& settings) {
    settings.unlimited = unlimited;
  };
}

struct RestaurantsResponseBuilderTestCase {
  std::string name{};
  RequestParams request_params{};
  std::vector<models::ItemInfo> items_info{};
  std::vector<models::PromotedItem> promotions{};
  std::vector<models::RecommendedItem> recommendations{};
  models::PromoSettings promo_settings{};
  std::vector<handlers::UpsellItem> expected{};
};

void AssertPartiallyEq(const handlers::UpsellItem& lhs,
                       const handlers::UpsellItem& rhs) {
  ASSERT_EQ(lhs.id, rhs.id);
  ASSERT_EQ(lhs.promoted, rhs.promoted);
}

void AssertPartiallyEq(const std::vector<handlers::UpsellItem>& lhs,
                       const std::vector<handlers::UpsellItem>& rhs) {
  ASSERT_EQ(lhs.size(), rhs.size());

  auto lhs_it = lhs.begin();
  auto rhs_it = rhs.begin();
  while (lhs_it != lhs.end() && rhs_it != rhs.end()) {
    AssertPartiallyEq(*lhs_it++, *rhs_it++);
  }
}

std::vector<RestaurantsResponseBuilderTestCase>
MakeResponseBuilderBuildCases() {
  return {
      {
          "no items",           // name
          MakeRequestParams(),  // request_params
          {},                   // items_info
          {},                   // promotions
          {},                   // recommendations
          MakePromoSettings(),  // promo_settings
          {},                   // expected
      },
      {
          "no items info",      // name
          MakeRequestParams(),  // request_params
          {},                   // items_info
          {},                   // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {},                   // expected
      },
      {
          "only recommendations",  // name
          MakeRequestParams(),     // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
          },   // items_info
          {},  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
              {
                  models::CoreItemId(3),  // core_item_id
                  models::GroupId(3),     // group_id
              },
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
              MakeUpsellItem(models::CoreItemId(3)),
          },  // expected
      },
      {
          "filter recommendations by groups",  // name
          MakeRequestParams(),                 // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
          },   // items_info
          {},  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
              {
                  models::CoreItemId(3),  // core_item_id
                  models::GroupId(2),     // group_id
              },
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
          },  // expected
      },
      {
          "no promo positions",  // name
          MakeRequestParams(),   // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
          },  // items_info
          {
              {
                  models::CoreItemId{3},  // core_item_id
              },
          },  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
          },                    // recommendations
          MakePromoSettings(),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
          },  // expected
      },
      {
          "single promo position",  // name
          MakeRequestParams(),      // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
          },  // items_info
          {
              {
                  models::CoreItemId{3},  // core_item_id
              },
          },  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
          },                                       // recommendations
          MakePromoSettings(ApplyPositions({0})),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(3), true),
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
          },  // expected
      },
      {
          "deduplicate by core_id",  // name
          MakeRequestParams(),       // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
          },  // items_info
          {
              {
                  models::CoreItemId{3},  // core_item_id
              },
          },  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
              {
                  models::CoreItemId(3),  // core_item_id
                  models::GroupId(3),     // group_id
              },
          },                                       // recommendations
          MakePromoSettings(ApplyPositions({0})),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(3), true),
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
          },  // expected
      },
      {
          "single promo position excludes second advert",  // name
          MakeRequestParams(),                             // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
              MakeItemInfo(models::CoreItemId(4)),
          },  // items_info
          {
              {
                  models::CoreItemId{3},  // core_item_id
              },
              {
                  models::CoreItemId{4},  // core_item_id
              },
          },  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
          },                                       // recommendations
          MakePromoSettings(ApplyPositions({0})),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(3), true),
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
          },  // expected
      },
      {
          "unlimited adverts to the end",  // name
          MakeRequestParams(),             // request_params
          {
              MakeItemInfo(models::CoreItemId(1)),
              MakeItemInfo(models::CoreItemId(2)),
              MakeItemInfo(models::CoreItemId(3)),
              MakeItemInfo(models::CoreItemId(4)),
              MakeItemInfo(models::CoreItemId(5)),
          },  // items_info
          {
              {
                  models::CoreItemId{3},  // core_item_id
              },
              {
                  models::CoreItemId{4},  // core_item_id
              },
              {
                  models::CoreItemId{5},  // core_item_id
              },
          },  // promotions
          {
              {
                  models::CoreItemId(1),  // core_item_id
                  models::GroupId(1),     // group_id
              },
              {
                  models::CoreItemId(2),  // core_item_id
                  models::GroupId(2),     // group_id
              },
          },  // recommendations
          MakePromoSettings(ApplyPositions({0}),
                            ApplyUnlimitedAds(true)),  // promo_settings
          {
              MakeUpsellItem(models::CoreItemId(3), true),
              MakeUpsellItem(models::CoreItemId(1)),
              MakeUpsellItem(models::CoreItemId(2)),
              MakeUpsellItem(models::CoreItemId(4), true),
              MakeUpsellItem(models::CoreItemId(5), true),
          },  // expected
      },
  };
}

class RestaurantsResponseBuilderBuild
    : public ::testing::TestWithParam<RestaurantsResponseBuilderTestCase> {};

}  // namespace

TEST_P(RestaurantsResponseBuilderBuild, Test) {
  auto param = GetParam();

  RestaurantsResponseBuilder target(param.request_params,
                                    std::move(param.items_info));

  target.AddPromotions(std::move(param.promotions));
  target.AddRecommendations(std::move(param.recommendations));

  const auto actual = target.Build(param.promo_settings);
  AssertPartiallyEq(param.expected, actual);
}

INSTANTIATE_TEST_SUITE_P(RestaurantsResponseBuilderBuild,
                         RestaurantsResponseBuilderBuild,
                         ::testing::ValuesIn(MakeResponseBuilderBuildCases()),
                         [](const auto& test_case) -> std::string {
                           return eats_upsell::utils::GetTestName(test_case);
                         });

}  // namespace handlers::eats_upsell_v1_upsell::post::impl
