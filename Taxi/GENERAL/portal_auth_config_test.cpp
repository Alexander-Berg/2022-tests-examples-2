#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/portal_auth_config.hpp>

TEST(PortalAuth, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::PortalAuth& portal_auth_config =
      config.Get<config::PortalAuth>();

  ASSERT_EQ(portal_auth_config.enable_confirms_update_in_mongo.Get(), false);
  ASSERT_EQ(portal_auth_config.email_enable_identity.Get(), false);
  ASSERT_EQ(portal_auth_config.email_confirm_by_id.Get(), false);
}
