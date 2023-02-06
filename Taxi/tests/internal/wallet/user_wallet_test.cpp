#include <gtest/gtest.h>

#include "internal/wallet/wallet.hpp"

#include "tests/mocks/countries_service.hpp"
#include "tests/mocks/wallet_service.hpp"

namespace plus_plaque::wallet {

namespace {
const std::string kYandexUid = "some_uid";
const std::string kCountry = "some_country";
const std::string kUsdCountry = "USD_country";
const std::string kDefaultCurrency = "RUB";
const std::string kUsdCurrency = "USD";
}  // namespace

namespace {

core::Wallet MakeWallet(const std::string& wallet_id,
                        const std::string& balance,
                        const std::string& currency = kDefaultCurrency) {
  return {wallet_id, currency,
          decimal64::Decimal<4>::FromStringPermissive(balance)};
}

void AssertWallet(const std::optional<core::Wallet>& left,
                  const std::optional<core::Wallet>& right) {
  if (!left && !right) {
    SUCCEED();
    return;
  }

  if (!left || !right) {
    FAIL();
    return;
  }

  ASSERT_EQ(left->wallet_id, right->wallet_id);
  ASSERT_EQ(left->balance, right->balance);
  ASSERT_EQ(left->currency, right->currency);
}

auto default_countries_handler = [](const std::string&) {
  return std::string(kDefaultCurrency);
};

WalletDeps PrepareDeps(
    const std::optional<mocks::GetWalletsOfUserHandler>& wallets_handler =
        std::nullopt,
    const std::optional<mocks::HandlerGetCurrency>& countries_handler =
        default_countries_handler) {
  WalletDeps deps;
  if (wallets_handler) {
    deps.wallet_service =
        std::make_shared<mocks::WalletServiceMock>(*wallets_handler);
  }
  if (countries_handler) {
    deps.countries_service =
        std::make_shared<mocks::CountriesServiceMock>(*countries_handler);
  } else {
    deps.countries_service = std::make_shared<mocks::CountriesServiceMock>(
        default_countries_handler);
  }

  return deps;
}

}  // namespace

TEST(TestGetWalletForUser, OneWallet) {
  auto handler = [](const std::string&, const std::string&,
                    const std::string&) {
    return std::vector<core::Wallet>{MakeWallet("some_id", "140")};
  };

  auto deps = PrepareDeps(handler);

  auto wallet = GetWalletForUser(deps, kYandexUid, kCountry);

  AssertWallet(wallet, MakeWallet("some_id", "140"));
}

TEST(TestGetWalletForUser, ManyWallets) {
  auto handler = [](const std::string&, const std::string&,
                    const std::string&) {
    return std::vector<core::Wallet>{
        MakeWallet("some_id", "140"),
        MakeWallet("another_id", "160"),
    };
  };

  auto deps = PrepareDeps(handler);

  auto wallet = GetWalletForUser(deps, kYandexUid, kCountry);

  // only first returned
  AssertWallet(wallet, MakeWallet("some_id", "140"));
}

TEST(TestGetWalletForUser, NoWallets) {
  auto handler = [](const std::string&, const std::string&,
                    const std::string&) { return std::vector<core::Wallet>{}; };

  auto deps = PrepareDeps(handler);

  auto wallet = GetWalletForUser(deps, kYandexUid, kCountry);

  AssertWallet(wallet, std::nullopt);
}

TEST(TestGetWalletForUser, ErrorDuringFetch) {
  auto handler = [](const std::string&, const std::string&,
                    const std::string&) {
    throw core::WalletsServiceError("i am error");
    return std::vector<core::Wallet>{};
  };

  auto deps = PrepareDeps(handler);

  auto wallet = GetWalletForUser(deps, kYandexUid, kCountry);

  AssertWallet(wallet, std::nullopt);
}

TEST(TestGetWalletForUser, ErrorDuringGetCurrencyUseDefault) {
  auto handler_get_currency = [](const std::string&) {
    throw core::CountriesServiceError(
        "Failed to get currency by country, no country in territories. ");
    return std::string();
  };

  auto handler_get_wallets = [](const std::string&, const std::string& currency,
                                const std::string&) {
    if (currency == kDefaultCurrency) {
      return std::vector<core::Wallet>{
          MakeWallet("some_id", "140"),
      };
    }
    return std::vector<core::Wallet>();
  };

  auto deps = PrepareDeps(handler_get_wallets, handler_get_currency);

  auto wallet = GetWalletForUser(deps, kYandexUid, kCountry);

  AssertWallet(wallet, MakeWallet("some_id", "140"));
}

TEST(TestGetWalletForUser, GettingWalletWithCurrencyUsd) {
  auto handler_get_currency = [](const std::string& country) {
    if (country == kUsdCountry) {
      return std::string(kUsdCurrency);
    }
    return std::string(kDefaultCurrency);
  };

  auto handler_get_wallets = [](const std::string&, const std::string& currency,
                                const std::string&) {
    if (currency == kUsdCurrency) {
      return std::vector<core::Wallet>{
          MakeWallet("USD_wallet", "100"),
      };
    }
    return std::vector<core::Wallet>{MakeWallet("RUB_wallet", "100")};
  };

  auto deps = PrepareDeps(handler_get_wallets, handler_get_currency);

  auto wallet = GetWalletForUser(deps, kYandexUid, kUsdCountry);

  AssertWallet(wallet, MakeWallet("USD_wallet", "100"));
}

}  // namespace plus_plaque::wallet
