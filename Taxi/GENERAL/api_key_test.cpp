#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include "api_key.hpp"

TEST(SecdistTest, GeotracksApiKey) {
  secdist::GeotracksApiKey api_key =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::GeotracksApiKey>();

  EXPECT_STREQ("GEOTRACKS-VALID-API-KEY", api_key.api_key.c_str());
}
