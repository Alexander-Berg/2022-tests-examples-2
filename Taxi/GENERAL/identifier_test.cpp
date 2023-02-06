#include <userver/utest/utest.hpp>

#include <clickhouse_http_client/identifier.hpp>

TEST(ClickhouseHttpClientTest, IdentifierTest) {
  using Identifier = clickhouse_http_client::Identifier;

  ASSERT_EQ(Identifier("x").Get(), "x");
  ASSERT_EQ(Identifier("_1").Get(), "_1");
  ASSERT_EQ(Identifier("X_y__Z123_").Get(), "X_y__Z123_");

  ASSERT_EQ(Identifier("test_Z").Get(), "test_Z");
  ASSERT_EQ(Identifier("`test_Z").Get(), "\"`test_Z\"");
  ASSERT_EQ(Identifier("\"test").Get(), "\"\\\"test\"");
  ASSERT_EQ(Identifier("test ").Get(), "\"test \"");
  ASSERT_EQ(Identifier(" test").Get(), "\" test\"");
}
