#pragma once

#include "core/burning_balance.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetBurnsOfUserBalancesHandler =
    std::function<std::vector<core::BurningBalance>(const std::string&)>;

class BurningBalanceServiceMock : public core::BurningBalanceService {
 private:
  GetBurnsOfUserBalancesHandler handler_;

 public:
  BurningBalanceServiceMock(GetBurnsOfUserBalancesHandler handler)
      : handler_{std::move(handler)} {}

  std::vector<core::BurningBalance> GetBurnsOfUserBalances(
      const std::string& yandex_uid) const override {
    return handler_(yandex_uid);
  }
};

}  // namespace sweet_home::mocks
