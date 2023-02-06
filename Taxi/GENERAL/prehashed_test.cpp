#include <driver-id/dbid_uuid.hpp>
#include <driver-id/driver_id.hpp>
#include <driver-id/prehashed.hpp>
#include <driver-id/serialization/dbid_uuid.hpp>
#include <driver-id/serialization/driver_id.hpp>
#include <driver-id/serialization/prehashed.hpp>
#include <driver-id/shared.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace driver_id::test {

using namespace driver_id::literals;

struct BasicPrehashedFixture : public ::testing::Test {
  using PrehashedDriverId = Prehashed<DriverDbidUndscrUuid>;

  const DriverDbidUndscrUuid id1{"dbid1"_dbid, "uuid1"_uuid};
  const DriverDbidUndscrUuid id2{"dbid2"_dbid, "uuid2"_uuid};
};

TEST_F(BasicPrehashedFixture, Constructor) {
  PrehashedDriverId sid1(id1);
  PrehashedDriverId sid2(DriverDbidUndscrUuid{id2});
  PrehashedDriverId sid2_copy{sid2};

  // Equality
  EXPECT_EQ(sid2, sid2_copy);
  EXPECT_EQ(sid2, id2);
  EXPECT_EQ(sid2, sid2);
  EXPECT_NE(sid2, sid1);
  EXPECT_NE(sid2, id1);

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_NE(sid1, id2);
}

TEST_F(BasicPrehashedFixture, Assignement) {
  PrehashedDriverId sid1 = PrehashedDriverId{id1};
  PrehashedDriverId sid2 = PrehashedDriverId{id2};
  PrehashedDriverId sid2_copy = PrehashedDriverId{sid2};

  // Equality
  EXPECT_EQ(sid2, sid2_copy);
  EXPECT_EQ(sid2, id2);
  EXPECT_EQ(sid2, sid2);
  EXPECT_NE(sid2, sid1);
  EXPECT_NE(sid2, id1);

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_NE(sid1, id2);
}

TEST_F(BasicPrehashedFixture, Equality) {
  PrehashedDriverId sid1{id1};

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_EQ(id1, sid1);

  // testing operator !=
  EXPECT_FALSE(sid1 != id1);
  EXPECT_FALSE(id1 != sid1);
  EXPECT_FALSE(sid1 != sid1);
}

TEST_F(BasicPrehashedFixture, Default) {
  PrehashedDriverId id;
  EXPECT_EQ(id, id);
  EXPECT_EQ(id.GetDriverId(), DriverDbidUndscrUuid{});
}

TEST_F(BasicPrehashedFixture, SerializationCycle) {
  using namespace driver_id::literals;
  PrehashedDriverId reference{id1};
  // Serialize
  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // Parse
  auto test = json_object.As<DriverDbidUndscrUuid>();

  EXPECT_EQ(reference, test);
}

}  // namespace driver_id::test
