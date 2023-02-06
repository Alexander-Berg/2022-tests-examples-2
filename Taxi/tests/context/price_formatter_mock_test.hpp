#pragma once

#include <core/context/price_formatter.hpp>
#include <userver/utils/text.hpp>

namespace routestats::test {

class PriceFormatterMock : public core::PriceFormatter {
 public:
  std::string GetFormattedValue(double value, const std::string& currency,
                                const core::FormattingOptions&) override {
    int precision = 0;
    if (currency != "RUB") precision = 1;
    return utils::text::Format(value, "ru", precision);
  }

  std::string GetSumWithCurrency(double value, const std::string& currency,
                                 const core::FormattingOptions&) override {
    return GetFormattedValue(value, currency, {}) + " $SIGN$$CURRENCY$";
  }

  core::CurrencyRules GetCurrencyRules(
      const std::string&, const std::optional<std::string>&) const override {
    return core::CurrencyRules{"RUB", "₽", "$VALUE$ $SIGN$$CURRENCY$",
                               "руб."};
  }
};

}  // namespace routestats::test
