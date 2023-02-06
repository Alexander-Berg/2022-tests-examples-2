#include <views/driver/v1/userver-sample/v1/test/post/view.hpp>

#include <tuple>

#include <pro_app_parser/app_family.hpp>

#include <ua_parser/taximeter_application.hpp>

namespace handlers::driver_v1_userver_sample_v1_test::post {

std::tuple<std::string, std::string, std::string> GetOptionalAppParams(
    const ua_parser::TaximeterApp& app) {
  if (app.IsExtendedFormat()) {
    return {app.GetBrand(), app.GetBuildType(),
            app.platform_version ? app.platform_version->ToString() : ""};
  }
  return {"", "", ""};
}

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto app = request.driver_params.app;
  const auto [brand, build_type, platform_version] = GetOptionalAppParams(app);
  const auto& app_family =
      pro_app_parser::GetAppFamily(app, dependencies.config);  // may throw
  return Response200{request.driver_params.driver_profile_id,
                     request.driver_params.park_id,
                     app_family,
                     app.GetType(),
                     app.version.ToString(),
                     app.GetPlatform(),
                     brand,
                     build_type,
                     platform_version,
                     std::nullopt};
}

Response View::HandleNonAuthorized(Request&& request,
                                   Dependencies&& dependencies) {
  if (request.driver_params.IsPassportAuthorized()) {
    const auto& app = request.driver_params.app;
    const auto [brand, build_type, platform_version] =
        GetOptionalAppParams(app);
    const auto app_family =
        pro_app_parser::GetAppFamily(app, dependencies.config);  // may throw
    return Response200{"none",
                       "none",
                       app_family,
                       app.GetType(),
                       app.version.ToString(),
                       app.GetPlatform(),
                       brand,
                       build_type,
                       platform_version,
                       request.driver_params.passport_uid};
  }
  return Response200{"none", "none", "none", "none", "none",
                     "none", "none", "none", "none", std::nullopt};
}

}  // namespace handlers::driver_v1_userver_sample_v1_test::post
