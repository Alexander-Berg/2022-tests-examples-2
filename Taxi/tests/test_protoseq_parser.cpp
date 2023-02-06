#include <gmock/gmock.h>
#include <mission_progress_notification.pb.h>
#include <framing/framing.hpp>
#include <logbroker-consumer/message.hpp>
#include <modules/protoseq_parser/protoseq_parser.hpp>
#include <userver/crypto/base64.hpp>

namespace mc = plus::mc::core::v1;

std::vector<mc::MissionProgressNotification> GetNotifications(int count) {
  std::vector<mc::MissionProgressNotification> notifications;
  for (int i = 0; i < count; i++) {
    mc::MissionProgressNotification notification;
    notification.set_timestamp(i);
    notification.set_status(
        mc::NotificationStatus::NOTIFICATION_STATUS_UPDATED);
    notifications.push_back(notification);
  }
  return notifications;
}

std::vector<std::string_view> ConvertToStringViews(
    std::vector<logbroker_consumer::MessagePtr>& lb_messages) {
  std::vector<std::string_view> views;
  views.reserve(lb_messages.size());

  for (auto& msg : lb_messages) {
    views.emplace_back(msg->GetData());
  }

  return views;
}

template <typename T>
std::vector<logbroker_consumer::MessagePtr> ConvertToLbMessages(
    std::vector<T> notifications, int messages_per_pack) {
  std::vector<logbroker_consumer::MessagePtr> messages;
  framing::Packer packer{framing::Format::Protoseq};

  auto flush = [&packer, &messages](size_t i) {
    auto data = packer.Flush();
    logbroker_consumer::Message msg(
        data, "kek", std::chrono::system_clock::time_point(),
        std::chrono::system_clock::time_point(), {}, 1, "kek2", i, []() {});
    logbroker_consumer::MessagePtr ptr =
        std::make_unique<logbroker_consumer::Message>(msg);
    messages.push_back(std::move(ptr));
  };

  for (size_t i = 0; i < notifications.size(); i++) {
    packer.Add(notifications[i]);
    if (i > 0 && i % messages_per_pack == 0) {
      flush(i);
    }
  }
  flush(notifications.size());
  return messages;
}

TEST(TestProtoseqParser, TestParseMultipleProgressNotifications) {
  int kNotificationsCount = 100;
  int kNotificationsPerMessage = 10;

  auto notifications = GetNotifications(kNotificationsCount);
  ASSERT_EQ(notifications.size(), kNotificationsCount);

  auto lb_messages =
      ConvertToLbMessages(notifications, kNotificationsPerMessage);
  ASSERT_EQ(lb_messages.size(), kNotificationsCount / kNotificationsPerMessage);

  auto lb_messages_views = ConvertToStringViews(lb_messages);

  auto result = protoseq_parser::ParseMessages<mc::MissionProgressNotification>(
      lb_messages_views);
  ASSERT_EQ(result.proto_messages.size(), kNotificationsCount);

  for (int i = 0; i < kNotificationsCount; i++) {
    ASSERT_EQ(result.proto_messages[i].timestamp(),
              notifications[i].timestamp());
    ASSERT_EQ(result.proto_messages[i].status(), notifications[i].status());
  }
}

TEST(TestProtoseqParser, TestParseCorruptedMessages) {
  int kNotificationsCount = 100;
  int kNotificationsPerMessage = 10;

  std::vector<std::string> notifications;
  for (int i = 0; i < kNotificationsCount; i++) {
    notifications.push_back("this is not a notification" + std::to_string(i));
  }

  auto lb_messages =
      ConvertToLbMessages(notifications, kNotificationsPerMessage);
  ASSERT_EQ(lb_messages.size(), kNotificationsCount / kNotificationsPerMessage);

  auto lb_messages_views = ConvertToStringViews(lb_messages);

  auto result = protoseq_parser::ParseMessages<mc::MissionProgressNotification>(
      lb_messages_views);
  ASSERT_EQ(result.proto_messages.size(), 0);
}

TEST(TestProtoseqParser, TestParseManualMessage) {
  using namespace std::literals;
  auto str2_view = std::string_view(
      "\x01\x00\x00\x00"sv
      "8"sv
      "\x1F\xF7\xF7~\xBE\xA6^\2367\xA6\xF6.\xFE\xAEG\xA7"sv
      "\xB7n\xBF\xAF\x16\x9E\2377\xF6W\367f\xA7\6\xAF\xF7"sv);
  framing::Unpacker unpacker2(framing::Format::Protoseq, str2_view);

  std::string out;
  ASSERT_TRUE(unpacker2.NextFrame(out));
  ASSERT_EQ(out, "8");
}
