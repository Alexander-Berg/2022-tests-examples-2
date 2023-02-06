#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include "exam_score.hpp"

namespace cf = candidates::filters;

const cf::FilterInfo kEmptyInfo;

class ExamScoreTest : public testing::Test {
 protected:
  void SetUp() override {
    // exam_score = 5, allow
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license1", "license10"};
      unique_driver.exam_score = 5;
      unique_drivers["uid1"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    // exam_score = 1, disallow
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license2", "license20"};
      unique_driver.exam_score = 1;
      unique_drivers["uid2"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }

    // exam_score = none, allow
    {
      models::UniqueDriver unique_driver;
      unique_driver.licenses_ids = {"license3", "license30"};
      unique_drivers["uid3"] =
          std::make_shared<models::UniqueDriver>(std::move(unique_driver));
    }
  }

  cf::Context& GetContext(const std::string& unique_driver_id) {
    context.ClearData();
    cf::infrastructure::FetchUniqueDriver::Set(
        context, unique_drivers[unique_driver_id]);
    return context;
  }

  std::unordered_map<std::string, models::UniqueDriverPtr> unique_drivers;
  cf::Context context;
};

TEST_F(ExamScoreTest, Sample) {
  const int min_valid_exam_score = 2;
  cf::partners::ExamScore filter(kEmptyInfo, min_valid_exam_score);
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid1")));
  ASSERT_EQ(cf::Result::kDisallow, filter.Process({}, GetContext("uid2")));
  ASSERT_EQ(cf::Result::kAllow, filter.Process({}, GetContext("uid3")));
}
