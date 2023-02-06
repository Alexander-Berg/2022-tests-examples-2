#pragma once

#include <applicators/cart.hpp>
#include <applicators/item_applier.hpp>
#include <applicators/menu.hpp>
#include <experiments3.hpp>
#include <requesters/utils.hpp>

namespace eats_discounts_applicator::tests {

namespace discounts_client = clients::eats_discounts;
namespace discounts_lib = discounts_client::libraries::discounts;

using DiscountApplier = eats_discounts_applicator::applicators::DiscountApplier;

inline const std::string kPlaceDeliveryId = "44";
inline const std::string kPlaceDeliveryName = "place_discount";
inline const std::string kPlaceDeliveryDescription = "place_descr";
inline const std::string kPlaceDeliveryPictureUri = "place_picture";
inline const std::string kYandexDeliveryId = "55";
inline const std::string kYandexDeliveryName = "yandex_discount";
inline const std::string kYandexDeliveryDescription = "yandex_descr";
inline const std::string kYandexDeliveryPictureUri = "yandex_picture";
inline const std::string kRestaurantCartDiscountId = "66";
inline const std::string kRestaurantCartDiscountName =
    "restaurant_cart_discount_name";
inline const std::string kRestaurantCartDiscountDescription =
    "restaurant_cart_discount_descr";
inline const std::string kRestaurantCartDiscountPictureUri =
    "restaurant_cart_discount_picture";
inline const std::string kYandexCartDiscountId = "77";
inline const std::string kYandexCartDiscountName = "yandex_cart_discount_name";
inline const std::string kYandexCartDiscountDescription =
    "yandex_cart_discount_descr";
inline const std::string kYandexCartDiscountPictureUri =
    "yandex_cart_discount_picture";

inline const experiments::ExcludedInformation kEmptyExcludedInformation;
inline const std::vector<ExpDiscountType> kEmptyExcludedDiscounts = {};

inline const std::unordered_map<
    std::string, experiments3::eats_discounts_promo_types_info::PromoTypeInfo>
    kPromoTypesInfo{
        {"menu_discounts", {"name", "descr", "picture"}},
        {"restaurant_menu_discounts", {"name", "descr", "picture"}},
        {"place_delivery_discounts", {"name", "descr", "picture"}},
        {"restaurant_discounts", {"name", "descr", "picture"}},
        {"yandex_delivery_discounts", {"name", "descr", "picture"}}};

struct CustomPromoInfo {
  std::optional<std::string> name;
  std::optional<std::string> description;
  std::optional<std::string> picture_uri;
};

// TODO(nakap, EDAJAM-543) эта константа для поддержки старых тестов, надо
// отрефакторить их
inline const CustomPromoInfo old_promo_type_info{"name", "descr",
                                                 "picture_uri"};

enum class DiscountType {
  NoDiscount,
  FractionWithMaximum,
  AbsoluteValue,
  TableValue,
  ProductValue,
  ProductWithAbsoluteValue
};

enum class CashbackType {
  NoCashback,
  AbsoluteValue,
  FractionWithMaximum,
  TableValue
};

enum class DeliveryDiscountType {
  NoDiscount,
  AbsoluteValue,
  FractionWithMaximum,
  TableValue
};

enum class CartDiscount {
  YandexDiscount,
  RestaurantDiscount,
  CofinancingDiscount
};

struct FetchCashbackData {
  std::string public_id;
  CashbackType type;
  std::string value;
  std::optional<std::string> max_cashback;
};

struct TableData {
  DiscountType type;
  std::string cart_subtotal;
  std::string value;
};

requesters::MatchedDiscounts MakeResponses(
    DiscountType type,
    const experiments::ExcludedInformation& excluded_information,
    const PromoTypesInfo& promo_types_info, const std::string& value = "10",
    const std::optional<std::string>& max_disc = std::nullopt,
    std::optional<int> bundle = std::nullopt,
    const std::optional<std::string>& promotype = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakeMenuDiscountResponse(
    DiscountType type, const std::string& value = "10",
    const std::optional<std::string>& max_disc = std::nullopt,
    std::optional<int> bundle = std::nullopt,
    const std::optional<std::string>& product_id = std::nullopt,
    const std::optional<std::string>& promotype = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakeRestaurantMenuDiscountResponse(
    DiscountType type, const std::string& value = "10",
    const std::optional<std::string>& max_disc = std::nullopt,
    std::optional<int> bundle = std::nullopt,
    const std::optional<std::string>& product_id = std::nullopt,
    const std::optional<std::string>& promotype = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakePlaceCashbackResponse(
    CashbackType type, const std::string& value = "10",
    const std::optional<std::string>& max_cashback = std::nullopt,
    const std::optional<std::string>& product_id = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakeDeliveryDiscountResponse(
    DeliveryDiscountType place_discount_type,
    DeliveryDiscountType yandex_discount_type, const std::string& value = "10",
    const std::optional<std::string>& max_discount = std::nullopt,
    const std::optional<std::string>& promotype = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakeTableDeliveryDiscountResponse(
    const std::vector<TableData>& table_data,
    const std::optional<std::string>& promotype = std::nullopt);

discounts_client::V2MatchDiscountsResponse MakeDiscountCartResponse(
    const std::vector<TableData>& table_data,
    const std::optional<std::string>& promotype = std::nullopt,
    CartDiscount cart_discount = CartDiscount::RestaurantDiscount);

discounts_client::V2MatchDiscountsResponse MakeYandexCashbackResponse(
    CashbackType type, const std::string& value = "10",
    const std::optional<std::string>& max_cashback = std::nullopt,
    const std::optional<std::string>& product_id = std::nullopt);

discounts_client::V2MatchedMoneyProductDiscount MakeV2MenuDiscount(
    DiscountType type, const std::string& value = "10",
    const std::optional<std::string>& max_disc = std::nullopt,
    const std::optional<std::string>& promotype = std::nullopt,
    const std::optional<CustomPromoInfo>& = old_promo_type_info,
    const std::optional<std::string> discount_id = std::nullopt);

FetchedCashbacks MakeFetchedCashbacks(
    const std::vector<FetchCashbackData>& cashbacks);

std::optional<discounts_client::V2MatchedCashback> MakeMatchedCashback(
    CashbackType type, const std::string& value = "10",
    const std::optional<std::string>& max_cashback = std::nullopt);

std::vector<DiscountInfo> CreateDiscountsInfo(
    std::vector<std::string> discount_ids, std::vector<std::string> names,
    std::vector<std::string> descriptions,
    std::vector<std::string> picture_uris, std::vector<Money> amounts,
    std::vector<DiscountType> discount_types,
    std::vector<std::string> discount_values,
    std::vector<std::string> providers,
    std::vector<std::optional<int>> additional_item_quantity);

}  // namespace eats_discounts_applicator::tests
