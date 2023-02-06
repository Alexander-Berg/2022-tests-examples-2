#include <exception>
#include <optional>
#include <vector>

#include <gtest/gtest.h>

#include <taxi_config/variables/DRIVER_PAYMENT_TYPE_MAPPING.hpp>
#include <testing/taxi_config.hpp>

#include <driver_payment_type/get_payment_type.hpp>
#include <driver_payment_type/models/models.hpp>
#include "models/country.hpp"

namespace dpt = driver_payment_type;
namespace dptm = taxi_config::driver_payment_type_mapping;
using Park = parks_activation::models::Park;

using namespace ::driver_payment_type;

namespace {

using order_types::kCard;
using order_types::kCorp;
using order_types::kCoupon;

const std::unordered_map<std::string, dptm::Extra> payment_types_map{
    {"agent", dptm::Extra::kOnline},
    {"applepay", dptm::Extra::kOnline},
    {"card", dptm::Extra::kOnline},
    {"cash", dptm::Extra::kCash},
    {"coop_account", dptm::Extra::kOnline},
    {"corp", dptm::Extra::kOnline},
    {"coupon", dptm::Extra::kCash},
    {"creditcard", dptm::Extra::kOnline},
    {"googlepay", dptm::Extra::kOnline},
    {"personal_wallet", dptm::Extra::kOnline},
    {"yandex_card", dptm::Extra::kOnline}};

class RequestBuilder {
 public:
  PaymentTypeRequest Build() {
    return {
        park,
        country,
        driver_park_balance,
        driver_park_balance_limit,
        current_payment_type,
        zone_payment_options,
        is_in_surge,
        config_payment_type_mapping,
        config_payment_type_max_enabled_count,
        config_disabled_countries,
    };
  }
  std::optional<parks_activation::models::Park> park;
  std::optional<models::Country> country;
  std::optional<double> driver_park_balance;
  std::optional<double> driver_park_balance_limit;
  std::optional<DriverPaymentType> current_payment_type;
  std::unordered_set<dpt::OrderPaymentType> zone_payment_options;
  bool is_in_surge;
  DriverPaymentTypeMapping config_payment_type_mapping;
  int config_payment_type_max_enabled_count;
  std::vector<std::string> config_disabled_countries;
};

struct ParkOnlyCash : public Park {
  ParkOnlyCash() : Park() { can_cash = true; };
};

struct ParkCashAndOnline : public Park {
  ParkCashAndOnline() : Park() {
    can_cash = true;
    can_card = true;
    can_corp = true;
    can_coupon = true;
  };
};

struct DeactivatedPark : public ParkCashAndOnline {
  DeactivatedPark() : ParkCashAndOnline() { deactivated = true; };
};

RequestBuilder DefaultBuilder() {
  Park park;
  models::Country country{};
  country.id = "country0";
  country.allow_onlycard = false;
  double balance = 1000;
  double balance_limit = 0;
  return {park,
          country,
          balance,
          balance_limit,
          std::make_optional<dpt::DriverPaymentType>(),
          {},
          false,
          dpt::ToTypeMapping(payment_types_map),
          5,
          {"country1"}};
}

}  // namespace

TEST(DriverPaymentType, NoPark) {
  auto builder = DefaultBuilder();
  builder.park = std::nullopt;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  ASSERT_EQ(response, std::nullopt);
}

TEST(DriverPaymentType, ParkHasNoAvailablePaymentTypes) {
  auto builder = DefaultBuilder();
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  ASSERT_EQ(response, std::nullopt);
}

TEST(DriverPaymentType, DeactivatedPark) {
  auto builder = DefaultBuilder();
  auto storage = dynamic_config::MakeDefaultStorage({});
  // ensure nullopt is due to only park.deactivated = true
  builder.park = DeactivatedPark();
  builder.zone_payment_options = {dpt::OrderPaymentType::kCard,
                                  dpt::OrderPaymentType::kCorp,
                                  dpt::OrderPaymentType::kCoupon};
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  ASSERT_EQ(response, std::nullopt);
}

TEST(DriverPaymentType, CountryDisabledCashOnly) {
  auto builder = DefaultBuilder();
  builder.park = ParkOnlyCash();
  builder.country->id = "country1";
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);

  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kCash);
  auto response_cash_reasons = response->GetReasonsByType(payment_type);
  auto expect_cash_reasons = dpt::BlockReasons{dpt::BlockReason::kDisabled};
  auto response_none_reasons = response->GetReasonsByType(dpt::Type::kNone);
  auto expect_none_reasons = BlockReasons{dpt::BlockReason::kParksActivation};
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCash,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, NoZoneDriverPayments) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  ASSERT_EQ(response, std::nullopt);
}

TEST(DriverPaymentType, ZoneDriverPaymentsOnline) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {dpt::OrderPaymentType::kCard,
                                  dpt::OrderPaymentType::kCorp};
  builder.current_payment_type = std::make_optional<dpt::DriverPaymentType>();
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kOnline);
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{BlockReason::kZoneSettings};
  auto response_cash_reasons = response->GetReasonsByType(Type::kCash);
  auto expect_cash_reasons = BlockReasons{BlockReason::kZoneSettings};
  ASSERT_EQ(response_none_reasons, expect_none_reasons);
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, BalanceBelowLimitOnline) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.driver_park_balance = 1;
  builder.driver_park_balance_limit = 2;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kOnline);
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{BlockReason::kLowBalance};
  auto response_cash_reasons = response->GetReasonsByType(Type::kCash);
  auto expect_cash_reasons = BlockReasons{BlockReason::kLowBalance};
  ASSERT_EQ(response_none_reasons, expect_none_reasons);
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, LimitExceededNone) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->enabled_count = 5;
  builder.current_payment_type->payment_type = Type::kNone;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kNone);
  auto response_online_reasons = response->GetReasonsByType(Type::kOnline);
  auto expect_online_reasons = BlockReasons{BlockReason::kLimitExceed};
  auto response_cash_reasons = response->GetReasonsByType(Type::kCash);
  auto expect_cash_reasons = BlockReasons{BlockReason::kLimitExceed};
  ASSERT_EQ(response_online_reasons, expect_online_reasons);
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCash,
      dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp,
      dpt::OrderPaymentType::kCoupon,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, InSurgeCash) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->payment_type = Type::kCash;
  builder.is_in_surge = true;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kCash);

  auto response_online_reasons = response->GetReasonsByType(Type::kOnline);
  auto expect_online_reasons = BlockReasons{BlockReason::kSurge};
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{};
  ASSERT_EQ(response_online_reasons, expect_online_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);

  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCash,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, InSurgeOnline) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->payment_type = Type::kOnline;
  builder.is_in_surge = true;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kOnline);

  auto response_cash_reasons = response->GetReasonsByType(Type::kCash);
  auto expect_cash_reasons = BlockReasons{BlockReason::kSurge};
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{};
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);

  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCard, dpt::OrderPaymentType::kCorp,
      dpt::OrderPaymentType::kCoupon};

  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, InSurgeNone) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->payment_type = Type::kNone;
  builder.is_in_surge = true;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kNone);

  auto response_cash_reasons = response->GetReasonsByType(Type::kCash);
  auto expect_cash_reasons = BlockReasons{BlockReason::kSurge};
  auto response_online_reasons = response->GetReasonsByType(Type::kOnline);
  auto expect_online_reasons = BlockReasons{BlockReason::kSurge};
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{};
  ASSERT_EQ(response_cash_reasons, expect_cash_reasons);
  ASSERT_EQ(response_online_reasons, expect_online_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);

  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, NoProblemTakeYourCash) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->payment_type = Type::kCash;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kCash);
  auto response_online_reasons = response->GetReasonsByType(Type::kOnline);
  auto expect_online_reasons = BlockReasons{};
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{};
  ASSERT_EQ(response_online_reasons, expect_online_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCash,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, NoProblemTakeYourCard) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type->payment_type = Type::kOnline;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  auto payment_type = response->GetActive().value_or(Type::kNone);
  ASSERT_EQ(payment_type, Type::kOnline);
  auto response_online_reasons = response->GetReasonsByType(Type::kOnline);
  auto expect_online_reasons = BlockReasons{};
  auto response_none_reasons = response->GetReasonsByType(Type::kNone);
  auto expect_none_reasons = BlockReasons{};
  ASSERT_EQ(response_online_reasons, expect_online_reasons);
  ASSERT_EQ(response_none_reasons, expect_none_reasons);
  auto response_order_payment_types = response->GetOrderTypesSet();
  std::unordered_set<dpt::OrderPaymentType> expected_order_payment_types{
      dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp,
      dpt::OrderPaymentType::kCoupon,
  };
  ASSERT_EQ(response_order_payment_types, expected_order_payment_types);
}

TEST(DriverPaymentType, NoCurrentPaymentType) {
  auto builder = DefaultBuilder();
  builder.park = ParkCashAndOnline();
  builder.zone_payment_options = {
      dpt::OrderPaymentType::kCash, dpt::OrderPaymentType::kCard,
      dpt::OrderPaymentType::kCorp, dpt::OrderPaymentType::kCoupon};
  builder.current_payment_type = std::nullopt;
  auto params = builder.Build();

  auto response = dpt::GetDriverPaymentType(params);
  ASSERT_EQ(response, std::nullopt);
}
