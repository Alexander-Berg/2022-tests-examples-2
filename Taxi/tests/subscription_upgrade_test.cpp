#include <gmock/gmock.h>

#include <clients/mediabilling-v2/client_mock_base.hpp>
#include <modules/cashback_subscription/cashback_subscription.hpp>

namespace cashback_subscription::test {

namespace client = clients::mediabilling_v2;
namespace handle = clients::mediabilling_v2::billing_cashback_status::post;

class MediabillingClientMock : public client::ClientMockBase {
 public:
  MOCK_METHOD(handle::Response, changeCashbackOffer,
              (const handle::Request& request,
               const client::CommandControl& command_control),
              (const, override));
};

TEST(UpgradeSubscriptionTest, HappyPath) {
  MediabillingClientMock client_mock;
  auto m = testing::Field(&handle::Request::uid, testing::StrEq("123456"));
  EXPECT_CALL(client_mock, changeCashbackOffer(m, testing::_));

  CashbackSubscriptionDeps deps{client_mock};
  plus::Wallet wallet{"some_wallet_id", "RUB",
                      decimal64::Decimal<4>("100.0000")};
  UserInfo user_info{"123456", true, false, wallet};
  EffectiveExperiments effective_experiments{true, true, true, true,
                                             std::nullopt};

  ASSERT_NO_THROW(UpgradeSubscription(deps, user_info, effective_experiments));
}

TEST(UpgradeSubscriptionTest, NotExpCouldUpgradePlusEnabled) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, false, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, NotASubscriber) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", false, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, AlreadyUpgraded) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, true, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, ExperimentDisabled) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{false, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, NoWallet) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{false, true, true, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, ZeroWalletBalance) {
  MediabillingClientMock client_mock;
  EXPECT_CALL(client_mock, changeCashbackOffer(testing::_, testing::_))
      .Times(0);

  CashbackSubscriptionDeps deps{client_mock};
  plus::Wallet wallet{"some_wallet_id", "RUB", decimal64::Decimal<4>("0.0000")};
  UserInfo user_info{"123456", true, false, wallet};
  EffectiveExperiments effective_experiments{false, true, true, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               UpgradeError);
}

TEST(UpgradeSubscriptionTest, MediabillingError400) {
  MediabillingClientMock client_mock;
  auto m = testing::Field(&handle::Request::uid, testing::StrEq("123456"));
  EXPECT_CALL(client_mock, changeCashbackOffer(m, testing::_))
      .WillOnce(testing::Throw(handle::Response400{}));

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               MediabillingError);
}

TEST(UpgradeSubscriptionTest, MediabillingError409) {
  MediabillingClientMock client_mock;
  auto m = testing::Field(&handle::Request::uid, testing::StrEq("123456"));
  EXPECT_CALL(client_mock, changeCashbackOffer(m, testing::_))
      .WillOnce(testing::Throw(handle::Response409{}));

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               MediabillingError);
}

TEST(UpgradeSubscriptionTest, MediabillingError500) {
  MediabillingClientMock client_mock;
  auto m = testing::Field(&handle::Request::uid, testing::StrEq("123456"));
  EXPECT_CALL(client_mock, changeCashbackOffer(m, testing::_))
      .WillOnce(testing::Throw(handle::Response500{}));

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               MediabillingError);
}

TEST(UpgradeSubscriptionTest, MediabillingErrorUnexpected) {
  MediabillingClientMock client_mock;
  auto m = testing::Field(&handle::Request::uid, testing::StrEq("123456"));
  EXPECT_CALL(client_mock, changeCashbackOffer(m, testing::_))
      .WillOnce(testing::Throw(std::exception{}));

  CashbackSubscriptionDeps deps{client_mock};
  UserInfo user_info{"123456", true, false, std::nullopt};
  EffectiveExperiments effective_experiments{true, true, false, true,
                                             std::nullopt};

  ASSERT_THROW(UpgradeSubscription(deps, user_info, effective_experiments),
               MediabillingError);
}

}  // namespace cashback_subscription::test
