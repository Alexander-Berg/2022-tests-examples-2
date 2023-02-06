#include <gmock/gmock.h>
#include <modules/wallets/models.hpp>
#include <modules/wallets/wallets.hpp>
#include <set>

TEST(TestWalletsDiff, TestEqualSameOrder) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(300000)},
      {"wallet_id2", "yandex_uid2", "RUB", decimal64::Decimal<4>(310000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = wallets_billing;
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_TRUE(diff.empty());
}

TEST(TestWalletsDiff, TestEqualDifferentOrder) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
      {"wallet_id2", "yandex_uid2", "RUB", decimal64::Decimal<4>(200000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {
      {"wallet_id2", "yandex_uid2", "RUB", decimal64::Decimal<4>(200000)},
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
  };
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_TRUE(diff.empty());
}

TEST(TestWalletsDiff, TestEqualOneItem) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
  };
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_TRUE(diff.empty());
}

TEST(TestWalletsDiff, TestEqualZeroItems) {
  std::vector<personal_wallet::Wallet> wallets_billing = {};
  std::vector<personal_wallet::Wallet> wallets_db = {};
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_TRUE(diff.empty());
}

TEST(TestWalletsDiff, TestNotEqualDifferentBalance) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(200000)},
  };
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_EQ(diff.size(), 1);
  ASSERT_EQ(diff[0].yandex_uid, "yandex_uid1");
  ASSERT_EQ(diff[0].id, "wallet_id1");
}

TEST(TestWalletsDiff, TestNotEqualDifferentBalanceMultiple) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
      {"wallet_id2", "yandex_uid1", "KZT", decimal64::Decimal<4>(100000)},
      {"wallet_id3", "yandex_uid1", "UAH", decimal64::Decimal<4>(200000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(200000)},
      {"wallet_id2", "yandex_uid1", "KZT", decimal64::Decimal<4>(100000)},
      {"wallet_id3", "yandex_uid1", "UAH", decimal64::Decimal<4>(150000)},
  };
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  std::set<std::string> yandex_uids = {diff[0].yandex_uid, diff[1].yandex_uid};
  std::set<std::string> expected_uids = {"yandex_uid1"};

  std::set<std::string> wallet_ids = {diff[0].id, diff[1].id};
  std::set<std::string> expected_ids = {"wallet_id1", "wallet_id3"};

  ASSERT_EQ(diff.size(), 2);
  ASSERT_EQ(yandex_uids, expected_uids);
  ASSERT_EQ(wallet_ids, expected_ids);
}

TEST(TestWalletsDiff, TestNotEqualEmptyInDb) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
      {"wallet_id2", "yandex_uid1", "UAH", decimal64::Decimal<4>(100000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {};
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  std::set<std::string> yandex_uids = {diff[0].yandex_uid, diff[1].yandex_uid};
  std::set<std::string> expected_uids = {"yandex_uid1"};

  std::set<std::string> wallet_ids = {diff[0].id, diff[1].id};
  std::set<std::string> expected_ids = {"wallet_id1", "wallet_id2"};

  ASSERT_EQ(diff.size(), 2);
  ASSERT_EQ(yandex_uids, expected_uids);
  ASSERT_EQ(wallet_ids, expected_ids);
}

TEST(TestWalletsDiff, TestNotEqualDifferentItemsInDb) {
  std::vector<personal_wallet::Wallet> wallets_billing = {
      {"wallet_id111", "yandex_uid111", "RUB", decimal64::Decimal<4>(100000)},
  };
  std::vector<personal_wallet::Wallet> wallets_db = {
      {"wallet_id1", "yandex_uid1", "RUB", decimal64::Decimal<4>(100000)},
      {"wallet_id2", "yandex_uid2", "RUB", decimal64::Decimal<4>(100000)},
  };
  auto diff = personal_wallet::WalletsDiff(wallets_billing, wallets_db);
  ASSERT_EQ(diff.size(), 1);
  ASSERT_EQ(diff[0].yandex_uid, "yandex_uid111");
  ASSERT_EQ(diff[0].id, "wallet_id111");
}
