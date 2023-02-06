#include <gtest/gtest.h>

#include <handlers/common/exceptions.hpp>
#include <utils/crypto/aes_encryption.hpp>

namespace crypto {

const std::string kSecdistKey{"emFpMW5haDN0aGFlQ2hhaXNoMG9oanVrZWk4cGF3YWg="};
const std::string kKey{"zai1nah3thaeChaish0ohjukei8pawah"};
const std::string kPassword{"пароль от wifi"};

inline std::string GetCorruptedKey() {
  auto result = kKey;
  result.back() = 'Z';
  return result;
}

TEST(Crypto, DecodeKey) {
  EXPECT_THROW(DecodeKey(""), handlers::InvalidDbDataException);
  EXPECT_THROW(DecodeKey("abcd"), handlers::InvalidDbDataException);
  EXPECT_THROW(DecodeKey("$^^%"), handlers::InvalidDbDataException);
  EXPECT_EQ(kKey, DecodeKey(kSecdistKey));
}

TEST(Crypto, EncodeDecode) {
  EXPECT_EQ("", AesDecrypt(AesEncrypt("", kKey), kKey));
  EXPECT_EQ(kPassword, AesDecrypt(AesEncrypt(kPassword, kKey), kKey));
}

// usual case
TEST(Crypto, CorruptedKeyThrow) {
  static const std::string kThrowIv =
      "\x99\x54\x27\x2c\x3c\x39\x7d\x32\xc0\xf7\x27\x1b\x90\x1f\x94\x82";
  const auto encoded = impl::EncodeWithGivenIv(kPassword, kKey, kThrowIv);
  EXPECT_THROW(AesDecrypt(encoded, GetCorruptedKey()),
               handlers::InvalidDbDataException);
}

// very seldom case
TEST(Crypto, CorruptedKeyTrash) {
  static const std::string kTrashIv =
      "\x9b\xf9\x5b\x36\xcc\x67\xfa\xca\xac\x63\xe0\x27\x5a\x59\x5d\xb5";
  const auto encoded = impl::EncodeWithGivenIv(kPassword, kKey, kTrashIv);
  EXPECT_NE(AesDecrypt(encoded, GetCorruptedKey()), kPassword);
}

}  // namespace crypto
