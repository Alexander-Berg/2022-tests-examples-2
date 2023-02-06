#include <gtest/gtest.h>

#include "json_traversal.hpp"

#include <boost/optional.hpp>
#include <utils/helpers/pack.hpp>

using utils::helpers::JsonTraversal;
using utils::helpers::JsonTraversalConst;
using utils::helpers::JsonTraverseError;

enum class SomeEnum { kSome };

namespace serializers {

template <>
const std::vector<std::pair<SomeEnum, std::string>>
    EnumMapper<SomeEnum, std::string>::map = {{SomeEnum::kSome, "some"}};
}

Json::Value GetSampleJson() {
  Json::Value sample(Json::objectValue);
  Json::Value query(Json::objectValue);
  Json::Value sub_query(Json::objectValue);
  Json::Value sub_sub_query(Json::objectValue);
  Json::Value contacts(Json::arrayValue);
  contacts.append("vk");
  contacts.append("instagram");
  contacts.append("github");
  sub_sub_query["contacts"] = std::move(contacts);
  sub_sub_query["birth_date"] = "1994-01-01T10:15:00+0300";
  sub_sub_query["realy_birth_date"] = "1994-01-01";
  sub_query["sub_sub_query"] = std::move(sub_sub_query);
  sub_query["empty_string"] = "";
  sub_query["empty_array"] = Json::Value(Json::arrayValue);
  query["sub_query"] = std::move(sub_query);
  sample["query"] = std::move(query);
  sample["age"] = 24;
  sample["name"] = "Anton Todua";
  sample["null"] = Json::Value{Json::nullValue};
  sample["enum1"] = "some";
  sample["enum2"] = "other";
  Json::Value enum_array1(Json::arrayValue);
  enum_array1.append("some");
  sample["enum_array1"] = enum_array1;
  Json::Value enum_array2(Json::arrayValue);
  enum_array2.append("some");
  enum_array2.append("other");
  sample["enum_array2"] = enum_array2;
  return sample;
}

TEST(JsonTraversalConst, Ok) {
  const auto sample = GetSampleJson();
  const JsonTraversalConst traversal{sample};

  ASSERT_EQ("", traversal.GetPath());
  ASSERT_FALSE(traversal.GetMemberOptional("abc"));

  const auto age = traversal.GetMember("age");
  ASSERT_EQ("age", age.GetPath());
  ASSERT_EQ(24, age.GetInteger());
  ASSERT_EQ(24, age.GetInteger<std::int8_t>());
  ASSERT_EQ(24, age.GetInteger<std::int16_t>());
  ASSERT_EQ(24, age.GetInteger<std::int32_t>());
  ASSERT_EQ(24, age.GetInteger<std::int64_t>());
  ASSERT_EQ(24u, age.GetInteger<std::uint8_t>());
  ASSERT_EQ(24u, age.GetInteger<std::uint16_t>());
  ASSERT_EQ(24u, age.GetInteger<std::uint32_t>());
  ASSERT_EQ(24u, age.GetInteger<std::uint64_t>());

  const auto name = traversal.GetMember("name");
  ASSERT_EQ("name", name.GetPath());
  ASSERT_EQ("Anton Todua", name.GetString(true));
  ASSERT_EQ("Anton Todua", name.GetString(false));
  ASSERT_EQ("Anton Todua", name.GetString(11, 11));

  const auto sub_query = traversal.GetMember("query").GetMember("sub_query");
  ASSERT_EQ("query.sub_query", sub_query.GetPath());
  ASSERT_EQ("", sub_query.GetMember("empty_string").GetString(true));
  ASSERT_EQ("", sub_query.GetMember("empty_string").GetString(0, 0));
  ASSERT_EQ(0u, sub_query.GetMember("empty_array").GetUniqueStrings().size());

  const auto sub_sub_query = sub_query.GetMember("sub_sub_query");
  ASSERT_FALSE(sub_sub_query.GetMemberOptional("xxx"));
  EXPECT_THROW(sub_sub_query.GetMember("realy_birth_date").GetTimePoint(),
               JsonTraverseError);
  ASSERT_EQ(std::chrono::system_clock::from_time_t(757408500),
            sub_sub_query.GetMember("birth_date").GetTimePoint());
  EXPECT_THROW(sub_sub_query.GetMember("birth_date").GetDate(),
               JsonTraverseError);
  ASSERT_EQ(std::chrono::system_clock::from_time_t(757382400),
            sub_sub_query.GetMember("realy_birth_date").GetDate());

  const auto contacts = sub_sub_query.GetMember("contacts");
  ASSERT_EQ("query.sub_query.sub_sub_query.contacts", contacts.GetPath());

  const auto contacts_values = contacts.GetUniqueStrings();
  ASSERT_EQ(3u, contacts_values.size());
  ASSERT_EQ("vk", contacts_values.at(0));
  ASSERT_EQ("instagram", contacts_values.at(1));
  ASSERT_EQ("github", contacts_values.at(2));

  EXPECT_THROW(name.GetString(0, 10), JsonTraverseError);
  EXPECT_THROW(name.GetString(12, 100), JsonTraverseError);

  const auto enum1 = traversal.GetMember("enum1");
  ASSERT_EQ(SomeEnum::kSome, enum1.GetEnum<SomeEnum>());

  const auto enum2 = traversal.GetMember("enum2");
  EXPECT_THROW(enum2.GetEnum<SomeEnum>(), JsonTraverseError);

  const auto enum_array1 = traversal.GetMember("enum_array1");
  ASSERT_EQ(std::vector<SomeEnum>{SomeEnum::kSome},
            enum_array1.GetUniqueEnums<SomeEnum>());

  const auto enum_array2 = traversal.GetMember("enum_array2");
  EXPECT_THROW(enum_array2.GetUniqueEnums<SomeEnum>(), JsonTraverseError);
}

TEST(JsonTraversal, Ok) {
  auto sample = GetSampleJson();
  JsonTraversal traversal{sample};

  ASSERT_FALSE(traversal.GetMemberOptional("abc"));
  EXPECT_THROW(traversal.GetMember("abc"), JsonTraverseError);
  traversal.SetMember("abc").SetMember("def", 13);
  ASSERT_EQ(13, traversal.GetMember("abc").GetMember("def").GetInteger());
  ASSERT_EQ(13u, traversal.GetOrCreateMember("abc")
                     .GetMember("def")
                     .GetInteger<std::uint8_t>());

  auto test = traversal.GetOrCreateMember("test");
  ASSERT_FALSE(test.GetMemberOptional("val"));
  test.SetMember("val", "xxx");
  ASSERT_EQ("xxx", traversal.GetMember("test").GetMember("val").GetString());
  EXPECT_THROW(test.GetMember("val").SetMember("any_key"), JsonTraverseError);
  EXPECT_THROW(test.GetMember("val").GetMember("no_key"), JsonTraverseError);

  auto removed = traversal.RemoveMember("abc");
  ASSERT_TRUE(removed);
  ASSERT_FALSE(traversal.GetMemberOptional("abc"));
  JsonTraversal abc{*removed};
  ASSERT_EQ(13, abc.GetMember("def").GetInteger());

  traversal.SetMember("integer_member", Json::Int64{3111000111});
  const auto& integer_member = traversal.GetMember("integer_member");
  EXPECT_THROW(integer_member.GetInteger<std::int8_t>(), JsonTraverseError);
  EXPECT_THROW(integer_member.GetInteger<std::int16_t>(), JsonTraverseError);
  EXPECT_THROW(integer_member.GetInteger<std::int32_t>(), JsonTraverseError);
  EXPECT_THROW(integer_member.GetInteger<std::uint8_t>(), JsonTraverseError);
  EXPECT_THROW(integer_member.GetInteger<std::uint16_t>(), JsonTraverseError);
  ASSERT_EQ(3111000111, integer_member.GetInteger<std::int64_t>());
  ASSERT_EQ(3111000111u, integer_member.GetInteger<std::uint32_t>());
  ASSERT_EQ(3111000111u, integer_member.GetInteger<std::uint64_t>());

  traversal.SetMember("negative_integer", -657);
  const auto& negative_integer = traversal.GetMember("negative_integer");
  EXPECT_THROW(negative_integer.GetInteger<std::uint8_t>(), JsonTraverseError);
  EXPECT_THROW(negative_integer.GetInteger<std::uint16_t>(), JsonTraverseError);
  EXPECT_THROW(negative_integer.GetInteger<std::uint32_t>(), JsonTraverseError);
  EXPECT_THROW(negative_integer.GetInteger<std::uint64_t>(), JsonTraverseError);
  EXPECT_THROW(negative_integer.GetInteger<std::int8_t>(), JsonTraverseError);
  ASSERT_EQ(-657, negative_integer.GetInteger<std::int16_t>());
  ASSERT_EQ(-657, negative_integer.GetInteger<std::int32_t>());
  ASSERT_EQ(-657, negative_integer.GetInteger<std::int64_t>());

  {
    const std::vector<std::uint32_t> source{1, 2, 3, 4};
    traversal.SetMember("unique_integers",
                        utils::helpers::PackToJson<std::uint32_t>(source));
    const auto& result = traversal.GetMember("unique_integers")
                             .GetUniqueIntegers<std::uint32_t>();
    EXPECT_EQ(source, result);
  }
  {
    const std::vector<std::uint32_t> source{1, 2, 2, 4};
    traversal.SetMember("non_unique_integers",
                        utils::helpers::PackToJson<std::uint32_t>(source));
    EXPECT_THROW(traversal.GetMember("non_unique_integers")
                     .GetUniqueIntegers<std::uint32_t>(),
                 JsonTraverseError);
  }
}

TEST(JsonTraversal, TreatNullIsAbsent) {
  auto sample = GetSampleJson();
  JsonTraversal traversal{sample};

  ASSERT_EQ(boost::none, traversal.GetMemberOptional("null"));
}

TEST(JsonTraversal, Utf8) {
  Json::Value sample(Json::objectValue);

  std::string str;
  str = static_cast<char>(0xf1);
  sample["test"] = str;
  auto json = JsonTraversal{sample};

  EXPECT_THROW(json.GetMember("test").GetString(false), JsonTraverseError);

  sample["test"] = "привет";
  json = JsonTraversal{sample};

  EXPECT_THROW(json.GetMember("test").GetString(1, 5), JsonTraverseError);
  ASSERT_EQ(json.GetMember("test").GetString(1, 6), "привет");
}

TEST(JsonTraversal, GetString) {
  Json::Value sample(Json::objectValue);
  static const std::vector<std::string> kWrongSamples = {
      "\ufeff5555", "55\ufeff55", "5555\ufeff", "\ufeff", "5\ufeff5555",
  };

  static const std::vector<std::string> kValidSamples = {
      "Привет", "Иван", "Pavel", "94454867", "Moscow",
  };

  for (const auto& str : kWrongSamples) {
    sample["test"] = str;
    auto json = JsonTraversal{sample};
    EXPECT_THROW(json.GetMember("test").GetString(), JsonTraverseError);
  }

  for (const auto& str : kValidSamples) {
    sample["test"] = str;
    auto json = JsonTraversal{sample};
    ASSERT_EQ(json.GetMember("test").GetString(), str);
  }
}

TEST(JsonTraversalConst, GetDate) {
  using Case = std::pair<std::string, boost::optional<std::string>>;
  static const std::vector<Case> kCases{
      {"0216-03-28", boost::none},
      {"1699-12-31", boost::none},
      {"1700-00-01", boost::none},
      {"1700-01-01", std::string{"1700-01-01T00:00:00+0000"}},
      {"1700-01-01T00:00:00+0000", boost::none},
      {"2000-13-13", boost::none},
      {"2000-03-28", std::string{"2000-03-28T00:00:00+0000"}},
      {"2199-12-31", std::string{"2199-12-31T00:00:00+0000"}},
      {"2200-01-01", boost::none},
      {"2931-03-28", boost::none},
  };

  for (const auto& [src, dst] : kCases) {
    const Json::Value value{src};
    const JsonTraversalConst traversal{value};

    if (dst) {
      EXPECT_EQ(utils::datetime::Timestring(traversal.GetDate()), *dst);
    } else {
      EXPECT_THROW(traversal.GetDate(), JsonTraverseError);
    }
  }
}

TEST(JsonTraversalConst, GetTimePoint) {
  using Case = std::pair<std::string, boost::optional<std::string>>;
  static const std::vector<Case> kCases{
      {"0216-03-28T10:15:00+0300", boost::none},
      {"1699-12-31T10:15:00+0300", boost::none},
      {"1700-00-01T10:15:00+0300", boost::none},
      {"1700-01-01T10:15:00+0300", std::string{"1700-01-01T07:15:00+0000"}},
      {"1700-01-01", boost::none},
      {"2000-13-13T10:15:00+0300", boost::none},
      {"1999-08-21T25:13:13+0300", boost::none},
      {"1999-09-04T99:99:99-0300", boost::none},
      {"2000-03-28T14:58:33-0130", std::string{"2000-03-28T16:28:33+0000"}},
      {"2199-12-31T00:00:00+0000", std::string{"2199-12-31T00:00:00+0000"}},
      {"2200-01-01T10:15:00+0300", boost::none},
      {"2931-03-28T10:15:00+0300", boost::none},
  };

  for (const auto& [src, dst] : kCases) {
    const Json::Value value{src};
    const JsonTraversalConst traversal{value};

    if (dst) {
      EXPECT_EQ(utils::datetime::Timestring(traversal.GetTimePoint()), *dst);
    } else {
      EXPECT_THROW(traversal.GetTimePoint(), JsonTraverseError);
    }
  }
}
