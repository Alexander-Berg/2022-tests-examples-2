#include <userver/utest/utest.hpp>

#include <vector>

#include <core/balance_cache/types.hpp>

namespace {

namespace types = billing_wallet::core::balance_cache::types;

const types::Balance kDefaultBalance{"some_wallet_id",
                                     types::Amount{"100500.0000"}, "RUB",
                                     "deposit", 9999990001};

}  // namespace

TEST(BalanceArrays, Differ) {
  types::Balance a1{"existing", types::Amount{"100.0000"}, "RUB", "deposit", 1};
  types::Balance a2{"wallet/yataxi", types::Amount{"201.0000"}, "RUB",
                    "deposit", 1};
  types::Balance b1{"existing", types::Amount{"100.0000"}, "RUB", "deposit",
                    6000000000};
  types::Balance b2{"wallet/yataxi", types::Amount{"1.0000"}, "RUB", "deposit",
                    6000000001};
  std::vector<types::Balance> a{a1, a2};
  std::vector<types::Balance> b{b1, b2};
  EXPECT_EQ(a[0].wallet_id, "existing");
  EXPECT_EQ(a[1].wallet_id, "wallet/yataxi");
  EXPECT_EQ(b[0].wallet_id, "existing");
  EXPECT_EQ(b[1].wallet_id, "wallet/yataxi");
  EXPECT_NE(a, b);
}

TEST(Balances, DifferInWalletId) {
  types::Balance changed(kDefaultBalance);

  changed.wallet_id = "aaa_some_wallet_id";
  EXPECT_FALSE(kDefaultBalance == changed);

  changed.wallet_id = "zzz_some_wallet_id";
  EXPECT_FALSE(kDefaultBalance == changed);
}

TEST(Balances, DifferInCurrency) {
  types::Balance changed(kDefaultBalance);

  changed.currency = "AAA";
  EXPECT_FALSE(kDefaultBalance == changed);

  changed.currency = "ZZZ";
  EXPECT_FALSE(kDefaultBalance == changed);
}

TEST(Balances, DifferInSubAccount) {
  types::Balance changed(kDefaultBalance);

  changed.sub_account = "aaa";
  EXPECT_FALSE(kDefaultBalance == changed);

  changed.sub_account = "zzz";
  EXPECT_FALSE(kDefaultBalance == changed);
}

TEST(Balances, DifferInAmount) {
  types::Balance changed(kDefaultBalance);

  changed.amount = types::Amount{"0.0000"};
  EXPECT_FALSE(kDefaultBalance == changed);

  changed.amount = types::Amount{"999999.0000"};
  EXPECT_FALSE(kDefaultBalance == changed);
}

TEST(Balances, DifferInLastEntryId) {
  types::Balance changed(kDefaultBalance);

  changed.last_entry_id = 0;
  EXPECT_EQ(kDefaultBalance, changed);

  changed.last_entry_id = 19999990001;
  EXPECT_EQ(kDefaultBalance, changed);
}
