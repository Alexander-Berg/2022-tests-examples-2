#include "experience_settings.hpp"

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_driver/models/drivers.hpp>
#include <models/classes.hpp>

namespace {

const auto kJsonExperienceSettings = R"({
    "zones": {
      "moscow": {
        "econom": [
          {"category": "B", "experience": 2}
        ]
      },
      "spb": {
        "econom": [
          {"category": "B", "experience": 2},
          {"category": "C", "experience": 1}
        ]
      }
    },
    "countries": {
      "rus": {
        "econom": [
          {"category": "B", "experience": 5}
        ],
        "comfort": [
          {"category": "B", "experience": 2}
        ]
      }
    },
    "__default__": {
      "business": [
        {"category": "B", "experience": 1}
      ]
    }
})";

}  // namespace

UTEST(LicenseExperience, Sample) {
  using TimePoint = std::chrono::system_clock::time_point;
  using Duration = std::chrono::duration<int32_t, std::ratio<2629746>>;
  utils::datetime::MockNowSet(TimePoint(Duration(5)));
  const auto now = utils::datetime::Now();

  const auto license_experience_settings =
      formats::json::FromString(kJsonExperienceSettings)
          .As<taxi_config::license_experience_settings::
                  LicenseExperienceSettings>();

  const models::ClassType econom = models::ClassesMapper::Parse("econom");
  const models::ClassType comfort = models::ClassesMapper::Parse("comfort");
  const models::ClassType comfortplus =
      models::ClassesMapper::Parse("comfortplus");
  const models::ClassType business = models::ClassesMapper::Parse("business");
  const models::Classes allowed_classes(
      {"econom", "comfort", "comfortplus", "business"});

  models::experience::ExperienceSettings experience_settings1(
      "moscow", "rus", license_experience_settings, now, allowed_classes);

  EXPECT_FALSE(experience_settings1.IsEmpty());

  models::Driver driver;
  driver.experience = {{"B", TimePoint(Duration(4))},
                       {"C", TimePoint(Duration(4))}};

  EXPECT_FALSE(experience_settings1.CheckExperience(econom, driver.experience)
                   .is_satisfied);
  EXPECT_FALSE(experience_settings1.CheckExperience(comfort, driver.experience)
                   .is_satisfied);
  EXPECT_TRUE(
      experience_settings1.CheckExperience(comfortplus, driver.experience)
          .is_satisfied);
  EXPECT_TRUE(experience_settings1.CheckExperience(business, driver.experience)
                  .is_satisfied);

  models::experience::ExperienceSettings experience_settings2(
      "spb", "rus", license_experience_settings, now, allowed_classes);

  EXPECT_FALSE(experience_settings2.IsEmpty());

  EXPECT_TRUE(experience_settings2.CheckExperience(econom, driver.experience)
                  .is_satisfied);

  models::experience::ExperienceSettings experience_settings3(
      "minsk", "blr", license_experience_settings, now, allowed_classes);

  EXPECT_FALSE(experience_settings3.IsEmpty());

  EXPECT_TRUE(experience_settings3.CheckExperience(econom, driver.experience)
                  .is_satisfied);
}
