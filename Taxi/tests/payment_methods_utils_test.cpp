#include <userver/utest/utest.hpp>

#include <fmt/format.h>

#include <payment-methods-utils/payment_methods_utils.hpp>

namespace {
template <typename PaymentType>
struct Params {
  std::vector<std::string> payment_methods;
  PaymentType expected_payment_type;
  bool should_throw = false;
};

template <typename PaymentType>
std::ostream& operator<<(std::ostream& os, const Params<PaymentType>& params) {
  return os << fmt::format("({})", fmt::join(params.payment_methods, ","));
}
}  // namespace

class PaymentMethodParametrizeString
    : public ::testing::TestWithParam<Params<std::string>> {};

TEST_P(PaymentMethodParametrizeString, ConvertToString) {
  const Params<std::string>& params = GetParam();

  if (params.should_throw) {
    EXPECT_THROW(
        payment_methods_utils::ConvertToPaymentType(params.payment_methods),
        payment_methods_utils::NoPaymentTypeError);
  } else {
    const std::string result =
        payment_methods_utils::ConvertToPaymentType(params.payment_methods);
    EXPECT_EQ(result, params.expected_payment_type);
  }
}

// clang-format off
INSTANTIATE_TEST_SUITE_P(
  PaymentMethodUtils, PaymentMethodParametrizeString,
  ::testing::Values(
    Params<std::string>{{"cash"}, "cash"},
    Params<std::string>{{"card"}, "online"},
    Params<std::string>{{"cash", "card"}, "none"},
    Params<std::string>{{"card", "coupon", "corp"}, "online"},
    Params<std::string>{{"cash", "card", "coupon", "corp"}, "none"},
    Params<std::string>{{"coupon", "corp"}, "", true},
    Params<std::string>{{}, "", true}
  )
);
// clang-format on

namespace {

enum class CustomPaymentType { kNone, kOnline, kCash };

CustomPaymentType Parse(const std::string& string,
                        formats::parse::To<CustomPaymentType>) {
  if (string == "none") {
    return CustomPaymentType::kNone;
  } else if (string == "online") {
    return CustomPaymentType::kOnline;
  } else if (string == "cash") {
    return CustomPaymentType::kCash;
  }
  throw std::invalid_argument("unknown payment type");
}
}  // namespace

class PaymentMethodParametrizeCustom
    : public ::testing::TestWithParam<Params<CustomPaymentType>> {};

TEST_P(PaymentMethodParametrizeCustom, ConvertToCustomType) {
  const Params<CustomPaymentType>& params = GetParam();

  if (params.should_throw) {
    EXPECT_THROW(
        payment_methods_utils::ConvertToPaymentType(params.payment_methods),
        payment_methods_utils::NoPaymentTypeError);
  } else {
    const CustomPaymentType result =
        payment_methods_utils::ConvertToPaymentType<CustomPaymentType>(
            params.payment_methods);
    EXPECT_EQ(result, params.expected_payment_type);
  }
}

// clang-format off
INSTANTIATE_TEST_SUITE_P(
  PaymentMethodUtils, PaymentMethodParametrizeCustom,
  ::testing::Values(
    Params<CustomPaymentType>{{"cash"}, CustomPaymentType::kCash},
    Params<CustomPaymentType>{{"card"}, CustomPaymentType::kOnline},
    Params<CustomPaymentType>{{"cash", "card"}, CustomPaymentType::kNone},
    Params<CustomPaymentType>{{"card", "coupon", "corp"}, CustomPaymentType::kOnline},
    Params<CustomPaymentType>{{"cash", "card", "coupon", "corp"}, CustomPaymentType::kNone},
    Params<CustomPaymentType>{{"coupon", "corp"}, CustomPaymentType::kNone, true},
    Params<CustomPaymentType>{{}, CustomPaymentType::kNone, true}
  )
);
// clang-format on
