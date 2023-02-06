#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>

#include <caches/match/entities_tags.hpp>

TEST(EntitesTagsCache, Empty) {
  caches::match::EntitiesTags cache;

  ASSERT_FALSE(cache
                   .FindId(models::Entity{models::EntityName{"unknown"},
                                          models::EntityType::kDbidUuid})
                   .has_value());
  ASSERT_EQ(cache.size(), 0u);
  ASSERT_EQ(cache.revision(), 0);
}

namespace {

using DbEntry = caches::match::EntityTagDbRow;

models::Match MatchFromDb(DbEntry db_entry) {
  return {models::TagNameId{db_entry.tag_name_id},
          models::ProviderId{db_entry.provider_id}, db_entry.ttl};
}

models::EntityName EntityNameFor(const int i) {
  return models::EntityName{"Entity_" + std::to_string(i)};
}

models::EntityType EntityTypeFor(const int i) {
  return i % 2 ? models::EntityType::kDbidUuid : models::EntityType::kParkCarId;
}

models::Entity EntityFor(const int i) {
  return models::Entity{EntityNameFor(i), EntityTypeFor(i)};
}

}  // namespace

UTEST(EntitesTagsCache, BasicInsertion) {
  static constexpr int32_t kEntitiesCount = 20;
  caches::match::EntitiesTags cache;

  std::vector<DbEntry> entries;
  for (int i = 0; i < kEntitiesCount; ++i) {
    const auto ttl = std::chrono::system_clock::time_point::max();
    entries.emplace_back(DbEntry{models::EntityId{i}, EntityNameFor(i),
                                 EntityTypeFor(i), models::TagNameId{i},
                                 models::ProviderId{i}, i, ttl, true});
  }

  for (const auto& entry : entries) {
    cache.insert_or_assign(entry.tag_name_id.GetUnderlying(), entry);
  }

  ASSERT_EQ(cache.size(), static_cast<size_t>(kEntitiesCount));
  ASSERT_EQ(cache.revision(), kEntitiesCount - 1);

  for (int i = 0; i < kEntitiesCount; i++) {
    const auto tags = cache.FindMatches(EntityFor(i));
    ASSERT_EQ(tags.size(), 1u);
    ASSERT_EQ(tags[0], MatchFromDb(entries[i]));
  }
}

UTEST(EntitesTagsCache, Deletion) {
  static constexpr int32_t kEntitiesCount = 20;
  caches::match::EntitiesTags cache;

  std::vector<DbEntry> entries;
  for (int i = 0; i < kEntitiesCount; i++) {
    const auto ttl = std::chrono::system_clock::time_point::max();
    entries.push_back(DbEntry{models::EntityId{i}, EntityNameFor(i),
                              EntityTypeFor(i), models::TagNameId{i},
                              models::ProviderId{i}, i, ttl, true});
  }

  for (const auto& entry : entries) {
    cache.insert_or_assign(entry.tag_name_id.GetUnderlying(), entry);
  }

  for (int i = 0; i < kEntitiesCount; i += 2) {
    DbEntry entry{entries[i]};
    entry.is_active = false;
    cache.insert_or_assign(entry.tag_name_id.GetUnderlying(), entry);
  }

  for (int i = 0; i < kEntitiesCount; i++) {
    const auto tags = cache.FindMatches(EntityFor(i));
    if (i % 2 == 0) {
      ASSERT_TRUE(tags.empty());
    } else {
      ASSERT_EQ(tags.size(), 1u);
      ASSERT_EQ(tags[0], MatchFromDb(entries[i]));
    }
  }
}

namespace {

template <typename T>
void VerifyVectorHas(const std::vector<T>& vec, const T& val) {
  ASSERT_TRUE(std::find(vec.begin(), vec.end(), val) != vec.end());
}

void VerifyCache(const caches::match::EntitiesTags& cache,
                 const std::vector<DbEntry>& entries, int32_t num_of_entities) {
  ASSERT_EQ(cache.size(), entries.size());
  for (int i = 0; i < num_of_entities; i++) {
    const auto tags = cache.FindMatches(EntityFor(i));
    ASSERT_EQ(tags.size(), 2u);
    VerifyVectorHas(tags, MatchFromDb(entries[i]));
    VerifyVectorHas(tags, MatchFromDb(entries[i + num_of_entities]));

    const auto entity_id = cache.FindId(EntityFor(i));
    ASSERT_TRUE(entity_id.has_value());
    ASSERT_EQ(entity_id->GetUnderlying(), i);
  }
}

}  // namespace

UTEST(EntitesTagsCache, IterativeUpdates) {
  static constexpr int32_t kEntitiesCount = 20;
  caches::match::EntitiesTags cache0;

  std::vector<DbEntry> entries;
  for (int i = 0; i < kEntitiesCount * 2; i++) {
    const auto ttl = std::chrono::system_clock::time_point::max();
    const int entity_id = i % kEntitiesCount;
    entries.push_back({models::EntityId{entity_id}, EntityNameFor(entity_id),
                       EntityTypeFor(entity_id), models::TagNameId{i},
                       models::ProviderId{i}, i, ttl, true});
  }

  for (int i = 0; i < kEntitiesCount; i++) {
    cache0.insert_or_assign(entries[i].revision, entries[i]);
  }
  ASSERT_EQ(cache0.size(), static_cast<size_t>(kEntitiesCount));
  for (int i = 0; i < kEntitiesCount; i++) {
    const auto tags = cache0.FindMatches(EntityFor(i));
    ASSERT_EQ(tags.size(), 1u);
    ASSERT_EQ(tags[0], MatchFromDb(entries[i]));
  }

  caches::match::EntitiesTags cache1 = cache0;
  ASSERT_EQ(cache1.revision(), cache0.revision());
  for (int i = 0; i < kEntitiesCount * 2; i++) {
    cache1.insert_or_assign(entries[i].revision, entries[i]);
  }
  VerifyCache(cache1, entries, kEntitiesCount);

  caches::match::EntitiesTags cache2 = cache1;
  ASSERT_EQ(cache2.revision(), cache1.revision());
  for (int i = 0; i < kEntitiesCount; i++) {
    entries[i].ttl =
        std::chrono::system_clock::now() + std::chrono::seconds(10);
    cache2.insert_or_assign(entries[i].revision, entries[i]);
  }
  VerifyCache(cache2, entries, kEntitiesCount);
}

TEST(EntitesTagsCache, DumpRestoreEmpty) {
  dump::TestWriteReadCycle(caches::match::EntitiesTags{});
}

TEST(EntitesTagsCache, DumpRestoreEmptyFixedBuckets) {
  dump::TestWriteReadCycle(caches::match::EntitiesTags{});
}

TEST(EntitesTagsCache, DumpRestoreFilled) {
  caches::match::EntitiesTags cache;

  for (int i = 0; i < 1024; ++i) {
    const int64_t revision = i * 2;
    cache.insert_or_assign(
        0,
        {models::EntityId{i}, EntityNameFor(i), EntityTypeFor(i),
         models::TagNameId{i % 100}, models::ProviderId{i % 100 + 5}, revision,
         i % 2 ? utils::kInfinity : std::chrono::system_clock::now(), true});
  }

  dump::TestWriteReadCycle(cache);
}
