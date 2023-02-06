#include <userver/formats/bson/exception.hpp>
#include <userver/formats/bson/types.hpp>

#include <userver/utest/utest.hpp>

// MongoDB Object format:
// 4 bytes: timestamp
// 5 bytes: random value
// 3 bytes: incrementing counter
// 12 bytes in total

TEST(OidTest, good_oid_check) {
  const auto t = std::string{"123456789abcdef0deadbeef"};
  EXPECT_TRUE(bson_oid_is_valid(t.data(), t.size()));
}

TEST(OidTest, good_oid_init) {
  const auto t = std::string{"123456789abcdef0deadbeef"};
  const auto oid = formats::bson::Oid{t};
  EXPECT_EQ(oid.ToString(), t);
}

TEST(OidTest, bad_oid_check) {
  const auto t = std::string{"bad1d"};
  EXPECT_FALSE(bson_oid_is_valid(t.data(), t.size()));
}

TEST(OidTest, bad_oid_init) {
  const auto t = std::string{"bad1d"};
  [[maybe_unused]] auto oid = formats::bson::Oid{};
  EXPECT_THROW(oid = formats::bson::Oid{t}, formats::bson::BsonException);
}
