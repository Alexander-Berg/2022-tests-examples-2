#include <gtest/gtest.h>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>

#include <taxi_config/variables/EXTRA_EXAMS_BY_ZONE.hpp>

#include "extra_exams.hpp"

TEST(ExtraExamsTest, Sample) {
  const auto conf = R"({
    "moscow": {
      "vip": ["business"],
      "comfortplus": ["comfortplus", "business"]
    }
  })";
  dynamic_config::StorageMock config_storage{
      {taxi_config::EXTRA_EXAMS_BY_ZONE, formats::json::FromString(conf)}};
  const auto config = config_storage.GetSnapshot();

  models::ExtraExams extra_exams{};

  EXPECT_EQ(extra_exams,
            models::GetExtraExams("spb", models::Classes({"econom"}), config));

  EXPECT_EQ(extra_exams, models::GetExtraExams(
                             "moscow", models::Classes({"econom"}), config));

  const auto class_type_vip = models::ClassesMapper::Parse("vip");
  extra_exams[class_type_vip] = models::drivers::Exams({"business"});

  EXPECT_EQ(extra_exams,
            models::GetExtraExams("moscow", models::Classes({"econom", "vip"}),
                                  config));

  const auto class_type_comfortplus =
      models::ClassesMapper::Parse("comfortplus");
  extra_exams[class_type_comfortplus] =
      models::drivers::Exams({"comfortplus", "business"});

  EXPECT_EQ(
      extra_exams,
      models::GetExtraExams(
          "moscow", models::Classes({"econom", "vip", "comfortplus"}), config));
}
