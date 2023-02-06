#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <userver/utils/text.hpp>

#include <price-format/taximeter_price.hpp>
#include <price-format/template.hpp>

namespace {

using price_format::taximeter::Money;
using price_format::taximeter::RoundingType;

inline const std::string kTextTemplate = "$VALUE$ $SIGN$$CURRENCY$";
inline const std::string kCurrencySign = "₽";
inline const std::string kNegativeSign = "-";

std::string FormatPrice(
    const double price, const price_format::CurrencyRules& rules,
    uint32_t precision, RoundingType rounding_type = RoundingType::kNormal,
    const std::string& system_locale =
        price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
    const std::string& minus_sign = kNegativeSign,
    const bool make_frac_digits_small = false, const bool is_fixed = false) {
  return price_format::taximeter::impl::FormatPrice(
      price, rules, precision, rounding_type, system_locale, minus_sign,
      make_frac_digits_small, is_fixed);
}

std::string DecimalFormatPrice(const Money& price,
                               const decimal64::FormatOptions& options = {},
                               const bool without_currency = false) {
  const auto value = decimal64::ToString(price, options);
  if (without_currency) {
    return value;
  }
  return price_format::tpl::Fill(kTextTemplate, value, kCurrencySign, "");
}

price_format::CurrencyRules MakeRules(const std::string& tpl,
                                      const std::string& sign,
                                      const std::string& code,
                                      const std::string& text) {
  price_format::CurrencyRules rules;
  rules.text_template = tpl;
  rules.sign = sign;
  rules.code = price_format::Currency{code};
  rules.text = text;
  return rules;
}

}  // namespace

TEST(TaximeterPriceTest, DecimalFormatPrice) {
  EXPECT_EQ(DecimalFormatPrice(Money("1234.0100")), "1234.01 ₽");

  decimal64::FormatOptions format_options{
      price_format::taximeter::kDecimalPoint,
      price_format::taximeter::kThousandsSep,
      price_format::taximeter::kGrouping,
      kNegativeSign,
      Money::kDecimalPoints,
      false};
  EXPECT_EQ(DecimalFormatPrice(Money("-1234.0100"), format_options),
            "-1\u00A0234,01 ₽");
  EXPECT_EQ(DecimalFormatPrice(Money("-1234.0100"), format_options, true),
            "-1\u00A0234,01");

  format_options.precision = 6;
  format_options.is_fixed = true;
  EXPECT_EQ(DecimalFormatPrice(Money("1234.1234"), format_options),
            "1\u00A0234,123400 ₽");

  format_options.precision = 2;
  EXPECT_EQ(DecimalFormatPrice(Money("1234.1250"), format_options),
            "1\u00A0234,13 ₽");
  EXPECT_EQ(DecimalFormatPrice(Money("1234.1000"), format_options),
            "1\u00A0234,10 ₽");

  format_options.is_fixed = false;
  EXPECT_EQ(DecimalFormatPrice(Money("1234.1250"), format_options),
            "1\u00A0234,13 ₽");
  EXPECT_EQ(DecimalFormatPrice(Money("1234.1000"), format_options),
            "1\u00A0234,1 ₽");
  EXPECT_EQ(DecimalFormatPrice(Money("-0.0049"), format_options), "0 ₽");
}

TEST(TaximeterPriceTest, FormatPrice) {
  RunInCoro([] {
    const auto rules = MakeRules(kTextTemplate, kCurrencySign, "RUB", "руб.");

    EXPECT_EQ(FormatPrice(1000.06, rules, 0), "1 000 ₽");
    EXPECT_EQ(FormatPrice(1000.00, rules, 2), "1 000 ₽");
    EXPECT_EQ(FormatPrice(1000.04, rules, 2), "1 000,04 ₽");
    EXPECT_EQ(FormatPrice(1000.05, rules, 1), "1 000,1 ₽");
    EXPECT_EQ(FormatPrice(1000.06, rules, 1, RoundingType::kCeil),
              "1 000,1 ₽");
    EXPECT_EQ(FormatPrice(1000.06, rules, 1, RoundingType::kFloor),
              "1 000 ₽");
    EXPECT_EQ(FormatPrice(1000.065, rules, 2, RoundingType::kNormal, "C"),
              "1000.07 ₽");
    EXPECT_EQ(
        FormatPrice(1000.065, rules, 3, RoundingType::kNormal, "en_US.UTF-8"),
        "1,000.065 ₽");

    EXPECT_EQ(
        FormatPrice(1000.065, rules, 3, RoundingType::kNormal, "en_US.UTF-8"),
        "1,000.065 ₽");
    // hyphen
    EXPECT_EQ(
        FormatPrice(-1000, rules, 0, RoundingType::kNormal, "en_US.UTF-8", "-"),
        "-1,000 ₽");
    // minus
    EXPECT_EQ(
        FormatPrice(-1000, rules, 0, RoundingType::kNormal, "en_US.UTF-8", "−"),
        "−1,000 ₽");
    // small fraction digits
    EXPECT_EQ(FormatPrice(-1000.065, rules, 3, RoundingType::kNormal,
                          "en_US.UTF-8", "-", true),
              "-1,000.<small>065</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  1000.04, rules, 2, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, false),
              "1 000,<small>04</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -0.16, rules, 3, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, true),
              "-0,<small>160</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -10.0, rules, 3, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, true),
              "-10,<small>000</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -1000111.17, rules, 1, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, false),
              "-1 000 111,<small>2</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -1000111.0, rules, 1, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, false),
              "-1 000 111 <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -1000111.0, rules, 1, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, true),
              "-1 000 111,<small>0</small> <small>₽</small>");
    EXPECT_EQ(FormatPrice(
                  -1000111.67, rules, 0, RoundingType::kNormal,
                  price_format::taximeter::kSystemLocaleSpaceThousandsSeparator,
                  "-", true, true),
              "-1 000 112 <small>₽</small>");
  });
}
