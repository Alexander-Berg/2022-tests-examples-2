#include <userver/utest/utest.hpp>

#include <userver/formats/json.hpp>

#include <clients/promotions/client.hpp>
#include <clients/promotions/component.hpp>
#include <clients/promotions/definitions.hpp>

#include <promotions_cache/models/promotions_cache.hpp>
#include <tests/test_utils.hpp>

namespace promotions_cache::tests {

using PromoOnSummary = promotions_cache::models::PromoOnSummary;
using IdToPromoOnSummaryMap = promotions_cache::models::IdToPromoOnSummaryMap;
using PromotionsCache = promotions_cache::models::PromotionsCache;
using PromoblockContentTextItem =
    clients::promotions::PromoblockContentTextItem;
using PromoOnSummaryTextWidget = clients::promotions::PromoOnSummaryTextWidget;

PromoblockContentTextItem CreatePromoblockContentTextItem(
    const std::string& text) {
  PromoblockContentTextItem promoblock_content_text_item;

  promoblock_content_text_item.text = text;

  return promoblock_content_text_item;
}

PromoOnSummaryTextWidget CreatePromoOnSummaryTextWidget(
    const std::vector<std::string> texts) {
  PromoOnSummaryTextWidget text_widget;

  for (const auto& text : texts) {
    text_widget.items.push_back(CreatePromoblockContentTextItem(text));
  }

  return text_widget;
}

PromoOnSummary CreatePromoOnSummary(const std::string& id) {
  PromoOnSummary promo_on_summary;

  promo_on_summary.id = id;
  promo_on_summary.text = CreatePromoOnSummaryTextWidget({"text"});

  return promo_on_summary;
}

UTEST(PromotionsCacheTest, PromosOnSummary) {
  const PromoOnSummary promo = CreatePromoOnSummary("id");
  clients::promotions::InternalListResponse promos;

  promos.promos_on_summary = {promo};

  const auto& cache = PromotionsCache(promos);

  ASSERT_TRUE(cache.GetPromoOnSummary(promo.id).has_value());
  promotions_cache::tests::utils::AssertEqAsJson(
      promo, cache.GetPromoOnSummary(promo.id).value());

  promotions_cache::tests::utils::AssertEqAsJson(
      IdToPromoOnSummaryMap({{promo.id, promo}}),
      cache.GetIdToPromoOnSummaryMap());
}

}  // namespace promotions_cache::tests
