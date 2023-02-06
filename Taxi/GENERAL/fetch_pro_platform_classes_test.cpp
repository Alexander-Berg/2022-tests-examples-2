#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <userver/utest/utest.hpp>

#include "fetch_pro_platform_classes.hpp"

namespace {

void PerformTest(std::vector<ua_parser::TaximeterPlatform> platforms_to_filter,
                 models::Classes classes_to_filter,
                 const models::Classes& expected_classes) {
  const candidates::filters::FilterInfo kEmptyInfo;
  static const models::Classes kAllowedClasses{
      {"econom", "courier", "express"}};

  ua_parser::TaximeterApp app;
  app.platform = ua_parser::TaximeterPlatform::kIos;

  models::Driver dbdriver;
  dbdriver.app = app;

  candidates::filters::Context context;
  candidates::filters::infrastructure::FetchDriver::Set(
      context, std::make_shared<const models::Driver>(std::move(dbdriver)));

  candidates::filters::cargo::FetchProPlatformClasses filter{
      kEmptyInfo,
      kAllowedClasses,
      {},
      std::move(platforms_to_filter),
      std::move(classes_to_filter)};

  ASSERT_EQ(candidates::filters::Result::kAllow,
            filter.Process(candidates::GeoMember{}, context));
  const auto& profile_classes =
      candidates::filters::cargo::FetchProPlatformClasses::Get(context);
  ASSERT_EQ(profile_classes, expected_classes);
}

}  // namespace

UTEST(FetchTaximeterPlatformClassesFilter, Sample) {
  PerformTest({}, {}, {{"econom", "courier", "express"}});
  PerformTest({ua_parser::TaximeterPlatform::kAndroid},
              {{"courier", "express"}}, {{"econom", "courier", "express"}});
  PerformTest({ua_parser::TaximeterPlatform::kIos},
              {{"courier", "express", "cargo"}}, {"econom"});
  PerformTest({ua_parser::TaximeterPlatform::kIos},
              {{"econom", "courier", "express"}}, {});
}
