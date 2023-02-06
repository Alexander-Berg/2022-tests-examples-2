#pragma once

#include "core/wallets.hpp"

#include <functional>

namespace cashback_int_api::mocks {

using GetWalletsOfUserHandler = std::function<std::vector<core::Wallet>(
    const std::string&, const std::string&)>;

class WalletServiceMock : public core::WalletService {
 private:
  GetWalletsOfUserHandler handler_;

 public:
  WalletServiceMock(const GetWalletsOfUserHandler& handler)
      : handler_(handler){};

  std::vector<core::Wallet> GetWalletsOfUser(
      const std::string& yandex_uid,
      const std::string& currency) const override {
    return handler_(yandex_uid, currency);
  }
};

}  // namespace cashback_int_api::mocks
