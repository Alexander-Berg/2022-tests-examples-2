#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include "mds_settings.hpp"

TEST(SecdistTest, GeotracksMdsSettings) {
  secdist::GeotracksMdsSettings mds_settings =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::GeotracksMdsSettings>();

  EXPECT_STREQ("GEOTRACKS_MDS_S3_access_key_id",
               mds_settings.access_key.c_str());
  EXPECT_STREQ("GEOTRACKS_MDS_S3_secret_key", mds_settings.secret_key.c_str());
  EXPECT_STREQ("s3.mdst.yandex.net", mds_settings.url.c_str());
}
