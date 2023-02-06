#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/s3_api_settings.hpp>

TEST(TestS3ApiSettings, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& s3_api_settings = config.Get<config::S3ApiSettings>();
  ASSERT_EQ(std::chrono::milliseconds(3000), s3_api_settings.request_timeout);
}
