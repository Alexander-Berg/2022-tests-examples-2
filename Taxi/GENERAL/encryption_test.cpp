#include "encryption.hpp"
#include <gmock/gmock.h>

namespace crypto = eats_restapp_support_chat::utils::crypto;

constexpr auto INVALID_KEY = "G+KbPeShVmYq3t6w9z$C&F)H@McQ";
constexpr auto VALID_KEY = "G+KbPeShVmYq3t6w9z$C&F)H@McQfTjW";

TEST(Encryption, InvalidKey) {
  // key size != 16
  ASSERT_ANY_THROW(crypto::Encode("qwe", INVALID_KEY));
}

TEST(Encryption, Encode) { ASSERT_NO_THROW(crypto::Encode("qwe", VALID_KEY)); }

TEST(Encryption, Decode) {
  const std::string text = "test text";
  auto data = crypto::Encode(text, VALID_KEY);
  std::string res;
  ASSERT_NO_THROW(res = crypto::Decode(data, VALID_KEY));
  ASSERT_EQ(res, text);
}

TEST(Encryption, ErrorKeyDecode) {
  const std::string text = "test text";
  auto data = crypto::Encode(text, VALID_KEY);
  const auto new_key = "gVkYp3s6v8y/B?E(H+MbQeThWmZq4t7w";
  std::string res;
  ASSERT_THROW(crypto::Decode(data, new_key), crypto::CryptoError);
}

TEST(Encryption, DISABLED_DecodeFromList) {
  const std::string text = "test text";
  auto data = crypto::Encode(text, VALID_KEY);

  auto keys = std::vector<std::string>{"gVkYp3s6v8y/B?E(H+MbQeThWmZq4t7w",
                                       "n2r5u8x/A?D(G+KbPeSgVkYp3s6v9y$B",
                                       "2r5u8x/A?D(G-KaPdSgVkYp3s6v9y$B&"};

  auto opt_data = crypto::DecodeFromList(data, keys);
  // нужного ключа нет в списке
  ASSERT_FALSE(opt_data.has_value());
  // добавляем нужный ключ в начало
  // чтобы убедиться что он пройдет по всем ключам
  // и нормально расшифрует
  keys.insert(keys.begin(), VALID_KEY);
  opt_data = crypto::DecodeFromList(data, keys);
  ASSERT_TRUE(opt_data.has_value());
  ASSERT_EQ(opt_data.value(), text);
}

TEST(Encryption, DISABLED_DecodeFromListEnd) {
  const std::string text = "test text";
  auto data = crypto::Encode(text, VALID_KEY);

  auto keys = std::vector<std::string>{"gVkYp3s6v8y/B?E(H+MbQeThWmZq4t7w",
                                       "n2r5u8x/A?D(G+KbPeSgVkYp3s6v9y$B",
                                       "2r5u8x/A?D(G-KaPdSgVkYp3s6v9y$B&"};

  auto opt_data = crypto::DecodeFromList(data, keys);
  // нужного ключа нет в списке
  ASSERT_FALSE(opt_data.has_value());
  // добавляем нужный ключ в конец
  // чтобы убедиться, что все равно
  // нормально расшифрует
  keys.emplace_back(VALID_KEY);
  opt_data = crypto::DecodeFromList(data, keys);
  ASSERT_TRUE(opt_data.has_value());
  ASSERT_EQ(opt_data.value(), text);
}

TEST(Encryption, DISABLED_DecodeFromListMiddle) {
  const std::string text = "test text";
  auto data = crypto::Encode(text, VALID_KEY);

  auto keys = std::vector<std::string>{"gVkYp3s6v8y/B?E(H+MbQeThWmZq4t7w",
                                       "n2r5u8x/A?D(G+KbPeSgVkYp3s6v9y$B",
                                       "2r5u8x/A?D(G-KaPdSgVkYp3s6v9y$B&"};

  auto opt_data = crypto::DecodeFromList(data, keys);
  // нужного ключа нет в списке
  ASSERT_FALSE(opt_data.has_value());
  // добавляем нужный ключ в середину
  // чтобы убедиться, что все равно
  // нормально расшифрует
  keys.insert(keys.begin() + 2, VALID_KEY);
  opt_data = crypto::DecodeFromList(data, keys);
  ASSERT_TRUE(opt_data.has_value());
  ASSERT_EQ(opt_data.value(), text);
}
