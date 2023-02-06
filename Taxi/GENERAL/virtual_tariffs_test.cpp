#include <virtual-tariffs/models/virtual_tariffs.hpp>

#include <gtest/gtest.h>

#include <models/classes.hpp>
#include <utils/helpers/json.hpp>

using namespace virtual_tariffs::models;

namespace {
const auto kTestJson = R"(
{
"order": {
  "virtual_tariffs": [
    {
      "class": "econom",
      "special_requirements": [
        {
          "id": "special_requirement"
        }
      ]
    }
  ]
}
}
)";

const auto kInvalidJson = R"(
{
  "virtual_tariffs": [
    {
      "class": "econom",
      "special_requirements": [
        {
          "id": "special_requirement"
        }
      ]
    }
  ]
}
)";
}  // namespace

TEST(VirtualTariffs, ParseParamsTest) {
  SpecialRequirements requirements = {
      {"special_requirement",
       {{{ContextId::kTags,
          {Requirement(RequirementId::kTags, OperationId::kContainsAll,
                       {"tag1", "tag2", "tag3"})}}}}}};

  VirtualTariffs virtual_tariffs(
      ContextId::kTags, utils::helpers::ParseJson(kTestJson), requirements);

  std::unordered_set<std::string>{"tag1", "tag2", "tag3"};

  EXPECT_TRUE(virtual_tariffs.Check(
      std::unordered_set<std::string>{"tag1", "tag2", "tag3"},
      models::Classes({"econom"})))
      << virtual_tariffs.ToString();
  EXPECT_TRUE(virtual_tariffs.Check(
      std::unordered_set<std::string>{"tag1", "tag2", "tag3", "tag4"},
      models::Classes({"econom"})))
      << virtual_tariffs.ToString();
  EXPECT_FALSE(
      virtual_tariffs.Check(std::unordered_set<std::string>{"tag1", "tag2"},
                            models::Classes({"econom"})))
      << virtual_tariffs.ToString();
  EXPECT_TRUE(
      virtual_tariffs.Check(std::unordered_set<std::string>{"tag1", "tag2"},
                            models::Classes({"econom", "business"})))
      << virtual_tariffs.ToString();

  EXPECT_TRUE(VirtualTariffs(ContextId::kTags,
                             utils::helpers::ParseJson(kInvalidJson),
                             requirements)
                  .IsEmpty());
}
