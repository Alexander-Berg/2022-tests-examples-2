#include <gtest/gtest.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>

#include <access-control-info/exceptions.hpp>
#include <access-control-info/models/parsed_http_request.hpp>
#include <access-control-info/models/user_access_info.hpp>

#include <clients/access-control/definitions.hpp>

namespace {
const std::string restriction_str = R"=(
{
  "init": {
    "predicates": [
      {
        "init": {
          "arg_name": "body:sample_field.subfield",
          "set": [
            "value1",
            "value2"
          ],
          "set_elem_type": "string"
        },
        "type": "in_set"
      },
      {
        "init": {
          "arg_name": "query:sample_double_value",
          "arg_type": "double",
          "value": 5.6
        },
        "type": "lt"
      },
      {
        "init": {
          "arg_name": "headers:X-Test-String",
          "set": [
            "test-header",
            "test-header-2"
          ],
          "set_elem_type": "string"
        },
        "type": "in_set"
      }
    ]
  },
  "type": "all_of"
}
)=";

const std::string restriction_only_query_str = R"=(
{
  "init": {
    "predicates": [
      {
        "init": {
          "arg_name": "query:sample_double_value",
          "arg_type": "double",
          "value": 5.6
        },
        "type": "lt"
      }
    ]
  },
  "type": "all_of"
}
)=";

const std::string restriction_only_body_str = R"=(
{
  "init": {
    "predicates": [
      {
        "init": {
          "arg_name": "body:sample_field.subfield",
          "set": [
            "value1",
            "value2"
          ],
          "set_elem_type": "string"
        },
        "type": "in_set"
      }
    ]
  },
  "type": "all_of"
}
)=";

const std::string restriction_only_headers_str = R"=(
{
  "init": {
    "predicates": [
      {
        "init": {
          "arg_name": "headers:X-Test-Double",
          "arg_type": "double",
          "value": 4
        },
        "type": "lt"
      }
    ]
  },
  "type": "all_of"
}
)=";

std::string SerializeQuery(
    const std::unordered_map<std::string, std::string>& map) {
  std::string result;
  bool first = true;
  for (const auto& [key, value] : map) {
    if (!first) {
      result += "&";
    }
    first = false;
    result += key + "=" + value;
  }
  return result;
}

}  // namespace

namespace access_control_info {

TEST(AccessControlInfoRestrictions, ParseTest) {
  auto restriction_json = formats::json::FromString(restriction_str);

  clients::access_control::UserAccessInfo response;
  clients::access_control::RestrictionV1 api_restriction;
  api_restriction.handler_path = "/v1/example";
  api_restriction.handler_method = clients::access_control::HandlerMethod::kPut;
  api_restriction.restriction.extra = restriction_json;
  clients::access_control::UserAccessInfoRole role;
  role.role = "role1";
  role.restrictions.push_back(api_restriction);
  response.roles.push_back(role);
  response.restrictions.push_back(api_restriction);

  auto parsed = models::UserAccessInfo::ParseResponse(response);
  ASSERT_EQ(1, parsed.roles.size());
  ASSERT_EQ(1, parsed.roles[0].restrictions.size());
  auto parsed_restriction = parsed.roles[0].restrictions[0];
  EXPECT_EQ("/v1/example", parsed_restriction.handler_path);
  EXPECT_EQ(models::HttpMethod::kPut, parsed_restriction.handler_method);
  EXPECT_TRUE(bool(std::dynamic_pointer_cast<::experiments3::models::AllOf>(
      parsed_restriction.restriction)));
}

template <bool is_double, class T>
void TestExtractKwarg(const models::ParsedHttpRequest& parsed_request,
                      const ::experiments3::models::KwargName& name,
                      T expected) {
  auto value_variant =
      models::Restriction::ExtractKwarg(parsed_request, name, typeid(T));
  T* extracted = std::get_if<T>(&value_variant);
  ASSERT_TRUE(bool(extracted));
  if constexpr (is_double) {
    EXPECT_DOUBLE_EQ(expected, *extracted);
  } else {
    EXPECT_EQ(expected, *extracted);
  }
}

TEST(AccessControlInfoRestrictions, ExtractTest) {
  models::HttpRequest request;
  auto path_query =
      "/v1/example?" + SerializeQuery({{"sample_double_value", "10.5"},
                                       {"sample_int_value", "1"},
                                       {"sample_bool_value", "true"},
                                       {"sample_string_value", "value1"}});
  request.path_query = path_query;

  request.body = R"=(
      {
        "sample_string_value": "value2",
        "sample_int_value": 2,
        "sample_bool_value": false,
        "sample_double_value": 2.6
      }
    )=";

  request.headers.emplace("X-Test", "test-value");
  request.headers.emplace("X-Test-int", "2");
  request.headers.emplace("X-Test-bool", "false");
  request.headers.emplace("X-Test-double", "10.3");

  models::ParsedHttpRequest parsed_request(request);

  TestExtractKwarg<true, ::experiments3::models::KwargTypeDouble>(
      parsed_request, "query:sample_double_value", 10.5);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeInt>(
      parsed_request, "query:sample_int_value", 1);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeBool>(
      parsed_request, "query:sample_bool_value", true);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeString>(
      parsed_request, "query:sample_string_value", "value1");

  TestExtractKwarg<true, ::experiments3::models::KwargTypeDouble>(
      parsed_request, "body:sample_double_value", 2.6);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeInt>(
      parsed_request, "body:sample_int_value", 2);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeBool>(
      parsed_request, "body:sample_bool_value", false);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeString>(
      parsed_request, "body:sample_string_value", "value2");

  TestExtractKwarg<false, ::experiments3::models::KwargTypeString>(
      parsed_request, "headers:x-test", "test-value");
  TestExtractKwarg<false, ::experiments3::models::KwargTypeBool>(
      parsed_request, "headers:x-test-BOOL", false);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeInt>(
      parsed_request, "headers:X-Test-Int", 2);
  TestExtractKwarg<false, ::experiments3::models::KwargTypeDouble>(
      parsed_request, "headers:X-Test-double", 10.3);
}

TEST(AccessControlInfoRestrictions, CheckTest) {
  models::Restriction restriction;
  restriction.handler_path = "/v1/example";
  restriction.handler_method = models::HttpMethod::kPut;

  auto restriction_json = formats::json::FromString(restriction_str);

  restriction.restriction = ::experiments3::models::PredicateFromJson(
      restriction_json, experiments3::models::kMockFilesManager);

  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=10";
    request.method = models::HttpMethod::kGet;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=10";
    request.method = models::HttpMethod::kGet;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=10";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "unknown_value"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = "invalid_body:}";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query =
        "/v1/example?sample_double_value=2.5&sample_double_value=3.0";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query =
        "/v1/example?sample_double_value&sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query =
        "/v1/example?sample_double_value=2.5&sample_double_value";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header-3";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
}

TEST(ACcessControlInfoRestrictions, CheckWithRegexTest) {
  models::Restriction restriction;
  restriction.handler_path = "/v1/example.*";
  restriction.handler_method = models::HttpMethod::kPut;

  auto restriction_json = formats::json::FromString(restriction_str);

  restriction.restriction = ::experiments3::models::PredicateFromJson(
      restriction_json, experiments3::models::kMockFilesManager);

  {
    models::HttpRequest request;
    request.path_query = "/v1/example/some-path?sample_double_value=5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header-3";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example/some-path?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }

  restriction.handler_path = "/v1/example/\\d+/test";

  {
    models::HttpRequest request;
    request.path_query = "/v1/example/some-path?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value2"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example/12345/test?sample_double_value=5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header-3";

    EXPECT_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)),
                 access_control_info::AccessDenied);
  }
  {
    models::HttpRequest request;
    request.path_query = "/v1/example/abcde/test?sample_double_value=5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-Test-String"] = "test-header-3";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
}

TEST(AccessControlInfoRestrictions, CheckOnlyQueryTest) {
  models::Restriction restriction;
  restriction.handler_path = "/v1/example";
  restriction.handler_method = models::HttpMethod::kPut;

  auto restriction_json = formats::json::FromString(restriction_only_query_str);

  restriction.restriction = ::experiments3::models::PredicateFromJson(
      restriction_json, experiments3::models::kMockFilesManager);

  {
    models::HttpRequest request;
    request.path_query = "/v1/example?sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    // we don't check body if we have no restriction on it
    request.body = "some_invalid_body:}}";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
}

TEST(AccessControlInfoRestrictions, CheckOnlyBodyTest) {
  models::Restriction restriction;
  restriction.handler_path = "/v1/example";
  restriction.handler_method = models::HttpMethod::kPut;

  auto restriction_json = formats::json::FromString(restriction_only_body_str);

  restriction.restriction = ::experiments3::models::PredicateFromJson(
      restriction_json, experiments3::models::kMockFilesManager);

  {
    models::HttpRequest request;
    // we don't check query if we don't have restriction on it
    request.path_query =
        "/v1/example?sample_double_value=2.5&sample_double_value=2.5";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
}

TEST(AccessControlInfoRestrictions, CheckOnlyHeadersTest) {
  models::Restriction restriction;
  restriction.handler_path = "/v1/example";
  restriction.handler_method = models::HttpMethod::kPut;

  auto restriction_json =
      formats::json::FromString(restriction_only_headers_str);

  restriction.restriction = ::experiments3::models::PredicateFromJson(
      restriction_json, experiments3::models::kMockFilesManager);

  {
    models::HttpRequest request;
    request.path_query = "/v1/example";
    request.method = models::HttpMethod::kPut;

    request.body = R"=(
      {
        "sample_field": {
          "subfield": "value1"
        }
      }
    )=";
    request.headers["X-test-double"] = "2.2";

    EXPECT_NO_THROW(restriction.CheckThrow(models::ParsedHttpRequest(request)));
  }
}

}  // namespace access_control_info
