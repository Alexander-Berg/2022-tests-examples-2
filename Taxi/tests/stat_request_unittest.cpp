#include <gtest/gtest.h>

#include <handlers/stat_request_handler.hpp>

namespace handlers {

TEST(parse_request, prefix) {
  const auto data =
      ParseStatisticsRequestPrefix("metrics.by-service.zoneinfo.fallbacks");

  ASSERT_TRUE(data.is_metrics_needed);
  ASSERT_TRUE(data.is_by_service_needed);
  ASSERT_FALSE(data.is_db_buffer_needed);
  ASSERT_TRUE(data.is_service_fallbacks_needed);
  ASSERT_TRUE(data.service);
  ASSERT_EQ(*data.service, "zoneinfo");
}

}  // namespace handlers
