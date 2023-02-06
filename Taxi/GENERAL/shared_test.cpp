#include <driver-id/driver_id.hpp>
#include <driver-id/serialization/driver_id.hpp>
#include <driver-id/serialization/shared.hpp>
#include <driver-id/shared.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace driver_id::test {

using namespace driver_id::literals;

struct BasicSharedFixture : public ::testing::Test {
  using SharedDriverId = Shared<DriverId>;

  const DriverId id1{"dbid1"_dbid, "uuid1"_uuid};
  const DriverId id2{"dbid2"_dbid, "uuid2"_uuid};
};

TEST_F(BasicSharedFixture, Constructor) {
  SharedDriverId sid1(id1);
  SharedDriverId sid2(DriverId{id2});
  SharedDriverId sid2_copy{sid2};

  // Equality
  EXPECT_EQ(sid2, sid2_copy);
  EXPECT_EQ(sid2, id2);
  EXPECT_EQ(sid2, sid2);
  EXPECT_NE(sid2, sid1);
  EXPECT_NE(sid2, id1);

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_NE(sid1, id2);
  EXPECT_NE(sid1, nullptr);
}

TEST_F(BasicSharedFixture, Assignement) {
  SharedDriverId sid1 = id1;
  SharedDriverId sid2 = DriverId{id2};
  SharedDriverId sid2_copy = sid2;

  // Equality
  EXPECT_EQ(sid2, sid2_copy);
  EXPECT_EQ(sid2, id2);
  EXPECT_EQ(sid2, sid2);
  EXPECT_NE(sid2, sid1);
  EXPECT_NE(sid2, id1);

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_NE(sid1, id2);
  EXPECT_NE(sid1, nullptr);
}

TEST_F(BasicSharedFixture, Equality) {
  SharedDriverId sid1{id1};

  EXPECT_EQ(sid1, id1);
  EXPECT_EQ(sid1, sid1);
  EXPECT_EQ(id1, sid1);

  // testing operator !=
  EXPECT_FALSE(sid1 != id1);
  EXPECT_FALSE(id1 != sid1);
  EXPECT_FALSE(sid1 != sid1);

  // testing with nullptr
  EXPECT_NE(nullptr, sid1);
  EXPECT_NE(sid1, nullptr);

  EXPECT_FALSE(sid1 == nullptr);
  EXPECT_FALSE(nullptr == sid1);
  EXPECT_TRUE(sid1 != nullptr);
  EXPECT_TRUE(nullptr != sid1);
}

TEST_F(BasicSharedFixture, Default) {
  SharedDriverId id;
  EXPECT_EQ(nullptr, id);
  EXPECT_EQ(id, id);
}

TEST_F(BasicSharedFixture, SerializationCycle) {
  using namespace driver_id::literals;
  SharedDriverId reference{DriverId{id1}};
  // Serialize
  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // Parse
  auto test = json_object.As<DriverId>();

  EXPECT_EQ(reference, test);
}

TEST_F(BasicSharedFixture, SerializationException) {
  SharedDriverId null_reference;
  ASSERT_ANY_THROW(formats::json::ValueBuilder(null_reference).ExtractValue());
}

}  // namespace driver_id::test
