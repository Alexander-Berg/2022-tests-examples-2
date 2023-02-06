#include "httpclient/external_request.hpp"
#include <gtest/gtest.h>

TEST(ExternalRequests, ConfigValid) {
  const int count = utils::external_request::kCount;
  for (int i = 0; i < count; ++i) {
    ASSERT_FALSE(utils::external_request::ToString(
                     static_cast<utils::external_request::Type>(i))
                     .empty());
  }
}
