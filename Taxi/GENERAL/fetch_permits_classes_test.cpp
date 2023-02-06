#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_car_classes/fetch_car_classes.hpp>

#include "fetch_permits_classes.hpp"

namespace cf = candidates::filters;
namespace vp = views::permits;

const cf::FilterInfo kEmptyInfo;

TEST(FetchPermitsClassesTest, Sample) {
  candidates::GeoMember member;
  cf::Context context;

  models::Car car;
  car.number = "B123BB";
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  cf::infrastructure::FetchCarClasses::Set(context, models::Classes());

  auto permits = std::make_shared<models::Permits>();
  auto whitelist_permits = std::make_shared<models::WhitelistPermits>();

  // Driver has classes without permit
  // see testsuite

  // Driver hasn't classes without permit and no permit issuer ids
  cf::partners::FetchPermitsClasses filter1(
      kEmptyInfo, models::Classes({"econom"}), {},
      std::make_unique<vp::Classifier>(
          models::Classes({"econom"}), std::vector<short>{}, whitelist_permits,
          permits, nullptr, vp::AllowedClassesMap(), models::Classes(),
          models::Classes()));
  filter1.Process(member, context);
  EXPECT_EQ(models::Classes({"econom"}),
            cf::partners::FetchPermitsClasses::Get(context));

  whitelist_permits->Set({"B123BB"});

  // Driver's car is in whitelist
  cf::partners::FetchPermitsClasses filter2(
      kEmptyInfo, models::Classes({"econom", "vip"}), {},
      std::make_unique<vp::Classifier>(
          models::Classes({"econom", "vip"}), std::vector<short>{3, 4},
          whitelist_permits, permits, nullptr, vp::AllowedClassesMap(),
          models::Classes(), models::Classes()));
  filter2.Process(member, context);
  EXPECT_EQ(models::Classes({"econom", "vip"}),
            cf::partners::FetchPermitsClasses::Get(context));

  // Driver's car is not in whitelist and doesn't have a permit
  whitelist_permits->Set({});
  cf::partners::FetchPermitsClasses filter3(
      kEmptyInfo, models::Classes({"econom", "comfort", "vip"}), {},
      std::make_unique<vp::Classifier>(
          models::Classes({"econom", "comfort", "vip"}),
          std::vector<short>{3, 4}, whitelist_permits, permits, nullptr,
          vp::AllowedClassesMap(), models::Classes(), models::Classes()));
  filter3.Process(member, context);
  EXPECT_EQ(models::Classes(), cf::partners::FetchPermitsClasses::Get(context));

  // Driver's car doesn't have a permit
  permits->Add({"B123BB", 2}, "val1");
  cf::partners::FetchPermitsClasses filter4(
      kEmptyInfo, models::Classes({"econom", "vip", "comfort"}), {},
      std::make_unique<vp::Classifier>(
          models::Classes({"econom", "vip", "comfort"}),
          std::vector<short>{3, 4}, whitelist_permits, permits, nullptr,
          vp::AllowedClassesMap(), models::Classes(), models::Classes()));
  filter4.Process(member, context);
  EXPECT_EQ(models::Classes(), cf::partners::FetchPermitsClasses::Get(context));

  // Driver's car has a permit
  permits->Add({"B123BB", 3}, "val1");
  cf::partners::FetchPermitsClasses filter5(
      kEmptyInfo, models::Classes({"comfort", "vip"}), {},
      std::make_unique<vp::Classifier>(
          models::Classes({"comfort", "vip"}), std::vector<short>{3, 4},
          whitelist_permits, permits, nullptr, vp::AllowedClassesMap(),
          models::Classes(), models::Classes()));
  filter5.Process(member, context);
  EXPECT_EQ(models::Classes({"comfort", "vip"}),
            cf::partners::FetchPermitsClasses::Get(context));
}
