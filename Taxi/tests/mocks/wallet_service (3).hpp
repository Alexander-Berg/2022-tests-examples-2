#pragma once

#include "core/wallets.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetWalletsOfUserHandler = std::function<std::vector<core::Wallet>(
    const std::string&, const std::string&, const std::string&)>;

class WalletServiceMock : public core::WalletService {
 private:
  GetWalletsOfUserHandler handler_;

 public:
  WalletServiceMock(const GetWalletsOfUserHandler& handler)
      : handler_(handler){};

  std::vector<core::Wallet> GetWalletsOfUser(
      const std::string& yandex_uid, const std::string& currency,
      const std::string& rounding_factor) const override {
    return handler_(yandex_uid, currency, rounding_factor);
  }
};

}  // namespace sweet_home::mocks
