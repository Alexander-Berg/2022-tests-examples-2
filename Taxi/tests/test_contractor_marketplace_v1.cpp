#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/common/json.hpp>
#include <ml/common/resources.hpp>
#include <ml/contractors/marketplace/resources/v1/objects.hpp>
#include <ml/contractors/marketplace/resources/v1/static_resource.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("contractors_marketplace_v1");
}  // namespace

TEST(MarketPlaceResourceV1, load_resource) {
  const auto resources_path = kTestDataDir + "/resources_dir";

  auto resource = ml::contractors::marketplace::resources::v1::static_resource::
      LoadStaticResource(kTestDataDir);

  ASSERT_FALSE(resource->GetOfferInfo("wdwdwdwdw"));
  ASSERT_FALSE(resource->GetContractorInfo("fake"));
  ASSERT_FALSE(resource->GetCategoryInfo("fake"));
  ASSERT_EQ(resource->GetCategoryInfo("groceries")->category_name, "groceries");
  ASSERT_EQ(resource->GetContractorInfo("8d3b42f990394945b5e4d9dd19858470")
                ->most_frequent_tariff,
            "econom");
  std::unordered_set<std::string> expected_category_offers{
      "04339d2895f54252ad53be26e736e8de", "13b51d3f6c5e4577b02f2207982fd719"};
  ASSERT_EQ(resource->GetIntegralStatistics().viewed, 13524.0);
  ASSERT_EQ(resource->GetIntegralStatistics().done_final_step, 93.0);
  ASSERT_EQ(resource->GetStatisticsWithinCategory("car_maintenance", "econom")
                ->done_final_step,
            7.0);
  const auto* resource_category_offers =
      resource->GetCategoryOffers("car_maintenance");
  ASSERT_EQ(expected_category_offers.size(), resource_category_offers->size());

  for (const auto& elem : *resource_category_offers) {
    ASSERT_TRUE(expected_category_offers.count(elem));
  }
}
