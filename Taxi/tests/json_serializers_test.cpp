#include <gtest/gtest.h>

#include <utils/json_serializers.hpp>

TEST(JsonSerializers, BasicTypes) {
  Json::Value json;

  std::string s = "stroka";
  std::string s2;
  serializers::Serialize(s, &json);
  EXPECT_STREQ("stroka", json.asString().c_str());
  serializers::Deserialize(json, &s2);
  EXPECT_EQ(s2, s);

  unsigned n = 273;
  unsigned n2 = 0;
  serializers::Serialize(n, &json);
  EXPECT_EQ(273u, json.asUInt());
  serializers::Deserialize(json, &n2);
  EXPECT_EQ(n2, n);
}

TEST(JsonSerializers, LongInts) {
  const unsigned long umax = std::numeric_limits<unsigned>::max();
  {
    Json::Value json;
    serializers::Serialize(umax - 1, &json);
    EXPECT_EQ(static_cast<unsigned>(umax - 1), json.asUInt());  // not 64
  }

  for (unsigned long val : {umax - 1, umax + 1}) {
    Json::Value json;
    serializers::Serialize(val, &json);
    EXPECT_EQ(val, json.asUInt64());
  }

  const long smax = std::numeric_limits<int>::max();
  const long smin = std::numeric_limits<int>::min();

  {
    Json::Value json;
    serializers::Serialize(smax - 1, &json);
    EXPECT_EQ(static_cast<int>(smax - 1), json.asInt());  // not 64

    serializers::Serialize(smin + 1, &json);
    EXPECT_EQ(static_cast<int>(smin + 1), json.asInt());  // not 64
  }

  for (long val : {smax - 1, smax + 1, smin + 1, smin - 1}) {
    Json::Value json;
    serializers::Serialize(val, &json);
    EXPECT_EQ(val, json.asInt64());
  }
}

TEST(JsonSerializers, Arrays) {
  // std::vector<T> is converted to json array and vice versa
  std::vector<unsigned> a, a2;
  Json::Value json;

  a = {1, 2, 3, 4, 5};
  serializers::Serialize(a, &json);
  for (Json::Value::ArrayIndex i = 0; i < a.size(); ++i)
    EXPECT_EQ(a.at(i), json[i].asUInt());
  serializers::Deserialize(json, &a2);
  EXPECT_EQ(a2, a);

  // You can also deserialize a string:
  auto as = serializers::Deserialize<std::vector<std::string>>(
      R"(["How", "do", "you", "do?"])");
  EXPECT_EQ(as, std::vector<std::string>({"How", "do", "you", "do?"}));
  // and serialize to string
  std::string str =
      serializers::Serialize(std::vector<std::string>({"Peachy!"}));
  // str: "[\"Peachy!\"]\n"
  EXPECT_TRUE(serializers::Deserialize<std::vector<std::string>>(str).at(0) ==
              "Peachy!");
}

// For custom types you need to define specialization of ConverterImpl
// somewhere and link with it
struct WeirdCustomType {
  unsigned id = 0;
};
namespace serializers {
template <>
struct ConverterImpl<WeirdCustomType> {
  static void ToJson(const WeirdCustomType& obj, Json::Value* json) {
    *json = Json::arrayValue;
    json->append(obj.id);
  }
  static void FromJson(const Json::Value& json, WeirdCustomType* obj) {
    if (!json.isArray() || json.size() != 1 || !json[0].isUInt())
      throw SerializeError("It's not a weird type");
    obj->id = json[0].asUInt();
  }
};
}  // namespace serializers
TEST(JsonSerializers, CustomType) {
  Json::Value json;
  WeirdCustomType t, t2;
  t.id = 24;
  serializers::Serialize(t, &json);
  serializers::Deserialize(json, &t2);
  EXPECT_EQ(t.id, t2.id);
  EXPECT_EQ(1u, serializers::Deserialize<WeirdCustomType>("[1]").id);
}

// Enums are fine too
enum class Doge { Wow, SoTempleit, MuchSfinai };
namespace serializers {
template <>
struct ConverterImpl<Doge> : EnumMapper<Doge, std::string> {};
template <>
const std::vector<std::pair<Doge, std::string>>
    EnumMapper<Doge, std::string>::map = {{Doge::Wow, "wow"},
                                          {Doge::SoTempleit, "so templeit"},
                                          {Doge::MuchSfinai, "much sfinai"}};
}  // namespace serializers
TEST(JsonSerializers, Enums) {
  Doge d = Doge::Wow;
  Doge d2 = Doge::Wow;
  Json::Value json;

  d = Doge ::SoTempleit;
  serializers::Serialize(d, &json);
  EXPECT_STREQ("so templeit", json.asCString());
  serializers::Deserialize(json, &d2);
  EXPECT_EQ(Doge::SoTempleit, d2);
}

// For structs it is possible to define a mapping:
// json field name <-> pointer to struct member.
// Mapped structs are converted to json objects
struct S {
  // This is required to treat this struct as mapped
  typedef void tag_mapped;

  std::string s;
  unsigned n;
  // missing optionals are not (de-)serialized
  boost::optional<std::string> opt;
  boost::optional<std::string> opt2;
};
namespace serializers {
template <>
const Mapping<S> MappedConverter<S>::mapping = {
    Map("s", &S::s), Map("n", &S::n), Map("opt", &S::opt),
    Map("opt2", &S::opt2)};
}  // namespace serializers
TEST(JsonSerializers, MappedStructs) {
  S s = {"str", 12, std::string("present"), boost::none};
  Json::Value json;
  serializers::Serialize(s, &json);
  EXPECT_STREQ("str", json["s"].asCString());
  EXPECT_EQ(12u, json["n"].asUInt());
  EXPECT_STREQ("present", json["opt"].asCString());
  EXPECT_FALSE(json.isMember("opt2"));
  S s2 = serializers::Deserialize<S>(
      R"({"s": "str", "n": 15, "opt2": "not missing"})");
  EXPECT_STREQ("str", s2.s.c_str());
  EXPECT_EQ(15u, s2.n);
  EXPECT_TRUE(s2.opt2.is_initialized() && *s2.opt2 == "not missing");
  EXPECT_FALSE(s2.opt.is_initialized());
}

// Complex nested structs are also possible
struct Nested {
  typedef void tag_mapped;

  bool ok;
  S s;
  std::vector<std::vector<Doge>> doges;
  std::map<int, int> mop;
};
namespace serializers {
template <>
const Mapping<Nested> MappedConverter<Nested>::mapping = {
    Map("ok", &Nested::ok), Map("s", &Nested::s), Map("doges", &Nested::doges),
    Map(SerializerFunc<Nested>([](const Nested& obj, Json::Value* json) {
          (*json)["mop"] = (obj.mop.count(100)) ? 1 : 0;
        }),
        DeserializerFunc<Nested>([](const Json::Value&, Nested* obj) {
          obj->mop.clear();
          obj->mop[0] = 0;
        }))};
}  // namespace serializers

TEST(JsonSerializers, NestedComplex) {
  Nested n = {true,
              {"str", 100, boost::none, boost::none},
              {{Doge::Wow, Doge::SoTempleit}, {Doge::MuchSfinai, Doge::Wow}},
              {}};
  Json::Value json;
  serializers::Serialize(n, &json);
  EXPECT_EQ(true, json["ok"].asBool());
  EXPECT_STREQ(n.s.s.c_str(), json["s"]["s"].asCString());
  EXPECT_STREQ("wow", json["doges"][1][1].asCString());
  Nested n2 = serializers::Deserialize<Nested>(
      R"({"ok":false,"s":{"s":"!","n":9001},"doges":[],"mop":"who cares?"})");
  EXPECT_FALSE(n2.ok);
  EXPECT_EQ(9001u, n2.s.n);
  EXPECT_TRUE(n2.doges.empty());
  EXPECT_TRUE(n2.mop.at(0) == 0);
}

namespace {

struct A {
  typedef void tag_mapped;  // enable serialization

  bool x;
  double q;
};

struct B : public A {
  typedef A tag_mapped;  // enable serialization

  unsigned int y;
};

struct C : public B {
  typedef B tag_mapped;  // enable serialization

  std::string z;
};

}  // namespace

namespace serializers {

template <>
const Mapping<A> MappedConverter<A>::mapping = {
    //
    Map("x", &A::x),  //
    Map("q", &A::q),  //
};

template <>
const Mapping<B> MappedConverter<B>::mapping = {
    //
    Map("y", &B::y),  //
};

template <>
const Mapping<C> MappedConverter<C>::mapping = {
    //
    Map("z", &C::z),  //
};

}  // namespace serializers

TEST(JsonSerializers, Inheritance) {
  C c;
  c.x = false;
  c.q = 2019.02;
  c.y = 17;
  c.z = "anton";

  Json::Value json;
  serializers::Serialize(c, &json);
  EXPECT_EQ(c.x, json["x"].asBool());
  EXPECT_EQ(c.q, json["q"].asDouble());
  EXPECT_EQ(c.y, json["y"].asUInt());
  EXPECT_STREQ(c.z.c_str(), json["z"].asCString());

  C cc;
  serializers::Deserialize<C>(json, &cc);
  EXPECT_EQ(c.x, cc.x);
  EXPECT_EQ(c.q, cc.q);
  EXPECT_EQ(c.y, cc.y);
  EXPECT_STREQ(c.z.c_str(), cc.z.c_str());
}
