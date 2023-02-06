#include <driver-id/dbid_uuid.hpp>
#include <driver-id/serialization/dbid_uuid.hpp>
#include <driver-id/serialization/driver_id.hpp>
#include <driver-id/test/print_to.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <gtest/gtest.h>

namespace driver_id::test {

using namespace driver_id::literals;

namespace {

struct TestData {
  const std::string dbid;
  const std::string uuid;
  const std::string dbid_uuid;
  bool empty;
  bool valid;
};

inline std::string PrintToString(const TestData& data) {
  return (data.dbid_uuid.empty() ? "0empty0" : data.dbid_uuid);
}

const char kDbid1[] = "dbid1";
const char kUuid1[] = "uuid1";
const char kDbid2[] = "dbid2";
const char kUuid2[] = "uuid2";

template <std::size_t Length>
constexpr std::string_view MakeStringView(const char (&data)[Length]) {
  return std::string_view{data, Length - 1};
}

}  // namespace

struct BasicDriverUuid_Dbid : public ::testing::Test {
  inline static const DriverIdView id1{DriverDbidView{MakeStringView(kDbid1)},
                                       DriverUuidView{MakeStringView(kUuid1)}};
  inline static const DriverIdView id2{DriverDbidView{MakeStringView(kDbid2)},
                                       DriverUuidView{MakeStringView(kUuid2)}};
  inline static const DriverDbidUndscrUuid du1{std::string{"dbid1_uuid1"}};
  inline static const DriverDbidUndscrUuid du2{std::string{"dbid2_uuid2"}};
};

struct VPDriverUuid_Dbid : public ::testing::TestWithParam<TestData> {
  DriverIdView id_ref() const {
    return DriverIdView{DriverDbidView{std::string_view{GetParam().dbid}},
                        DriverUuidView{std::string_view{GetParam().uuid}}};
  }

  DriverDbidUndscrUuid dbid_uuid() const {
    return DriverDbidUndscrUuid{GetParam().dbid_uuid};
  }
};

TEST_F(BasicDriverUuid_Dbid, Uniformity) {
  EXPECT_EQ(id1.dbid, du1.GetDbid());
  EXPECT_EQ(id1.uuid, du1.GetUuid());
  EXPECT_EQ(id2.dbid, du2.GetDbid());
  EXPECT_EQ(id2.uuid, du2.GetUuid());
  EXPECT_EQ(id1.dbid.GetUnderlying(), std::string{kDbid1});
  EXPECT_EQ(id1.uuid.GetUnderlying(), std::string{kUuid1});

  EXPECT_NE(du1, du2);
  EXPECT_NE(du1.GetDbid(), du2.GetDbid());
  EXPECT_NE(du1.GetUuid(), du2.GetUuid());
  EXPECT_NE(id1, id2);
}

TEST_F(BasicDriverUuid_Dbid, Validness) {
  EXPECT_TRUE(du1.IsValid());
  EXPECT_TRUE(du2.IsValid());

  DriverDbidUndscrUuid empty{std::string{""}};
  EXPECT_TRUE(empty.IsEmpty());
  // It is of utmost importance that empty driver id is not valid!
  EXPECT_FALSE(empty.IsValid());

  EXPECT_TRUE(id1.IsValid());
  EXPECT_FALSE(id1.IsEmpty());

  EXPECT_EQ(du1.GetDbidUndscrUuid(), "dbid1_uuid1");
}

TEST_F(BasicDriverUuid_Dbid, Default) {
  DriverIdView id;
  EXPECT_FALSE(id.IsValid());
  EXPECT_TRUE(id.IsEmpty());
}

TEST_F(BasicDriverUuid_Dbid, EmptyDbid) {
  DriverDbidUndscrUuid no_dbid{std::string{"abcde"}};
  EXPECT_EQ(no_dbid.GetUuid().GetUnderlying(), "abcde");
  EXPECT_TRUE(no_dbid.GetDbid().empty());
}

TEST_F(BasicDriverUuid_Dbid, Creation) {
  using namespace std::string_literals;
  DriverDbidUndscrUuid dbid_str{std::string{"abc_def"}};
  DriverDbidUndscrUuid dbid_strv{std::string_view{"abc_def"}};
  EXPECT_EQ(dbid_str, dbid_strv);
}

TEST_F(BasicDriverUuid_Dbid, SerializationCycle) {
  using namespace driver_id::literals;
  DriverDbidUndscrUuid reference{du1};
  // Serialize
  auto json_object = formats::json::ValueBuilder(reference).ExtractValue();

  // Parse
  auto test = json_object.As<DriverDbidUndscrUuid>();

  EXPECT_EQ(reference, test);
}

TEST_F(BasicDriverUuid_Dbid, JsonParse) {
  // as string
  const char* id_as_string = R"json({"data": "dbid1_uuid1"})json";
  const char* id_as_object =
      R"json({"data": { "dbid": "dbid1", "uuid" : "uuid1"}})json";

  auto test_input = [](const auto& input) {
    auto json = formats::json::FromString(input);
    auto object = json["data"].template As<DriverDbidUndscrUuid>();
    EXPECT_EQ(du1, object);
  };

  test_input(id_as_string);
  test_input(id_as_object);
}

TEST_F(BasicDriverUuid_Dbid, JsonParseException) {
  // as string
  const char* invalid1 = R"json({"data": "_uuid1"})json";
  const char* invalid2 = R"json({"data": { "dbid": "dbid1", "uuid" : ""}})json";
  const char* invalid3 = R"json({"data": ""})json";

  auto test_input = [](const auto& input) {
    auto json = formats::json::FromString(input);
    EXPECT_THROW(json["data"].template As<DriverDbidUndscrUuid>(),
                 formats::json::ParseException);
  };

  test_input(invalid1);
  test_input(invalid2);
  test_input(invalid3);
}

TEST_P(VPDriverUuid_Dbid, Validness) {
  const auto du1 = dbid_uuid();
  const auto id1 = id_ref();
  EXPECT_EQ(GetParam().valid, du1.IsValid());
  EXPECT_EQ(id1.IsValid(), du1.IsValid());

  EXPECT_EQ(id1.GetDbid(), du1.GetDbid());
  EXPECT_EQ(id1.GetUuid(), du1.GetUuid());
}

TEST_P(VPDriverUuid_Dbid, Copy) {
  const auto du1 = dbid_uuid();
  const auto id1 = id_ref();
  DriverDbidUndscrUuid du_other{std::string{"wtf_wtf"}};
  DriverDbidUndscrUuid du1_copy{du1};

  EXPECT_EQ(du1, du1);
  EXPECT_EQ(id1, du1);
  EXPECT_EQ(du1, du1_copy);
  EXPECT_EQ(id1, du1_copy);
  EXPECT_NE(du1, du_other);
}

TEST_P(VPDriverUuid_Dbid, Move) {
  const auto du1 = dbid_uuid();
  DriverDbidUndscrUuid du1_copy{du1};

  DriverDbidUndscrUuid du1_mv{std::move(du1_copy)};

  // We guarantee that moved-from object will be empty
  EXPECT_TRUE(du1_copy.IsEmpty());

  EXPECT_EQ(du1, du1_mv);
}

TEST_P(VPDriverUuid_Dbid, Underlying) {
  const auto du1 = dbid_uuid();
  EXPECT_EQ(GetParam().dbid_uuid, du1.GetDbidUndscrUuid());
}

INSTANTIATE_TEST_SUITE_P(
    TestBasic, VPDriverUuid_Dbid,
    ::testing::ValuesIn(std::vector<TestData>{
        // clang-format off
                        // dbid      uuid       dbid_uuid       empty  valid
                        {"dbid"    ,"uuid"    ,"dbid_uuid"     ,false ,true  },
                        {"dbid2"   ,"uuid2"   ,"dbid2_uuid2"   ,false ,true  },
                        {""        ,""        ,""              ,true  ,false },
                        {""        ,"uuid"    ,"uuid"          ,false ,false },
                        // test with and without short string optimization
                        // sso on clang x64 is 22bytes and lower
                        {"d"       ,"u"       ,"d_u"           ,false ,true  },
                        {"veryverylongdbid"
                                   ,"verylonguuid"
                                             ,"veryverylongdbid_verylonguuid"
                                                               ,false ,true  },
                        // some weird variants
                        // dbid      uuid       dbid_uuid       empty  valid
                        {""        ,"u"       ,"_u"            ,false ,false  },
                        {"d"       ,""        ,"d_"            ,false ,false  },
                        {""        ,""        ,"_"             ,true  ,false  },
                        // no short string optimization
                        {""        ,"25charactersminimumshouldbeusedtodisable"
                                              ,"_25charactersminimumshouldbeusedtodisable"
                                                               ,false ,false  },
                        {"25charactersminimumshouldbeusedtodisable"
                                  ,""        ,"25charactersminimumshouldbeusedtodisable_"
                                                               ,false ,false  },
        // clang-format on
    }),
    ::testing::PrintToStringParamName());

}  // namespace driver_id::test
