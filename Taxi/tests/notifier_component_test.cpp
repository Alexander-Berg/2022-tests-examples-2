#include <clients/eats-restapp-communications/client_gmock.hpp>
#include <components/notifier.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/utest/utest.hpp>

namespace testing {
using ::eats_partners::components::notifier::ComponentImpl;
using ::eats_partners::components::notifier::EventType;
using ::eats_partners::components::notifier::NotificationError;
namespace Notifications = ::defs::internal::notifications;

struct NotifierComponentTest : public Test {
  std::shared_ptr<StrictMock<clients::eats_restapp_communications::ClientGMock>>
      communications_mock = std::make_shared<
          StrictMock<clients::eats_restapp_communications::ClientGMock>>();

  ComponentImpl component;

  NotifierComponentTest() : component(*communications_mock) {}

  static ::formats::json::Value MakeArgs() {
    ::formats::json::ValueBuilder builder;
    builder["arg1"] = "val1";
    builder["arg2"] = "val2";
    return builder.ExtractValue();
  }
};
TEST_F(NotifierComponentTest, by_partner_id) {
  eats_partners::types::partner::Id partner_id{42};
  auto event = EventType::kPasswordReset;
  auto args = MakeArgs();
  {
    namespace client = clients::eats_restapp_communications::
        internal_communications_v1_send_event::post;
    client::Request request;

    request.event_type = Notifications::ToString(event);
    request.body.recipients.partner_ids = {partner_id.GetUnderlying()};
    request.body.data.extra = args;

    client::Response204 response204;

    EXPECT_CALL(*communications_mock,
                InternalCommunicationsV1SendEvent(request, _))
        .WillOnce(Return(response204));
  }
  component.SendEvent(partner_id, event, args);
}

TEST_F(NotifierComponentTest, by_partnerish_uuid) {
  eats_partners::types::partnerish::UuidToken uuid{"1abv"};
  auto event = EventType::kPasswordReset;
  auto args = MakeArgs();
  {
    namespace client = clients::eats_restapp_communications::
        internal_communications_v1_send_event::post;
    client::Request request;

    request.event_type = Notifications::ToString(event);
    request.body.recipients.partnerish_uuids = {uuid.GetUnderlying()};
    request.body.data.extra = args;

    client::Response204 response204;

    EXPECT_CALL(*communications_mock,
                InternalCommunicationsV1SendEvent(request, _))
        .WillOnce(Return(response204));
  }
  component.SendEvent(uuid, event, args);
}

TEST_F(NotifierComponentTest, by_partner_email) {
  eats_partners::types::partner::Email email{"1abv@mail.ru"};
  auto event = EventType::kPasswordReset;
  auto args = MakeArgs();
  {
    namespace client = clients::eats_restapp_communications::
        internal_communications_v1_send_event::post;
    client::Request request;

    request.event_type = Notifications::ToString(event);
    request.body.recipients.emails = {email.GetUnderlying()};
    request.body.data.extra = args;

    client::Response204 response204;

    EXPECT_CALL(*communications_mock,
                InternalCommunicationsV1SendEvent(request, _))
        .WillOnce(Return(response204));
  }
  component.SendEvent(email, event, args);
}

}  // namespace testing

namespace clients::eats_restapp_communications {
namespace internal_communications_v1_send_event::post {

inline bool operator==(const Request& lhs, const Request& rhs) {
  return std::tie(lhs.event_type, lhs.body) ==
         std::tie(rhs.event_type, rhs.body);
}

}  // namespace internal_communications_v1_send_event::post
}  // namespace clients::eats_restapp_communications
