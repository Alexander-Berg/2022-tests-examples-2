#include <gtest/gtest.h>

#include <string>

#include <ml/common/filesystem.hpp>
#include <ml/common/json.hpp>
#include <ml/eats/suggest/mappings/v1.hpp>
#include <ml/eats/suggest/v1/mappings/generated/objects.hpp>
#include <vector>

#include "common/utils.hpp"

namespace {
namespace generated = ml::eats::suggest::v1::mappings::generated;
namespace mappings = ml::eats::suggest::mappings::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("eats/mappings");
}  // namespace

TEST(ParseUniversalItem, LocalToUniversalItem) {
  const generated::LocalToUniversalItem expected{
      0,            // place_menu_item_id
      "testid123",  // universal_id
  };

  const auto kJson = R"({"place_menu_item_id":0,"universal_id":"testid123"})";
  const auto actual =
      ml::common::FromJsonString<generated::LocalToUniversalItem>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(ParseLocalItem, UniversalToLocalItem) {
  std::vector<int64_t> sorted_equivalent_ids = {4, 8, 15, 16, 23, 42};
  const generated::UniversalToLocalItem expected{
      "124idtest",           // universal_id
      2,                     // place_id
      sorted_equivalent_ids  // sorted_equivalent_ids
  };

  const auto kJson =
      R"({"universal_id":"124idtest","place_id":2,"sorted_equivalent_ids":[4, 8, 15, 16, 23, 42]})";
  const auto actual =
      ml::common::FromJsonString<generated::UniversalToLocalItem>(kJson);

  ASSERT_EQ(expected, actual);
}

TEST(LoadStaticMappingsFromDir, Simple) {
  std::vector<int64_t> local_item2_expected_equivalent_ids = {544109648,
                                                              544109528};
  std::vector<int64_t> local_item3_expected_equivalent_ids = {18573625,
                                                              13748117};
  ASSERT_NO_THROW(
      auto mappings_obj = mappings::LoadStaticMappingsFromDir(kTestDataDir);

      {
        const auto universal_item = mappings_obj.GetUniversalId(31549);
        ASSERT_TRUE(!universal_item.has_value());

        const auto universal_item2 = mappings_obj.GetUniversalId(23247919);
        ASSERT_TRUE(universal_item2.has_value());
        ASSERT_EQ("d6aa26b976a8c6dbd9bd12a7654eada3", universal_item2.value());

        const auto universal_item3 = mappings_obj.GetUniversalId(23294851);
        ASSERT_TRUE(universal_item3.has_value());
        ASSERT_EQ("f6cba62d167707bf9eea88f7495cc08b", universal_item3.value());
      }

      {
        const auto local_item =
            mappings_obj.GetEquivalentIds(31549, "nonexistent_item_id");
        ASSERT_TRUE(!local_item.has_value());

        const auto local_item2 = mappings_obj.GetEquivalentIds(
            2, "40c4dababce4e23ba39d754500d9ac7b");
        ASSERT_TRUE(local_item2.has_value());
        ASSERT_EQ(local_item2_expected_equivalent_ids, local_item2.value());

        const auto local_item3 = mappings_obj.GetEquivalentIds(
            3, "d7f0351be67cc53a32c3878788bf4c81");
        ASSERT_TRUE(local_item3.has_value());
        ASSERT_EQ(local_item3_expected_equivalent_ids, local_item3.value());
      });
}
