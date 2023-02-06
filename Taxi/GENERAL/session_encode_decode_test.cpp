#include "session_encode_decode.hpp"
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>
#include "session.hpp"

namespace eater_authorizer::models {
TEST(Session, SessionDecodeUserWithOffer) {
  std::string input =
      "_sf2_attributes|a:2:{s:5:\"offer\";s:130:\"{\"till\":\"2020-03-10T16:11:"
      "19+03:00\",\"since\":\"2020-03-10T16:01:19+03:00\",\"counter\":0,"
      "\"location\":{\"lat\":55.823879,\"long\":37.497216}}\";s:13:\"_security_"
      "api\";s:144:\"C:36:\"Eda\\Eater\\Common\\Security\\EaterToken\":95:{a:1:"
      "{i:0;C:15:\"App\\Entity\\User\":57:{a:2:{i:0;i:62888001;i:1;s:24:\"+"
      "79876543210@example.com\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:1583845279;"
      "s:1:\"c\";i:1582975478;s:1:\"l\";s:7:\"2592000\";}";
  std::string input_switch_args =
      "_sf2_meta|a:3:{s:1:\"u\";i:1583845279;s:1:\"c\";i:1582975478;s:1:\"l\";"
      "s:7:\"2592000\";}_sf2_attributes|a:2:{s:5:\"offer\";s:130:\"{\"till\":"
      "\"2020-03-10T16:11:19+03:00\",\"since\":\"2020-03-10T16:01:19+03:00\","
      "\"counter\":0,\"location\":{\"lat\":55.823879,\"long\":37.497216}}\";s:"
      "13:\"_security_api\";s:144:\"C:36:"
      "\"Eda\\Eater\\Common\\Security\\EaterToken\":95:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":57:{a:2:{i:0;i:62888001;i:1;s:24:\"+79876543210@"
      "example.com\";}}}}\";}";
  std::string input_switch_attrs =
      "_sf2_meta|a:3:{s:1:\"u\";i:1583845279;s:1:\"c\";i:1582975478;s:1:\"l\";"
      "s:7:\"2592000\";}_sf2_attributes|a:2:{s:13:\"_security_api\";s:144:\"C:"
      "36:\"Eda\\Eater\\Common\\Security\\EaterToken\":95:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":57:{a:2:{i:0;i:62888001;i:1;s:24:\"+79876543210@"
      "example.com\";}}}}\";s:5:\"offer\";s:130:\"{\"till\":\"2020-03-10T16:11:"
      "19+03:00\",\"since\":\"2020-03-10T16:01:19+03:00\",\"counter\":0,"
      "\"location\":{\"lat\":55.823879,\"long\":37.497216}}\";}";
  std::string output =
      "_sf2_attributes|a:1:{s:13:\"_security_api\";s:144:"
      "\"C:36:\"Eda\\Eater\\Common\\Security\\EaterToken\":95:{a:1:"
      "{i:0;C:15:\"App\\Entity\\User\":57:{a:2:{i:0;i:62888001;i:1;s:24:\"+"
      "79876543210@example.com\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:1583845279;"
      "s:1:\"c\";i:1582975478;s:1:\"l\";s:7:\"2592000\";}";

  Session session = encode::DecodeSessionPhp(input);
  std::string result = encode::EncodeSessionPhp(session);

  Session session_switch_args = encode::DecodeSessionPhp(input_switch_args);
  std::string result_switch_args =
      encode::EncodeSessionPhp(session_switch_args);

  Session session_switch_attrs = encode::DecodeSessionPhp(input_switch_attrs);
  std::string result_switch_attrs =
      encode::EncodeSessionPhp(session_switch_attrs);

  EXPECT_EQ(output, result);
  EXPECT_EQ(output, result_switch_args);
  EXPECT_EQ(output, result_switch_attrs);
}

TEST(Session, SessionDecodeAnonWithOffer) {
  std::string input =
      "_sf2_attributes|a:1:{s:5:\"offer\";s:130:\"{\"till\":\"2020-03-12T19:47:"
      "10+03:00\",\"since\":\"2020-03-12T19:37:10+03:00\",\"counter\":0,"
      "\"location\":{\"lat\":55.823879,\"long\":37.497216}}\";}_sf2_meta|a:3:{"
      "s:1:\"u\";i:1584031032;s:1:\"c\";i:1584031032;s:1:\"l\";s:7:\"2592000\";"
      "}";
  std::string output =
      "_sf2_attributes|a:0:{}_symfony_flashes|a:0:{}_sf2_meta|a:3:{"
      "s:1:\"u\";i:1584031032;s:1:\"c\";i:1584031032;s:1:\"l\";s:7:\"2592000\";"
      "}";

  Session session = encode::DecodeSessionPhp(input);
  std::string result = encode::EncodeSessionPhp(session);

  EXPECT_EQ(output, result);
}

TEST(Session, SessionDecodeOldFlashes) {
  std::string input =
      "_sf2_attributes|a:1:{s:5:\"offer\";s:130:\"{\"till\":\"2020-03-12T19:47:"
      "10+03:00\",\"since\":\"2020-03-12T19:37:10+03:00\",\"counter\":0,"
      "\"location\":{\"lat\":55.823879,\"long\":37.497216}}\";}_sf2_flashes|a:"
      "0:{}_sf2_meta|a:3:{"
      "s:1:\"u\";i:1584031032;s:1:\"c\";i:1584031032;s:1:\"l\";s:7:\"2592000\";"
      "}";
  std::string output =
      "_sf2_attributes|a:0:{}_symfony_flashes|a:0:{}_sf2_meta|a:3:{"
      "s:1:\"u\";i:1584031032;s:1:\"c\";i:1584031032;s:1:\"l\";s:7:\"2592000\";"
      "}";

  Session session = encode::DecodeSessionPhp(input);
  std::string result = encode::EncodeSessionPhp(session);

  EXPECT_EQ(output, result);
}

TEST(Session, SessionDecodeAnon) {
  std::string input =
      "_sf2_attributes|a:0:{}_symfony_flashes|a:0:{}_sf2_meta|a:3:{s:1:\"u\";i:"
      "1583179216;s:1:\"c\";i:1583179216;s:1:\"l\";s:7:\"2592000\";}";
  Session session = encode::DecodeSessionPhp(input);
  std::string result = encode::EncodeSessionPhp(session);

  EXPECT_EQ(input, result);
}

TEST(Session, SessionDecodeUser) {
  std::string input =
      "_sf2_attributes|a:1:{s:13:\"_security_api\";s:144:\"C:36:"
      "\"Eda\\Eater\\Common\\Security\\EaterToken\":95:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":57:{a:2:{i:0;i:72620066;i:1;s:24:\"+79111111111@"
      "example.com\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:1584099689;s:1:\"c\";i:"
      "1584099689;s:1:\"l\";s:7:\"2592000\";}";
  Session session = encode::DecodeSessionPhp(input);
  std::string result = encode::EncodeSessionPhp(session);
  EXPECT_EQ(input, result);

  std::string input2 =
      "_sf2_attributes|a:1:{s:13:\"_security_api\";s:145:\"C:36:"
      "\"Eda\\Eater\\Common\\Security\\EaterToken\":96:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":58:{a:2:{i:0;i:72620066;i:1;s:25:\"+792222222222@"
      "example.com\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:1584099689;s:1:\"c\";i:"
      "1584099689;s:1:\"l\";s:7:\"2592000\";}";
  Session session2 = encode::DecodeSessionPhp(input2);
  std::string result2 = encode::EncodeSessionPhp(session2);
  EXPECT_EQ(input2, result2);

  std::string input3 =
      "_sf2_attributes|a:1:{s:13:\"_security_api\";s:147:\"C:36:"
      "\"Eda\\Eater\\Common\\Security\\EaterToken\":98:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":60:{a:2:{i:0;i:6535257;i:1;s:28:\"iva."
      "petrovitch2014@yandex.ru\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:"
      "1592561358;s:1:\"c\";i:1555242215;s:1:\"l\";s:7:\"2592000\";}";
  Session session3 = encode::DecodeSessionPhp(input3);
  std::string result3 = encode::EncodeSessionPhp(session3);
  EXPECT_EQ(input3, result3);

  std::string input4 =
      "_sf2_attributes|a:1:{s:13:\"_security_api\";s:136:\"C:36:"
      "\"Eda\\Eater\\Common\\Security\\EaterToken\":87:{a:1:{i:0;C:15:"
      "\"App\\Entity\\User\":49:{a:2:{i:0;i:72620066;i:1;s:16:\"+792@"
      "example.com\";}}}}\";}_sf2_meta|a:3:{s:1:\"u\";i:1584099689;s:1:\"c\";i:"
      "1584099689;s:1:\"l\";s:7:\"2592000\";}";
  Session session4 = encode::DecodeSessionPhp(input4);
  std::string result4 = encode::EncodeSessionPhp(session4);
  EXPECT_EQ(input4, result4);
}

typedef std::tuple<Session, std::string> SessionJsonType;
class SessionJson : public testing::TestWithParam<SessionJsonType> {
 protected:
  void ToJsonTest(const Session& session, const std::string& expected) {
    std::string result = formats::json::ToString(encode::ToJson(session));
    ASSERT_EQ(expected, result);
  }

  void FromJsonTest(const std::string& session_data, const Session& expected) {
    Session session = encode::FromJson(formats::json::FromString(session_data));
    ASSERT_EQ(expected, session);
  }
};

TEST_P(SessionJson, ToJson) {
  Session session(std::get<0>(GetParam()));
  std::string expected(std::get<1>(GetParam()));

  ToJsonTest(session, expected);
}

TEST_P(SessionJson, FromJson) {
  std::string session_data(std::get<1>(GetParam()));
  Session expected(std::get<0>(GetParam()));

  FromJsonTest(session_data, expected);
}

namespace {
SessionMetadata meta{0, 0, 0};
Eater eater{1, "iam"};
Partner partner{2};
}  //  namespace

INSTANTIATE_TEST_SUITE_P(
    Suite, SessionJson,
    testing::Values(
        SessionJsonType({meta, {}},
                        "{\"m\":{\"c\":0,\"u\":0,\"t\":0},\"a\":null}"),
        SessionJsonType({meta, {eater, {}}},
                        "{\"m\":{\"c\":0,\"u\":0,\"t\":0},\"a\":{\"e\":{\"i\":"
                        "1,\"u\":\"iam\"}}}"),
        SessionJsonType({meta, {{}, partner}},
                        "{\"m\":{\"c\":0,\"u\":0,\"t\":0},\"a\":{\"p\":2}}")));
}  // namespace eater_authorizer::models
