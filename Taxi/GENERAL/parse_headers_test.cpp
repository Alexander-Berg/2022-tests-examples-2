#include <userver/utest/utest.hpp>

#include <base-proxy-passport/http/parse_headers.hpp>

TEST(Crypto, IsB64Token) {
  EXPECT_TRUE(base_proxy_passport::http::IsB64Token("aaaa"));
  EXPECT_TRUE(base_proxy_passport::http::IsB64Token("dGVzdA=="));
  EXPECT_TRUE(base_proxy_passport::http::IsB64Token("azAZ0123456789"));
  EXPECT_TRUE(base_proxy_passport::http::IsB64Token("-._~+/="));
  EXPECT_TRUE(base_proxy_passport::http::IsB64Token(""));

  EXPECT_FALSE(base_proxy_passport::http::IsB64Token(" "));
  EXPECT_FALSE(base_proxy_passport::http::IsB64Token("%"));
  EXPECT_FALSE(base_proxy_passport::http::IsB64Token("&"));
}
