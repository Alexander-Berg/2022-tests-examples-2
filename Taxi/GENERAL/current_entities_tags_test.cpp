#include <chrono>

#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>
#include <userver/tracing/span.hpp>
#include <userver/utest/utest.hpp>

#include <caches/match/current_entities_tags.hpp>
#include <caches/match/entities_tags.hpp>

namespace {

using DbEntry = caches::match::EntityTagDbRow;

models::EntityName EntityNameFor(const int i) {
  return models::EntityName{"Entity_" + std::to_string(i)};
}

models::EntityType EntityTypeFor(const int i) {
  return i % 2 ? models::EntityType::kDbidUuid : models::EntityType::kParkCarId;
}

models::Entity EntityFor(const int i) {
  return models::Entity{EntityNameFor(i), EntityTypeFor(i)};
}

DbEntry DbEntryFor(const int entity_index, const models::TagNameId tag_name_id,
                   const utils::TimePoint ttl,
                   const models::ProviderId provider_id = models::ProviderId{
                       32167}) {
  return DbEntry{models::EntityId{entity_index},
                 EntityNameFor(entity_index),
                 EntityTypeFor(entity_index),
                 tag_name_id,
                 provider_id,
                 0,
                 ttl,
                 true};
}

const models::TagNameId kPresentTagNameId{10};
const models::TagNameId kAbsentTagNameId{13};

const auto kAtMoment = utils::datetime::Now();
const auto kInFuture = kAtMoment + std::chrono::hours{1};
const auto kInThePast = kAtMoment - std::chrono::seconds{1};

caches::match::CurrentEntitiesTags MakeCurrentTags() {
  const models::ProviderId kProvider1{1};
  const models::ProviderId kProvider2{2};

  auto cache_ptr = std::make_shared<caches::match::EntitiesTags>();

  // One outdated tag, one present
  cache_ptr->insert_or_assign(0, DbEntryFor(0, kPresentTagNameId, kInFuture));
  cache_ptr->insert_or_assign(1, DbEntryFor(0, kAbsentTagNameId, kInThePast));

  // Same tag from different providers
  cache_ptr->insert_or_assign(
      2, DbEntryFor(1, kPresentTagNameId, kInThePast, kProvider1));
  cache_ptr->insert_or_assign(
      2, DbEntryFor(1, kPresentTagNameId, kInFuture, kProvider2));

  return {cache_ptr, kAtMoment};
}

}  // namespace

UTEST(CurrentEntitiesTags, AddTagNames) {
  const auto cache = MakeCurrentTags();

  using Set = std::unordered_set<models::TagNameId>;

  const Set kExpectedTagNames{kPresentTagNameId};

  {
    Set matched;
    cache.AddMatchedTagIds(matched, EntityFor(0));
    ASSERT_EQ(matched, kExpectedTagNames);
  }

  {
    Set matched;
    cache.AddMatchedTagIds(matched, EntityFor(1));
    ASSERT_EQ(matched, kExpectedTagNames);
  }
}

UTEST(CurrentEntitiesTags, AddTagNamesWithTTLs) {
  const auto cache = MakeCurrentTags();

  using Map = std::unordered_map<models::TagNameId, utils::TimePoint>;

  const Map kExpected{std::make_pair(kPresentTagNameId, kInFuture)};

  {
    Map matched;
    cache.AddMatchedTagIdWithTtls(matched, EntityFor(0));
    ASSERT_EQ(matched, kExpected);
  }

  {
    Map matched;
    cache.AddMatchedTagIdWithTtls(matched, EntityFor(1));
    ASSERT_EQ(matched, kExpected);
  }
}
