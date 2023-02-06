#include <userver/formats/json.hpp>
#include <userver/storages/postgres/io/range_types.hpp>
#include <userver/utest/utest.hpp>

#include <views/match_tree_view.hpp>

namespace {
namespace views = rules_match::views;

const rules_match::models::Hierarchy kHierarchy{
    formats::json::FromString(R"JSON(
{
    "name": "some_hierarchy",
    "conditions": [
        {
            "condition_name": "integer_other",
            "default": {"value_type": "Other"},
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "text_any_other",
            "default": {"value_type": "Other"},
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "zone",
            "default": {
                "value": {
                    "name": "br_root",
                    "is_prioritized": false,
                    "type": "geonode"
                }
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "zone"
        },
        {
            "condition_name": "integer_any_other",
            "default": {"value_type": "Other"},
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "array",
            "default": {"value": []},
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "array"
        },
        {
            "condition_name": "double_range_exclusions_any_other",
            "default": {"value_type": "Other"},
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "double_range"
        }
    ]
}
)JSON")
        .As<handlers::libraries::discounts_match::HierarchyDescription>()};

}  // namespace

TEST(RevisionsRanges, AddRevisionTest) {
  std::vector<views::RevisionsRange> revisions;
  views::AddRevision(revisions, rules_match::RulesMatchBase::Revision{0});
  std::vector<views::RevisionsRange> expected_revisions{{0, 0}};
  EXPECT_EQ(revisions, expected_revisions);
  views::AddRevision(revisions, rules_match::RulesMatchBase::Revision{1});
  expected_revisions.back().end = 1;
  EXPECT_EQ(revisions, expected_revisions);
  views::AddRevision(revisions, rules_match::RulesMatchBase::Revision{2});
  expected_revisions.back().end = 2;
  EXPECT_EQ(revisions, expected_revisions);
  views::AddRevision(revisions, rules_match::RulesMatchBase::Revision{4});
  expected_revisions.push_back(views::RevisionsRange{4, 4});
  EXPECT_EQ(revisions, expected_revisions);
}

TEST(RevisionsRanges, GenerateRevisionsTest) {
  namespace pg = storages::postgres;
  auto revisions =
      views::GenerateRevisions(rules_match::RulesMatchBase::Revision{0}, {}, 0);
  EXPECT_TRUE(revisions.empty());
  revisions =
      views::GenerateRevisions(rules_match::RulesMatchBase::Revision{0},
                               std::vector<pg::BoundedBigintRange>{{1, 20}}, 0);
  EXPECT_TRUE(revisions.empty());

  revisions =
      views::GenerateRevisions(rules_match::RulesMatchBase::Revision{0},
                               std::vector<pg::BoundedBigintRange>{{1, 20}}, 5);

  EXPECT_EQ(revisions,
            (std::vector<rules_match::RulesMatchBase::Revision::UnderlyingType>{
                1, 2, 3, 4, 5}));

  revisions =
      views::GenerateRevisions(rules_match::RulesMatchBase::Revision{0},
                               std::vector<pg::BoundedBigintRange>{{1, 3}}, 5);

  EXPECT_EQ(revisions,
            (std::vector<rules_match::RulesMatchBase::Revision::UnderlyingType>{
                1, 2}));

  revisions =
      views::GenerateRevisions(rules_match::RulesMatchBase::Revision{5},
                               std::vector<pg::BoundedBigintRange>{{1, 20}}, 5);
  EXPECT_EQ(revisions,
            (std::vector<rules_match::RulesMatchBase::Revision::UnderlyingType>{
                6, 7, 8, 9, 10}));

  revisions = views::GenerateRevisions(
      rules_match::RulesMatchBase::Revision{5},
      std::vector<pg::BoundedBigintRange>{{1, 5}, {7, 8}, {9, 10}, {11, 16}},
      5);
  EXPECT_EQ(revisions,
            (std::vector<rules_match::RulesMatchBase::Revision::UnderlyingType>{
                7, 9, 11, 12, 13}));

  revisions = views::GenerateRevisions(
      rules_match::RulesMatchBase::Revision{5},
      std::vector<pg::BoundedBigintRange>{{1, 7}, {7, 8}}, 5);
  EXPECT_EQ(revisions,
            (std::vector<rules_match::RulesMatchBase::Revision::UnderlyingType>{
                6, 7}));

  revisions = views::GenerateRevisions(
      rules_match::RulesMatchBase::Revision{10},
      std::vector<pg::BoundedBigintRange>{{1, 6}, {7, 8}}, 5);
  EXPECT_TRUE(revisions.empty());
}
