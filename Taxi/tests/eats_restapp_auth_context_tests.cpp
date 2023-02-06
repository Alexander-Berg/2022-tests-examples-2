#include <eats-restapp-authproxy-backend/models/eats_restapp_auth_context.hpp>

#include <userver/server/http/http_request.hpp>
#include <userver/utest/utest.hpp>

namespace eats_restapp_authproxy_backend::models {

struct HttpRequestHeaders {
  std::string GetHeader(const std::string& header_name) const {
    if (!headers.count(header_name)) {
      return "";
    }
    return headers.at(header_name);
  }

  bool HasHeader(const std::string& header_name) const {
    return headers.count(header_name);
  }

  server::http::HttpRequest::HeadersMap headers;
};

struct TestParseHeaderData {
  HttpRequestHeaders http_request;
  AuthContext expected_result;
};

class ParseHeadersTest : public ::testing::TestWithParam<TestParseHeaderData> {
};

const std::vector<TestParseHeaderData> kParseHeaders{
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, "111,222,333,444"},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, "111"},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111}),
      std::make_optional("RU"), std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, ""},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{}),
      std::make_optional("RU"), std::make_optional("9999")}},
    {{{{{http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, "111,222,333,444"},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {{},
      std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"),
      std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerPlaces, "111"},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123),
      {},
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111}),
      std::make_optional("RU"),
      std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerCountryCode, "RU"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123),
      std::make_optional("1234"),
      {},
      std::make_optional("RU"),
      std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, "111,222,333,444"},
        {http::headers::kPartnerPersonalEmailId, "9999"}}}},
     {std::make_optional(123),
      std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      {},
      std::make_optional("9999")}},
    {{{{{http::headers::kPartnerId, "123"},
        {http::headers::kPartnerUid, "1234"},
        {http::headers::kPartnerPlaces, "111,222,333,444"},
        {http::headers::kPartnerCountryCode, "RU"}}}},
     {std::make_optional(123),
      std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"),
      {}}},
    {{{{{http::headers::kPartnerPermissions, "first,second,third"}}}},
     {{},
      {},
      {},
      {},
      {},
      {},
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"first", "second", "third"})}},
};

INSTANTIATE_UTEST_SUITE_P(kParseHeaders, ParseHeadersTest,
                          ::testing::ValuesIn(kParseHeaders));

UTEST_P(ParseHeadersTest, should_return_correct_authcontext) {
  const auto& param = GetParam();
  const auto& current_result = ParseAuthContext(param.http_request);

  ASSERT_EQ(current_result, param.expected_result);
}

struct TestCheckAccessData {
  AuthContext auth_context;
  std::vector<int64_t> requested_partner_places;
  bool expected_result;
};

class CheckAccessTest : public ::testing::TestWithParam<TestCheckAccessData> {};

const std::vector<TestCheckAccessData> kCheckAccess{
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999")},
     {111, 333},
     true},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999")},
     {111, 555, 666},
     false},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999")},
     {111, 222, 333, 444, 555},
     false},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{}),
      std::make_optional("RU"), std::make_optional("9999")},
     {111},
     false},
    {{std::make_optional(123),
      std::make_optional("1234"),
      {},
      std::make_optional("RU"),
      std::make_optional("9999")},
     {111},
     false},
    {{std::make_optional(123),
      std::make_optional("1234"),
      {},
      std::make_optional("RU"),
      std::make_optional("9999")},
     {},
     true},
};

INSTANTIATE_UTEST_SUITE_P(kCheckAccess, CheckAccessTest,
                          ::testing::ValuesIn(kCheckAccess));

UTEST_P(CheckAccessTest, should_return_valid_access_check) {
  const auto& param = GetParam();

  ASSERT_EQ(param.auth_context.CheckAccess(param.requested_partner_places),
            param.expected_result);
}

struct TestCheckPermissionsData {
  AuthContext auth_context;
  std::vector<std::string> requested_partner_permissions;
  bool expected_result;
};

class CheckPermissionsTest
    : public ::testing::TestWithParam<TestCheckPermissionsData> {};

const std::vector<TestCheckPermissionsData> kCheckPermissions{
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999"),
      std::make_optional("ru"),
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"permission.restaurant.functionality",
                                          "permission.communications.read"})},
     {},
     true},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999"),
      std::make_optional("ru"),
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"permission.restaurant.functionality",
                                          "permission.communications.read"})},
     {"permission.restaurant.functionality"},
     true},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999"),
      std::make_optional("ru"),
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"permission.restaurant.functionality",
                                          "permission.communications.read"})},
     {"permission.communications.read", "permission.restaurant.functionality"},
     true},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999"),
      std::make_optional("ru"),
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"permission.restaurant.functionality",
                                          "permission.communications.read"})},
     {"permission.restaurant.menu"},
     false},
    {{std::make_optional(123), std::make_optional("1234"),
      std::make_optional<std::unordered_set<int64_t>>(
          std::unordered_set<int64_t>{111, 222, 333, 444}),
      std::make_optional("RU"), std::make_optional("9999"),
      std::make_optional("ru"),
      std::make_optional<std::unordered_set<std::string>>(
          std::unordered_set<std::string>{"permission.restaurant.functionality",
                                          "permission.communications.read"})},
     {"permission.restaurant.menu", "permission.restaurant.functionality"},
     false}};

INSTANTIATE_UTEST_SUITE_P(kCheckPermissions, CheckPermissionsTest,
                          ::testing::ValuesIn(kCheckPermissions));

UTEST_P(CheckPermissionsTest, should_return_valid_permissions_check) {
  const auto& param = GetParam();

  ASSERT_EQ(
      param.auth_context.CheckPermissions(param.requested_partner_permissions),
      param.expected_result);
}

}  // namespace eats_restapp_authproxy_backend::models
