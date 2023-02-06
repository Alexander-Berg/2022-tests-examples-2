#include <utils/experiments/experiments.hpp>

#include <fmt/format.h>
#include <gtest/gtest.h>

namespace eats_products::utils::experiments::test {

namespace {

void Check(
    const models::RequestContext& request_context,
    const experiments3::kwargs_builders::MenuGoodsKwargsBuilder& expected) {
  const auto& expected_build = expected.Build();
  const auto kwargs = BuildExperimentKwargs<
      experiments3::kwargs_builders::MenuGoodsKwargsBuilder>(request_context);
  const auto& build = kwargs.Build();
  expected_build.ForEach(
      [&build](const experiments3::models::KwargName& name,
               const experiments3::models::KwargValue& expected_value) {
        const auto value = build.FindOptional(name);
        ASSERT_NE(value, nullptr);
        ASSERT_EQ(*value, expected_value);
      });
}

}  // namespace

TEST(BuildExperimentKwargs, TestDeviceId) {
  models::RequestContext request_context;
  models::DeviceId device_id("some_id");
  request_context.device_id = device_id;
  request_context.eats_auth_context.app_metrica_device_id =
      "some_app_device_id";
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateDeviceId(device_id.GetUnderlying());
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestEmptyDeviceId) {
  models::RequestContext request_context;
  request_context.device_id = models::DeviceId("");
  auto app_metrica = "some_app_device_id";
  request_context.eats_auth_context.app_metrica_device_id = app_metrica;
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateDeviceId(app_metrica);
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestMissingDeviceId) {
  models::RequestContext request_context;
  auto app_metrica = "some_app_device_id";
  request_context.eats_auth_context.app_metrica_device_id = app_metrica;
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateDeviceId(app_metrica);
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestPlatform) {
  models::RequestContext request_context;
  models::Platform platform("some_plaform");
  request_context.platform = platform;
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdatePlatform(platform.GetUnderlying());
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestAppVersion) {
  models::RequestContext request_context;
  ua_parser::ApplicationVersion version(3, 1, 2);
  request_context.app_version = version;
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateAppVersion(version);
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestUserPhoneId) {
  models::RequestContext request_context;
  auto user_id = "userid_1";
  auto phone_id = "phoneid_1";
  request_context.eats_auth_context.eats_personal.user_id = user_id;
  request_context.eats_auth_context.eats_personal.phone_id = phone_id;
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateEatsUserId(user_id);
  expected.UpdatePersonalPhoneId(phone_id);
  Check(request_context, expected);
}

TEST(BuildExperimentKwargs, TestBrandPlace) {
  models::RequestContext request_context;
  auto brand_id = 123;
  auto place_slug = "slug";
  request_context.place = models::Place{models::PlaceId(1),
                                        models::PlaceSlug(place_slug),
                                        models::BrandId(brand_id),
                                        models::IsPlaceEnabled(true),
                                        /*currency_code*/ std::nullopt,
                                        /*currency_sign*/ std::nullopt};
  experiments3::kwargs_builders::MenuGoodsKwargsBuilder expected;
  expected.UpdateBrandId(std::to_string(brand_id));
  expected.UpdatePlaceSlug(place_slug);
  Check(request_context, expected);
}

}  // namespace eats_products::utils::experiments::test
