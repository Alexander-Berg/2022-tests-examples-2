#include <virtual-tariffs/models/requirements.hpp>

#include <gtest/gtest.h>

#include <string>
#include <unordered_set>

#include <testing/taxi_config.hpp>

using namespace virtual_tariffs::models;

TEST(VirtualTariffs, RequirementsTest) {
  using TagsContext = std::unordered_set<std::string>;

  TagsContext tags_from_cache = {"tag1", "tag2", "tag3", "tag4"};

  auto functor = MakeFunctor("Tags", "ContainsAll", {"tag1", "tag2", "tag3"});
  EXPECT_TRUE(functor->Apply(tags_from_cache));
  Requirement requirement(ContextId::kTags, RequirementId::kTags,
                          OperationId::kContainsAll, {"tag1", "tag2", "tag3"},
                          "special_requirement1");
  EXPECT_TRUE(ApplyById(tags_from_cache, RequirementId::kTags, functor,
                        dynamic_config::GetDefaultSnapshot()));
  EXPECT_TRUE(
      requirement.Apply(tags_from_cache, dynamic_config::GetDefaultSnapshot()));

  EXPECT_THROW(MakeFunctor("pizza_delivery", "Greater", {"10"}),
               std::logic_error);
}
