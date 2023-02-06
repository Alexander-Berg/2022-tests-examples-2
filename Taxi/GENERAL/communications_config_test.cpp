#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/communications_config.hpp>
#include <config/config.hpp>

TEST(TestCommunicationsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  const auto& xiva = config.Get<config::CommunicationsXiva>();
  ASSERT_EQ(std::chrono::milliseconds(500), xiva.timeout_ms.Get());
  ASSERT_EQ(std::chrono::milliseconds(1500), xiva.batch_timeout_ms.Get());
  ASSERT_EQ(3u, xiva.retries.Get());

  const auto& device_notify = config.Get<config::CommunicationsDeviceNotify>();
  ASSERT_EQ(std::chrono::milliseconds(500), device_notify.timeout_ms.Get());
  ASSERT_EQ(std::chrono::milliseconds(500),
            device_notify.batch_timeout_ms.Get());
  ASSERT_EQ(3u, xiva.retries.Get());

  const auto& notification = config.Get<config::CommunicationsNotification>();
  std::vector<std::string> clients = {"device-notify", "xiva", "queue",
                                      "taximeter"};
  ASSERT_EQ(notification.driver_notification_send_clients.Get(), clients);

  ASSERT_EQ(10000u, notification.bulk_send_max_size.Get());
  ASSERT_EQ(false, notification.fallback.enabled);
  ASSERT_EQ(3000u, notification.fallback.min_requests_count);
  ASSERT_EQ(40, notification.fallback.max_error_percent);
  ASSERT_EQ(std::chrono::seconds{60}, notification.fallback.recheck_period);
  ASSERT_EQ(std::chrono::seconds{180}, notification.fallback.statistics_period);
  ASSERT_EQ(std::chrono::seconds{600}, notification.fallback.disable_period);

  const auto& push_actions_settings = notification.push_actions_settings;
  ASSERT_EQ(1u, push_actions_settings.GetMap().size());
  ASSERT_EQ(std::chrono::seconds(60),
            push_actions_settings.Get("__default__").ttl);
  ASSERT_EQ(std::chrono::seconds(60),
            push_actions_settings.Get("OrderChangeStatus").ttl);
  ASSERT_EQ(true, push_actions_settings.Get("__default__").use_fallback_queue);
  ASSERT_EQ(true,
            push_actions_settings.Get("OrderChangeStatus").use_fallback_queue);
}
