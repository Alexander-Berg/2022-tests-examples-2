#include "models/tariff_calc/tariff_preparer.hpp"

#include <gtest/gtest.h>

using namespace tariff_calc;

namespace {

tariff::Category MakeEmptyCategory(const std::string& name,
                                   utils::datetime::timepair_t time_from,
                                   utils::datetime::timepair_t time_to,
                                   tariff::DayType day_type,
                                   tariff::CategoryType category_type) {
  tariff::Category category;
  category.name = name;
  category.time_from = time_from;
  category.time_to = time_to;
  category.day_type = day_type;
  category.category_type = category_type;
  return category;
}

tariff::Category MakeCategoryWithTransfers(int transfers_count) {
  tariff::Category category;
  for (int i = 0; i < transfers_count; i++) {
    tariff::Transfer transfer;
    category.transfers.push_back(transfer);
  }
  return category;
}

}  // namespace

TEST(TariffPreparerTest, FilterByTime) {
  tariff::Tariff tariff;
  tariff.categories = {
      MakeEmptyCategory("econom", std::make_pair(0, 0), std::make_pair(9, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
      MakeEmptyCategory("econom", std::make_pair(9, 0), std::make_pair(12, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
      MakeEmptyCategory("econom", std::make_pair(12, 0), std::make_pair(23, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
  };

  auto result = tariff_calc::TariffPreparer(tariff)
                    .SelectCategories({10, 0, false},
                                      tariff::CategoryType::Application, {})
                    .GetTariff();

  EXPECT_EQ(result.categories.size(), (size_t)1);
  EXPECT_EQ(tariff.categories.size(), (size_t)3);  // should not be modified
}

TEST(TariffPreparerTest, FilterByCategory) {
  tariff::Tariff tariff;
  tariff.categories = {
      MakeEmptyCategory("econom", std::make_pair(0, 0), std::make_pair(2, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
      MakeEmptyCategory("business", std::make_pair(0, 0), std::make_pair(2, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
      MakeEmptyCategory("econom", std::make_pair(0, 0), std::make_pair(2, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
  };

  auto result =
      tariff_calc::TariffPreparer(tariff)
          .SelectCategories(
              {1, 0, false}, tariff::CategoryType::Application,
              tariff_calc::SurgeValues{{{"business", models::SurgeParams()}}})
          .GetTariff();

  EXPECT_EQ(result.categories.size(), (size_t)1);
  EXPECT_EQ(tariff.categories.size(), (size_t)3);  // should not be modified
}

TEST(TariffPreparerTest, FilterByCategoryType) {
  tariff::Tariff tariff;
  tariff.categories = {
      MakeEmptyCategory("econom", std::make_pair(0, 0), std::make_pair(2, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::Application),
      MakeEmptyCategory("econom", std::make_pair(0, 0), std::make_pair(2, 0),
                        tariff::DayType::Everyday,
                        tariff::CategoryType::CallCenter),
  };

  auto result =
      tariff_calc::TariffPreparer(tariff)
          .SelectCategories({1, 0, false}, tariff::CategoryType::CallCenter, {})
          .GetTariff();

  EXPECT_EQ(result.categories.size(), (size_t)1);
  EXPECT_EQ(tariff.categories.size(), (size_t)2);  // should not be modified
}

TEST(TariffPreparerTest, ForceFreeRoute) {
  tariff::Tariff tariff;
  tariff.categories = {
      MakeCategoryWithTransfers(1),
      MakeCategoryWithTransfers(0),
      MakeCategoryWithTransfers(4),
  };

  auto result =
      tariff_calc::TariffPreparer(tariff).ForceFreeRoute(true).GetTariff();

  EXPECT_EQ(result.categories.size(), (size_t)3);
  for (const auto& category : result.categories) {
    EXPECT_EQ(category.transfers.size(), (size_t)0);
  }
  EXPECT_EQ(tariff.categories[0].transfers.size(), (size_t)1);
  EXPECT_EQ(tariff.categories[1].transfers.size(), (size_t)0);
  EXPECT_EQ(tariff.categories[2].transfers.size(), (size_t)4);
}

TEST(TariffPreparerTest, TestGetParams) {
  tariff::Transfer transfer_without_jams;
  transfer_without_jams.route_without_jams = true;

  tariff::Transfer transfer_with_jams;
  transfer_with_jams.route_without_jams = false;

  tariff::Category category;

  tariff::Tariff tariff;
  tariff.categories = {category};

  tariff.categories[0].transfers = {};
  EXPECT_FALSE(tariff_calc::TariffPreparer(tariff)
                   .GetParams()
                   .contains_transfer_without_jams);

  tariff.categories[0].transfers = {transfer_with_jams};
  EXPECT_FALSE(tariff_calc::TariffPreparer(tariff)
                   .GetParams()
                   .contains_transfer_without_jams);

  tariff.categories[0].transfers = {transfer_without_jams};
  EXPECT_TRUE(tariff_calc::TariffPreparer(tariff)
                  .GetParams()
                  .contains_transfer_without_jams);

  tariff.categories[0].transfers = {transfer_with_jams, transfer_without_jams};
  EXPECT_TRUE(tariff_calc::TariffPreparer(tariff)
                  .GetParams()
                  .contains_transfer_without_jams);
}
