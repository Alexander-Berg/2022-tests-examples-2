#include <gtest/gtest.h>

#include <bcrypt/bcrypt.hpp>

namespace {

struct TestData {
  std::string hash;
  bcrypt::Password password;
};

class BundledTest : public testing::TestWithParam<TestData> {};

// Tests bundled with the original code
const TestData kBundledTests[] = {
    {"$2a$05$CCCCCCCCCCCCCCCCCCCCC.E5YPO9kmyuRGyh0XouQYb4YMJKvyOeW",
     bcrypt::Password{"U*U"}},
    {"$2a$05$CCCCCCCCCCCCCCCCCCCCC.VGOzA784oUp/Z0DY336zx7pLYAy0lwK",
     bcrypt::Password{"U*U*"}},
    {"$2a$05$XXXXXXXXXXXXXXXXXXXXXOAcXxm9kjPGEMsLznoKqmqw7tc8WCx4a",
     bcrypt::Password{"U*U*U"}},
    {"$2a$05$abcdefghijklmnopqrstuu5s2v8.iXieOjg/.AySBTTZIIVFJeBui",
     bcrypt::Password{"0123456789abcdefghijklmnopqrstuvwxyz"
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.CE5elHaaO4EbggVDjb8P19RukzXSM3e",
     bcrypt::Password{"\xa3"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.CE5elHaaO4EbggVDjb8P19RukzXSM3e",
     bcrypt::Password{"\xff\xff\xa3"}},
    {"$2y$05$/OK.fbVrR/bpIqNJ5ianF.CE5elHaaO4EbggVDjb8P19RukzXSM3e",
     bcrypt::Password{"\xff\xff\xa3"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.nqd1wy.pTMdcvrRWxyiGL2eMz.2a85.",
     bcrypt::Password{"\xff\xff\xa3"}},
    {"$2b$05$/OK.fbVrR/bpIqNJ5ianF.CE5elHaaO4EbggVDjb8P19RukzXSM3e",
     bcrypt::Password{"\xff\xff\xa3"}},
    {"$2y$05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq",
     bcrypt::Password{"\xa3"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq",
     bcrypt::Password{"\xa3"}},
    {"$2b$05$/OK.fbVrR/bpIqNJ5ianF.Sa7shbm4.OzKpvFnX1pQLmQW96oUlCq",
     bcrypt::Password{"\xa3"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.o./n25XVfn6oAPaUvHe.Csk4zRfsYPi",
     bcrypt::Password{"1\xa3"
                      "345"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.o./n25XVfn6oAPaUvHe.Csk4zRfsYPi",
     bcrypt::Password{"\xff\xa3"
                      "345"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.o./n25XVfn6oAPaUvHe.Csk4zRfsYPi",
     bcrypt::Password{"\xff\xa3"
                      "34"
                      "\xff\xff\xff\xa3"
                      "345"}},
    {"$2y$05$/OK.fbVrR/bpIqNJ5ianF.o./n25XVfn6oAPaUvHe.Csk4zRfsYPi",
     bcrypt::Password{"\xff\xa3"
                      "34"
                      "\xff\xff\xff\xa3"
                      "345"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.ZC1JEJ8Z4gPfpe1JOr/oyPXTWl9EFd.",
     bcrypt::Password{"\xff\xa3"
                      "34"
                      "\xff\xff\xff\xa3"
                      "345"}},
    {"$2y$05$/OK.fbVrR/bpIqNJ5ianF.nRht2l/HRhr6zmCp9vYUvvsqynflf9e",
     bcrypt::Password{"\xff\xa3"
                      "345"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.nRht2l/HRhr6zmCp9vYUvvsqynflf9e",
     bcrypt::Password{"\xff\xa3"
                      "345"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.6IflQkJytoRVc1yuaNtHfiuq.FRlSIS",
     bcrypt::Password{"\xa3"
                      "ab"}},
    {"$2x$05$/OK.fbVrR/bpIqNJ5ianF.6IflQkJytoRVc1yuaNtHfiuq.FRlSIS",
     bcrypt::Password{"\xa3"
                      "ab"}},
    {"$2y$05$/OK.fbVrR/bpIqNJ5ianF.6IflQkJytoRVc1yuaNtHfiuq.FRlSIS",
     bcrypt::Password{"\xa3"
                      "ab"}},
    {"$2x$05$6bNw2HLQYeqHYyBfLMsv/OiwqTymGIGzFsA4hOTWebfehXHNprcAS",
     bcrypt::Password{"\xd1\x91"}},
    {"$2x$05$6bNw2HLQYeqHYyBfLMsv/O9LIGgn8OMzuDoHfof8AQimSGfcSWxnS",
     bcrypt::Password{"\xd0\xc1\xd2\xcf\xcc\xd8"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.swQOIzjOiJ9GHEPuhEkvqrUyvWhEMx6",
     bcrypt::Password{"\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"
                      "\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"
                      "\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"
                      "\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"
                      "\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"
                      "\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.R9xrDjiycxMbQE2bp.vgqlYpW5wx2yy",
     bcrypt::Password{"\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"
                      "\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"
                      "\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"
                      "\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"
                      "\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"
                      "\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55\xaa\x55"}},
    {"$2a$05$/OK.fbVrR/bpIqNJ5ianF.9tQZzcJfm3uj2NvJ/n5xkhpqLrMpWCe",
     bcrypt::Password{"\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"
                      "\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"
                      "\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"
                      "\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"
                      "\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"
                      "\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff\x55\xaa\xff"}},
    {"$2a$05$CCCCCCCCCCCCCCCCCCCCC.7uG0VCzI2bS7j6ymqJi9CdcdxiRTWNy",
     bcrypt::Password{}},
};

}  // namespace

TEST_P(BundledTest, Bundled) {
  const auto& data = GetParam();
  EXPECT_TRUE(bcrypt::IsCorrectHash(data.password, data.hash));
}

INSTANTIATE_TEST_SUITE_P(Bcrypt, BundledTest, testing::ValuesIn(kBundledTests));

TEST(Bcrypt, Cost) {
  EXPECT_NO_THROW(bcrypt::Hash({}));
  EXPECT_NO_THROW(bcrypt::Hash({}, bcrypt::kMinCost));
  EXPECT_THROW(bcrypt::Hash({}, bcrypt::kMinCost - 1), bcrypt::BcryptException);
  EXPECT_THROW(bcrypt::Hash({}, bcrypt::kMaxCost + 1), bcrypt::BcryptException);
}

TEST(Bcrypt, PasswordSize) {
  bcrypt::Password password;
  for (size_t i = 0; i <= bcrypt::kMaxPasswordSize; ++i) {
    EXPECT_NO_THROW(bcrypt::Hash(password, bcrypt::kMinCost));
    password.GetUnderlying().push_back('*');
  }
  EXPECT_THROW(bcrypt::Hash(password), bcrypt::BcryptException);
}
