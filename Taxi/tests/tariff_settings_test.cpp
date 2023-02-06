#include <mongo/mongo.hpp>

#include "models/tariff_settings.hpp"

#include "utils/helpers/bson.hpp"
#include "utils/helpers/json.hpp"

#include <gtest/gtest.h>

using models::Classes;
using models::TariffSettings;
using Category = models::TariffSettings::Category;

TEST(TariffSettings, GetSimilarClass) {
  Category econom;
  econom.class_type = Classes::Econom;
  econom.service_levels = {50};

  Category business;
  business.class_type = Classes::Business;
  business.service_levels = {60};

  Category vip;
  vip.class_type = Classes::Vip;
  vip.service_levels = {70};

  Category uberx;
  uberx.class_type = Classes::UberX;
  uberx.service_levels = {50};

  // Getting by service_level
  std::vector<Category> categories = {vip, econom, business};  // not ordered

  EXPECT_EQ(Classes::Econom,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 30),
                                    categories));
  EXPECT_EQ(Classes::Econom,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 40),
                                    categories));
  EXPECT_EQ(Classes::Econom,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 50),
                                    categories));
  EXPECT_EQ(Classes::Business,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 57),
                                    categories));
  EXPECT_EQ(Classes::Business,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 60),
                                    categories));
  EXPECT_EQ(Classes::Business,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 63),
                                    categories));
  EXPECT_EQ(Classes::Vip,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 70),
                                    categories));
  EXPECT_EQ(Classes::Vip,
            models::GetSimilarClass(models::TariffImprint(Classes::Unknown, 80),
                                    categories));

  // Getting by class type + service_level (when service_level is not enough)
  std::vector<Category> yandex_uber = {uberx, econom};

  EXPECT_EQ(Classes::UberX,
            models::GetSimilarClass(models::TariffImprint(Classes::UberX, 50),
                                    yandex_uber));
  EXPECT_EQ(Classes::Econom,
            models::GetSimilarClass(models::TariffImprint(Classes::Econom, 50),
                                    yandex_uber));
}
