#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include "childchairs.hpp"

TEST(Car, HasChildTariff) {
  models::childchairs::ChairsInfo chairs_info;

  const models::childchairs::Chair::Groups groups2{2};

  const models::childchairs::Chair& chair2{"Other", groups2, false};
  const models::childchairs::ConfirmedChair& confirmed_chair2_ok{chair2, true,
                                                                 groups2};
  const models::childchairs::ConfirmedChair& confirmed_chair2_disabled{
      chair2, false, groups2};

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid1"),
            models::childchairs::ChildTariffState::kNoChairs);

  // with booster
  chairs_info.boosters = 1;

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid1"),
            models::childchairs::ChildTariffState::kNoConfirmedChairs);

  // with confirmed booster
  chairs_info.confirmed_boosters = 1;

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid1"),
            models::childchairs::ChildTariffState::kEnabled);

  // with driver booster
  chairs_info.boosters = 0;
  chairs_info.confirmed_boosters = 0;
  chairs_info.driver_boosters = {{"uuid1", 1}};

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid1"),
            models::childchairs::ChildTariffState::kNoConfirmedChairs);

  // with driver confirmed booster
  chairs_info.driver_confirmed_boosters = {{"uuid1", 1}};

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid1"),
            models::childchairs::ChildTariffState::kEnabled);

  // with driver confirmed(disabled) child chair
  chairs_info.driver_chairs = {{"uuid2", {chair2}}};
  chairs_info.driver_confirmed_chairs = {
      {"uuid2", {confirmed_chair2_disabled}}};

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid2"),
            models::childchairs::ChildTariffState::kNoConfirmedChairs);

  // with driver confirmed child chair
  chairs_info.driver_confirmed_chairs = {{"uuid2", {confirmed_chair2_ok}}};

  EXPECT_EQ(chairs_info.GetChildTariffState("uuid2"),
            models::childchairs::ChildTariffState::kEnabled);
}
