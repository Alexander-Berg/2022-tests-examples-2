#include <gtest/gtest.h>

#include <common/include/serialization.h>

namespace taxi::rate_limiter2::tests {

TEST(Serialization, ParseQuotaResponse) {
  const auto& request1 = SerializeQuotaRequest("test1", "/test/path", 10);
  const auto& response1 = ParseQuotaResponse(request1);
  EXPECT_EQ(response1.client_id, "test1");
  EXPECT_EQ(response1.path, "/test/path");
  EXPECT_EQ(response1.value, 10);

  const auto& request2 = SerializeQuotaRequest("", "resource.test", -1);
  const auto& response2 = ParseQuotaResponse(request2);
  EXPECT_EQ(response2.client_id, "");
  EXPECT_EQ(response2.path, "resource.test");
  EXPECT_EQ(response2.value, -1);

  EXPECT_THROW(ParseQuotaResponse("invalid data"), std::runtime_error);

  const auto& request3 =
      SerializeQuotaRequest("test3", "/test/path3", 10, true, "my_test_path");
  const auto& response3 = ParseQuotaResponse(request3);
  EXPECT_EQ(response3.client_id, "test3");
  EXPECT_EQ(response3.path, "/test/path3");
  EXPECT_EQ(response3.value, 10);
  EXPECT_EQ(response3.is_regexp, true);
  EXPECT_EQ(response3.handler_name, "my_test_path");
}

}  // namespace taxi::rate_limiter2::tests
