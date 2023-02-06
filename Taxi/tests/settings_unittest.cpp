#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include <secdist/settings/rfid.hpp>

TEST(SecdistTest, RfidSettings) {
  secdist::RfidSettings rfid = secdist::SecdistConfig(std::string(SECDIST_PATH))
                                   .Get<secdist::RfidSettings>();

  EXPECT_STREQ("RFID_LABELS_login", rfid.login.c_str());
  EXPECT_STREQ("RFID_LABELS_password", rfid.password.c_str());
  EXPECT_STREQ("AA BB CC DD", rfid.token.c_str());
}
