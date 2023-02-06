#include <eats-catalog-storage-cache/models/missing_revision.hpp>
#include <eats-catalog-storage-cache/models/revision.hpp>

#include <chrono>
#include <string>
#include <vector>

#include <userver/dump/test_helpers.hpp>
#include <userver/utils/mock_now.hpp>

#include <userver/dump/aggregates.hpp>
#include <userver/dump/common.hpp>
#include <userver/dump/common_containers.hpp>
#include <userver/dump/operations.hpp>

#include <gtest/gtest.h>

namespace eats_catalog_storage_cache::models {

namespace {

constexpr const auto kDefaultMissInterval = std::chrono::seconds(60);

using TestRevision = models::Revision<int, std::string>;

TestRevision NewRevision(int id) {
  return TestRevision{RevisionId(id), ::utils::datetime::Now()};
}

void AssertEqual(const std::vector<MissingRevisionsBatch>& lhs,
                 const std::vector<MissingRevisionsBatch>& rhs) {
  ASSERT_EQ(lhs.size(), rhs.size());
  for (size_t i = 0; i < lhs.size(); i++) {
    std::vector<MissingRevision> left(lhs[i].first, lhs[i].second);
    std::vector<MissingRevision> right(rhs[i].first, rhs[i].second);

    ASSERT_EQ(left, right);
  }
}

}  // namespace

TEST(GetMissingRevisions, empty) {
  std::vector<TestRevision> revisions;
  const auto missing = GetMissingRevisions(revisions, kDefaultMissInterval);
  ASSERT_TRUE(missing.empty());
}

TEST(GetMissingRevisions, contiguos) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(2));
  revisions.push_back(NewRevision(3));

  const auto missing = GetMissingRevisions(revisions, kDefaultMissInterval);

  ASSERT_TRUE(missing.empty());
}

TEST(GetMissingRevisions, single_miss) {
  std::vector<TestRevision> revisions;

  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(2));
  revisions.push_back(NewRevision(4));

  const auto missing = GetMissingRevisions(revisions, kDefaultMissInterval);
  const std::vector<MissingRevision> expected = {
      {RevisionId(3), ::utils::datetime::SteadyNow()}};

  ::utils::datetime::MockNowUnset();

  ASSERT_EQ(expected, missing);
}

TEST(GetMissingRevisions, range_miss) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(5));
  revisions.push_back(NewRevision(8));

  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const auto missing =
      models::GetMissingRevisions(revisions, kDefaultMissInterval);
  const std::vector<MissingRevision> expected = {
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
      {RevisionId(7), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  ASSERT_EQ(expected, missing);
}

TEST(GetMissingRevisions, skip_old) {
  std::vector<TestRevision> revisions;

  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const auto skip_update_stamp =
      now - (kDefaultMissInterval + std::chrono::seconds(1));
  ASSERT_TRUE(skip_update_stamp < ::utils::datetime::Now());

  revisions.push_back({RevisionId(1), skip_update_stamp});
  revisions.push_back(NewRevision(5));
  revisions.push_back(NewRevision(8));

  const auto missing = GetMissingRevisions(revisions, kDefaultMissInterval);
  const std::vector<MissingRevision> expected = {
      {RevisionId(6), ::utils::datetime::SteadyNow()},
      {RevisionId(7), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  ASSERT_EQ(expected, missing);
}

TEST(MergeMissingRevisions, empty) {
  const std::vector<MissingRevision> left;
  const std::vector<MissingRevision> right;

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_TRUE(merged.empty());
}

TEST(MergeMissingRevisions, left) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> left = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
  };
  const std::vector<MissingRevision> right;

  ::utils::datetime::MockNowUnset();

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_EQ(merged, left);
}

TEST(MergeMissingRevisions, right) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> left;
  const std::vector<MissingRevision> right = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_EQ(merged, right);
}

TEST(MergeMissingRevisions, contiguos) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> left = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
  };
  const std::vector<MissingRevision> right = {
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(5), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
  };

  const std::vector<MissingRevision> expected = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(5), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_EQ(merged, expected);
}

TEST(MergeMissingRevisions, mixed) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> left = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(5), ::utils::datetime::SteadyNow()},
  };
  const std::vector<MissingRevision> right = {
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
  };

  const std::vector<MissingRevision> expected = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(5), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_EQ(merged, expected);
}

TEST(MergeMissingRevisions, unique) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T09:31:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> left = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
  };
  const std::vector<MissingRevision> right = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
  };

  const std::vector<MissingRevision> expected = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto merged = MergeMissingRevisions(left, right);
  ASSERT_EQ(merged, expected);
}

TEST(CountRevisionMisses, empty) {
  std::vector<TestRevision> revisions;

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 0);
}

TEST(CountRevisionMisses, single_no_miss) {
  std::vector<TestRevision> revisions;
  revisions.push_back(NewRevision(1));

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 0);
}

TEST(CountRevisionMisses, no_misses) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(2));
  revisions.push_back(NewRevision(3));

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 0);
}

TEST(CountRevisionMisses, single) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(3));

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 1);
}

TEST(CountRevisionMisses, two_no_skip) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(4));

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 2);
}

TEST(CountRevisionMisses, two_with_skip) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(3));
  revisions.push_back(NewRevision(5));

  const auto misses_count = CountRevisionMisses(revisions);
  ASSERT_EQ(misses_count, 2);
}

TEST(CountRevisionMisses, hundred) {
  std::vector<TestRevision> revisions;

  revisions.push_back(NewRevision(1));
  revisions.push_back(NewRevision(100));

  const auto misses_count = CountRevisionMisses(revisions);

  // т.к. у нас всего 100 ревизий между 1 и 100-й включительно, но 1 и 100-я
  // есть.
  ASSERT_EQ(misses_count, 98);
}

TEST(SplitByBatches, empty) {
  std::vector<MissingRevision> revisions;
  const auto batches = SplitByBatches(revisions, 1'000'000);
  ASSERT_TRUE(batches.empty());
}

TEST(SplitByBatches, less_than_batch_size) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T19:45:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  std::vector<MissingRevision> revisions = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto batches = SplitByBatches(revisions, 1'000'000);
  const std::vector<MissingRevisionsBatch> expected = {
      {revisions.begin(), revisions.end()}};

  AssertEqual(batches, expected);
}

TEST(SplitByBatches, triples) {
  const auto now = ::utils::datetime::Stringtime(
      "2021-02-17T19:45:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  std::vector<MissingRevision> revisions = {
      {RevisionId(1), ::utils::datetime::SteadyNow()},
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
      {RevisionId(5), ::utils::datetime::SteadyNow()},
      {RevisionId(6), ::utils::datetime::SteadyNow()},
      {RevisionId(7), ::utils::datetime::SteadyNow()},
  };

  ::utils::datetime::MockNowUnset();

  const auto batches = SplitByBatches(revisions, 3);
  const std::vector<MissingRevisionsBatch> expected = {
      {
          revisions.begin(),
          std::next(revisions.begin(), 3),
      },
      {
          std::next(revisions.begin(), 3),
          std::next(revisions.begin(), 6),
      },
      {
          std::next(revisions.begin(), 6),
          revisions.end(),
      },
  };

  AssertEqual(batches, expected);
}

TEST(GetMisingRevisions, equal_ids) {
  const auto first = RevisionId(1);
  const auto last = RevisionId(1);
  ASSERT_TRUE(GetMissingRevisions(first, last).empty());
}

TEST(GetMissingRevisions, ids_range) {
  const auto first = RevisionId(1);
  const auto last = RevisionId(5);

  const auto now = ::utils::datetime::Stringtime(
      "2021-02-19T10:15:00+00:00", "UTC", ::utils::datetime::kRfc3339Format);
  ::utils::datetime::MockNowSet(now);

  const std::vector<MissingRevision> expected = {
      {RevisionId(2), ::utils::datetime::SteadyNow()},
      {RevisionId(3), ::utils::datetime::SteadyNow()},
      {RevisionId(4), ::utils::datetime::SteadyNow()},
  };
  const auto actual = GetMissingRevisions(first, last);

  ::utils::datetime::MockNowUnset();

  ASSERT_EQ(expected, actual);
}

TEST(MissingRevisionDump, empty_ok) {
  dump::TestWriteReadCycle(MissingRevision{});
}

TEST(MissingRevisionDump, simple) {
  MissingRevision revision;

  revision.id = RevisionId(1);
  revision.missing_since = ::utils::datetime::SteadyNow();

  dump::TestWriteReadCycle(revision);
}

TEST(RevisionDump, SimpleTestRevision) {
  TestRevision tr;

  tr.id = RevisionId(1);
  tr.updated_at = ::utils::datetime::Now();
  tr.key = 10;
  tr.value = "hello";
  tr.archived = false;

  auto binary = dump::ToBinary(tr);
  const auto actual = dump::FromBinary<TestRevision>(binary);

  ASSERT_EQ(tr.id, actual.id);
  ASSERT_EQ(tr.updated_at, actual.updated_at);
  ASSERT_EQ(tr.key, actual.key);
  ASSERT_EQ(tr.value, actual.value);
  ASSERT_EQ(tr.archived, actual.archived);
}

}  // namespace eats_catalog_storage_cache::models

template <>
struct dump::IsDumpedAggregate<
    eats_catalog_storage_cache::models::TestRevision> {};
