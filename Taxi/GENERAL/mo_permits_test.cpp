#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_car_classes/fetch_car_classes.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include "mo_permits.hpp"

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

const cf::FilterInfo kEmptyInfo;

TEST(MOPermits, Sample) {
  auto permits = std::make_shared<models::Permits>();
  cfi::MOPermits filter(kEmptyInfo, permits, {}, false, {}, {});

  permits->Add({"A123AA", models::kMoscowRegionLicenseIssuer}, "val1");

  cf::Context context;
  cfi::FetchFinalClasses::Set(context, {"econom"});
  models::Car car;

  // No permit
  car.number = "B123BB";
  cfi::FetchCar::Set(context, std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);

  // With permit
  car.number = "A123AA";
  cfi::FetchCar::Set(context, std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  const auto& permit = cfi::MOPermits::Get(context);
  EXPECT_EQ(permit.permission->value, "val1");
  EXPECT_EQ(permit.permission->issuer_id, models::kMoscowRegionLicenseIssuer);
  EXPECT_EQ(permit.classes_without_permission_requirement,
            std::vector<std::string>{});
}

UTEST(MOPermits, BusinessCars) {
  for (const auto perform_classification_for_licensed : {false, true}) {
    auto permits = std::make_shared<models::Permits>();
    std::vector<std::string> classes{"ultima", "elite"};

    cfi::MOPermits filter(
        kEmptyInfo, permits,
        [&classes](const auto&) { return models::Classes{classes}; },
        perform_classification_for_licensed, {}, {});

    permits->Add({"A123AA", models::kMoscowRegionLicenseIssuer}, "val1");

    cf::Context context;
    cfi::FetchFinalClasses::Set(context, classes);
    models::Car car;

    // No permit
    car.number = "B123BB";
    cfi::FetchCar::Set(context, std::make_shared<const models::Car>(car));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    auto permit = cfi::MOPermits::Get(context);
    EXPECT_EQ(permit.permission, std::nullopt);
    EXPECT_EQ(permit.classes_without_permission_requirement, classes);

    // With permit
    car.number = "A123AA";
    cfi::FetchCar::Set(context, std::make_shared<const models::Car>(car));
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
    permit = cfi::MOPermits::Get(context);
    EXPECT_EQ(permit.permission->value, "val1");
    EXPECT_EQ(permit.permission->issuer_id, models::kMoscowRegionLicenseIssuer);
    if (perform_classification_for_licensed) {
      EXPECT_EQ(permit.classes_without_permission_requirement, classes);
    } else {
      EXPECT_EQ(permit.classes_without_permission_requirement,
                std::vector<std::string>{});
    }
  }
}

UTEST(MOPermits, SkipClasses) {
  auto permits = std::make_shared<models::Permits>();
  permits->Add({"A123AA", models::kMoscowRegionLicenseIssuer}, "val1");
  models::Car car;
  car.number = "A123AA";

  cfi::MOPermits filter(kEmptyInfo, permits, {}, false, {"express", "courier"},
                        {});

  cf::Context context;
  cfi::FetchCar::Set(context, std::make_shared<const models::Car>(car));

  // All classes should be skipped
  cfi::FetchFinalClasses::Set(context, {"express", "courier"});
  EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);

  // Has non-skip class "econom"
  cfi::FetchFinalClasses::Set(context, {"express", "courier", "econom"});
  EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
}
