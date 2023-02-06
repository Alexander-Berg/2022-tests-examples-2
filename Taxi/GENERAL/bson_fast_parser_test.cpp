#include "bson_fast_parser.hpp"

#include <gtest/gtest.h>

struct Data {
  std::string str;
  int num;
  bool flag;

  struct Sub {
    std::string str;
  } sub;
};

const auto& DataSubParser = utils::bson_fast::ParserBuilder<Data::Sub>()
                                .Push("str", &Data::Sub::str)
                                .Done();

const auto& DataSubDefParser = utils::bson_fast::ParserBuilder<Data::Sub>()
                                   .PushDef("str", &Data::Sub::str, "World")
                                   .Done();

const auto& DataOptDefParser = utils::bson_fast::ParserBuilder<Data::Sub>()
                                   .PushOpt("str", &Data::Sub::str)
                                   .Done();

const auto& DataParser = utils::bson_fast::ParserBuilder<Data>()
                             .Push("str", &Data::str)
                             .Push("num", &Data::num)
                             .Push("flag", &Data::flag)
                             .Push("sub", &Data::sub, DataSubParser)
                             .Done();

const auto& DataDefParser = utils::bson_fast::ParserBuilder<Data>()
                                .PushDef("str", &Data::str, "Hello")
                                .PushDef("num", &Data::num, 1)
                                .PushDef("flag", &Data::flag, true)
                                .Push("sub", &Data::sub, DataSubDefParser)
                                .Done();

const auto& DataOptParser = utils::bson_fast::ParserBuilder<Data>()
                                .PushOpt("str", &Data::str)
                                .PushOpt("num", &Data::num)
                                .PushOpt("flag", &Data::flag)
                                .Push("sub", &Data::sub, DataOptDefParser)
                                .Done();

TEST(BsonFastParser, Strong) {
  ::mongo::BSONObjBuilder builder;
  builder.append("str", "Hello");
  builder.append("num", 1);
  builder.append("flag", true);
  ::mongo::BSONObjBuilder sub_builder(builder.subobjStart("sub"));
  sub_builder.append("str", "World");
  sub_builder.done();

  Data data;
  ASSERT_NO_THROW(DataParser.Parse(builder.obj(), data));

  EXPECT_STREQ("Hello", data.str.c_str());
  EXPECT_EQ(1, data.num);
  EXPECT_TRUE(data.flag);
  EXPECT_STREQ("World", data.sub.str.c_str());
}

TEST(BsonFastParser, StrongThrow) {
  ::mongo::BSONObjBuilder builder;
  ::mongo::BSONObjBuilder sub_builder(builder.subobjStart("sub"));
  sub_builder.done();

  Data data;
  EXPECT_THROW(DataParser.Parse(builder.obj(), data),
               utils::bson_fast::ParseException);
}

TEST(BsonFastParser, Def) {
  ::mongo::BSONObjBuilder builder;
  ::mongo::BSONObjBuilder sub_builder(builder.subobjStart("sub"));
  sub_builder.done();

  Data data;
  ASSERT_NO_THROW(DataDefParser.Parse(builder.obj(), data));

  EXPECT_STREQ("Hello", data.str.c_str());
  EXPECT_EQ(1, data.num);
  EXPECT_TRUE(data.flag);
  EXPECT_STREQ("World", data.sub.str.c_str());
}

TEST(BsonFastParser, Opt) {
  ::mongo::BSONObjBuilder builder;
  ::mongo::BSONObjBuilder sub_builder(builder.subobjStart("sub"));
  sub_builder.done();

  Data data{"Hello", 1, true, {"World"}};
  ASSERT_NO_THROW(DataOptParser.Parse(builder.obj(), data));

  EXPECT_STREQ("Hello", data.str.c_str());
  EXPECT_EQ(1, data.num);
  EXPECT_TRUE(data.flag);
  EXPECT_STREQ("World", data.sub.str.c_str());
}
