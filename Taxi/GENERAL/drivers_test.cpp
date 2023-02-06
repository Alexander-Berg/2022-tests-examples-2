#include <gtest/gtest.h>

#include "drivers.hpp"

TEST(DriverId, FromClidUuid) {
  const auto& id = models::DriverId::FromClidUuid("asd_fgh");
  EXPECT_TRUE(id.IsValid());
  EXPECT_TRUE(id.dbid.empty());
  EXPECT_STREQ("asd", id.clid.c_str());
  EXPECT_STREQ("fgh", id.uuid.c_str());
  EXPECT_STREQ("asd_fgh", id.clid_uuid().c_str());
}

TEST(DriverId, FromDbidUuid) {
  const auto& id = models::DriverId::FromDbidUuid("asd_fgh");
  EXPECT_TRUE(id.IsValid());
  EXPECT_TRUE(id.clid.empty());
  EXPECT_STREQ("asd", id.dbid.c_str());
  EXPECT_STREQ("fgh", id.uuid.c_str());
  EXPECT_STREQ("asd_fgh", id.dbid_uuid().c_str());
}

TEST(DriverIdMap, Simple) {
  models::DriverIdMap<int> map;
  map.emplace(models::DriverId{"qwe", "abc", "zxc"}, 0);
  map.emplace(models::DriverId{"wer", "abc", "xcv"}, 1);
  map.emplace(models::DriverId{"ert", "sdf", "zxc"}, 2);
  map.emplace(models::DriverId{"rty", "", "cvb"}, 3);

  EXPECT_EQ(4u, map.size());

  EXPECT_EQ(0, map[models::DriverId::FromDbidUuid("qwe_zxc")]);
  EXPECT_EQ(0, map[models::DriverId::FromClidUuid("abc_zxc")]);

  EXPECT_EQ(1, map[models::DriverId::FromDbidUuid("wer_xcv")]);
  EXPECT_EQ(1, map[models::DriverId::FromClidUuid("abc_xcv")]);

  EXPECT_EQ(2, map[models::DriverId::FromDbidUuid("ert_zxc")]);
  EXPECT_EQ(2, map[models::DriverId::FromClidUuid("sdf_zxc")]);

  EXPECT_EQ(3, map[models::DriverId::FromDbidUuid("rty_cvb")]);
}
