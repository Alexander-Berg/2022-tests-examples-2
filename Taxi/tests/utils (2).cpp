#include "utils.hpp"

#include <string>
#include <userver/logging/log.hpp>
#include "eats-discounts-applicator/common.hpp"

namespace eats_discounts_applicator::tests {

namespace {

std::optional<discounts_lib::ProductDiscount> MakeProductValue(
    DiscountType type, const std::string& value, std::optional<int> bundle) {
  switch (type) {
    case DiscountType::NoDiscount:
      // fallthrough
    case DiscountType::AbsoluteValue:
      // fallthrough
    case DiscountType::FractionWithMaximum:
      // fallthrough
    case DiscountType::TableValue:
      return std::nullopt;
    case DiscountType::ProductValue:
      // fallthrough
    case DiscountType::ProductWithAbsoluteValue:
      return discounts_lib::ProductDiscount{
          value, static_cast<unsigned int>(bundle.value_or(2))};
  }
}

discounts_lib::AbsoluteValue MakeAbsoluteDisc(const std::string& value) {
  return {discounts_lib::AbsoluteValueValuetype::kAbsolute /*value_type*/,
          value /*value*/};
}

discounts_lib::FractionValueWithMaximum MakeFractionWithMaxDisc(
    const std::string& value,
    const std::optional<std::string>& max_disc = std::nullopt) {
  return {discounts_lib::FractionValueWithMaximumValuetype::
              kFraction /*value_type*/,
          value /*value*/, max_disc /*maximum_discount*/};
}

discounts_lib::FractionValue MakeFractionDisc(const std::string& value) {
  return {discounts_lib::FractionValueValuetype::kFraction /*value_type*/,
          value /*value*/};
}

std::optional<discounts_lib::TableItemDiscount> MakeTableItem(
    const TableData& table_item) {
  switch (table_item.type) {
    case DiscountType::NoDiscount:
    case DiscountType::TableValue:
    case DiscountType::ProductWithAbsoluteValue:
      throw;
    case DiscountType::ProductValue:
      return std::nullopt;
    case DiscountType::AbsoluteValue:
      return discounts_lib::TableItemDiscount{
          MakeAbsoluteDisc(table_item.value)};
    case DiscountType::FractionWithMaximum:
      return discounts_lib::TableItemDiscount{
          MakeFractionDisc(table_item.value)};
  }
}

std::vector<discounts_lib::TableItem> MakeTableItems(
    const std::vector<TableData>& table_data) {
  std::vector<discounts_lib::TableItem> table_value;
  if (!table_data.empty()) {
    for (const auto& table_item : table_data) {
      const auto& table_item_opt = MakeTableItem(table_item);
      if (table_item_opt) {
        table_value.push_back(
            {table_item.cart_subtotal, table_item_opt.value()});
      }
    }
    return table_value;
  }

  // default value
  table_value.push_back(
      {"100" /*from_cost*/,
       discounts_lib::TableItemDiscount{MakeAbsoluteDisc("15")} /*discount*/});
  table_value.push_back(
      {"500" /*from_cost*/,
       discounts_lib::TableItemDiscount{MakeFractionDisc("10")} /*discount*/});
  return table_value;
}

discounts_lib::TableValue MakeTableDisc(
    const std::vector<TableData>& table_data = {}) {
  return {discounts_lib::TableValueValuetype::kTable /*value_type*/,
          MakeTableItems(table_data) /*value*/};
}

std::optional<discounts_lib::MoneyCashbackMenuDiscount> MakeMoneyValue(
    DiscountType type, const std::string& value,
    const std::optional<std::string>& max_disc = std::nullopt) {
  switch (type) {
    case DiscountType::NoDiscount:
      // fallthrough
    case DiscountType::ProductValue:
      return std::nullopt;
    case DiscountType::AbsoluteValue:
      // fallthrough
    case DiscountType::ProductWithAbsoluteValue:
      return discounts_lib::MoneyCashbackMenuDiscount{
          discounts_lib::DiscountValue{MakeAbsoluteDisc(value)}};
    case DiscountType::FractionWithMaximum:
      return discounts_lib::MoneyCashbackMenuDiscount{
          discounts_lib::DiscountValue{
              MakeFractionWithMaxDisc(value, max_disc)}};
    case DiscountType::TableValue:
      return discounts_lib::MoneyCashbackMenuDiscount{
          discounts_lib::DiscountValue{MakeTableDisc()}};
  }
}

std::optional<discounts_client::V2MatchedMoneyProductDiscount>
MakeMatchedMenuDiscount(DiscountType type, const std::string& value,
                        const std::optional<std::string>& max_disc,
                        std::optional<int> bundle,
                        const std::optional<std::string>& promotype,
                        const std::optional<CustomPromoInfo>& promo_info_opt,
                        const std::optional<std::string> discount_id) {
  if (type == DiscountType::NoDiscount) {
    return std::nullopt;
  }
  discounts_client::V2MatchedMoneyProductDiscount discount;
  discount.discount_id = discount_id.value_or("21");
  if (promo_info_opt.has_value()) {
    const auto& promo_info = promo_info_opt.value();
    if (promo_info.name.has_value()) {
      discount.discount_meta.promo.name = promo_info.name.value();
    }
    if (promo_info.description.has_value()) {
      discount.discount_meta.promo.description = promo_info.description.value();
    }
    if (promo_info.picture_uri.has_value()) {
      discount.discount_meta.promo.picture_uri = promo_info.picture_uri.value();
    }
  }
  if (promotype.has_value()) {
    discount.discount_meta.promo.promo_type = promotype.value();
  }
  discount.money_value = MakeMoneyValue(type, value, max_disc);
  discount.product_value = MakeProductValue(type, value, bundle);

  return discount;
}

template <class MenuCashbackResult>
MenuCashbackResult MakeMenuCashbackResult(
    CashbackType type, const std::string& value,
    const std::optional<std::string>& max_cashback,
    const std::optional<std::string>& product_id) {
  MenuCashbackResult matched_result;
  if (auto cashback = MakeMatchedCashback(type, value, max_cashback)) {
    matched_result.discounts = {std::move(*cashback)};
    matched_result.subquery_results.emplace(
        {discounts_client::SubqueryResult{product_id.value_or("1"), "111"}});
  }
  return matched_result;
}

template <class DeliveryDiscount>
std::optional<DeliveryDiscount> MakeMatchedDeliveryDiscount(
    DeliveryDiscountType type, const std::string& value, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& max_discount,
    const std::optional<std::string>& promotype) {
  DeliveryDiscount discount;
  discount.discount_meta.promo.name = name;
  discount.discount_meta.promo.description = description;
  discount.discount_meta.promo.picture_uri = picture_uri;
  discount.discount_id = id;
  discount.discount_meta.promo.promo_type = promotype;
  switch (type) {
    case DeliveryDiscountType::NoDiscount:
      return std::nullopt;
    case DeliveryDiscountType::AbsoluteValue:
      discount.money_value.menu_value = MakeAbsoluteDisc(value);
      break;
    case DeliveryDiscountType::FractionWithMaximum:
      discount.money_value.menu_value =
          MakeFractionWithMaxDisc(value, max_discount);
      break;
    case DeliveryDiscountType::TableValue:
      discount.money_value.menu_value = MakeTableDisc();
      break;
  }
  return discount;
}

template <class DeliveryDiscount>
std::optional<DeliveryDiscount> MakeMatchedTableDeliveryDiscount(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  DeliveryDiscount discount;
  discount.discount_meta.promo.name = name;
  discount.discount_meta.promo.description = description;
  discount.discount_meta.promo.picture_uri = picture_uri;
  discount.discount_meta.promo.promo_type = promotype;
  discount.discount_id = id;
  discount.money_value.menu_value = MakeTableDisc(table_data);
  return discount;
}

std::optional<discounts_lib::ProductCartDiscountTableItem> MakeProductTableItem(
    const TableData& step_data) {
  switch (step_data.type) {
    case DiscountType::NoDiscount:
    case DiscountType::TableValue:
    case DiscountType::ProductWithAbsoluteValue:
      throw;
    case DiscountType::ProductValue:
      return discounts_lib::ProductCartDiscountTableItem{
          {step_data.cart_subtotal, "100"},
          {discounts_lib::Product{step_data.value}},
          1};
    case DiscountType::AbsoluteValue:
    case DiscountType::FractionWithMaximum:
      return std::nullopt;
  }
}

discounts_lib::ProductCartDiscount MakeProductTable(
    const std::vector<TableData>& table_data) {
  std::vector<discounts_lib::ProductCartDiscountTableItem> table_value;
  for (const auto& table_item : table_data) {
    const auto& table_item_opt = MakeProductTableItem(table_item);
    if (table_item_opt) {
      table_value.push_back(table_item_opt.value());
    }
  }
  return {table_value};
}

template <class CartDiscount>
std::optional<CartDiscount> MakeMatchedTableCartDiscount(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  CartDiscount discount;
  discount.discount_meta.promo.name = name;
  discount.discount_meta.promo.description = description;
  discount.discount_meta.promo.picture_uri = picture_uri;
  discount.discount_meta.promo.promo_type = promotype;
  discount.discount_id = id;
  const auto& money_value = MakeTableDisc(table_data);
  if (!money_value.value.empty()) {
    discount.money_value = discounts_lib::MoneyCashbackMenuDiscount{
        discounts_lib::DiscountValue{money_value}};
  }

  const auto& product_value = MakeProductTable(table_data);
  if (!product_value.value.empty()) {
    discount.product_value = discounts_lib::ProductCartDiscount{product_value};
  }
  return discount;
}

template <class DeliveryDiscountsResult>
DeliveryDiscountsResult MakeDeliveryDiscountResult(
    DeliveryDiscountType type, const std::string& value,
    const std::optional<std::string>& max_discount, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  DeliveryDiscountsResult matched_result;
  if (auto discount =
          MakeMatchedDeliveryDiscount<MatchedDiscount<DeliveryDiscountsResult>>(
              type, value, id, name, description, picture_uri, max_discount,
              promotype)) {
    matched_result.discounts = {std::move(discount.value())};
    matched_result.discount_id = id;
  }
  return matched_result;
}

template <class DeliveryDiscountsResult>
DeliveryDiscountsResult MakeTableDeliveryDiscountResult(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  DeliveryDiscountsResult matched_result;
  if (auto discount = MakeMatchedTableDeliveryDiscount<
          MatchedDiscount<DeliveryDiscountsResult>>(
          table_data, id, name, description, picture_uri, promotype)) {
    matched_result.discounts = {std::move(discount.value())};
    matched_result.discount_id = id;
  }
  return matched_result;
}

template <class DeliveryDiscountsResult>
DeliveryDiscountsResult MakeCartDiscountResult(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  DeliveryDiscountsResult matched_result;
  if (auto discount = MakeMatchedTableCartDiscount<
          MatchedDiscount<DeliveryDiscountsResult>>(
          table_data, id, name, description, picture_uri, promotype)) {
    matched_result.discounts = {std::move(discount.value())};
    matched_result.discount_id = id;
  }
  return matched_result;
}

discounts_lib::MoneyCashbackCartDiscount MakeMoneyCashbackDiscount(
    const std::vector<TableData>& table_data) {
  discounts_lib::MoneyCashbackCartDiscount cart_discount;
  cart_discount.cart_value = discounts_lib::CartDiscountValue{
      std::nullopt,               // maximum_discount
      MakeTableItems(table_data)  // value
  };
  return cart_discount;
}

discounts_client::V2MatchedCartDiscount MakeYandexCartDiscount(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchedCartDiscount discount;
  discount.discount_meta.promo.name = name;
  discount.discount_meta.promo.description = description;
  discount.discount_meta.promo.picture_uri = picture_uri;
  discount.discount_meta.promo.promo_type = promotype;
  discount.discount_id = id;
  const auto& money_value = MakeMoneyCashbackDiscount(table_data);
  if (!money_value.cart_value.value().value.empty()) {
    discount.money_value = money_value;
  }

  const auto& product_value = MakeProductTable(table_data);
  if (!product_value.value.empty()) {
    discount.product_value = discounts_lib::ProductCartDiscount{product_value};
  }
  return discount;
}

discounts_client::V2MatchedCartDiscountsResult MakeLegacyCartDiscount(
    const std::vector<TableData>& table_data, const std::string& id,
    const std::string& name, const std::string& description,
    const std::string& picture_uri,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchedCartDiscountsResult matched_result;
  matched_result.discounts = {MakeYandexCartDiscount(
      table_data, id, name, description, picture_uri, promotype)};
  matched_result.discount_id = id;
  return matched_result;
}

}  // namespace

discounts_client::V2MatchedMoneyProductDiscount MakeV2MenuDiscount(
    DiscountType type, const std::string& value,
    const std::optional<std::string>& max_disc,
    const std::optional<std::string>& promotype,
    const std::optional<CustomPromoInfo>& promo_info,
    const std::optional<std::string> discount_id) {
  if (promotype.has_value()) {
    LOG_INFO() << promotype.value();
  }
  return MakeMatchedMenuDiscount(type, value, max_disc, std::nullopt /*bundle*/,
                                 promotype, promo_info, discount_id)
      .value();
}

requesters::MatchedDiscounts MakeResponses(
    DiscountType type,
    const experiments::ExcludedInformation& excluded_information,
    const PromoTypesInfo& promo_types_info, const std::string& value,
    const std::optional<std::string>& max_disc, std::optional<int> bundle,
    const std::optional<std::string>& promotype) {
  return requesters::ParseMatchResponse(
      {MakeMenuDiscountResponse(type, value, max_disc, bundle, std::nullopt,
                                promotype)},
      excluded_information, promo_types_info);
}

discounts_client::V2MatchDiscountsResponse MakeMenuDiscountResponse(
    DiscountType type, const std::string& value,
    const std::optional<std::string>& max_disc, std::optional<int> bundle,
    const std::optional<std::string>& product_id,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchedMenuDiscountsResult matched_result;
  matched_result.hierarchy_name =
      discounts_lib::MenuDiscountsHierarchyName::kMenuDiscounts;
  if (auto discount =
          MakeMatchedMenuDiscount(type, value, max_disc, bundle, promotype,
                                  old_promo_type_info, std::nullopt)) {
    matched_result.discounts = {std::move(*discount)};
    matched_result.subquery_results.emplace(
        {discounts_client::SubqueryResult{product_id.value_or("1"), "21"}});
  }

  return discounts_client::V2MatchDiscountsResponse{
      {discounts_client::MatchResult{matched_result}}};
}

discounts_client::V2MatchDiscountsResponse MakeRestaurantMenuDiscountResponse(
    DiscountType type, const std::string& value,
    const std::optional<std::string>& max_disc, std::optional<int> bundle,
    const std::optional<std::string>& product_id,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchedRestaurantMenuDiscountsResult matched_result;
  matched_result.hierarchy_name = discounts_client::
      RestaurantMenuDiscountsHierarchyName::kRestaurantMenuDiscounts;
  if (auto discount = MakeMatchedMenuDiscount(type, value, max_disc, bundle,
                                              promotype, old_promo_type_info,
                                              std::nullopt /*discount_id*/)) {
    matched_result.discounts = {std::move(*discount)};
    matched_result.subquery_results.emplace(
        {discounts_client::SubqueryResult{product_id.value_or("1"), "21"}});
  }

  return discounts_client::V2MatchDiscountsResponse{
      {discounts_client::MatchResult{matched_result}}};
}

discounts_client::V2MatchDiscountsResponse MakeDiscountCartResponse(
    const std::vector<TableData>& table_data,
    const std::optional<std::string>& promotype, CartDiscount cart_discount) {
  discounts_client::V2MatchDiscountsResponse response;
  if (cart_discount == CartDiscount::RestaurantDiscount ||
      cart_discount == CartDiscount::CofinancingDiscount) {
    response.match_results.emplace_back(
        MakeCartDiscountResult<
            discounts_client::V2MatchedRestaurantDiscountsResult>(
            table_data, kRestaurantCartDiscountId, kRestaurantCartDiscountName,
            kRestaurantCartDiscountDescription,
            kRestaurantCartDiscountPictureUri, promotype));
  }

  if (cart_discount == CartDiscount::YandexDiscount ||
      cart_discount == CartDiscount::CofinancingDiscount) {
    response.match_results.emplace_back(MakeLegacyCartDiscount(
        table_data, kYandexCartDiscountId, kYandexCartDiscountName,
        kYandexCartDiscountDescription, kYandexCartDiscountPictureUri,
        promotype));
  }
  return response;
}

discounts_client::V2MatchDiscountsResponse MakeYandexCartDiscountResponse(
    const std::vector<TableData>& table_data,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchDiscountsResponse response;
  response.match_results.emplace_back(MakeLegacyCartDiscount(
      table_data, kYandexCartDiscountId, kYandexCartDiscountName,
      kYandexCartDiscountDescription, kYandexCartDiscountPictureUri,
      promotype));

  return response;
}

discounts_client::V2MatchDiscountsResponse MakeDeliveryDiscountResponse(
    DeliveryDiscountType place_discount_type,
    DeliveryDiscountType yandex_discount_type, const std::string& value,
    const std::optional<std::string>& max_discount,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchDiscountsResponse response;
  response.match_results.emplace_back(
      MakeDeliveryDiscountResult<
          discounts_client::V2MatchedPlaceDeliveryDiscountsResult>(
          place_discount_type, value, max_discount, kPlaceDeliveryId,
          kPlaceDeliveryName, kPlaceDeliveryDescription,
          kPlaceDeliveryPictureUri, promotype));

  response.match_results.emplace_back(
      MakeDeliveryDiscountResult<
          discounts_client::V2MatchedYandexDeliveryDiscountsResult>(
          yandex_discount_type, value, max_discount, kYandexDeliveryId,
          kYandexDeliveryName, kYandexDeliveryDescription,
          kYandexDeliveryPictureUri, promotype));

  return response;
}

discounts_client::V2MatchDiscountsResponse MakeTableDeliveryDiscountResponse(
    const std::vector<TableData>& table_data,
    const std::optional<std::string>& promotype) {
  discounts_client::V2MatchDiscountsResponse response;
  response.match_results.emplace_back(
      MakeTableDeliveryDiscountResult<
          discounts_client::V2MatchedPlaceDeliveryDiscountsResult>(
          table_data, kPlaceDeliveryId, kPlaceDeliveryName,
          kPlaceDeliveryDescription, kPlaceDeliveryPictureUri, promotype));

  response.match_results.emplace_back(
      MakeTableDeliveryDiscountResult<
          discounts_client::V2MatchedYandexDeliveryDiscountsResult>(
          table_data, kYandexDeliveryId, kYandexDeliveryName,
          kYandexDeliveryDescription, kYandexDeliveryPictureUri, promotype));

  return response;
}

discounts_client::V2MatchDiscountsResponse MakePlaceCashbackResponse(
    CashbackType type, const std::string& value,
    const std::optional<std::string>& max_cashback,
    const std::optional<std::string>& product_id) {
  auto matched_result = MakeMenuCashbackResult<
      discounts_client::V2MatchedPlaceMenuCashbackResult>(
      type, value, max_cashback, product_id);
  return discounts_client::V2MatchDiscountsResponse{
      {discounts_client::MatchResult{std::move(matched_result)}}};
}

discounts_client::V2MatchDiscountsResponse MakeYandexCashbackResponse(
    CashbackType type, const std::string& value,
    const std::optional<std::string>& max_cashback,
    const std::optional<std::string>& product_id) {
  auto matched_result = MakeMenuCashbackResult<
      discounts_client::V2MatchedYandexMenuCashbackResult>(
      type, value, max_cashback, product_id);
  return discounts_client::V2MatchDiscountsResponse{
      {discounts_client::MatchResult{std::move(matched_result)}}};
}

FetchedCashbacks MakeFetchedCashbacks(
    const std::vector<FetchCashbackData>& cashbacks) {
  FetchedCashbacks result;
  for (const auto& cashback_data : cashbacks) {
    auto cashback = MakeMatchedCashback(cashback_data.type, cashback_data.value,
                                        cashback_data.max_cashback);
    if (cashback) {
      result[cashback_data.public_id].push_back(cashback.value());
    }
  }
  return result;
}

std::optional<discounts_client::V2MatchedCashback> MakeMatchedCashback(
    CashbackType type, const std::string& value,
    const std::optional<std::string>& max_cashback) {
  discounts_client::V2MatchedCashback cashback;
  cashback.discount_meta.name = "Cashback";
  cashback.discount_id = "111";
  switch (type) {
    case CashbackType::NoCashback:
      return std::nullopt;
    case CashbackType::AbsoluteValue:
      cashback.cashback_value.menu_value = MakeAbsoluteDisc(value);
      break;
    case CashbackType::FractionWithMaximum:
      cashback.cashback_value.menu_value =
          MakeFractionWithMaxDisc(value, max_cashback);
      break;
    case CashbackType::TableValue:
      cashback.cashback_value.menu_value = MakeTableDisc();
      break;
  }
  return cashback;
}

std::vector<DiscountInfo> CreateDiscountsInfo(
    std::vector<std::string> discount_ids, std::vector<std::string> names,
    std::vector<std::string> descriptions,
    std::vector<std::string> picture_uris, std::vector<Money> amounts,
    std::vector<DiscountType> discount_types,
    std::vector<std::string> discount_values,
    std::vector<std::string> providers,
    std::vector<std::optional<int>> additional_item_quantity) {
  std::vector<DiscountInfo> discounts_info;
  for (size_t i = 0; i < discount_ids.size(); i++) {
    DiscountMeta meta{
        discount_ids[i],
        discount_types[i] == DiscountType::AbsoluteValue ? impl::kMoneyTypeId
                                                         : impl::kProductTypeId,
        discount_types[i] == DiscountType::AbsoluteValue
            ? impl::kMoneyTypeName
            : impl::kProductTypeName,
        names[i],
        descriptions[i],
        picture_uris[i],
        std::nullopt,
        amounts[i],
        providers[i],
    };
    auto money_value = MakeMoneyValue(discount_types[i], discount_values[i]);
    discounts_info.push_back({
        1,                            // payed_item_quantit
        meta,                         // meta
        additional_item_quantity[i],  // additional_item_quantity
        money_value.has_value()
            ? std::make_optional(money_value.value().menu_value)
            : std::nullopt  // money_value
    });
  }
  return discounts_info;
}

}  // namespace eats_discounts_applicator::tests
