#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include <secdist/settings/afs_mds.hpp>
#include <secdist/settings/antifraud.hpp>

TEST(SecdistTest, AfsMdsSettings) {
  secdist::AfsMdsSettings afs_mds =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::AfsMdsSettings>();

  EXPECT_STREQ("s3.mdst.yandex.net", afs_mds.url.c_str());
}

TEST(SecdistTest, AntifraudSettings) {
  secdist::AntifraudSettings antifraud =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::AntifraudSettings>();

  EXPECT_STREQ("100500", antifraud.protector_api_key.c_str());
}
