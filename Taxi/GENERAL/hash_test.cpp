#include <gtest/gtest.h>

#include "hash.hpp"

const std::string kTestKey = "secret key";
const std::string kTestMessage = "hello, world!";
const std::string kTestMessageEncoded =
    "aGVsbG8sIHdvcmxkIVH9rjXUNSHbo/S4ssqaxd+j1xN/";

TEST(TestEncodeBase64_SHA1Hmac, EncodeBase64_SHA1Hmac) {
  const std::string output =
      utils::hash::EncodeBase64_SHA1Hmac(kTestMessage, kTestKey);

  EXPECT_EQ(kTestMessageEncoded, output);
}

TEST(TestDecodeBase64_SHA1Hmac, DecodeBase64_SHA1Hmac) {
  const std::string output =
      utils::hash::DecodeBase64_SHA1Hmac(kTestMessageEncoded, kTestKey);

  EXPECT_EQ(kTestMessage, output);
}

TEST(EncodeDecode, EncodeDecode) {
  const auto messages = {"foo", "bar", "maurice"};

  for (auto message : messages) {
    const std::string encoded =
        utils::hash::EncodeBase64_SHA1Hmac(message, kTestKey);
    const std::string decoded =
        utils::hash::DecodeBase64_SHA1Hmac(encoded, kTestKey);
    EXPECT_EQ(message, decoded) << message;
  }
}

TEST(DecodeFailures, DecodeFailures) {
  const auto messages = {
      "zxzxc123123112312312!@#$%%^&",                  // bad base64
      "Zm9vMQ",                                        // too short
      "xGVsbG8sIHdvcmxkIVH9rjXUNSHbo/S4ssqaxd+j1xN/",  // wrong signature
  };

  for (auto encoded : messages) {
    EXPECT_THROW(utils::hash::DecodeBase64_SHA1Hmac(encoded, kTestKey),
                 utils::hash::VerificationError)
        << encoded;
  }
}

TEST(Hash, Pbkdf2Hex) {
  ASSERT_EQ("b622f075e5d1169ca09a9b3f0adba87e06f43964ae14859c",
            utils::hash::Pbkdf2Hex("test", "salt"));
  ASSERT_EQ("751d3701901ef3cc59d4bbc06b898003d1749db7b50dcbbc",
            utils::hash::Pbkdf2Hex("test", ("\xcd"
                                            ">ym,i\x9c"
                                            "f")));
  ASSERT_EQ("c366e7c93e711deaa968babbf1b685ba6a262e561140133b",
            utils::hash::Pbkdf2Hex("some relatively long code...",
                                   "with the salt that is not so small also"));
}

TEST(Hash, Fnv0_64) {
  using utils::hash::Fnv0_64;

  const std::string kSong{"Taxi, taxi, drive, drive, along night houses..."};

  EXPECT_EQ(0ULL, Fnv0_64(""));
  EXPECT_EQ(0x2dfd4502953db311ULL, Fnv0_64(kTestMessage));
  EXPECT_EQ(0xd46317d70f650692ULL, Fnv0_64(kSong));
}

TEST(Hash, Fnv0_64Salt) {
  using utils::hash::Fnv0_64;

  const std::string kSong{"Taxi, taxi, drive, drive, along night houses..."};
  const std::string kSalt{"Gett must die!"};

  EXPECT_EQ(Fnv0_64("" + kSalt), utils::hash::Fnv0_64("", kSalt));
  EXPECT_EQ(Fnv0_64(kTestMessage + kSalt), Fnv0_64(kTestMessage, kSalt));
  EXPECT_EQ(Fnv0_64(kSong + kSalt), Fnv0_64(kSong, kSalt));
}
