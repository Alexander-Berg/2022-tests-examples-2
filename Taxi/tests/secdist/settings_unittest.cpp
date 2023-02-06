#include <gtest/gtest.h>

#include <secdist/secdist.hpp>
#include <secdist/settings/driver_info.hpp>
#include <secdist/settings/promotion.hpp>

TEST(SecdistTest, PromotionSettings) {
  secdist::PromotionSettings promotion =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::PromotionSettings>();

  EXPECT_STREQ("auth_key_1", promotion.promo_sms_auth_key.c_str());
}

TEST(SecdistTest, DriverInfoSettings) {
  secdist::DriverInfoSettings driver_info_settings =
      secdist::SecdistConfig(std::string(SECDIST_PATH))
          .Get<secdist::DriverInfoSettings>();

  EXPECT_STREQ("driver_info_hash_salt",
               driver_info_settings.experiment_photo_hash_salt.c_str());
}
