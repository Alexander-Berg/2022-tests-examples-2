#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include "confirmed_childchairs.hpp"
#include "models/childchairs.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

TEST(ConfirmedChilchairsTest, Sample) {
  candidates::GeoMember member;
  member.id = "dbid0_uuid0";

  cf::Context context;
  const auto config = dynamic_config::GetDefaultSnapshot();

  const models::childchairs::Chair::Groups groups2{2};
  const models::childchairs::Chair::Groups groups23{2, 3};

  const models::childchairs::Chair& chair23{"Other", groups23, false};

  const models::childchairs::ConfirmedChair& confirmed_chair2{chair23, true,
                                                              groups2};
  const models::childchairs::ConfirmedChair& confirmed_chair23{chair23, true,
                                                               groups23};
  const models::childchairs::ConfirmedChair& confirmed_chair23_disabled{
      chair23, false, groups23};

  models::Car car;
  car.car_id = "car1";
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));

  // requested categories [7]
  cf::partners::ConfirmedChildchairs filter1(kEmptyInfo, {7}, config);

  // driver without confirmed chairs
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kDisallow);

  // driver with confirmed booster old way [7]
  car.chairs_info.confirmed_boosters = 1;
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // driver with confirmed chair old way [3, 7]
  car.chairs_info.confirmed_boosters = 0;
  car.chairs_info.confirmed_chairs = {confirmed_chair23};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // driver with confirmed chair new way [3, 7]
  member.id = "dbid0_uuid1";

  car.chairs_info.confirmed_chairs = {};
  car.chairs_info.driver_confirmed_chairs = {{"uuid1", {confirmed_chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // driver with confirmed booster new way [7]
  car.chairs_info.driver_confirmed_chairs = {};
  car.chairs_info.driver_confirmed_boosters = {{"uuid1", 1}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter1.Process(member, context), cf::Result::kAllow);

  // requested categories [3, 7]
  cf::partners::ConfirmedChildchairs filter2(kEmptyInfo, {3, 7}, config);

  // driver with chair [3, 7] and disabled chair [3, 7]
  member.id = "dbid0_uuid2";

  car.chairs_info.driver_confirmed_chairs = {
      {"uuid2", {confirmed_chair23, confirmed_chair23_disabled}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter2.Process(member, context), cf::Result::kDisallow);

  // requested categories [7, 7]
  cf::partners::ConfirmedChildchairs filter3(kEmptyInfo, {7, 7}, config);

  // driver with chairs [3], [3, 7]
  member.id = "dbid0_uuid3";

  car.chairs_info.driver_confirmed_chairs = {
      {"uuid3", {confirmed_chair2, confirmed_chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter3.Process(member, context), cf::Result::kDisallow);

  // driver with chairs [3, 7], [3, 7]
  member.id = "dbid0_uuid4";

  car.chairs_info.driver_confirmed_chairs = {
      {"uuid4", {confirmed_chair23, confirmed_chair23}}};
  cf::infrastructure::FetchCar::Set(context,
                                    std::make_shared<const models::Car>(car));
  EXPECT_EQ(filter3.Process(member, context), cf::Result::kAllow);
}
