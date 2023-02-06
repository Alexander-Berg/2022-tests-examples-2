#include <grocery-shared/auth_context.hpp>

#include <experiments3/kwargs_builders/grocery_shared_kwargs_test.hpp>
#include <experiments3/kwargs_names.hpp>

#include <userver/utest/utest.hpp>

namespace grocery_shared {

namespace auth_context {

TEST(Grocery_shared_test, grocery_shared_kwargs_test_is_save) {
  using HeaderTag = superapp_backend::AuthContext::HeaderTag;

  const std::string device_id = "1121212412";
  const std::string taxi_phone_id = "sdqwd1212";
  const std::string yandex_uid = "a12313112";
  const std::string taxi_geo_id = "qw12123-qwe";
  const std::string phone_id = "wqe1231231qw-123123";
  const std::string eats_id = "2112e12qwwewqe12123";
  const std::string locale = "ru";
  const std::string application_value = "application_value";

  superapp_backend::AuthContext auth_context;
  auth_context.SetSession("taxi:uuuuu");
  auth_context.SetLocale(locale);
  auth_context.SetHeader(HeaderTag::kXAppMetricaDeviceId, device_id);
  auth_context.SetHeader(HeaderTag::kXYandexTaxiPhoneId, taxi_phone_id);
  auth_context.SetHeader(HeaderTag::kXYandexUid, yandex_uid);
  auth_context.SetHeader(HeaderTag::kXYaTaxiGeoId, taxi_geo_id);

  ua_parser::AppVars appVar;
  appVar.SetVar(ua_parser::AppVars::kVarAppName, application_value);
  auth_context.SetAppVars(appVar);

  passenger_authorizer::models::PersonalData personalData;
  personalData.phone_id = phone_id;
  personalData.eats_id = eats_id;
  auth_context.SetPersonal(personalData);

  experiments3::kwargs_builders::GrocerySharedKwargsTest kwargs;
  AdjustKwargsFromAuthContext(auth_context, kwargs);
  std::unordered_map<std::string, std::string> map_value;
  for (const auto& kwargsSchemaItem : kwargs.GetSchema()) {
    const auto* value = kwargs.Build().FindOptional(kwargsSchemaItem.first);
    if (value != nullptr) {
      if (auto valueKwarg =
              std::get_if<experiments3::models::KwargTypeString>(value)) {
        map_value.insert({kwargsSchemaItem.first, *valueKwarg});
      }
    }
  }

  auto check_value = [map_value](const std::string& name_header,
                                 const auto& value) {
    auto value_map = map_value.find(name_header);
    ASSERT_TRUE(value_map != map_value.end() && value_map->second == value);
  };

  check_value(experiments3::kwargs_names::kPersonalPhoneId, phone_id);
  check_value(experiments3::kwargs_names::kUserId,
              ExtractYandexTaxiUserId(auth_context).value());
  check_value(experiments3::kwargs_names::kLocale, locale);
  check_value(experiments3::kwargs_names::kEatsUserId, eats_id);

  const auto appmetrica_tag = HeaderTag::kXAppMetricaDeviceId;
  const auto appmetrica_device_id = auth_context.GetHeaderValue(appmetrica_tag);
  check_value(experiments3::kwargs_names::kAppmetricaDeviceId,
              *appmetrica_device_id);

  const auto phone_id_tag = HeaderTag::kXYandexTaxiPhoneId;
  const auto phone_id_value = auth_context.GetHeaderValue(phone_id_tag);
  check_value(experiments3::kwargs_names::kPhoneId, *phone_id_value);

  check_value(experiments3::kwargs_names::kYandexUid, yandex_uid);
  check_value(experiments3::kwargs_names::kGeoId, taxi_geo_id);
  check_value(experiments3::kwargs_names::kApplication, application_value);
}

}  // namespace auth_context

}  // namespace grocery_shared
