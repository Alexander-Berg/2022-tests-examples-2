#include "fetch_version_classes.hpp"

#include <gtest/gtest.h>

#include <pro_app_parser/app_family.hpp>
#include <userver/dynamic_config/test_helpers.hpp>

#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <userver/utest/utest.hpp>

namespace {

namespace features = configs::taximeter_version_features;
using candidates::filters::Context;
using candidates::filters::Result;
using candidates::filters::infrastructure::FetchDriver;
using candidates::filters::infrastructure::FetchVersionClasses;

const candidates::filters::FilterInfo kEmptyInfo;

class CheckClasses
    : public ::testing::TestWithParam<
          std::tuple<features::Type, features::Platform, features::Version,
                     std::vector<std::string>>> {};

FetchVersionClasses::Map CreateMap() {
  return {
      {models::ClassesMapper::Parse("econom"),
       {
           {pro_app_parser::kAppFamilyTaximeter,
            {
                {features::Platform::kAndroid, features::Version("1.0")},
                {features::Platform::kIos, features::Version("2.0")},
            }},
           {pro_app_parser::kAppFamilyUberdriver,
            {
                {features::Platform::kAndroid, features::Version("3.0")},
            }},
       }},
      {models::ClassesMapper::Parse("comfort"),
       {
           {pro_app_parser::kAppFamilyTaximeter,
            {
                {features::Platform::kAndroid, features::Version("4.0")},
                {features::Platform::kIos, features::Version("5.0")},
            }},
       }},
  };
}

}  // namespace

UTEST_P(CheckClasses, Check) {
  const auto& param = GetParam();

  const auto [type, platform, version, classes] = param;

  Context context;

  auto driver = std::make_shared<models::Driver>();
  driver->app = ua_parser::TaximeterApp(type, version, platform);
  driver->app_family = pro_app_parser::GetAppFamily(
      driver->app, dynamic_config::GetDefaultSnapshot());
  FetchDriver::Set(context, std::move(driver));

  FetchVersionClasses filter(
      kEmptyInfo, models::Classes{"econom", "comfort", "vip"}, {}, CreateMap());
  EXPECT_EQ(Result::kAllow, filter.Process({}, context));

  EXPECT_EQ(models::Classes(classes), FetchVersionClasses::Get(context));
}

INSTANTIATE_UTEST_SUITE_P(
    FetchVersionClasses, CheckClasses,
    ::testing::Values(
        std::make_tuple(features::Type::Vezet, features::Platform::kAndroid,
                        "1.0",
                        std::vector<std::string>{"econom", "comfort", "vip"}),
        std::make_tuple(features::Type::Uber, features::Platform::kIos, "1.0",
                        std::vector<std::string>{"econom", "comfort", "vip"}),
        std::make_tuple(features::Type::Production, features::Platform::kIos,
                        "1.0", std::vector<std::string>{"vip"}),
        std::make_tuple(features::Type::Uber, features::Platform::kAndroid,
                        "1.0", std::vector<std::string>{"comfort", "vip"}),
        std::make_tuple(features::Type::Production,
                        features::Platform::kAndroid, "1.0",
                        std::vector<std::string>{"econom", "vip"}),
        std::make_tuple(features::Type::Production, features::Platform::kIos,
                        "2.0", std::vector<std::string>{"econom", "vip"}),
        std::make_tuple(features::Type::Uber, features::Platform::kAndroid,
                        "3.0",
                        std::vector<std::string>{"econom", "comfort", "vip"}),
        std::make_tuple(features::Type::Production,
                        features::Platform::kAndroid, "2.0",
                        std::vector<std::string>{"econom", "vip"}),
        std::make_tuple(features::Type::Production, features::Platform::kIos,
                        "3.0", std::vector<std::string>{"econom", "vip"}),
        std::make_tuple(features::Type::Uber, features::Platform::kAndroid,
                        "3.0",
                        std::vector<std::string>{"econom", "comfort", "vip"}),
        std::make_tuple(features::Type::Production,
                        features::Platform::kAndroid, "5.0",
                        std::vector<std::string>{"econom", "comfort", "vip"})));
