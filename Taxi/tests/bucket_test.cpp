#include <gtest/gtest.h>

#include <models/bucket.hpp>

namespace {

using Bucket = tags::models::Bucket;
using Gen = tags::models::Generation;
using Type = tags::models::EntityType;
using Entity = tags::models::Entity;
using EntityView = tags::models::EntityView;
using Id = tags_cache::models::Names::Id;

const std::string kValue{"value"};
const Entity kEntity{kValue, Type::kCarNumber};

const std::vector<Id> kEmptyIds{};
const std::vector<Id> kTestTagIds{34u, 52u, 128u};
const std::vector<Id> kTestTagIds2{104u, 38u, 34u};

}  // namespace

TEST(TagsBucket, SetTagIds) {
  Bucket bucket{Gen{10}};

  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kEmptyIds);

  // .GetSize() counts entities
  bucket.SetEntitiesTags({{kEntity, std::vector<Id>(kTestTagIds)}});
  ASSERT_EQ(bucket.GetSize(), 1u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kTestTagIds);

  // should remove entity record without tags
  bucket.SetEntitiesTags({{kEntity, std::vector<Id>()}});
  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kEmptyIds);

  bucket.SetEntitiesTags({{kEntity, std::vector<Id>(kTestTagIds)}});
  ASSERT_EQ(bucket.GetSize(), 1u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kTestTagIds);
}

TEST(TagsBucket, PreserveHashes) {
  const tags::models::EntityHash hasher;

  ASSERT_EQ(hasher(kEntity), hasher(EntityView{kEntity}));
  Bucket bucket{Gen{10}};

  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kEmptyIds);

  // .GetSize() counts entities
  bucket.SetEntitiesTags({{kEntity, std::vector<Id>(kTestTagIds)}});
  ASSERT_EQ(bucket.GetSize(), 1u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kTestTagIds);

  // should remove entity record without tags
  bucket.SetEntitiesTags({{kEntity, std::vector<Id>()}});
  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kEmptyIds);

  bucket.SetEntitiesTags({{kEntity, std::vector<Id>(kTestTagIds)}});
  ASSERT_EQ(bucket.GetSize(), 1u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kTestTagIds);
}

TEST(TagsBucket, TestDuplicates) {
  Bucket bucket{Gen{10}};

  // check ordered entity application
  bucket.SetEntitiesTags(
      {{kEntity, std::vector<Id>(kTestTagIds)}, {kEntity, std::vector<Id>{}}});
  ASSERT_EQ(bucket.GetSize(), 0u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kEmptyIds);

  Entity kUdidEntity{std::string("udid"), Type::kUdid};

  bucket.SetEntitiesTags({{kEntity, std::vector<Id>(kTestTagIds)},
                          {kUdidEntity, std::vector<Id>{kTestTagIds2}}});
  ASSERT_EQ(bucket.GetSize(), 2u);
  ASSERT_EQ(bucket.FetchTags(EntityView{kEntity}), kTestTagIds);
  ASSERT_EQ(bucket.FetchTags(EntityView{kUdidEntity}), kTestTagIds2);
}

TEST(TagsBucket, Generation) {
  Bucket bucket{Gen{10u}};
  ASSERT_EQ(bucket.GetGeneration(), Gen{10u});

  Bucket next_gen{bucket, Gen{11}};
  ASSERT_EQ(next_gen.GetGeneration(), Gen{11});
}

TEST(TagsBucket, GenerationLimit) {
  Bucket bucket{tags::models::MaxGeneration()};
  ASSERT_EQ(bucket.GetGeneration(), tags::models::MaxGeneration());
}
