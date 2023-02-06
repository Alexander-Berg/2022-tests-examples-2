#include <gtest/gtest.h>
#include <sstream>
#include <unordered_map>

#include <utils/helpers/enum_hash.hpp>
#include "bonus.hpp"

namespace {
std::string ToString(const models::dispatch::BonusInfo& bonus_info) {
  std::ostringstream stream;
  stream << bonus_info;
  return stream.str();
}

Json::Value GetDefaultJson() {
  Json::Value ret;
  ret["eta_etr"] = 0;
  ret["grade"] = 0;
  ret["class"] = 0;
  ret["new_driver"] = 0;
  ret["home_button"] = 0;
  ret["airport_queue"] = 0;
  ret["tags"] = 0;
  ret["park"] = 0;
  ret["surge_area"] = 0;
  ret["reposition"] = 0;
  ret["approximate_position"] = 0;
  ret["surges_ratio"] = 0;
  ret["verybusy"] = 0;
  return ret;
}
}  // namespace

TEST(BonusInfo, TestSet) {
  models::dispatch::BonusInfo bi;
  ASSERT_EQ(0, bi[models::dispatch::BonusInfo::Type::kTags]);

  bi[models::dispatch::BonusInfo::Type::kTags] = 10;
  ASSERT_EQ(10, bi[models::dispatch::BonusInfo::Type::kTags]);

  ASSERT_THROW(bi[models::dispatch::BonusInfo::Type::kSize], std::out_of_range);
  ASSERT_THROW(bi[static_cast<models::dispatch::BonusInfo::Type>(100000)],
               std::out_of_range);
}

TEST(BonusInfo, TestLogging) {
  models::dispatch::BonusInfo bi;

  ASSERT_EQ(ToString(bi),
            "eta_etr 0, grade 0, class 0, new_driver 0, home_button 0, "
            "airport_queue 0, tags 0, park 0, surge_area 0, "
            "reposition 0, approximate_position 0, surges_ratio 0, verybusy 0");

  bi[models::dispatch::BonusInfo::Type::kGrade] = 10;
  ASSERT_EQ(ToString(bi),
            "eta_etr 0, grade 10, class 0, new_driver 0, home_button 0, "
            "airport_queue 0, tags 0, park 0, surge_area 0, reposition 0, "
            "approximate_position 0, surges_ratio 0, verybusy 0");

  bi[models::dispatch::BonusInfo::Type::kPark] = 20;
  ASSERT_EQ(ToString(bi),
            "eta_etr 0, grade 10, class 0, new_driver 0, home_button 0, "
            "airport_queue 0, tags 0, park 20, surge_area 0, reposition 0, "
            "approximate_position 0, surges_ratio 0, verybusy 0");
}

TEST(BonusInfo, TestJsonify) {
  models::dispatch::BonusInfo bi;
  Json::Value orig_json = GetDefaultJson();

  ASSERT_EQ(bi.ToJson(), orig_json);

  bi[models::dispatch::BonusInfo::Type::kGrade] = 10;
  orig_json["grade"] = 10;

  ASSERT_EQ(bi.ToJson(), orig_json);

  bi[models::dispatch::BonusInfo::Type::kPark] = 20;
  orig_json["park"] = 20;

  ASSERT_EQ(bi.ToJson(), orig_json);
}

namespace {
using BonusInfo = models::dispatch::BonusInfo;
using Bonus = models::dispatch::BonusInfo::Type;

struct TotalTestData {
  boost::optional<int32_t> maximum_positive;
  boost::optional<int32_t> minimum_negative;
  EnumUnorderedMap<Bonus, int32_t> bonuses;
  int32_t expected;
};

std::vector<TotalTestData> total_data{
    {boost::none, -20, {{Bonus::kTags, 20}}, 20},
    {20, boost::none, {{Bonus::kSurgeArea, -20}}, -20},
    {boost::none, boost::none, {{Bonus::kTags, 2}, {Bonus::kSurgeArea, -2}}, 0},
    {10, -10, {{Bonus::kTags, 20}}, 10},
    {100, -10, {{Bonus::kTags, 20}, {Bonus::kPark, 20}}, 40},
    {10, -10, {}, 0},
    {20, -10, {{Bonus::kTags, 20}}, 20},
    {10, -10, {{Bonus::kSurgeArea, -20}}, -10},
    {10, -15, {{Bonus::kSurgeArea, -10}, {Bonus::kAirportQueue, -10}}, -15},
    {10, -10, {{Bonus::kTags, 15}, {Bonus::kSurgeArea, -5}}, 5},
    {boost::none, -5, {{Bonus::kTags, 15}, {Bonus::kSurgeArea, -15}}, 10},
    {5, boost::none, {{Bonus::kTags, 15}, {Bonus::kSurgeArea, -15}}, -10}};
}  // namespace

class BonusInfoTotalTest : public ::testing::TestWithParam<TotalTestData> {};

TEST_P(BonusInfoTotalTest, Parametrized) {
  const auto& params = GetParam();

  models::dispatch::BonusInfo bi;
  for (const auto& it : params.bonuses) {
    bi[it.first] = it.second;
  }

  ASSERT_EQ(params.expected,
            bi.GetTotal(params.maximum_positive, params.minimum_negative));
}

INSTANTIATE_TEST_CASE_P(BonusInfo, BonusInfoTotalTest,
                        ::testing::ValuesIn(total_data), );
