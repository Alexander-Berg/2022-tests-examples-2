#include <gtest/gtest.h>
#include <boost/algorithm/string.hpp>
#include <clients/s3api_methods.hpp>

static const char* bucket = "test_bucket";
static const char* path = "path";

TEST(s3apimethods, TestGet) {
  auto result = clients::s3api::api_methods::GetObject(bucket, path);
  ASSERT_EQ(utils::http::GET, result.method);
}

TEST(s3apimethods, TestPut) {
  const char* path = "path";
  auto result = clients::s3api::api_methods::PutObject(bucket, path, "Ъ");
  ASSERT_EQ(utils::http::PUT, result.method);
}

TEST(s3apimethods, TestList) {
  const char* path = "path";
  auto result =
      clients::s3api::api_methods::ListBucketContents(bucket, path, 42);
  ASSERT_EQ(utils::http::GET, result.method);
  ASSERT_NE(result.req.find("delimeter"), std::string::npos);
  ASSERT_NE(result.req.find("max-keys"), std::string::npos);

  auto result2 = clients::s3api::api_methods::ListBucketContents(bucket, path);
  ASSERT_EQ(result2.req.find("max-keys"), std::string::npos);
}

TEST(s3apimethods, TestDelete) {
  auto result = clients::s3api::api_methods::DeleteObjects(
      bucket, {"path/obj1", "path/obj2"});
  ASSERT_EQ(utils::http::POST, result.method);
  ASSERT_EQ("text/xml", result.headers["Content-Type"]);

  std::string expected_body =
      "<Delete>"
      "<Object><Key>path/obj1</Key></Object>"
      "<Object><Key>path/obj2</Key></Object>"
      "</Delete>";
  ASSERT_EQ(result.body, expected_body);
}
