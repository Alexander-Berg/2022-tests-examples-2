#include <clients/tariffs-promotions/requests.hpp>
#include <endpoints/common/core/service_level/models.hpp>
#include <endpoints/full/plugins/tariffs-promotions-hook/build_request.hpp>

#include <tests/endpoints/common/service_level_mock_test.hpp>
#include <userver/utest/utest.hpp>
#include <utility>

namespace routestats::plugins::tariffs_promotions_hook {

using clients::tariffs_promotions::CategoryData;
using clients::tariffs_promotions::OfferData;
using clients::tariffs_promotions::OfferDataPlusPromo;
using clients::tariffs_promotions::OfferDataRouteinfo;
using full::tariffs_promotions_hook::BuildRequest;
using full::tariffs_promotions_hook::Request;

namespace {
core::ServiceLevel MockServiceLevel(
    std::string cls, std::optional<core::Decimal> price,
    std::optional<core::Decimal> driver_funded_discount_value = std::nullopt,
    std::optional<core::TariffUnavailable> unavailable = std::nullopt,
    std::optional<core::Decimal> surge_value = std::nullopt) {
  auto result = test::MockDefaultServiceLevel(cls);
  result.final_price = price;
  result.driver_funded_discount_value = driver_funded_discount_value;
  result.tariff_unavailable = std::move(unavailable);
  if (surge_value) {
    result.surge = {*surge_value};
  }
  return result;
}
}  // namespace

void TestBuildRequest() {
  handlers::RoutestatsRequest original_request;
  original_request.state = {
      std::nullopt /* location */,
      {{"a", "Moscow, Main Street"}, {"b", std::nullopt}}};
  original_request.selected_class = "vip";

  const std::vector<core::Alternative> alternatives_vector = {
      {"explicit_antisurge",
       "alt_offer_1",
       {},
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt},
      {"plus_promo",
       "alt_offer_2",
       {
           {"business", "alt_offer_2", core::Decimal{"123"}, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt},
           {"comfortplus", "alt_offer_2", core::Decimal{"321"}, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt},
       },
       core::AlternativePlusPromo{"11", "econom", "comfort"},
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt},
      {"perfect_chain",
       "alt_offer_3",
       {{"econom", "alt_offer_3", core::Decimal{"123"},
         core::EstimatedWaiting{120, "2 min"}, std::nullopt, std::nullopt,
         std::nullopt, std::nullopt, std::nullopt, std::nullopt, std::nullopt,
         std::nullopt}},
       std::nullopt,
       std::nullopt,
       core::Decimal{"43"},
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt},
  };

  core::Alternatives alternatives;
  for (const auto& item : alternatives_vector) {
    alternatives.options.push_back(item);
  }

  const auto req = BuildRequest(
      original_request, "some_offer_id", "RUB",
      {
          MockServiceLevel("econom", core::Decimal{"1.12"}),
          MockServiceLevel("business", core::Decimal{200}, core::Decimal{9},
                           std::nullopt, core::Decimal{"2.4"} /* surge */),
          MockServiceLevel("comfortplus", core::Decimal{"0.0"}, std::nullopt,
                           core::TariffUnavailable{"free_cars", "No cars"}),
      },
      alternatives,
      // route_info
      {{"1234", "4567"}});

  ASSERT_EQ(req.body.offers.size(), 3);

  ASSERT_EQ(req.body.offers[0].offer_id, "some_offer_id");
  ASSERT_EQ(req.body.offers[0].data,
            (OfferData{
                OfferDataRouteinfo{
                    "1234",
                    "4567",
                    {{"a", "Moscow, Main Street"}, {"b", std::nullopt}}},
                "vip",
                "RUB",
                std::vector<CategoryData>{
                    CategoryData{"econom", core::Decimal{"1.12"}, 60},
                    CategoryData{"business", core::Decimal{"200"}, 60,
                                 std::nullopt /* eta */, core::Decimal{"9"},
                                 core::Decimal{"2.4"}}},
            }));

  ASSERT_EQ(req.body.offers[1].offer_id, "alt_offer_2");
  ASSERT_EQ(
      req.body.offers[1].data,
      (OfferData{std::nullopt /* route_info */,
                 std::nullopt /* selected_class */, "RUB",
                 std::vector<CategoryData>{{"business", core::Decimal{"123"}}},
                 OfferDataPlusPromo{"11", "econom", "comfort"}}));

  ASSERT_EQ(req.body.offers[2].offer_id, "alt_offer_3");
  ASSERT_EQ(
        req.body.offers[2].data,
        (OfferData{std::nullopt /* route_info */,
                   std::nullopt /* selected_class */, "RUB",
                   std::vector<CategoryData>{
                       {"econom", core::Decimal{"123"}, std::nullopt, "2" /* eta minutes
                       */}},
                   std::nullopt /* plus_promo */, core::Decimal{"43"}}));
}

TEST(BuildRequest, valid) { TestBuildRequest(); }

}  // namespace routestats::plugins::tariffs_promotions_hook
