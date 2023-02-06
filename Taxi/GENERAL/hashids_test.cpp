#include <gtest/gtest.h>

#include "hashids.hpp"

TEST(TestHashids, EncodeSimple) {
  auto hash = hashids::Encode(123123);
  EXPECT_EQ(hash, "O37N1aM8mq5eWmpn");
  size_t decoded = hashids::DecodeSingle(hash);
  EXPECT_EQ(decoded, static_cast<size_t>(123123));
}

TEST(TestHashids, Encode64) {
  auto hash = hashids::Encode(4309837028);
  EXPECT_EQ(hash, "NJAPdRylpr7VbGyO");
  size_t decoded = hashids::DecodeSingle(hash);
  EXPECT_EQ(decoded, static_cast<size_t>(4309837028));
}
