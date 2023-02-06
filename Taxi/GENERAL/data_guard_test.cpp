#include <userver/utest/utest.hpp>

#include <custom/data_guard.hpp>

class DataGuardTest : public testing::Test {
 protected:
  static constexpr auto kPlaintext0 = "";
  static constexpr auto kPlaintext1 = "0123456789abcdef";

  static auto SetUpCipherKey() {
    custom::DataGuard::CipherKey key;
    key.fill(0xFF);
    return key;
  }

  static auto SetUpHashKey() {
    custom::DataGuard::HashKey key;
    key.fill(0xFF);
    return key;
  }

  void SetUp() override {
    data_guard_ =
        std::make_unique<custom::DataGuard>(SetUpCipherKey(), SetUpHashKey());
  }

  void TearDown() override { data_guard_.reset(); }

  std::unique_ptr<custom::DataGuard> data_guard_;
};

TEST_F(DataGuardTest, EncryptDecrypt0) {
  const auto enc = data_guard_->Encrypt(kPlaintext0);
  const auto dec = data_guard_->Decrypt(enc);
  ASSERT_EQ(dec, kPlaintext0);
}

TEST_F(DataGuardTest, EncryptDecrypt1) {
  const auto enc = data_guard_->Encrypt(kPlaintext1);
  const auto dec = data_guard_->Decrypt(enc);
  ASSERT_EQ(dec, kPlaintext1);
}

TEST_F(DataGuardTest, EncryptRandomness) {
  const auto enc1 = data_guard_->Encrypt(kPlaintext1);
  const auto enc2 = data_guard_->Encrypt(kPlaintext1);
  ASSERT_NE(enc1, enc2);
}

TEST_F(DataGuardTest, Decrypt) {
  const auto dec = data_guard_->Decrypt(
      "\xCB\x19\x6F\x4F\xB5\xCC\xD0\x1D\x53\x4D\xD0\x8C\x4D\x80\x63\xFB\xAD\xAD"
      "\xBC\x82\x04\x19\xE5\x5E\xEB\x10\x4D\x5F\x77\xFF\x92\xF8\xBB\x06\xF3\xC7"
      "\xB3\x3F\x94\x59\x83\x70\xD7\x74\xE5\x15\x65\x66");
  ASSERT_EQ(dec, kPlaintext1);
}

TEST_F(DataGuardTest, DecryptThrow) {
  ASSERT_THROW(data_guard_->Decrypt(std::string(15, '\xFF')),
               std::runtime_error);
  ASSERT_THROW(data_guard_->Decrypt(std::string(16, '\xFF')),
               std::runtime_error);
  ASSERT_THROW(data_guard_->Decrypt(std::string(17, '\xFF')),
               std::runtime_error);
}

TEST_F(DataGuardTest, Digest) {
  const auto dig = data_guard_->Digest(kPlaintext1);
  ASSERT_EQ(dig,
            "\x7F\xAF\xC8\x34\xA6\xF6\xFD\x70\x06\x80\x10\xDC\xA8\x80\xA7\x12"
            "\xF8\xE9\x29\xEB\xE4\x60\x33\x40\xC1\x94\x48\xBE\x88\xAE\xC2\x4B");
}
