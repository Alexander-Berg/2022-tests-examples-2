#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tvm_settings.hpp>

TEST(TestTVMSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tvm_settings = config.Get<config::TVMSettings>();
  ASSERT_EQ(tvm_settings.api_url, "https://tvm-api.yandex.net");
}
