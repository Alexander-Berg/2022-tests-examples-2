#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/uber_config.hpp>

TEST(TestUberConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& uber_config = config.Get<config::Uber>();
  ASSERT_EQ(uber_config.uber_user_billing_data_api_key.Get(), std::string());
  ASSERT_EQ(uber_config.yauber_ext_api_block_reason.Get(),
            std::string("need_to_use_new_app"));
  ASSERT_EQ(
      uber_config.yauber_ext_api_android_block_url.Get(),
      std::string(
          "https://itunes.apple.com/ru/app/yandex-taxi/id472650686?mt=8"));
  ASSERT_EQ(
      uber_config.yauber_ext_api_ios_block_url.Get(),
      std::string(
          "https://itunes.apple.com/ru/app/yandex-taxi/id472650686?mt=8"));
}
