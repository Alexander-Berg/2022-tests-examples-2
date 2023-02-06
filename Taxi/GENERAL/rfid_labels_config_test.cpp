#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/rfid_labels_config.hpp>

TEST(TestRfidLabelsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::RfidLabels& rfid_labels_config =
      config.Get<config::RfidLabels>();
  ASSERT_EQ(rfid_labels_config.http_request_timeout, 1000);
  ASSERT_EQ(rfid_labels_config.chunk_size, 1000);
}
