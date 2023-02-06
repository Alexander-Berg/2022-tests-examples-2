#include <driver-id/driver_id.hpp>
#include <driver-id/serialization/driver_id.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace driver_id::test {

TEST(BasicDriverId, Validness) {
  using namespace driver_id::literals;

  DriverId id1{"dbid1"_dbid, "uuid1"_uuid};
  DriverId id2{"dbid2"_dbid, "uuid2"_uuid};

  DriverId id1_copy{id1};

  EXPECT_EQ(id1, id1);
  EXPECT_EQ(id1, id1_copy);
  EXPECT_NE(id1, id2);

  EXPECT_TRUE(id1.IsValid());

  EXPECT_FALSE(id1.IsEmpty());

  DriverId id1_move{std::move(id1_copy)};
  EXPECT_EQ(id1, id1_move);
}

TEST(BasicDriverId, Default) {
  DriverId id;
  EXPECT_FALSE(id.IsValid());
  EXPECT_TRUE(id.IsEmpty());
}

TEST(BasicDriverId, SerializationCycle) {
  using namespace driver_id::literals;
  DriverId reference{"dbid1"_dbid, "uuid1"_uuid};
  // Serialize
  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // Parse
  auto test = json_object.As<DriverId>();

  EXPECT_EQ(reference, test);
}

}  // namespace driver_id::test
