#include <models/pa_auth_context.hpp>

#include <userver/server/handlers/exceptions.hpp>

#include <userver/utest/utest.hpp>

using namespace passenger_authorizer::models;

namespace {

const std::string kKey1 = "key1";
const std::string kValue1 = "value1";
const std::string kKey2 = "key2";
const std::string kValue2 = "value2";

struct TestData {
  std::string key;
  std::string value;
  std::string serialized;
};

const std::vector<TestData> kTestData = {
    {"key", "value", "key=value"},
    {"key", "val,ue", "\"key=val,ue\""},
    {"key", ",value", "\"key=,value\""},
    {"key", "value,", "\"key=value,\""},
    {"k,ey", "value", "\"k,ey=value\""},
    {",key", "value", "\",key=value\""},
    {"key,", "value", "\"key,=value\""},
    {"key", " value", "key= value"},
    {"key", "value ", "\"key=value \""},
    {" key", "value", "\" key=value\""},
    {"key ", "value", "key =value"},
    {"k\"ey", "value", "\"k\"\"ey=value\""},
    {"key", "value\"", "\"key=value\"\"\""},
    {"key", "\"", "\"key=\"\"\""},
    {"\"", ",\",", "\"\"\"=,\"\",\""},
};

}  // namespace

TEST(UserApplicationInfo, Serialize) {
  ua_parser::AppVars app_vars;
  app_vars.SetVar(kKey1, kValue1);
  app_vars.SetVar(kKey2, kValue2);
  auto serialized = SerializeUserApplicationInfo(app_vars);
  EXPECT_TRUE(serialized == "key1=value1,key2=value2" ||
              serialized == "key2=value2,key1=value1")
      << serialized;
}

TEST(UserApplicationInfo, SerializeEscape) {
  for (const auto& test_data : kTestData) {
    ua_parser::AppVars app_vars;
    app_vars.SetVar(test_data.key, test_data.value);
    auto serialized = SerializeUserApplicationInfo(app_vars);
    EXPECT_EQ(serialized, test_data.serialized);
  }
}

TEST(UserApplicationInfo, Parse) {
  for (const auto& str : {
           "key1=value1,key2=value2",
           "\"key1=value1\",\"key2=value2\"",
           "   key1=value1  ,   key2=value2   ",
           "  key2=value2  ,   key1=value1  ",
           "   \"key1=value1\",   key2=value2   ",
           "   \"key1=value1\"  ,   key2=value2   ",
           "   key1=value1  ,   \"key2=value2\"   ",
           "  \"key2=value2\"  ,   \"key1=value1\"  ",
           ", ,,  ,key1=value1,  ,   , key2=value2,,, , ,",
           " ,,, , ,, \"key2=value2\"   , ,, ,,   \"key1=value1\" ,, ,, ,  ",
       }) {
    EXPECT_NO_THROW(auto app_vars = ParseUserApplicationInfo(str); EXPECT_EQ(
                        std::distance(app_vars.begin(), app_vars.end()), 2);
                    EXPECT_EQ(app_vars.GetVar(kKey1), kValue1);
                    EXPECT_EQ(app_vars.GetVar(kKey2), kValue2);)
        << str;
  }
}

TEST(UserApplicationInfo, ParseEscape) {
  for (const auto& test_data : kTestData) {
    auto app_vars = ParseUserApplicationInfo(test_data.serialized);
    EXPECT_EQ(std::distance(app_vars.begin(), app_vars.end()), 1);
    EXPECT_EQ(app_vars.GetVar(test_data.key), test_data.value);
  }
}

TEST(UserApplicationInfo, ParseInvalid) {
  EXPECT_THROW(ParseUserApplicationInfo("key"), server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key=value,key2,key3=value"),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key=\"value\""),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("\"key\"=value"),
               server::handlers::ClientError);
  EXPECT_NO_THROW(ParseUserApplicationInfo("\"key=value,key2\",key3=value"));
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,key2=\"val\"ue2,\""),
               server::handlers::ClientError);
  EXPECT_THROW(
      ParseUserApplicationInfo("key1=value1,key2=\"val,ue2,key3=value3"),
      server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1\""),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2"),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2\"\""),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2\"\","),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2\"\",\"\""),
               server::handlers::ClientError);
  EXPECT_NO_THROW(
      ParseUserApplicationInfo("key1=value1,\"key2=value2\"\",\"\"\""));
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2\"\" "),
               server::handlers::ClientError);
  EXPECT_THROW(ParseUserApplicationInfo("key1=value1,\"key2=value2\"\"\"\" ,"),
               server::handlers::ClientError);
}

TEST(UserApplicationInfo, SerializeAndParse) {
  ua_parser::AppVars app_vars;
  const std::map<std::string, std::string> kKeyValues = {
      {"key1", "value"},
      {"key2", "valu,e"},
      {"key3", "va\"\"lu,e"},
      {"k\"\"ey4", "va\"\"lu,e"},
      {"k\"\"ey5,,,", ",,,,va\"\"lu,e"},
      {"key6", ","},
      {",", "\""},
      {"\"", ","},
      {"\"\"", "value"},
      {",,", "\",\""},
      {" ,,", "\",\""},
      {" ,, ", " \",\"  "},
      {" ", " "},
      {"\" \"", ""},
      {"", ""},
  };
  for (const auto& [key, value] : kKeyValues) {
    app_vars.SetVar(key, value);
  }
  auto parsed =
      ParseUserApplicationInfo(SerializeUserApplicationInfo(app_vars));
  EXPECT_EQ(std::distance(parsed.begin(), parsed.end()), kKeyValues.size());
  for (const auto& [key, value] : kKeyValues) {
    EXPECT_EQ(parsed.GetVar(key), value);
  }
}
