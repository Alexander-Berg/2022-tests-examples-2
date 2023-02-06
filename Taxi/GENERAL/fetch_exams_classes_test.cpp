#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include <userver/utest/utest.hpp>
#include "fetch_exams_classes.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

class FetchExamsClassesTest : public testing::Test {
 public:
  cf::Context GetContext(const std::string& unique_driver_id) const {
    if (unique_drivers_.size() == 0) FillUniqueDrivers();

    cf::Context context;
    cf::infrastructure::FetchUniqueDriver::Set(
        context, unique_drivers_[unique_driver_id]);
    return context;
  }

 protected:
  void FillUniqueDrivers() const {
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license1", "license10"};
      unique_driver.exams = models::drivers::Exams({"comfort"});
      unique_drivers_["uid1"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.exams = models::drivers::Exams({"business"});
      unique_drivers_["uid2"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license3", "license30"};
      unique_driver.exams = models::drivers::Exams({"comfort", "business"});
      unique_drivers_["uid3"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license4", "license40"};
      unique_drivers_["uid4"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license5", "license50"};
      unique_driver.exams =
          models::drivers::Exams({"comfort", "comfortplus", "business"});
      unique_drivers_["uid5"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
  }

  mutable std::unordered_map<std::string, models::UniqueDriverPtr>
      unique_drivers_;
};

UTEST_F(FetchExamsClassesTest, Sample) {
  candidates::GeoMember member;
  cf::Context context;
  models::ExtraExams extra_exams;

  const auto class_type_vip = models::ClassesMapper::Parse("vip");
  extra_exams[class_type_vip] = models::drivers::Exams({"business"});
  const auto class_type_comfortplus =
      models::ClassesMapper::Parse("comfortplus");
  extra_exams[class_type_comfortplus] =
      models::drivers::Exams({"comfortplus", "business"});

  cf::partners::FetchExamsClasses filter1(
      kEmptyInfo, models::Classes({"econom", "vip"}), {}, extra_exams);

  // econom - doesn't need exam, vip - driver hasn't exam business
  context = GetContext("uid1");
  auto result = filter1.Process(member, context);
  EXPECT_EQ(models::Classes({"econom"}),
            cf::partners::FetchExamsClasses::Get(context));

  // econom - doesn't need exam, vip - driver has exam business
  context = GetContext("uid2");
  result = filter1.Process(member, context);
  EXPECT_EQ(models::Classes({"econom", "vip"}),
            cf::partners::FetchExamsClasses::Get(context));

  // econom - doesn't need exam, vip - driver has exam business
  context = GetContext("uid3");
  result = filter1.Process(member, context);
  EXPECT_EQ(models::Classes({"econom", "vip"}),
            cf::partners::FetchExamsClasses::Get(context));

  // driver doesn't have any exam
  context = GetContext("uid4");
  result = filter1.Process(member, context);
  EXPECT_EQ(models::Classes({"econom"}),
            cf::partners::FetchExamsClasses::Get(context));

  cf::partners::FetchExamsClasses filter2(
      kEmptyInfo, models::Classes({"econom", "comfortplus"}), {}, extra_exams);

  // econom - doesn't need exam, comfortplus - driver doesn't have business exam
  context = GetContext("uid3");
  result = filter2.Process(member, context);
  EXPECT_EQ(models::Classes({"econom"}),
            cf::partners::FetchExamsClasses::Get(context));

  // econom - doesn't need exam, comfortplus - driver has exams business,
  // comfortplus
  context = GetContext("uid5");
  result = filter2.Process(member, context);
  EXPECT_EQ(models::Classes({"econom", "comfortplus"}),
            cf::partners::FetchExamsClasses::Get(context));
}
