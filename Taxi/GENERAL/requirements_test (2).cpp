#include <virtual-tariffs/models/requirements.hpp>

#include <gtest/gtest.h>

#include <string>
#include <unordered_set>

using namespace virtual_tariffs::models;

TEST(VirtualTariffs, RequirementsTest) {
  using TagsContext = std::unordered_set<std::string>;

  TagsContext tags_from_cache = {"tag1", "tag2", "tag3", "tag4"};

  auto functor = MakeFunctor("Tags", "ContainsAll", {"tag1", "tag2", "tag3"});
  EXPECT_TRUE(functor->Apply(tags_from_cache));
  Requirement requirement(RequirementId::kTags, OperationId::kContainsAll,
                          {"tag1", "tag2", "tag3"});
  EXPECT_TRUE(ApplyById(tags_from_cache, RequirementId::kTags, functor));
  EXPECT_TRUE(requirement.Apply(tags_from_cache));

  EXPECT_THROW(MakeFunctor("pizza_delivery", "Greater", {"10"}),
               std::logic_error);
}
