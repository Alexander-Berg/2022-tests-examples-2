#include "s3api_methods.hpp"

#include <fmt/format.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/algo.hpp>

namespace clients::s3api::api_methods {

TEST(S3ApiMethods, CopyObject) {
  const std::string source_bucket = "source_bucket";
  const std::string source_key = "source_key";
  const std::string dest_bucket = "dest_bucket";
  const std::string dest_key = "dest_key";

  const Request request =
      CopyObject(source_bucket, source_key, dest_bucket, dest_key);
  EXPECT_EQ(request.method, clients::http::HttpMethod::kPut);
  EXPECT_EQ(request.req, dest_key);
  EXPECT_EQ(request.bucket, dest_bucket);
  EXPECT_TRUE(request.body.empty());
  const std::string* value =
      ::utils::FindOrNullptr(request.headers, headers::kAmzCopySource);
  ASSERT_NE(value, nullptr);
  EXPECT_EQ(*value, fmt::format("/{}/{}", source_bucket, source_key));
}

}  // namespace clients::s3api::api_methods
