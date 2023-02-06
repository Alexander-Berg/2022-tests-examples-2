#include <sstream>

#include <gtest/gtest.h>
#include <json/reader.h>
#include <json/value.h>
#include <mongo/mongo.hpp>

#include <clients/stq.hpp>

TEST(StqClient, RequestBody) {
  static const auto& expected_request_body = std::string{R"(
    {
      "task_id": "ololo",
      "args": [{"$oid": "507f1f77bcf86cd799439011"}],
      "kwargs": {
        "a": {"b": "c", "d": {"$date": "2018-12-27T19:38:00.123+0300"}},
        "e": 1
      },
      "eta": "2018-12-01T14:00:01.123456+0000"
    }
  )"};

  const auto& args = BSON_ARRAY(mongo::OID("507f1f77bcf86cd799439011"));
  const auto& kwargs = BSON("a" << BSON("b"
                                        << "c"
                                        << "d" << mongo::Date_t(1545928680123))
                                << "e" << 1);
  const auto& request_body = clients::stq::helpers::StqAgentRequestBody(
      "ololo", args, kwargs, 1543672801.123456);

  Json::Value expected_request_body_json;
  std::istringstream{expected_request_body} >> expected_request_body_json;
  Json::Value request_body_json;
  std::istringstream{request_body} >> request_body_json;

  EXPECT_EQ(request_body_json, expected_request_body_json);
}
