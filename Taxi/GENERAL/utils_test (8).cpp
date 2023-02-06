#include <userver/utest/utest.hpp>

#include <common/utils.hpp>

namespace api_proxy::common::utils {

TEST(TestUtils, TrimWhitespace) {
  EXPECT_EQ(TrimWhitespace("GET"), "GET");
  EXPECT_EQ(TrimWhitespace(" GET"), "GET");
  EXPECT_EQ(TrimWhitespace("GET "), "GET");
  EXPECT_EQ(TrimWhitespace("  GET "), "GET");
  EXPECT_EQ(TrimWhitespace(" GET  "), "GET");

  EXPECT_EQ(TrimWhitespace("HELLO WORLD"), "HELLO WORLD");
  EXPECT_EQ(TrimWhitespace(" HELLO WORLD"), "HELLO WORLD");
  EXPECT_EQ(TrimWhitespace("HELLO WORLD "), "HELLO WORLD");
  EXPECT_EQ(TrimWhitespace("  HELLO WORLD "), "HELLO WORLD");
  EXPECT_EQ(TrimWhitespace(" HELLO WORLD  "), "HELLO WORLD");
}

TEST(TestUtils, SplitHeaderFields) {
  {
    const std::string header = "OPTIONS, GET, POST";
    const auto fields = SplitHeaderFields(header);

    EXPECT_EQ(fields.size(), 3);
    EXPECT_EQ(fields[0], "OPTIONS");
    EXPECT_EQ(fields[1], "GET");
    EXPECT_EQ(fields[2], "POST");
  }

  {
    const std::string header = ",OPTIONS,, , GET, POST , PUT";
    const auto fields = SplitHeaderFields(header);

    EXPECT_EQ(fields.size(), 4);
    EXPECT_EQ(fields[0], "OPTIONS");
    EXPECT_EQ(fields[1], "GET");
    EXPECT_EQ(fields[2], "POST");
    EXPECT_EQ(fields[3], "PUT");
  }
}

}  // namespace api_proxy::common::utils
