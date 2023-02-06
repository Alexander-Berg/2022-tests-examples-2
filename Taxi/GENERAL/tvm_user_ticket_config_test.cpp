#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tvm_user_ticket_config.hpp>

TEST(TestTvmUserTicketConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& user_ticket_config = config.Get<config::TvmUserTicketConfig>();
  ASSERT_FALSE(user_ticket_config.use_fake_context);
}
