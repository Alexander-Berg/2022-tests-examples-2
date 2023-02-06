#include <userver/utest/utest.hpp>

#include <fmt/format.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>

#include <http/passenger_headers.hpp>
#include <superapp-backend/superapp_context.hpp>

#include <grocery-orders-shared/helpers/auth_context.hpp>

namespace grocery_orders_shared::helpers {

// Проверяет, что контекст авторизации сериализуется в json и ожижаемые
// заголовки присутствуют в сериализованном значении.
TEST(AuthContext_Serialize, result_json_value_contains_expected_headers) {
  const std::string login = "user";
  const std::string login_id = "1";
  const std::string remote_ip = "";

  const clients::http::Headers headers = {
      {http::kXYandexLogin, login},
      {http::kXLoginId, login_id},
      {http::headers::kXRemoteIp, remote_ip}};
  const auto auth_context =
      superapp_backend::FetchAuthContextFromStorage(headers);
  const auto serialized = SerializeAuthContext(auth_context);

  EXPECT_TRUE(serialized.IsObject());
  EXPECT_TRUE(serialized.HasMember(keys::kHeaders));
  const auto serialized_headers = serialized[keys::kHeaders];
  EXPECT_TRUE(serialized_headers.IsObject());
  EXPECT_TRUE(serialized_headers.HasMember(http::kXYandexLogin));
  ASSERT_EQ(serialized_headers[http::kXYandexLogin].As<std::string>(), login);
  EXPECT_TRUE(serialized_headers.HasMember(http::kXLoginId));
  ASSERT_EQ(serialized_headers[http::kXLoginId].As<std::string>(), login_id);
  EXPECT_TRUE(serialized_headers.HasMember(http::headers::kXRemoteIp));
  ASSERT_EQ(serialized_headers[http::headers::kXRemoteIp].As<std::string>(),
            remote_ip);
  ASSERT_EQ(serialized_headers.GetSize(), 3);
}

// Проверяет, что контекст авторизации корректно собирается из сериализованного
// значения.
TEST(AuthContext_Deserialize, auth_context_constructed_correctly) {
  const std::string empty = "";
  const std::string domain = "domain";
  const std::string session = domain + ":123";
  const std::string session1 = "session1";
  const std::string session2 = "session2";
  const std::string bound_sessions = session1 + "," + session2;
  const std::string pass_flags = "pdd,phonish,neophonish";
  const std::string remote_ip = "192.168.0.13";
  const std::string request_language = "ru";
  const std::string app_name = "qwe";
  const std::string app_ver = "123";
  const std::string personal_phone_id = "123";
  const std::string eats_user_id = "234";
  const std::string app_metrica_device_id = "345";

  const std::string json_template =
      R"({{
         "headers": {{
           "X-YaTaxi-Session": "{}",
           "X-YaTaxi-Bound-Sessions": "{}",
           "X-YaTaxi-Pass-Flags": "{}",
           "X-Remote-IP": "{}",
           "X-Request-Language": "{}",
           "X-Request-Application": "app_name={},app_ver={}",
           "X-YaTaxi-User": "personal_phone_id={},eats_user_id={}",
           "X-AppMetrica-DeviceId": "{}"
         }}
       }})";
  const std::string serialized =
      fmt::format(json_template, session, bound_sessions, pass_flags, remote_ip,
                  request_language, app_name, app_ver, personal_phone_id,
                  eats_user_id, app_metrica_device_id);

  const auto deserialized =
      DeserializeAuthContext(formats::json::FromString(serialized));
  EXPECT_TRUE(deserialized.has_value());

  const auto& auth_context = deserialized.value();

  // X-YaTaxi-Session
  EXPECT_TRUE(auth_context.IsAuthorized());
  EXPECT_EQ(auth_context.GetSession(), session);
  EXPECT_EQ(auth_context.GetSessionDomain(), domain);

  // X-YaTaxi-Bound-Sessions
  EXPECT_EQ(auth_context.GetBoundSessions(),
            (std::vector<std::string>{session1, session2}));

  // X-YaTaxi-Pass-Flags
  const auto& flags = auth_context.GetFlags();
  EXPECT_TRUE(flags.has_pdd);
  EXPECT_TRUE(flags.has_phonish);
  EXPECT_TRUE(flags.has_neophonish);
  EXPECT_FALSE(flags.has_portal);

  // X-Remote-IP
  EXPECT_EQ(auth_context.application_ip, remote_ip);

  // X-Request-Language
  EXPECT_EQ(auth_context.GetLocale(), request_language);

  // X-Request-Application
  const auto& app_vars = auth_context.GetAppVars();
  EXPECT_EQ(app_vars.GetApplicationName(), app_name);
  EXPECT_EQ(app_vars.GetVarAppVer(), app_ver);
  EXPECT_EQ(app_vars.GetVarAppVer1(), empty);

  // X-YaTaxi-User
  const auto& personal = auth_context.GetPersonal();
  EXPECT_EQ(personal.phone_id, personal_phone_id);
  EXPECT_EQ(personal.eats_id, eats_user_id);
  EXPECT_EQ(personal.email_id, empty);

  // X-AppMetrica-DeviceId
  EXPECT_EQ(auth_context.GetHeaderValue(superapp_backend::kXAppMetricaDeviceId),
            app_metrica_device_id);
}

// Проверяет, что при null возвращается std::nullopt.
TEST(AuthContext_Deserialize, returns_null_opt_if_null) {
  const auto deserialized = DeserializeAuthContext(formats::json::Value{});
  EXPECT_FALSE(deserialized.has_value());
}

// Проверяет, что при некорректном json-формате возвращается std::nullopt.
TEST(AuthContext_Deserialize, returns_null_opt_if_invalid_format) {
  const auto deserialized =
      DeserializeAuthContext(formats::json::FromString(R"({ "qwe": 123 })"));
  EXPECT_FALSE(deserialized.has_value());
}

}  // namespace grocery_orders_shared::helpers
