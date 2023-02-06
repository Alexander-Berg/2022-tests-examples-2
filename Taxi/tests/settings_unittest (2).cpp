#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include <secdist/settings/ml_md.hpp>

TEST(SecdistTest, MlMdSettings) {
  secdist::MlMdSettings mlmd = secdist::SecdistConfig(std::string(SECDIST_PATH))
                                   .Get<secdist::MlMdSettings>();

  EXPECT_STREQ("ML_MDS_S3_access_key_id", mlmd.access_key_id.c_str());
  EXPECT_FALSE(mlmd.secret_key.empty());
}
