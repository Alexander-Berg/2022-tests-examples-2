#pragma once

#include <core/context/wallets.hpp>

#include <functional>

namespace routestats::test {

using WalletHandler =
    std::function<std::optional<core::Wallet>(const std::string&)>;

class WalletsMock : public core::WalletsStorage {
 public:
  WalletsMock(const WalletHandler& handler) : handler_(handler){};

  std::optional<core::Wallet> GetEffectiveWallet(
      const std::string& currency) override {
    return handler_(currency);
  }

 private:
  WalletHandler handler_;
};

}  // namespace routestats::test
