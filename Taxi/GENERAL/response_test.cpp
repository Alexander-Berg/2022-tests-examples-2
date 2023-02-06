#include "response.hpp"

#include <string>

#include <gtest/gtest.h>

#include <utils/test_param.hpp>

namespace handlers::internal_eats_upsell_retail_v1_menu_recommendations::post::
    impl {

namespace {

using PublicId = ResponseBuilder::PublicId;
using Source = handlers::RecommendationItemSource;
using RetailPromoItem = eats_upsell::models::RetailPromoItem;
using PromoSettings = eats_upsell::models::PromoSettings;

const static std::vector<PublicId> kEmptyPublicIds{};
const static std::vector<RetailPromoItem> kEmptyPromotions{};

RequestParams MakeRequestParams(PublicId&& public_id) {
  RequestParams result{};

  result.item.public_id = std::move(public_id);

  return result;
}

template <typename... Apply>
ResponseSettings MakeResponseSettings(Apply... apply) {
  ResponseSettings settings;

  (apply(settings), ...);

  return settings;
}

auto ApplyMaxItems(size_t max_items) {
  return [max_items](ResponseSettings& settings) {
    settings.max_items = max_items;
  };
}

auto ApplyMinItems(size_t min_items) {
  return [min_items](ResponseSettings& settings) {
    settings.min_items = min_items;
  };
}

auto ApplyMinRecommendedItems(size_t min_recommended_items) {
  return [min_recommended_items](ResponseSettings& settings) {
    settings.min_recommended_items = min_recommended_items;
  };
}

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

struct TestResponseBuilderCase final {
  std::string name;
  RequestParams request_params;
  std::vector<RetailPromoItem> promotions;
  std::vector<PublicId> recommendations;
  ResponseSettings response_settings;
  PromoSettings promo_settings;

  handlers::RecommendationsResponse expected;
};

RetailPromoItem CreateRetailPromoItem(PublicId&& public_id) {
  return RetailPromoItem{
      std::move(public_id),  // public_id
      std::nullopt,          // core_id
      {},                    // suitable_categories
  };
}

}  // namespace

class TestResponseBuilder
    : public ::testing::TestWithParam<TestResponseBuilderCase> {};

TEST_P(TestResponseBuilder, Test) {
  const auto param = GetParam();

  ResponseBuilder builder(param.request_params, std::nullopt);

  builder.AddPromotions(param.promotions);
  builder.AddRecommendations(param.recommendations);

  const auto actual =
      builder.Build(param.response_settings, param.promo_settings);
  ASSERT_EQ(param.expected, actual);
}

std::vector<TestResponseBuilderCase> MakeTestResponseBuilderCases();

INSTANTIATE_TEST_SUITE_P(ResponseBuilderBuild, TestResponseBuilder,
                         ::testing::ValuesIn(MakeTestResponseBuilderCases()),
                         [](const auto& test_case) -> std::string {
                           return eats_upsell::utils::GetTestName(test_case);
                         });

std::vector<TestResponseBuilderCase> MakeTestResponseBuilderCases() {
  return std::vector<TestResponseBuilderCase>{
      TestResponseBuilderCase{
          "empty promotions and recommendations",  // name
          MakeRequestParams(PublicId{"1"}),        // request_params
          kEmptyPromotions,                        // promotions
          kEmptyPublicIds,                         // recommendations
          MakeResponseSettings(),                  // response_settings
          MakePromoSettings(),                     // promo_settings
          handlers::RecommendationsResponse{
              {},  // recommendations
          },       // expected
      },
      TestResponseBuilderCase{
          "promotions only",                 // name
          MakeRequestParams(PublicId{"1"}),  // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),  // should be filtered
              CreateRetailPromoItem(PublicId{"2"}),
          },                                       // promotions
          kEmptyPublicIds,                         // recommendations
          MakeResponseSettings(),                  // response_settings
          MakePromoSettings(ApplyPositions({0})),  // promo_settings
          handlers::RecommendationsResponse{
              {{
                  "2",              // public_id
                  Source::kAdvert,  // source
              }},                   // recommendations
          },                        // expected
      },
      TestResponseBuilderCase{
          "non-unique promotions",           // name
          MakeRequestParams(PublicId{"1"}),  // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),  // should be filtered
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
          },                                          // promotions
          kEmptyPublicIds,                            // recommendations
          MakeResponseSettings(),                     // response_settings
          MakePromoSettings(ApplyPositions({0, 1})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "3",              // public_id
                      Source::kAdvert,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "only recommendations",            // name
          MakeRequestParams(PublicId{"1"}),  // request_params
          kEmptyPromotions,                  // promotions
          {
              PublicId{"1"},  // should be filtered
              PublicId{"2"},
          },                       // recommendations
          MakeResponseSettings(),  // response_settings
          MakePromoSettings(),     // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "2",                  // public_id
                      Source::kComplement,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "non-unique recommendations",      // name
          MakeRequestParams(PublicId{"1"}),  // request_params
          kEmptyPromotions,                  // promotions
          {
              PublicId{"1"},  // should be filtered
              PublicId{"2"},
              PublicId{"2"},
              PublicId{"2"},
              PublicId{"2"},
              PublicId{"2"},
              PublicId{"3"},
              PublicId{"3"},
              PublicId{"4"},
          },                       // recommendations
          MakeResponseSettings(),  // response_settings
          MakePromoSettings(),     // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "2",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "3",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "4",                  // public_id
                      Source::kComplement,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "recommendations and promotions",  // name
          MakeRequestParams(PublicId{"1"}),  // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"5"}),
          },  // promotions
          {
              PublicId{"1"},  // should be filtered
              PublicId{"2"},
              PublicId{"3"},
              PublicId{"4"},
          },                                          // recommendations
          MakeResponseSettings(),                     // response_settings
          MakePromoSettings(ApplyPositions({0, 1})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },  // becase both adverts and recs have this item
                  {
                      "5",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "3",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "4",                  // public_id
                      Source::kComplement,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "recommendations and promotions on positions",  // name
          MakeRequestParams(PublicId{"1"}),               // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"5"}),
          },  // promotions
          {
              PublicId{"1"},  // should be filtered
              PublicId{"2"},
              PublicId{"3"},
              PublicId{"4"},
          },                                          // recommendations
          MakeResponseSettings(),                     // response_settings
          MakePromoSettings(ApplyPositions({1, 2})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "3",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },  // becase both adverts and recs have this item
                  {
                      "5",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "4",                  // public_id
                      Source::kComplement,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "response settings max_items cuts response",  // name
          MakeRequestParams(PublicId{"10"}),            // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
          },  // promotions
          {
              PublicId{"4"},
              PublicId{"5"},
              PublicId{"6"},
          },                                       // recommendations
          MakeResponseSettings(ApplyMaxItems(1)),  // response_settings
          MakePromoSettings(ApplyPositions({0})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "1",              // public_id
                      Source::kAdvert,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "response settings min_items cuts response",  // name
          MakeRequestParams(PublicId{"10"}),            // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
          },  // promotions
          {
              PublicId{"4"},
              PublicId{"5"},
              PublicId{"6"},
          },                                        // recommendations
          MakeResponseSettings(ApplyMinItems(10)),  // response_settings
          MakePromoSettings(),                      // promo_settings
          handlers::RecommendationsResponse{
              {},  // recommendations
          },       // expected
      },
      TestResponseBuilderCase{
          "empty response with not enough recommended items",  // name
          MakeRequestParams(PublicId{"10"}),                   // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
          },                // promotions
          {PublicId{"4"}},  // recommendations
          MakeResponseSettings(
              ApplyMinRecommendedItems(5)),              // response_settings
          MakePromoSettings(ApplyPositions({0, 1, 2})),  // promo_settings
          handlers::RecommendationsResponse{},           // expected
      },
      TestResponseBuilderCase{
          "non-empty response with enough recommended items",  // name
          MakeRequestParams(PublicId{"10"}),                   // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
          },  // promotions
          {
              PublicId{"4"},
              PublicId{"5"},
              PublicId{"6"},
          },  // recommendations
          MakeResponseSettings(
              ApplyMinRecommendedItems(3)),              // response_settings
          MakePromoSettings(ApplyPositions({0, 1, 2})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "1",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "3",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "4",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "5",                  // public_id
                      Source::kComplement,  // source
                  },
                  {
                      "6",                  // public_id
                      Source::kComplement,  // source
                  },
              },  // recommendations
          },      // expected
      },

      TestResponseBuilderCase{
          "test unlimited ads",               // name
          MakeRequestParams(PublicId{"10"}),  // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
              CreateRetailPromoItem(PublicId{"4"}),
              CreateRetailPromoItem(PublicId{"5"}),
              CreateRetailPromoItem(PublicId{"6"}),
              CreateRetailPromoItem(PublicId{"7"}),
          },                       // promotions
          kEmptyPublicIds,         // recommendations
          MakeResponseSettings(),  // response_settings
          MakePromoSettings(ApplyPositions({0, 1, 2}),
                            ApplyUnlimitedAds(true)),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "1",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "3",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "4",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "5",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "6",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "7",              // public_id
                      Source::kAdvert,  // source
                  },
              },  // recommendations
          },      // expected
      },
      TestResponseBuilderCase{
          "test non-unlimited ads",           // name
          MakeRequestParams(PublicId{"10"}),  // request_params
          {
              CreateRetailPromoItem(PublicId{"1"}),
              CreateRetailPromoItem(PublicId{"2"}),
              CreateRetailPromoItem(PublicId{"3"}),
              CreateRetailPromoItem(PublicId{"4"}),
              CreateRetailPromoItem(PublicId{"5"}),
              CreateRetailPromoItem(PublicId{"6"}),
              CreateRetailPromoItem(PublicId{"7"}),
          },                                             // promotions
          kEmptyPublicIds,                               // recommendations
          MakeResponseSettings(),                        // response_settings
          MakePromoSettings(ApplyPositions({0, 1, 2})),  // promo_settings
          handlers::RecommendationsResponse{
              {
                  {
                      "1",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "2",              // public_id
                      Source::kAdvert,  // source
                  },
                  {
                      "3",              // public_id
                      Source::kAdvert,  // source
                  },
              },  // recommendations
          },      // expected
      },
  };
}  // namespace
   // handlers::internal_eats_upsell_retail_v1_menu_recommendations::post::impl

// clang-format off
}  // namespace
   // handlers::internal_eats_upsell_retail_v1_menu_recommendations::post::impl
// clang-format on
