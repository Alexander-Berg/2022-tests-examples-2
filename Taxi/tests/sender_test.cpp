#include <clients/sender/client_gmock.hpp>
#include <components/sender.hpp>
#include <experiments3/components/experiments3_cache.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/utest/utest.hpp>

#include "restrict_send_helper_mock.hpp"
#include "types/recipients.hpp"

namespace testing {

struct TestSendingPreparing {
  void BeforeSend(const std::string_view,
                  const eats_restapp_communications::types::Recipient&,
                  formats::json::Value&) const {}
  void AfterSend(const std::string_view,
                 const eats_restapp_communications::types::Recipient&,
                 formats::json::Value&) const {}
};

using ::eats_restapp_communications::components::sender::ComponentImpl;
using ::eats_restapp_communications::components::sender::NotificationError;
using ::eats_restapp_communications::components::sender::detail::
    ConfigEmailSettings;
using ::eats_restapp_communications::components::sender::detail::EmailSettings;

constexpr auto sender_token = "sender_token";

struct EmailSettingsFixture {
  EmailSettings settings;
  EmailSettingsFixture()
      : settings(
            ConfigEmailSettings{"yandex.food",
                                {{"password-request-reset", "slug-request"},
                                 {"password-reset", "slug-reset"}},
                                {}}) {}
};

using SlugMapTestParams = std::tuple<std::string, std::optional<std::string>>;

struct SlugMapTest : public EmailSettingsFixture,
                     public TestWithParam<SlugMapTestParams> {};

INSTANTIATE_TEST_SUITE_P(
    SlugMapTest, SlugMapTest,
    Values(SlugMapTestParams{"password-request-reset", "slug-request"},
           SlugMapTestParams{"password-reset", "slug-reset"},
           SlugMapTestParams{"partnerish-register", std::nullopt}));

TEST_P(SlugMapTest, should_return_slug_by_type) {
  const auto [event, expected] = GetParam();
  ASSERT_EQ(settings.GetSlug(event), expected);
}

using ::eats_restapp_communications::components::sender::detail::EnabledAddress;
using Method = ::taxi_config::eats_restapp_communications_email_settings::
    EnabledaddressAMethod;
using EnabledAddressTestParams =
    std::tuple<std::optional<std::vector<EnabledAddress>>, std::string, bool>;

struct EnabledAddressTest : public TestWithParam<EnabledAddressTestParams> {};

INSTANTIATE_TEST_SUITE_P(
    EnabledAddressTest, EnabledAddressTest,
    Values(EnabledAddressTestParams{std::nullopt, "real@yandex.ru", true},
           EnabledAddressTestParams{std::vector<EnabledAddress>{},
                                    "real@yandex.ru", false},
           EnabledAddressTestParams{std::vector<EnabledAddress>{
                                        {Method::kAddress, "real@yandex.ru"}},
                                    "real@yandex.ru", true},
           EnabledAddressTestParams{std::vector<EnabledAddress>{
                                        {Method::kAddress, "real@yandex.ru"}},
                                    "other@yandex.ru", false},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kDomain, "yandex.ru"}},
               "real@yandex.ru", true},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kDomain, "yandex.ru"}},
               "other@yandex.ru", true},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kDomain, "yandex.ru"}},
               "real@ya.ru", false},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kAddress, "real@yandex.ru"},
                                           {Method::kDomain, "ya.ru"}},
               "real@yandex.ru", true},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kAddress, "real@yandex.ru"},
                                           {Method::kDomain, "ya.ru"}},
               "other@yandex.ru", false},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kAddress, "real@yandex.ru"},
                                           {Method::kDomain, "ya.ru"}},
               "real@ya.ru", true},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kAddress, "real@yandex.ru"},
                                           {Method::kDomain, "ya.ru"}},
               "other@ya.ru", true},
           EnabledAddressTestParams{
               std::vector<EnabledAddress>{{Method::kAddress, "real@yandex.ru"},
                                           {Method::kDomain, "ya.ru"}},
               "real@mail.ru", false}));

TEST_P(EnabledAddressTest, should_check_if_email_enabled) {
  const auto [rules, email, expected] = GetParam();
  EmailSettings settings(ConfigEmailSettings{{}, {}, rules});
  ASSERT_EQ(settings.IsEmailEnabled(email), expected);
}

struct SenderComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::sender::ClientGMock>> sender_mock =
      std::make_shared<StrictMock<clients::sender::ClientGMock>>();

  std::shared_ptr<RestrictSendHelperMock> restrict_send_mock =
      std::make_shared<RestrictSendHelperMock>();

  ComponentImpl<TestSendingPreparing> component;
  TestSendingPreparing test_sending_preparing;

  SenderComponentTest()
      : component(*sender_mock, sender_token, restrict_send_mock,
                  test_sending_preparing) {}

  static std::string MakeAuthToken() {
    return "Basic " +
           ::crypto::base64::Base64Encode(std::string(sender_token) + ":");
  }

  static EmailSettings MakeEmailSettings() {
    return EmailSettings(ConfigEmailSettings{
        "yandex.food",
        {{"password-reset", "slug-reset"}},
        std::vector<EnabledAddress>{{Method::kDomain, "ya.ru"}}});
  }

  static ::formats::json::Value MakeArgs() {
    ::formats::json::ValueBuilder builder;
    builder["arg1"] = "val1";
    builder["arg2"] = "val2";
    return builder.ExtractValue();
  }

  static clients::sender::api_0_account_slug_transactional_campaign_slug_send::
      post::Request
      RequestByRecipient(
          eats_restapp_communications::types::Recipient recipient) {
    namespace client = clients::sender::
        api_0_account_slug_transactional_campaign_slug_send::post;
    client::Request request;
    request.authorization = MakeAuthToken();
    request.x_sender_i_am_sender = true;
    request.account_slug = "yandex.food";
    request.campaign_slug = "slug-reset";
    clients::sender::Recipient sender_recipient;
    sender_recipient.email = recipient.email.GetUnderlying();
    if (recipient.name.has_value() && !recipient.name->empty()) {
      sender_recipient.name = recipient.name;
    }
    request.body.to.push_back(sender_recipient);
    ::formats::json::ValueBuilder builder(MakeArgs());
    builder["locale"] = recipient.locale.value_or("ru");
    request.body.args =
        ::clients::sender::SenderRequestArgs{builder.ExtractValue()};

    return request;
  }
};

TEST_F(SenderComponentTest, empty_list_recipients) {
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  component.SendEvent(eats_restapp_communications::types::Recipients{},
                      "custom-event", MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, one_recipient_with_empty_email) {
  eats_restapp_communications::types::Recipient recipient{"", "Empty Email",
                                                          "ru"};
  std::string event = "password-reset";
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, one_recipient_with_false_email) {
  eats_restapp_communications::types::Recipient recipient{"email@mail.ru",
                                                          "Bad Email", "ru"};
  std::string event = "password-reset";
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));
  component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, list_recipients_with_false_email) {
  eats_restapp_communications::types::Recipient recipient{"email@mail.ru",
                                                          "Bad Email", "ru"};
  std::string event = "password-reset";
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));
  component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, one_recipient_with_false_event_throw) {
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  const auto recipient = eats_restapp_communications::types::Recipient{
      "email@ya.ru", "Good Email", "ru"};
  std::string event = "custom-event";
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));
  EXPECT_THROW(
      component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings()),
      NotificationError);
}

TEST_F(SenderComponentTest, list_recipients_with_false_event) {
  const auto recipient = eats_restapp_communications::types::Recipient{
      "email@ya.ru", "Good Email", "ru"};
  std::string event = "custom-event";
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(_, _))
      .Times(0);
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));
  EXPECT_THROW(
      component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings()),
      NotificationError);
}

TEST_F(SenderComponentTest, recipient_one_send) {
  const auto recipient = eats_restapp_communications::types::Recipient{
      "email@ya.ru", "Good Email", "ru"};
  std::string event = "password-reset";

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Response200 response200;

  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipient), _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));

  component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, recipient_one_send_with_empty_name) {
  const auto recipient =
      eats_restapp_communications::types::Recipient{"email@ya.ru", "", "ru"};
  std::string event = "password-reset";

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Response200 response200;

  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipient), _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));

  component.SendEvent(recipient, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, list_recipients) {
  const auto recipients = eats_restapp_communications::types::Recipients{
      eats_restapp_communications::types::Recipient{"qwe1@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe2@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe3@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe4@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe5@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe6@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe7@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe8@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe9@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe10@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe11@ya.ru", "ku", "ru"},
  };
  std::string event = "password-reset";

  for (const auto& recipient : recipients) {
    clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
        Response200 response200;
    EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                  RequestByRecipient(recipient), _))
        .WillOnce(Return(response200));
    EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
        .WillOnce(Return(false));
  }
  component.SendEvent(recipients, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, list_recipients_disabled_all) {
  const auto recipients = eats_restapp_communications::types::Recipients{
      eats_restapp_communications::types::Recipient{"qwe1@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe2@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe3@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe4@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe5@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe6@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe7@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe8@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe9@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe10@ya.ru", "ku", "ru"},
      eats_restapp_communications::types::Recipient{"qwe11@ya.ru", "ku", "ru"},
  };
  std::string event = "password-reset";

  for (const auto& recipient : recipients) {
    clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
        Response200 response200;
    EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
        .WillOnce(Return(true));
    EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                  RequestByRecipient(recipient), _))
        .Times(0);
  }
  component.SendEvent(recipients, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, list_recipients_not_all) {
  const auto recipients = eats_restapp_communications::types::Recipients{
      eats_restapp_communications::types::Recipient{"qwe@ya.ru", "Good", "kz"},
      eats_restapp_communications::types::Recipient{"qwe3@ya.ru", std::nullopt,
                                                    std::nullopt},
      eats_restapp_communications::types::Recipient{"qwe2@yandex.ru", "Bad",
                                                    "ru"},
      eats_restapp_communications::types::Recipient{"qwe4@qwertyu.ru",
                                                    std::nullopt, std::nullopt},
  };
  std::string event = "password-reset";

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Response200 response200;
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[0]), _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[1]), _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[2]), _))
      .Times(0);
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[3]), _))
      .Times(0);
  for (const auto& recipient : recipients) {
    EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
        .WillOnce(Return(false));
  }
  component.SendEvent(recipients, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, list_recipients_not_all_one_disabled_by_config) {
  const auto recipients = eats_restapp_communications::types::Recipients{
      eats_restapp_communications::types::Recipient{"qwe@ya.ru", "Good", "kz"},
      eats_restapp_communications::types::Recipient{"qwe3@ya.ru", std::nullopt,
                                                    std::nullopt},
      eats_restapp_communications::types::Recipient{"qwe2@yandex.ru", "Bad",
                                                    "ru"},
      eats_restapp_communications::types::Recipient{"qwe4@qwertyu.ru",
                                                    std::nullopt, std::nullopt},
  };
  std::string event = "password-reset";

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Response200 response200;
  EXPECT_CALL(*restrict_send_mock, Disabled(recipients[0], event))
      .WillOnce(Return(false));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[0]), _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*restrict_send_mock, Disabled(recipients[1], event))
      .WillOnce(Return(true));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[1]), _))
      .Times(0);
  EXPECT_CALL(*restrict_send_mock, Disabled(recipients[2], event))
      .WillOnce(Return(false));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[2]), _))
      .Times(0);
  EXPECT_CALL(*restrict_send_mock, Disabled(recipients[3], event))
      .WillOnce(Return(false));
  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                RequestByRecipient(recipients[3]), _))
      .Times(0);
  component.SendEvent(recipients, event, MakeArgs(), MakeEmailSettings());
}

TEST_F(SenderComponentTest, send_mail_on_test_email) {
  const auto recipient = eats_restapp_communications::types::Recipient{
      "email@ya.ru", "Good Email", "ru"};
  auto request_with_test_mail = RequestByRecipient(recipient);
  request_with_test_mail.body.to.push_back(
      {"restapp-testing@yandex-team.ru", {}});
  std::string event = "password-reset";
  auto email_settings = MakeEmailSettings();
  email_settings.test_email = "restapp-testing@yandex-team.ru";

  clients::sender::api_0_account_slug_transactional_campaign_slug_send::post::
      Response200 response200;

  EXPECT_CALL(*sender_mock, Api0AccountSlugTransactionalCampaignSlugSend(
                                request_with_test_mail, _))
      .WillOnce(Return(response200));
  EXPECT_CALL(*restrict_send_mock, Disabled(recipient, event))
      .WillOnce(Return(false));

  component.SendEvent(recipient, event, MakeArgs(), email_settings);
}

}  // namespace testing

namespace clients::sender {
namespace api_0_account_slug_transactional_campaign_slug_send::post {

inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.authorization, lhs.x_sender_i_am_sender, lhs.account_slug,
                  lhs.campaign_slug, lhs.body) ==
         std::tie(rhs.authorization, rhs.x_sender_i_am_sender, rhs.account_slug,
                  rhs.campaign_slug, rhs.body);
}

}  // namespace api_0_account_slug_transactional_campaign_slug_send::post
}  // namespace clients::sender

namespace eats_restapp_communications::types {
inline bool operator==(const Recipient& lhs, const Recipient& rhs) {
  return lhs.email.GetUnderlying() == rhs.email.GetUnderlying();
}
}  // namespace eats_restapp_communications::types
