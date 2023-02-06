#include <personal/hasher/hasher.hpp>

#include <gtest/gtest.h>

#include <userver/crypto/base64.hpp>

TEST(PhoneHasher, Hash) {
  auto hasher = personal::hasher::Hasher("private");

  EXPECT_EQ(hasher.GetHash("+1234567890", "public"),
            "c9340bb4969e976dc1dff11f2b6820f3535221f1b7890e8b248a3cc488d54c07");
}

TEST(PhoneHasherTesting, HashMy) {
  auto hasher = personal::hasher::Hasher("eepaabooki4chewuNg4ULaizahthaiy1");

  EXPECT_EQ(hasher.GetHash("+79031520355",
                           crypto::base64::Base64Decode(
                               "66rWHYASJifdc9Q/+M8q6cm401B0zn3P3/ryK7wtVjw=")),
            "0cc26e241a09628769822a3a03c21461cacf06474f673bf1b196c2d30edf46e3");
}
