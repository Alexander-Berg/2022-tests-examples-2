#include <iterator>
#include <memory>
#include <utility>

#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <clients/eats-catalog/client.hpp>
#include <clients/eats-catalog/definitions.hpp>
#include <defs/all_definitions.hpp>
#include <handlers/dependencies.hpp>

#include <models/common.hpp>
#include <models/extra_fees.hpp>
#include <models/surge.hpp>
#include <utils/localizations.hpp>
#include "delivery_fee.hpp"
#include "eats-discounts-applicator/discounts_threshold.hpp"
#include "models/extra_fees.hpp"

namespace eats_cart::utils {
namespace {

using Decimal = decimal64::Decimal<2>;
using Threshold = clients::eats_catalog::Threshold;
using ExtraFeePayload = defs::internal::extra_fee_payload::ExtraFeePayload;

using ::utils::datetime::MockNowSet;

const cctz::time_zone kTimezone = cctz::utc_time_zone();

using NoDscountCalc = models::NoDeliveryDiscountCalculator;
using DeliveryDiscount = defs::internal::extra_fee_payload::Discount;

class ConstDeliveryDiscountCalculator
    : public models::DeliveryDiscountCalculator {
 private:
  models::DeliveryDiscountInfo result_;

 public:
  ConstDeliveryDiscountCalculator(models::DeliveryDiscountInfo info)
      : result_(std::move(info)) {}
  models::DeliveryDiscountInfo Calculate(
      const models::PriceMoney&, const models::PriceMoney&) const final {
    LOG_INFO() << "calculate db delivery discount=" << result_.eda_discount
               << result_.place_discount;
    return result_;
  };
};

models::PriceMoney CalculateSubtotal(
    const std::vector<std::pair<int, int>>& multipliers) {
  models::PriceMoney sum{0};
  for (const auto& [price, quantity] : multipliers) {
    sum += price * quantity;
  }
  return sum;
}

eats_cart::requesters::PlaceInfo MakePlaceInfo(
    const std::vector<Threshold>& thresholds, int assembly_cost = 0,
    std::optional<int> extra_fee = std::nullopt) {
  eats_cart::requesters::PlaceInfo result;
  result.thresholds = thresholds;
  if (extra_fee) {
    result.surge_delivery_fee = models::PriceMoney(*extra_fee);
    models::SurgeInfo surge;
    surge.level = 1;
    surge.additional_fee = models::PriceMoney("0.1");
    result.surge_info = surge;
  }
  result.assembly_cost = assembly_cost;
  return result;
}

eats_cart::requesters::DeliveryPrice MakeDeliveryPrice(const int delivery_fee) {
  eats_cart::requesters::DeliveryPrice result{};
  auto& cart_delivery_price = result.cart_delivery_price.emplace();
  cart_delivery_price.delivery_fee = Decimal{delivery_fee};
  return result;
}

}  // namespace

TEST(CalculateDeliveryFeeImpl, Empty) {
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                models::PriceMoney{0}, eats_cart::requesters::PlaceInfo{},
                std::nullopt, models::ShippingType::kDelivery, NoDscountCalc{})
                .money,
            models::PriceMoney{kDefaultDeliveryFee});
}

TEST(CalculateDeliveryFeeImpl, NoSurge) {
  std::vector<std::pair<int, int>> price_quantity;
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};

  price_quantity = {{1, 2}, {2, 3}};  // subtotal = 8
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery), std::nullopt,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{5});

  // place with non-zero assembly cost
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery, 2), std::nullopt,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{5});

  // subtotal is equal to threshold's order_price
  price_quantity = {{3, 1}, {1, 1}};  // subtotal = 4
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery), std::nullopt,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{10});

  // subtotal is less than minimal order_price
  price_quantity = {{1, 1}, {1, 1}};  // subtotal = 2
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery), std::nullopt,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{10});

  // subtotal exceeds maximal order_price from thresholds
  price_quantity = {{1, 10}, {2, 5}};  // subtotal = 20
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery), std::nullopt,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{0});

  // empty thresholds
  models::PriceMoney assembly_cost{10};
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo({}, assembly_cost.ToInteger()), std::nullopt,
                models::ShippingType::kDelivery, NoDscountCalc{})
                .money,
            models::PriceMoney{kDefaultDeliveryFee});
}

TEST(CalculateDeliveryFeeImpl, WithSurgeASAP) {
  auto extra_fee = 10, assembly_cost = 0;
  std::vector<std::pair<int, int>> price_quantity{{1, 2}, {2, 3}};
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};
  ExtraFeePayload delivery_fee_payload;
  models::ExtraFee delivery_fee;

  const auto now =
      cctz::convert(cctz::civil_second(2021, 4, 7, 12, 0, 0), kTimezone);
  MockNowSet(now);

  // zero assembly_cost
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, 0, extra_fee), std::nullopt,
                models::ShippingType::kDelivery, NoDscountCalc{}, now)
                .money,
            models::PriceMoney{extra_fee});

  // non-zero assembly_cost
  assembly_cost = 3;
  delivery_fee = CalculateDeliveryFeeImpl(
      CalculateSubtotal(price_quantity),
      MakePlaceInfo(order_delivery, assembly_cost, extra_fee), std::nullopt,
      models::ShippingType::kDelivery, NoDscountCalc{}, now);
  delivery_fee_payload = delivery_fee.payload.value();
  EXPECT_EQ(delivery_fee.money, models::PriceMoney{extra_fee});
  EXPECT_EQ(delivery_fee_payload.delivery_time.value(), now);

  // free delivey is only possible
  order_delivery = {{Decimal{10}, Decimal{0}}};
  delivery_fee = CalculateDeliveryFeeImpl(
      CalculateSubtotal(price_quantity),
      MakePlaceInfo(order_delivery, assembly_cost, extra_fee), std::nullopt,
      models::ShippingType::kDelivery, NoDscountCalc{}, now);
  delivery_fee_payload = delivery_fee.payload.value();
  EXPECT_EQ(delivery_fee.money, models::PriceMoney{extra_fee});
  EXPECT_EQ(delivery_fee_payload.delivery_time.value(), now);

  // empty thresholds
  delivery_fee = CalculateDeliveryFeeImpl(
      CalculateSubtotal(price_quantity),
      MakePlaceInfo({}, assembly_cost, extra_fee), std::nullopt,
      models::ShippingType::kDelivery, NoDscountCalc{}, now);
  delivery_fee_payload = delivery_fee.payload.value();
  EXPECT_EQ(delivery_fee.money, models::PriceMoney{extra_fee});
  EXPECT_EQ(delivery_fee_payload.delivery_time.value(), now);
}

TEST(CalculateDeliveryFeeImpl, WithSurgeNotASAP) {
  auto extra_fee = 10, assembly_cost = 0;
  std::vector<std::pair<int, int>> price_quantity{{1, 2}, {2, 3}};
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};

  const auto civil_now = cctz::civil_second(2021, 4, 7, 12, 0, 0);
  MockNowSet(cctz::convert(civil_now, kTimezone));

  // kAllowableTimeOffset < dealy
  const auto delay = 20;
  const auto delivery_time = cctz::convert(civil_now + delay, kTimezone);
  const auto delivery_fee = CalculateDeliveryFeeImpl(
      CalculateSubtotal(price_quantity),
      MakePlaceInfo(order_delivery, assembly_cost, extra_fee), std::nullopt,
      models::ShippingType::kDelivery, NoDscountCalc{}, delivery_time);
  const auto payload_delivery_time = delivery_fee.payload.value();
  EXPECT_EQ(delivery_fee.money, models::PriceMoney{5});
  EXPECT_EQ(payload_delivery_time.delivery_time.value(), delivery_time);
}

TEST(CalculateDeliveryFeeImplWithDeliveryPrice, Empty) {
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                models::PriceMoney{0}, eats_cart::requesters::PlaceInfo{},
                MakeDeliveryPrice(100), models::ShippingType::kDelivery,
                NoDscountCalc{})
                .money,
            models::PriceMoney{kDefaultDeliveryFee});
}

TEST(CalculateDeliveryFeeImplWithDeliveryPrice, NoSurge) {
  std::vector<std::pair<int, int>> price_quantity;
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};

  price_quantity = {{1, 2}, {2, 3}};  // subtotal = 8
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery), MakeDeliveryPrice(10),
                models::ShippingType::kDelivery, NoDscountCalc{})
                .money,
            models::PriceMoney{10});

  // place with non-zero assembly cost
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, 2), MakeDeliveryPrice(10),
                models::ShippingType::kDelivery, NoDscountCalc{})
                .money,
            models::PriceMoney{10});

  // Empty cart delivery price
  // (it is for marketplace)
  // expect using threshold
  requesters::DeliveryPrice delivery_price{};
  EXPECT_EQ(
      CalculateDeliveryFeeImpl(CalculateSubtotal(price_quantity),
                               MakePlaceInfo(order_delivery, 2), delivery_price,
                               models::ShippingType::kDelivery, NoDscountCalc{})
          .money,
      models::PriceMoney{5});
}

TEST(CalculateDeliveryFeeImplWithDeliveryPrice, WithSurgeASAP) {
  auto extra_fee = 10, assembly_cost = 0;
  const int delivery_fee{20};
  std::vector<std::pair<int, int>> price_quantity{{1, 2}, {2, 3}};
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};

  const auto now =
      cctz::convert(cctz::civil_second(2021, 4, 7, 12, 0, 0), kTimezone);
  MockNowSet(now);

  // zero assembly_cost
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, 0, extra_fee),
                MakeDeliveryPrice(delivery_fee),
                models::ShippingType::kDelivery, NoDscountCalc{}, now)
                .money,
            models::PriceMoney{delivery_fee});

  // non-zero assembly_cost
  assembly_cost = 3;
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, assembly_cost, extra_fee),
                MakeDeliveryPrice(delivery_fee),
                models::ShippingType::kDelivery, NoDscountCalc{}, now)
                .money,
            models::PriceMoney{delivery_fee});

  // empty delivery_fee
  // do not fallback to catalog's surge
  // user thresholds
  requesters::DeliveryPrice empty_delivery_price{};
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, assembly_cost, extra_fee),
                empty_delivery_price, models::ShippingType::kDelivery,
                NoDscountCalc{}, now)
                .money,
            models::PriceMoney{5});
}

TEST(CalculateDeliveryFeeImplWithDeliveryPrice, WithSurgeNotASAP) {
  auto extra_fee = 10, assembly_cost = 0;
  std::vector<std::pair<int, int>> price_quantity{{1, 2}, {2, 3}};
  std::vector<Threshold> order_delivery{{Decimal{4}, Decimal{10}},
                                        {Decimal{6}, Decimal{5}},
                                        {Decimal{9}, Decimal{3}},
                                        {Decimal{10}, Decimal{0}}};

  const auto civil_now = cctz::civil_second(2021, 4, 7, 12, 0, 0);
  MockNowSet(cctz::convert(civil_now, kTimezone));

  // kAllowableTimeOffset < dealy
  const auto delay = 20;
  const auto delivery_time = cctz::convert(civil_now + delay, kTimezone);
  const auto delivery_fee = CalculateDeliveryFeeImpl(
      CalculateSubtotal(price_quantity),
      MakePlaceInfo(order_delivery, assembly_cost, extra_fee), std::nullopt,
      models::ShippingType::kDelivery, NoDscountCalc{}, delivery_time);
  const auto payload_delivery_time = delivery_fee.payload.value();
  EXPECT_EQ(delivery_fee.money, models::PriceMoney{5});
  EXPECT_EQ(payload_delivery_time.delivery_time.value(), delivery_time);
  EXPECT_EQ(CalculateDeliveryFeeImpl(
                CalculateSubtotal(price_quantity),
                MakePlaceInfo(order_delivery, assembly_cost, extra_fee),
                MakeDeliveryPrice(10), models::ShippingType::kDelivery,
                NoDscountCalc{}, delivery_time)
                .money,
            models::PriceMoney{10});
}

TEST(CalculateDeliveryFeeImpl, WithDiscount) {
  auto zero = models::kZeroPrice;

  DeliveryDiscount discount;
  discount.amount = Decimal{"10"};
  const auto& res = CalculateDeliveryFeeImpl(
      zero, MakePlaceInfo({}, 0, std::nullopt), MakeDeliveryPrice(10),
      models::ShippingType::kDelivery,
      ConstDeliveryDiscountCalculator(
          {discount, std::nullopt,
           defs::internal::extra_fee_payload::DeliveryThreshold{}}));

  EXPECT_EQ(res.money, models::PriceMoney{0});
  EXPECT_EQ(res.payload->place_discount->amount, discount.amount);
}

}  // namespace eats_cart::utils
