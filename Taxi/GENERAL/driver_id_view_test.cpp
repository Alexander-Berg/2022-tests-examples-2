#include <driver-id/driver_id.hpp>
#include <driver-id/serialization/driver_id.hpp>
#include <driver-id/serialization/driver_id_view.hpp>

#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

#include <iostream>

namespace driver_id::test {

namespace {
template <std::size_t Length>
constexpr std::string_view MakeStringView(const char (&data)[Length]) {
  return std::string_view{data, Length - 1};
}

const char kDbid1[] = "dbid1";
const char kUuid1[] = "uuid1";
const char kDbid2[] = "dbid2";
const char kUuid2[] = "uuid2";
}  // namespace

TEST(BasicDriverIdView, Validness) {
  using namespace driver_id::literals;

  const DriverDbidView dbid_v1{MakeStringView(kDbid1)};
  const DriverUuidView uuid_v1{MakeStringView(kUuid1)};
  const DriverDbidView dbid_v2{MakeStringView(kDbid2)};
  const DriverUuidView uuid_v2{MakeStringView(kUuid2)};

  EXPECT_EQ(dbid_v1.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(uuid_v1.GetUnderlying(), std::string{"uuid1"});

  auto dbid_v_copy{dbid_v1};
  EXPECT_EQ(dbid_v_copy.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(dbid_v_copy, dbid_v1);

  auto dbid_v_move{std::move(dbid_v_copy)};
  EXPECT_EQ(dbid_v_move.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(dbid_v_move, dbid_v1);

  EXPECT_EQ(dbid_v1.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(uuid_v1.GetUnderlying(), std::string{"uuid1"});
  DriverIdView id1{dbid_v1, uuid_v1};
  EXPECT_EQ(id1.dbid, dbid_v1);
  EXPECT_EQ(id1.uuid, uuid_v1);
  EXPECT_EQ(dbid_v1.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(uuid_v1.GetUnderlying(), std::string{"uuid1"});
  EXPECT_EQ(id1.dbid.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(id1.uuid.GetUnderlying(), std::string{"uuid1"});

  DriverIdView id2{dbid_v2, uuid_v2};
  EXPECT_EQ(id2.dbid, dbid_v2);
  EXPECT_EQ(id2.uuid, uuid_v2);

  DriverIdView id1_copy{id1};
  EXPECT_EQ(id1_copy.dbid, id1.dbid);
  EXPECT_EQ(id1_copy.uuid, id1.uuid);

  EXPECT_EQ(id1.dbid.GetUnderlying(), std::string{"dbid1"});
  EXPECT_EQ(id1.uuid.GetUnderlying(), std::string{"uuid1"});

  EXPECT_EQ(id1, id1);
  EXPECT_EQ(id1, id1_copy);
  EXPECT_NE(id1, id2);

  EXPECT_TRUE(id1.IsValid());

  EXPECT_FALSE(id1.IsEmpty());

  DriverIdView id1_move{std::move(id1_copy)};
  EXPECT_EQ(id1, id1_move);
}

TEST(BasicDriverIdView, Default) {
  DriverIdView id;
  EXPECT_FALSE(id.IsValid());
  EXPECT_TRUE(id.IsEmpty());
}

TEST(BasicDriverIdView, SerializationCycle) {
  using namespace driver_id::literals;
  DriverIdView reference{DriverDbidView{MakeStringView(kDbid1)},
                         DriverUuidView{MakeStringView(kUuid1)}};
  // Serialize
  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // Parse (not as view!)
  auto test = json_object.As<DriverId>();

  EXPECT_EQ(reference, test);
}

TEST(BasicDriverIdView, NonRValueConstructible) {
  EXPECT_FALSE(
      (std::is_constructible_v<DriverIdView, DriverDbid&&, DriverUuidView&>));
  EXPECT_FALSE(
      (std::is_constructible_v<DriverIdView, DriverUuid&&, DriverDbidView&>));
  EXPECT_FALSE(
      (std::is_constructible_v<DriverIdView, DriverUuid&&, DriverDbid&&>));
}

}  // namespace driver_id::test
