#include <eats-catalog-storage-cache/caches/revision_cache.hpp>

#include <string>
#include <vector>

#include <userver/dump/test_helpers.hpp>
#include <userver/utils/datetime.hpp>

#include <gtest/gtest.h>

namespace eats_catalog_storage_cache::caches {

namespace {

using TestRevision = models::Revision<int, std::string>;
using TestCache = RevisionCache<TestRevision>;

TestRevision MockRevision(int id, std::string&& value) {
  TestRevision result;

  result.id = models::RevisionId(id);
  result.updated_at = ::utils::datetime::Now();
  result.key = id;
  result.value = value;
  result.archived = false;

  return result;
}

}  // namespace

TEST(DumpRevisionCache, empty) {
  TestCache cache;

  const auto binary = dump::ToBinary(cache);
  const auto actual = dump::FromBinary<TestCache>(binary);

  ASSERT_EQ(actual.size(), 0);
}

TEST(DumpRevisionCache, success) {
  TestCache cache;

  std::vector<TestRevision> revisions = {
      MockRevision(1, "test_1"),
      MockRevision(2, "test_2"),
      MockRevision(3, "test_3"),
      MockRevision(5, "test_5"),
  };
  const auto last_revision_id = revisions.back().id;
  const auto missing = GetMissingRevisions(revisions, std::chrono::seconds(60));

  cache.SetLastRevisionId(last_revision_id);
  cache.Insert(std::vector<TestRevision>(revisions));
  cache.SetMissingRevisions(missing);

  const auto binary = dump::ToBinary(cache);
  const auto actual = dump::FromBinary<TestCache>(binary);

  ASSERT_EQ(actual.size(), revisions.size());
  ASSERT_EQ(actual.GetLastRevisionId(), last_revision_id);

  ASSERT_TRUE(actual.GetValue(1).has_value());
  ASSERT_EQ(*actual.GetValue(1), revisions.front().value);

  ASSERT_FALSE(actual.GetValue(4).has_value());

  ASSERT_EQ(missing, actual.GetMissingRevisions());
}

}  // namespace eats_catalog_storage_cache::caches

template <>
struct dump::IsDumpedAggregate<
    eats_catalog_storage_cache::caches::TestRevision> {};
