#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <testing/taxi_config.hpp>
#include "childchairs.hpp"
#include "configs/childchairs.hpp"
#include "models/childchairs.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(ChilchairsTest, Sample) {
  candidates::GeoMember member;

  cf::Context context;
  const auto config = dynamic_config::GetDefaultSnapshot();

  const models::childchairs::Chair::Groups groups2{2};
  const models::childchairs::Chair::Groups groups23{2, 3};

  const models::childchairs::Chair& chair2{"Other", groups2, false};
  const models::childchairs::Chair& chair23{"Other", groups23, false};

  models::Car car;
  car.car_id = "car1";
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));

  // requested categories [7]
  cf::partners::Childchairs filter1(kEmptyInfo, {7}, config);

  // driver without chairs
  member.id = "dbid0_uuid0";

  EXPECT_EQ(filter1.Process(member, context), cf::Result::kDisallow);

  // driver with park booster [7]
  car.chairs_info.boosters = 1;
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // driver with own chair [3, 7]
  member.id = "dbid0_uuid1";

  car.chairs_info.boosters = 0;
  car.chairs_info.driver_chairs = {{"uuid1", {chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // requestd categories [3, 7]
  cf::partners::Childchairs filter2(kEmptyInfo, {3, 7}, config);

  // driver has only one own chair [3, 7]
  EXPECT_EQ(filter2.Process(member, context), cf::Result::kDisallow);

  // driver with with two own chairs [3], [3, 7]
  member.id = "dbid0_uuid2";

  car.chairs_info.driver_chairs = {{"uuid2", {chair2, chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter2.Process(member, context), cf::Result::kAllow);

  // requested categories [7, 7]
  cf::partners::Childchairs filter3(kEmptyInfo, {7, 7}, config);

  // driver with park chair [3, 7] and own chair [3, 7]
  member.id = "dbid0_uuid3";

  car.chairs_info.chairs = {chair23};
  car.chairs_info.driver_chairs = {{"uuid3", {chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter3.Process(member, context), cf::Result::kAllow);
}
