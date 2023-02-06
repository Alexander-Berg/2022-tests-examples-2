#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/extra_phone_config.hpp>

TEST(ExtraPhoneConfigma, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  const auto& extra_phone_config = config.Get<config::ExtraPhoneConfig>();

  ASSERT_TRUE(extra_phone_config.options_by_tariff.GetDefaultValue().IsEmpty());
}
