#include <userver/utest/utest.hpp>

#include <discounts-match/components/rules_match_hierarchy_conditions.hpp>

TEST(RulesMatchHierarchyConditions, GetValidatedMatchedDataCreators) {
  const rules_match::MatchedDataCreators creators{
      {{"hierarchy_name",
        rules_match::MakeMatchedDataCreator<formats::json::Value>()}}};
  EXPECT_NO_THROW(
      rules_match::components::RulesMatchHierarchyConditions::
          GetValidatedMatchedDataCreators(creators, {{"hierarchy_name", {}}}));
  EXPECT_THROW(rules_match::components::RulesMatchHierarchyConditions::
                   GetValidatedMatchedDataCreators(
                       creators, {{"missing_hierarchy_name", {}}}),
               rules_match::MatchedDataCreatorNotFoundError);
  EXPECT_THROW(rules_match::components::RulesMatchHierarchyConditions::
                   GetValidatedMatchedDataCreators(
                       creators, {{"missing_hierarchy_name", {}},
                                  {"hierarchy_name", {}}}),
               rules_match::MatchedDataCreatorNotFoundError);
}
