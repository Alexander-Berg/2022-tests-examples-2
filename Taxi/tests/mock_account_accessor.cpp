#include "mock_account_accessor.hpp"

namespace debts::coop_account {

AccountAccessor MockAccountAccessor(const std::optional<Account>& account) {
  return std::make_shared<MockAccount>(account);
}

}  // namespace debts::coop_account
