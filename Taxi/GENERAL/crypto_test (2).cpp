#include <cctv_definitions/views/crypto.hpp>

#include <iostream>

#include <gtest/gtest.h>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <cctv_definitions/models/secdist/crypto_hash_keys.hpp>

namespace {
formats::json::Value CreateSecdist() {
  formats::json::ValueBuilder secdist_builder(formats::common::Type::kObject);
  secdist_builder["settings_override"]["CCTV_ADMIN_CRYPTO_HASH_SETTINGS"]
                 ["crypto_keys"]["camera_uri"] =
                     "kDjNonVyRyaS/TuuQis0Sbm2yw9o/kcMn9aU9/clKq8=";
  secdist_builder["settings_override"]["CCTV_ADMIN_CRYPTO_HASH_SETTINGS"]
                 ["hash_keys"]["processor_ticket"] = "MTIzNHF3ZXJhc2Rmenhjdg==";
  return secdist_builder.ExtractValue();
}
}  // namespace

UTEST(CryptoTest, EncodeDecode) {
  {
    cctv_definitions::views::Crypto crypto(
        {std::make_shared<models::secdist::CryptoHashKeys>(CreateSecdist())});
    const std::string input = "HELLO, WORLD!!!";
    auto encrypted = crypto.EncryptCameraUri(input);
    EXPECT_TRUE(encrypted.data.size() > 0);
    auto output = crypto.DecryptCameraUri(encrypted);
    EXPECT_TRUE(encrypted.data.size() > 0);
    EXPECT_EQ(output, input);
  }
  {
    cctv_definitions::views::Crypto crypto(
        {std::make_shared<models::secdist::CryptoHashKeys>(CreateSecdist())});
    const std::string input = "";
    auto encrypted = crypto.EncryptCameraUri(input);
    EXPECT_TRUE(encrypted.data.size() > 0);
    auto output = crypto.DecryptCameraUri(encrypted);
    EXPECT_TRUE(encrypted.data.size() > 0);
    EXPECT_EQ(input, output);
  }
}

UTEST(CryptoTest, CorruptedData) {
  {
    cctv_definitions::views::Crypto crypto(
        {std::make_shared<models::secdist::CryptoHashKeys>(CreateSecdist())});
    const std::string input = "HELLO, WORLD";
    auto encrypted = crypto.EncryptCameraUri(input);
    EXPECT_TRUE(encrypted.data.size() > 0);
    encrypted.dek.pop_back();
    EXPECT_ANY_THROW(crypto.DecryptCameraUri(encrypted));
  }

  {
    cctv_definitions::views::Crypto crypto(
        {std::make_shared<models::secdist::CryptoHashKeys>(CreateSecdist())});
    const std::string input = "HELLO, WORLD";
    auto encrypted = crypto.EncryptCameraUri(input);
    EXPECT_TRUE(encrypted.data.size() > 0);
    encrypted.data.pop_back();
    EXPECT_ANY_THROW(crypto.DecryptCameraUri(encrypted));
  }
}

UTEST(CryptoTest, Hash) {
  cctv_definitions::views::Crypto crypto(
      {std::make_shared<models::secdist::CryptoHashKeys>(CreateSecdist())});
  auto ticket = crypto.GenerateProcesssorTicket();
  EXPECT_TRUE(ticket.size() > 0);
  auto hashed_ticket = crypto.HashProcessorTicket(ticket);
  EXPECT_TRUE(hashed_ticket.size() > 0);
}
