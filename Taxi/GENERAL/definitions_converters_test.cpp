#include <gtest/gtest.h>

#include <pricing-functions/lang/backend_variables.hpp>
#include <userver/utils/boost_uuid4.hpp>

#include <helpers/definitions_converters.hpp>

namespace {

namespace rd = clients::ride_discounts;

static const rd::HyperbolasValue kHyperbolasValue{
    rd::HyperbolasValueValuetype::kHyperbolas,
    rd::Hyperbolas{1.0, rd::Hyperbola{1.0, 2.0, 3.0},
                   rd::Hyperbola{4.0, 5.0, 6.0}}};

static const rd::TableValue kTableValue{
    rd::TableValueValuetype::kTable,
    {rd::TableItem{10.0, 100.0}, rd::TableItem{15.0, 200.0}}};

static const rd::FlatValue kFlatValue{rd::FlatValueValuetype::kFlat, 10.0};

class FromClientDataTestP
    : public testing::Test,
      public testing::WithParamInterface<rd::MatchedDiscount> {};

rd::MatchedDiscount GetDiscount(
    const rd::DiscountValue& discount_value,
    std::optional<bool> is_price_strikethrough = std::nullopt,
    std::optional<clients::ride_discounts::libraries::discounts::PaymentSystem>
        payment_system = std::nullopt) {
  auto discount = rd::MatchedDiscount{};
  discount.discount_id = "discount_id";
  discount.discount_class = "default";
  discount.name = "name";
  discount.discount_value = discount_value;
  discount.max_absolute_value = 100.0;
  discount.is_price_strikethrough = is_price_strikethrough;
  discount.payment_system = payment_system;
  return discount;
}

template <typename LhsHyperbola, typename RhsHyperbola>
void CompareHyperbolas(const LhsHyperbola& lhs, const RhsHyperbola& rhs) {
  ASSERT_EQ(lhs.p, rhs.p);
  ASSERT_EQ(lhs.a, rhs.a);
  ASSERT_EQ(lhs.c, rhs.c);
}

void CheckRestrictions(
    const lang::variables::DiscountRestrictions& restrictions,
    const rd::MatchedDiscount& discount) {
  ASSERT_EQ(restrictions.min_discount_coeff, 0.0);
  ASSERT_EQ(restrictions.max_discount_coeff, 1.0);
  ASSERT_EQ(restrictions.max_absolute_value, discount.max_absolute_value);
  ASSERT_EQ(restrictions.driver_less_coeff, 1.0);
}

void CompareTables(const std::vector<lang::variables::TableData>& lhs,
                   const std::vector<rd::TableItem>& rhs) {
  ASSERT_EQ(lhs.size(), rhs.size());
  for (size_t i = 0; i < rhs.size(); ++i) {
    const auto& lhs_item = lhs[i];
    const auto& rhs_item = rhs[i];
    ASSERT_EQ(lhs_item.price, rhs_item.from_cost);
    ASSERT_EQ(lhs_item.coeff, rhs_item.discount);
  }
}
}  // namespace

TEST_P(FromClientDataTestP, DefinitionsConverters) {
  const auto& discount = GetParam();

  const auto& discount_info = helpers::FromClientData(discount);

  ASSERT_EQ(discount_info.is_cashback, false);
  ASSERT_EQ(discount_info.id, discount.discount_id);
  ASSERT_EQ(discount_info.discount_class, discount.discount_class);
  const auto& discount_value = discount.discount_value.AsVariant();
  if (const auto* flat_value = std::get_if<rd::FlatValue>(&discount_value)) {
    ASSERT_EQ(discount_info.calc_data_hyperbolas, std::nullopt);
    ASSERT_EQ(discount_info.calc_data_table_data, std::nullopt);
    ASSERT_EQ(discount_info.calc_data_coeff, flat_value->value);
  } else if (const auto* table_value =
                 std::get_if<rd::TableValue>(&discount_value)) {
    ASSERT_EQ(discount_info.calc_data_hyperbolas, std::nullopt);
    ASSERT_EQ(discount_info.calc_data_coeff, std::nullopt);
    CompareTables(discount_info.calc_data_table_data.value(),
                  table_value->value);
  } else {
    const auto& hyperbolas_value =
        std::get<rd::HyperbolasValue>(discount_value);
    ASSERT_EQ(discount_info.calc_data_table_data, std::nullopt);
    ASSERT_EQ(discount_info.calc_data_coeff, std::nullopt);
    const auto& hyperbolas_data = discount_info.calc_data_hyperbolas.value();
    const auto& hyperbolas = hyperbolas_value.value;
    ASSERT_EQ(hyperbolas_data.threshold, hyperbolas.threshold);
    CompareHyperbolas(hyperbolas_data.hyperbola_lower,
                      hyperbolas.hyperbola_lower);
    CompareHyperbolas(hyperbolas_data.hyperbola_upper,
                      hyperbolas.hyperbola_upper);
  }

  CheckRestrictions(discount_info.restrictions, discount);
  std::optional<std::string> payment_system;
  if (discount.payment_system) {
    payment_system = ToString(*discount.payment_system);
  }
  ASSERT_EQ(discount_info.payment_system, payment_system);

  ASSERT_EQ(discount_info.limited_rides, false);
  ASSERT_EQ(discount_info.description, discount.name);
  ASSERT_EQ(discount_info.method, "subvention-fix");

  ASSERT_EQ(discount_info.is_price_strikethrough,
            discount.is_price_strikethrough);
}

INSTANTIATE_TEST_SUITE_P(
    FromClientDataTest, FromClientDataTestP,
    testing::Values(GetDiscount(rd::DiscountValue{kFlatValue}),
                    GetDiscount(rd::DiscountValue{kHyperbolasValue}),
                    GetDiscount(rd::DiscountValue{kTableValue}),
                    GetDiscount(rd::DiscountValue{kHyperbolasValue}, false),
                    GetDiscount(rd::DiscountValue{kHyperbolasValue}, true),
                    GetDiscount(rd::DiscountValue{kHyperbolasValue}, false,
                                clients::ride_discounts::libraries::discounts::
                                    PaymentSystem::kMir)));
