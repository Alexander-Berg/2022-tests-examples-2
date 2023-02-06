#pragma once

#include "core/countries.hpp"

#include <functional>

namespace plus_plaque::mocks {

using HandlerGetCurrency = std::function<std::string(const std::string&)>;

class CountriesServiceMock : public core::CountriesService {
 private:
  HandlerGetCurrency handler_;

 public:
  CountriesServiceMock(const HandlerGetCurrency& handler) : handler_(handler){};

  std::string GetCurrencyByCountry(
      const std::string& country_code) const override {
    return handler_(country_code);
  }
};

}  // namespace plus_plaque::mocks
