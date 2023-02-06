#pragma once

#include "core/price_formatter.hpp"

#include <functional>

namespace sweet_home::mocks {

using HandlerGetFormattedValue =
    std::function<std::string(double, const std::string&, const std::string&)>;
using HandlerGetSumWithCurrency =
    std::function<std::string(double, const std::string&, const std::string&)>;
using HandlerGetCurrencyRules =
    std::function<core::CurrencyRules(const std::string&, const std::string&)>;

class PriceFormatterMock : public core::PriceFormatter {
 private:
  HandlerGetFormattedValue handler_get_formatted_value_;
  HandlerGetSumWithCurrency handler_get_sum_with_currency_;
  HandlerGetCurrencyRules handler_get_currency_rules_;

 public:
  PriceFormatterMock(
      const HandlerGetFormattedValue& handler_get_value = nullptr,
      const HandlerGetSumWithCurrency& handler_get_sum = nullptr,
      const HandlerGetCurrencyRules& handler_get_currency_rules = nullptr)
      : handler_get_formatted_value_(handler_get_value),
        handler_get_sum_with_currency_(handler_get_sum),
        handler_get_currency_rules_(handler_get_currency_rules){};

  std::string GetFormattedValue(double value, const std::string& currency,
                                const std::string& locale) const override {
    if (!handler_get_formatted_value_) {
      return std::to_string(value);
    }
    return handler_get_formatted_value_(value, currency, locale);
  }

  std::string GetSumWithCurrency(double value, const std::string& currency,
                                 const std::string& locale) const override {
    if (!handler_get_sum_with_currency_) {
      return std::to_string(value) + "$SIGN$$CURRENCY$";
    }
    return handler_get_sum_with_currency_(value, currency, locale);
  }

  core::CurrencyRules GetCurrencyRules(
      const std::string& currency, const std::string& locale) const override {
    if (!handler_get_currency_rules_) {
      return {
          "RUB",
          "руб.",
          "$VALUE$ $SIGN$$CURRENCY$",
          "₽",
      };
    }
    return handler_get_currency_rules_(currency, locale);
  }
};

}  // namespace sweet_home::mocks
