#include <userver/utest/utest.hpp>

#include <gzip/gzip.hpp>

#include <userver/crypto/base64.hpp>

#include <agl/core/variant/io/body-loader.hpp>

namespace agl::modules::tests {

UTEST(TestBodyLoader, QueryString) {
  auto result = agl::core::variant::io::ParseRespectingContentType(
      "k1=value1&k2=value2", "application/x-www-form-urlencoded", "");
  auto result_map = result.AsMap();
  EXPECT_EQ(result_map.Size(), 2);

  EXPECT_EQ(result_map.Get<std::string>("k1"), "value1");
  EXPECT_EQ(result_map.Get<std::string>("k2"), "value2");
}

UTEST(TestBodyLoader, EmptyQueryString) {
  auto result = agl::core::variant::io::ParseRespectingContentType(
      "", "application/x-www-form-urlencoded", "");
  auto result_map = result.AsMap();
  EXPECT_EQ(result_map.Size(), 0);
}

UTEST(TestBodyLoader, CompressedQueryString) {
  std::string secret =
      "username=admin%21%21&password=pa%2A%2Asswd&grant_type=pa%22s%22sword&"
      "client_secret=secret";
  auto compressed = gzip::Compress(secret);
  auto encoded_secret = crypto::base64::Base64Encode(compressed);
  auto body_compressed_base64 = crypto::base64::Base64Decode(encoded_secret);

  auto result = agl::core::variant::io::ParseRespectingContentType(
      body_compressed_base64, "application/x-www-form-urlencoded", "gzip");
  auto result_map = result.AsMap();

  EXPECT_EQ(result_map.Size(), 4);

  EXPECT_EQ(result_map.Get<std::string>("username"), "admin!!");
  EXPECT_EQ(result_map.Get<std::string>("password"), "pa**sswd");
  EXPECT_EQ(result_map.Get<std::string>("grant_type"), "pa\"s\"sword");
  EXPECT_EQ(result_map.Get<std::string>("client_secret"), "secret");
}

UTEST(TestBodyLoader, SpecifiedMimeType) {
  auto result = agl::core::variant::io::ParseRespectingContentType(
      "{\"test\":\"value\"}", "application/specifier+json", "");
  auto result_json = result.AsJson();
  EXPECT_EQ(result_json["test"].As<std::string>(), "value");

  result = agl::core::variant::io::ParseRespectingContentType(
      "{\"test\":\"value\"}", "application/specifier+json+xml", "");
  EXPECT_THROW(result.AsJson(), boost::bad_get);
}

}  // namespace agl::modules::tests
