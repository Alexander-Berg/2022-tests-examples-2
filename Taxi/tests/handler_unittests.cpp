#include <gtest/gtest.h>
#include <handlers/base_ml_handler.hpp>

namespace {

TEST(MLaasHandlers, ParseFormatVersion) {
  ASSERT_EQ(handlers::BaseMLHandler::GetFormatVersion("/expected_destinations"),
            "");
  ASSERT_EQ(
      handlers::BaseMLHandler::GetFormatVersion("/v2.0/expected_destinations"),
      "v2.0");
}
}  // namespace
