#include <gtest/gtest.h>

#include <string>

#include <ml/common/filesystem.hpp>
#include <ml/common/json.hpp>
#include <ml/eats/suggest/resources/v1.hpp>
#include <ml/eats/suggest/v1/resources/generated/objects.hpp>

#include "common/utils.hpp"

namespace {
namespace generated = ml::eats::suggest::v1::resources::generated;
namespace resources = ml::eats::suggest::resources::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats/suggest");
}  // namespace

TEST(ParseSuggestItem, SuggestItem) {
  const generated::SuggestItem expected{
      0,        // id
      123.456,  // npmi
  };

  const auto kJson = R"({"id":0,"npmi":123.456})";
  const auto actual = ml::common::FromJsonString<generated::SuggestItem>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(Parse, FallbackCandidateItem) {
  const generated::FallbackCandidateItem expected{
      0,  // id
  };

  const auto kJson = R"({"id":0})";
  const auto actual =
      ml::common::FromJsonString<generated::FallbackCandidateItem>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(ParseEquivalentItem, EquivalentItem) {
  std::vector<int64_t> complements = {0, 1, 2};
  const generated::EquivalentItem expected{
      0,            // place_menu_item_id
      complements,  // sorted_equivalent_ids
  };

  const auto kJson = R"({"place_menu_item_id":0,
                         "sorted_equivalent_ids":[0, 1, 2]})";
  const auto actual =
      ml::common::FromJsonString<generated::EquivalentItem>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(Parse, EatsItem) {
  std::vector<generated::SuggestItem> filler_vec;
  const generated::SuggestItem suggest1{
      345777279,  // id
      123.456,    // npmi
  };
  const generated::SuggestItem suggest2{
      345893179,  // id
      456.789,    // npmi
  };
  filler_vec.push_back(suggest1);
  filler_vec.push_back(suggest2);

  std::optional<std::vector<generated::SuggestItem>> filler{filler_vec};
  std::string category_name = "для собак";
  const generated::EatsItem expected{
      0,              // place_menu_item_id
      93798,          // brand_id
      406694,         // place_id
      5,              // price
      6,              // popularity
      category_name,  // category_name
      0,              // additions
      0,              // views
      filler,         // suggest
  };
  const auto kJson =
      R"({"place_menu_item_id":0,"brand_id":93798,"place_id":406694,
      "price":5,"popularity":6,"category_name":"для собак","additions":0,"views":0,"suggest":
      [{"id":345777279,"npmi":123.456},
       {"id":345893179,"npmi":456.789}]})";

  const auto actual = ml::common::FromJsonString<generated::EatsItem>(kJson);
  ASSERT_EQ(expected, actual);
  ASSERT_TRUE(actual.suggest.has_value());
}

TEST(Parse, PlaceFallbackItems) {
  std::vector<generated::FallbackCandidateItem> filler_vec;
  const generated::FallbackCandidateItem item1{303673922};
  const generated::FallbackCandidateItem item2{3036739223};
  filler_vec.push_back(item1);
  filler_vec.push_back(item2);

  std::optional<std::vector<generated::FallbackCandidateItem>> filler{
      filler_vec};

  const generated::PlaceFallbackItems expected{
      93798,  // place_menu_item_id
      378497,
      filler,  // sorted_equivalent_ids
  };

  const auto kJson = R"({"brand_id": 93798, "place_id": 378497,
                         "suggest": [{"id": 303673922},
                         {"id": 3036739223}]})";
  const auto actual =
      ml::common::FromJsonString<generated::PlaceFallbackItems>(kJson);

  ASSERT_EQ(expected, actual);
  ASSERT_TRUE(actual.suggest.has_value());
}

TEST(LoadResourcesFromDir, Simple) {
  ASSERT_NO_THROW(
      auto resources_obj = resources::LoadStaticResourcesFromDir(kTestDataDir);

      {
        const auto candidates = resources_obj.GetCandidatesForItem(463735768);
        ASSERT_TRUE(candidates.has_value());
        ASSERT_TRUE(candidates.value()->suggest.has_value());

        const auto candidates2 = resources_obj.GetCandidatesForItem(345880914);
        ASSERT_TRUE(candidates2.has_value());
        ASSERT_TRUE(candidates2.value()->suggest.has_value());
      }

      {
        const auto equiv_ids = resources_obj.GetEquivalentIdsForItem(221975);
        ASSERT_TRUE(equiv_ids.empty());

        const auto equiv_ids2 =
            resources_obj.GetEquivalentIdsForItem(156608957);
        ASSERT_FALSE(equiv_ids2.empty());
      }

      {
        const auto fallback_items = resources_obj.GetFallbackItems(373183);
        ASSERT_TRUE(fallback_items.has_value());
        ASSERT_TRUE(fallback_items.value()->suggest.has_value());

        const auto fallback_items2 = resources_obj.GetFallbackItems(378497);
        ASSERT_TRUE(fallback_items2.has_value());
        ASSERT_TRUE(fallback_items2.value()->suggest.has_value());
      });
}