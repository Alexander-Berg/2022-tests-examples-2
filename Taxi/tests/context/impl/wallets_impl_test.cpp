#include <gtest/gtest.h>

#include <functional>

#include <userver/utest/utest.hpp>

#include <clients/plus-wallet/client_mock_base.hpp>
#include <core/context/wallets/wallets_impl.hpp>
#include <userver/engine/sleep.hpp>

namespace routestats::core {

namespace test {
using BalanceRequest = clients::plus_wallet::v1_balances::get::Request;
using BalanceResponse = clients::plus_wallet::v1_balances::get::Response;

using WalletHandler = std::function<BalanceResponse()>;
class MockWalletClient : public clients::plus_wallet::ClientMockBase {
 public:
  MockWalletClient(const WalletHandler& handler) : handler_(handler) {}

  BalanceResponse V1Balances(
      const BalanceRequest&,
      const clients::plus_wallet::CommandControl&) const override {
    return handler_();
  }

 private:
  WalletHandler handler_;
};
}  // namespace test

UTEST(WalletImpl, Errors) {
  test::MockWalletClient client([]() -> test::BalanceResponse  //
                                { throw std::runtime_error("error"); });

  WalletsViaPlusWallet wallets(client);
  wallets.StartLoadingWallets("1234");

  const auto& result = wallets.GetEffectiveWallet("RUB");
  ASSERT_EQ(result, std::nullopt);
}

UTEST(WalletImpl, ErrorsExc) {
  test::MockWalletClient client(
      []() -> test::BalanceResponse  //
      { throw clients::plus_wallet::v1_balances::get::Exception(); });

  WalletsViaPlusWallet wallets(client);
  wallets.StartLoadingWallets("1234");

  const auto& result = wallets.GetEffectiveWallet("RUB");
  ASSERT_EQ(result, std::nullopt);
}

UTEST(WalletImpl, WithSleep) {
  test::MockWalletClient client([]() -> test::BalanceResponse  //
                                {
                                  engine::SleepFor(
                                      std::chrono::milliseconds(10));
                                  return test::BalanceResponse{};
                                });

  WalletsViaPlusWallet wallets(client);
  wallets.StartLoadingWallets("1234");

  // two times
  wallets.GetEffectiveWallet("RUB");
  const auto& result = wallets.GetEffectiveWallet("RUB");

  ASSERT_EQ(result, std::nullopt);
}

UTEST(WalletImpl, HappyPath) {
  test::MockWalletClient client(
      []() -> test::BalanceResponse  //
      {
        test::BalanceResponse result;
        result.balances.push_back({"wallet_id", "50", "RUB"});
        return result;
      });

  {
    WalletsViaPlusWallet wallets(client);
    auto result = wallets.GetEffectiveWallet("EUR");
    ASSERT_EQ(result, std::nullopt);
  }

  {
    WalletsViaPlusWallet wallets(client);
    wallets.StartLoadingWallets("1234");
    auto result = wallets.GetEffectiveWallet("EUR");
    ASSERT_EQ(result, std::nullopt);
  }

  {
    WalletsViaPlusWallet wallets(client);
    wallets.StartLoadingWallets("1234");
    auto result = wallets.GetEffectiveWallet("RUB");
    ASSERT_FALSE(result == std::nullopt);
    ASSERT_EQ(result->wallet_id, "wallet_id");
    ASSERT_EQ(result->balance, decimal64::Decimal<4>{50});
  }
}

}  // namespace routestats::core
