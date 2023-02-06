#include <gtest/gtest.h>

#include <clients/eats-order-revision/definitions.hpp>

#include "revisions.hpp"

using namespace eats_retail_order_history;

using RevisionTags = std::vector<std::string>;
using RevisionListItem = clients::eats_order_revision::RevisionListItem;

TEST(TestFilterRevisions, Middle) {
  std::vector<RevisionListItem> revisions{
      {"0", {}}, {"1", {}}, {"2", RevisionTags{"closed"}}, {"3", {}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  std::vector<RevisionListItem> expected{
      {"0", {}}, {"1", {}}, {"2", RevisionTags{"closed"}}};
  ASSERT_EQ(revisions, expected);
}

TEST(TestFilterRevisions, Begin) {
  std::vector<RevisionListItem> revisions{
      {"0", RevisionTags{"closed"}}, {"1", {}}, {"2", {}}, {"3", {}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  std::vector<RevisionListItem> expected{{"0", RevisionTags{"closed"}}};
  ASSERT_EQ(revisions, revisions);
}

TEST(TestFilterRevisions, End) {
  std::vector<RevisionListItem> revisions{
      {"0", {}}, {"1", {}}, {"2", {}}, {"3", RevisionTags{"closed"}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  ASSERT_EQ(revisions, revisions);
}

TEST(TestFilterRevisions, MultipleClosed) {
  std::vector<RevisionListItem> revisions{
      {"0", {}}, {"1", RevisionTags{"closed"}}, {"2", RevisionTags{"closed"}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  std::vector<RevisionListItem> expected{{"0", {}},
                                         {"1", RevisionTags{"closed"}}};
  ASSERT_EQ(revisions, expected);
}

TEST(TestFilterRevisions, DifferentTags) {
  std::vector<RevisionListItem> revisions{
      {"0", {}},
      {"1", RevisionTags{"delivered"}},
      {"2", RevisionTags{"delivered", "closed"}},
      {"3", {}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  std::vector<RevisionListItem> expected{
      {"0", {}},
      {"1", RevisionTags{"delivered"}},
      {"2", RevisionTags{"delivered", "closed"}}};
  ASSERT_EQ(revisions, expected);
}

TEST(TestFilterRevisions, NoClosed) {
  std::vector<RevisionListItem> revisions{{"0", {}}, {"1", {}}, {"2", {}}};
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  ASSERT_EQ(revisions, revisions);
}

TEST(TestFilterRevisions, Empty) {
  std::vector<RevisionListItem> revisions;
  revisions = RemoveRevisionsAfterClosed(std::move(revisions));
  ASSERT_EQ(revisions, revisions);
}
