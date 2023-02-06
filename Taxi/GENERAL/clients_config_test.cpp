#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/clients_config.hpp>
#include <config/config.hpp>

TEST(TestClientsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& clients_config = config.Get<config::Clients>();

  ASSERT_EQ(clients_config.user_tracker_base_url.Get(),
            "http://user-tracker.taxi.yandex.net");
  ASSERT_EQ(clients_config.user_tracker_client_timeout.Get(), 200u);
  ASSERT_EQ(clients_config.user_tracker_client_retries.Get(), 0u);

  ASSERT_EQ(clients_config.stq_agent_client_timeout.Get(),
            std::chrono::milliseconds(500));
  ASSERT_EQ(clients_config.stq_agent_client_retries.Get(), 2);

  ASSERT_EQ(clients_config.broker_internal_client_retries.Get(), 3u);
}
