#include <gtest/gtest.h>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/shared_readable_ptr.hpp>

#include <taxi_config/variables/GROCERY_LOCALIZATION_CURRENCY_FORMAT.hpp>

#include <grocery-localization/price_formatter.hpp>

namespace grocery_l10n {

using grocery_pricing::Numeric;

std::string TestInterfaceFormatNumber(grocery_pricing::Numeric value,
                                      grocery_pricing::Numeric rounding,
                                      int precision, bool is_fixed,
                                      const std::string& decimal_separator) {
  return PriceFormatter::FormatNumber(value, rounding, precision, is_fixed,
                                      decimal_separator);
}

TEST(TestPriceFormatter, TestFormatNumber) {
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.6"},
                                      /* rounding */ Numeric{"0.1"},
                                      /* precision */ 1,
                                      /* is_fixed */ false,
                                      /* decimal separator */ "."),
            "5.6");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.6"},
                                      /* rounding */ Numeric{"0.1"},
                                      /* precision */ 1,
                                      /* is_fixed */ false,
                                      /* decimal separator */ ","),
            "5,6");
  ASSERT_EQ(TestInterfaceFormatNumber(
                /* value */ Numeric{"5.6"},
                /* rounding */ Numeric{"1"}, /* precision */ 1,
                /* is_fixed */ false, /* decimal separator */ "."),
            "5");
  ASSERT_EQ(TestInterfaceFormatNumber(
                /* value */ Numeric{"5.6"},
                /* rounding */ Numeric{"1"}, /* precision */ 1,
                /* is_fixed */ false, /* decimal separator */ ","),
            "5");
  ASSERT_EQ(TestInterfaceFormatNumber(
                /* value */ Numeric{"5.6"},
                /* rounding */ Numeric{"1"}, /* precision */ 1,
                /* is_fixed */ true, /* decimal separator */ "."),
            "5.0");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.6"},
                                      /* rounding */ Numeric{"0.01"},
                                      /* precision */ 2,
                                      /* is_fixed */ false,
                                      /* decimal separator */ ","),
            "5,6");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.6"},
                                      /* rounding */ Numeric{"0.01"},
                                      /* precision */ 2,
                                      /* is_fixed */ true,
                                      /* decimal separator */ ","),
            "5,60");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.6"},
                                      /* rounding */ Numeric{"0.03"},
                                      /* precision */ 2,
                                      /* is_fixed */ false,
                                      /* decimal separator */ ","),
            "5,58");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.634"},
                                      /* rounding */ Numeric{"0.001"},
                                      /* precision */ 1,
                                      /* is_fixed */ false,
                                      /* decimal separator */ "'"),
            "5'6");
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"5.034"},
                                      /* rounding */ Numeric{"0.001"},
                                      /* precision */ 1,
                                      /* is_fixed */ false,
                                      /* decimal separator */ "'"),
            "5");
}

std::string TestInterfaceFormatNumberByCurrency(
    grocery_pricing::Numeric value,
    const dynamic_config::Snapshot& dynamic_config, const Currency& currency,
    const std::string& decimal_separator, bool is_fixed) {
  return PriceFormatter::FormatNumberByCurrency(value, dynamic_config, currency,
                                                decimal_separator, is_fixed);
}

const std::string kDefault = "__default__";
const std::string kILS = "ILS";
const std::string kGBP = "GBP";
const std::string kRUB = "RUB";

dynamic_config::StorageMock GetConfig() {
  return {{taxi_config::GROCERY_LOCALIZATION_CURRENCY_FORMAT,
           {{kDefault,
             {/* precision */ 2,
              /* rounding */ Numeric{"0.01"}}},
            {"ROUND",
             {/* precision */ 2,
              /* rounding */ Numeric{"1000"}}},
            {kRUB,
             {/* precision */ 2,
              /* rounding */ Numeric{"0.01"}}},
            {kGBP,
             {/* precision */ 2,
              /* rounding */ Numeric{"0.01"}}},
            {kILS,
             {/* precision */ 1,
              /* rounding */ Numeric{"0.1"}}}}}};
}

TEST(TestPriceFormatter, TestRounding_1000) {
  // some round tests in TestFormatNumber
  ASSERT_EQ(TestInterfaceFormatNumber(/* value */ Numeric{"678913.967"},
                                      /* rounding */ Numeric{"1000"},
                                      /* precision */ 2,
                                      /* is_fixed */ true,
                                      /* decimal separator */ "."),
            "678000.00");

  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();
  ASSERT_EQ(TestInterfaceFormatNumberByCurrency(Numeric{"678913.967"}, config,
                                                Currency("ROUND"), ".",
                                                /* is_fixed */ true),
            "678000.00");
}

TEST(TestPriceFormatter, TestFormatNumberByCurrency) {
  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();
  ASSERT_EQ(TestInterfaceFormatNumberByCurrency(Numeric{"5.61"}, config,
                                                Currency(kILS), ".",
                                                /* is_fixed */ false),
            "5.6");
  ASSERT_EQ(TestInterfaceFormatNumberByCurrency(Numeric{"67325.613"}, config,
                                                Currency(kRUB), ",",
                                                /* is_fixed */ true),
            "67325,61");
  ASSERT_EQ(
      TestInterfaceFormatNumberByCurrency(
          Numeric{"5.613"}, config, Currency(kGBP), ".", /* is_fixed */ false),
      "5.61");
  // Test default
  ASSERT_EQ(TestInterfaceFormatNumberByCurrency(Numeric{"5.613"}, config,
                                                Currency("noname"), ",",
                                                /* is_fixed */ false),
            "5,61");
}

std::string TestInterfaceFormatPrice(const std::string& templ,
                                     const std::string& price,
                                     const std::string& currency_sign) {
  return PriceFormatter::FormatPrice(templ, price, currency_sign);
}

TEST(TestPriceFormatter, TestTemplates) {
  ASSERT_EQ(TestInterfaceFormatPrice(/* template */ "$VALUE$$SIGN$",
                                     /* price */ "миллион", /* sign */ "₽"),
            "миллион₽");
  ASSERT_EQ(TestInterfaceFormatPrice(/* template */ "$SIGN$$VALUE$",
                                     /* price */ "over_nine_thousand",
                                     /* sign */ "£"),
            "£over_nine_thousand");
  ASSERT_EQ(TestInterfaceFormatPrice(/* template */ "$SIGN$$VALUE$$SIGN$",
                                     /* price */ "money", /* sign */ "$"),
            "$money$");
  ASSERT_EQ(TestInterfaceFormatPrice(/* template */ "$SIGN$$VALUE$$SIGN$",
                                     /* price */ "$SIGN$", /* sign */ "$"),
            "$$$");
  ASSERT_EQ(TestInterfaceFormatPrice(/* template */ "$VALUE$$SIGN$",
                                     /* price */ "$SIGN", /* sign */ "$"),
            "$SIGN$");
}

TEST(TestPriceFormatter, TestFormatPrice) {
  const auto kTemplateSignFirst = "$SIGN$$VALUE$";
  const auto kTemplateValueFirst = "$VALUE$$SIGN$";

  const auto config_storage = GetConfig();
  const auto config = config_storage.GetSnapshot();
  std::string price;
  price = TestInterfaceFormatNumberByCurrency(
      Numeric{"5.61"}, config, Currency(kILS), /* decimal separator */ ".",
      /* is_fixed */ false);
  ASSERT_EQ(price, "5.6");
  ASSERT_EQ(TestInterfaceFormatPrice(kTemplateValueFirst, price, "₪"), "5.6₪");
  price = TestInterfaceFormatNumberByCurrency(
      Numeric{"5.613"}, config, Currency(kRUB), /* decimal separator */ ",",
      /* is_fixed */ true);
  ASSERT_EQ(price, "5,61");
  ASSERT_EQ(TestInterfaceFormatPrice(kTemplateValueFirst, price, "₽"),
            "5,61₽");

  price = TestInterfaceFormatNumberByCurrency(
      Numeric{"67325.603"}, config, Currency(kRUB),
      /* decimal separator */ ",", /* is_fixed */ false);
  ASSERT_EQ(price, "67325,6");
  ASSERT_EQ(TestInterfaceFormatPrice(kTemplateSignFirst, price, "₽"),
            "₽67325,6");

  price = TestInterfaceFormatNumberByCurrency(
      Numeric{"5.613"}, config, Currency(kGBP), /* decimal separator */ ".",
      /* is_fixed */ false);
  ASSERT_EQ(price, "5.61");
  ASSERT_EQ(TestInterfaceFormatPrice(kTemplateSignFirst, price, "£"), "£5.61");
}

}  // namespace grocery_l10n
