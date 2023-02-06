#pragma once

#include <optional>

#include <helpers/coop_account/coop_account.hpp>

namespace debts::coop_account {

class MockAccount : public AccountStorage {
 public:
  explicit MockAccount(const std::optional<Account>& account)
      : account_(account){};
  std::optional<Account> GetAccount(const std::string&) override {
    return account_;
  };

 private:
  const std::optional<Account> account_;
};

AccountAccessor MockAccountAccessor(const std::optional<Account>& account);

}  // namespace debts::coop_account
