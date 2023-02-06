#include <discounts/models/discount_usages.hpp>

#include <gtest/gtest.h>

#include <userver/utils/boost_uuid4.hpp>

using namespace std::chrono_literals;

namespace {

const auto kSeriesId = utils::generators::GenerateBoostUuid();
using Usage = discounts::models::DiscountUsages::Usage;

}  // namespace

TEST(DiscountUsages, Count) {
  discounts::models::DiscountUsages usages;
  std::chrono::system_clock::time_point tp{10h};
  usages.Add(boost::uuids::uuid{kSeriesId}, {tp + 1h, tp - 2h, tp + 5h});
  EXPECT_EQ(usages.Count(kSeriesId, std::nullopt), 3);
  EXPECT_EQ(usages.Count(kSeriesId, tp - 4h), 3);
  EXPECT_EQ(usages.Count(kSeriesId, tp + 1h), 2);
  EXPECT_EQ(usages.Count(kSeriesId, tp + 3h), 1);
  EXPECT_EQ(usages.Count(kSeriesId, tp + 5h), 1);
  EXPECT_EQ(usages.Count(kSeriesId, tp + 10h), 0);
  EXPECT_EQ(usages.Count(utils::generators::GenerateBoostUuid(), tp), 0);
}

TEST(DiscountUsages, SpentBudget) {
  discounts::models::DiscountUsages usages;
  std::chrono::system_clock::time_point tp{10h};
  usages.Add(boost::uuids::uuid{kSeriesId},
             {{tp + 1h, 1}, {tp - 2h, 3}, {tp + 5h, 7}});
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, std::nullopt), 11);
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, tp - 4h), 11);
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, tp + 1h), 8);
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, tp + 3h), 7);
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, tp + 5h), 7);
  EXPECT_EQ(usages.GetSpentBudget(kSeriesId, tp + 10h), 0);
  EXPECT_EQ(usages.GetSpentBudget(utils::generators::GenerateBoostUuid(), tp),
            0);
}

TEST(DiscountUsages, ParseSerialize) {
  discounts::models::DiscountUsages usages;
  std::chrono::system_clock::time_point tp{10h};
  usages.Add(boost::uuids::uuid{kSeriesId},
             {{tp + 1h, 1}, {tp - 2h, 3}, {tp + 5h, 7}});
  usages.Add(utils::generators::GenerateBoostUuid(), {{tp + 6h}});
  EXPECT_EQ(usages, formats::json::ValueBuilder(usages)
                        .ExtractValue()
                        .As<discounts::models::DiscountUsages>());
}
