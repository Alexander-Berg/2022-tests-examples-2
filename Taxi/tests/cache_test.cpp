#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>

#include <models/cache.hpp>

namespace {

using Gen = tags::models::Generation;
using Type = tags::models::EntityType;
using Entities = tags::models::Entities;
using EntityViews = tags::models::EntityViews;
using TagSet = tags::models::TagSet;
using Entity = tags::models::Entity;
using EntityView = tags::models::EntityView;

const std::string kCarNumber = "A777MP777";
const std::string kCarNumberSpb = "E666KX178";
const std::string kUdid = "udid";

const EntityViews kDriverList{
    {Type::kCarNumber, kCarNumber},
    {Type::kUdid, kUdid},
};

const EntityViews kDriver{
    {Type::kCarNumber, kCarNumber},
    {Type::kUdid, kUdid},
};

const Entity kUniqueDriverId{kUdid, Type::kUdid};
const std::vector<std::string> kNoTags{};

using namespace tags::models;

}  // namespace

TEST(TagsCache, Empty) {
  Cache cache{17};

  ASSERT_EQ(cache.GetGeneration(), Gen{0u});
  ASSERT_TRUE(cache.IsEmpty());
  ASSERT_TRUE(cache.GetTagsFast(EntityViews{}).empty());
  ASSERT_TRUE(cache.GetTagsFast(kDriver).empty());
  EXPECT_TRUE(cache.GetTagsFast(kDriverList).empty());

  // buckets generation equals cache's one (first update)
  ASSERT_EQ(cache.UpdateTags({{kUniqueDriverId, kNoTags}}), 0u);
  ASSERT_TRUE(cache.IsEmpty());

  ASSERT_EQ(cache.GetRevision(), 0);

  cache.UpdateRevision(1);
  ASSERT_FALSE(cache.IsEmpty());
  ASSERT_EQ(cache.GetRevision(), 1);

  cache.UpdateRevision(0);
  ASSERT_TRUE(cache.IsEmpty());
  ASSERT_EQ(cache.GetRevision(), 0);
}

TEST(TagsCache, CacheCopy) {
  Cache cache{10};

  const Entity udid0{std::string{"udid0"}, Type::kUdid};

  // since cache was not copied not even once, no buckets copy should be applied
  ASSERT_EQ(cache.UpdateTags({{udid0, {"moscow", "vip"}}}), 0u);
  ASSERT_EQ(cache.GetTags(Entities{{udid0.type, udid0.name}}),
            TagSet({"vip", "moscow"}));

  tags::models::Cache cache_copy{cache};
  ASSERT_EQ(cache_copy.GetTags(Entities{{udid0.type, udid0.name}}),
            TagSet({"vip", "moscow"}));
  // after copying the cache bucket should be updated
  ASSERT_EQ(cache_copy.UpdateTags({{udid0, {"moscow", "vip", "joke"}}}), 1u);
  // and only once
  ASSERT_EQ(cache_copy.UpdateTags({{udid0, {"moscow", "vip", "joke"}}}), 0u);

  cache_copy.UpdateTags(
      {{Entity{std::string("udid1"), Type::kUdid}, {"sbp", "econom"}}});
  ASSERT_EQ(cache_copy.GetTags(Entities{{udid0.type, udid0.name}}),
            TagSet({"vip", "moscow", "joke"}));
  ASSERT_EQ(cache_copy.GetTags(Entities{{Type::kUdid, "udid1"}}),
            TagSet({"sbp", "econom"}));

  // initial cache is not affected by the changes
  ASSERT_EQ(cache.GetTags(Entities{{udid0.type, udid0.name}}),
            TagSet({"vip", "moscow"}));
  ASSERT_EQ(cache.GetTags(Entities{{Type::kUdid, "udid1"}}), TagSet({}));

  ASSERT_EQ(cache_copy.GetGeneration(), Gen{1u});
}

TEST(TagsCache, Tags) {
  Cache cache{123};

  ASSERT_EQ(cache.UpdateTags({{Entity{kCarNumber, Type::kCarNumber}, {"vip"}},
                              {Entity{kCarNumberSpb, Type::kCarNumber},
                               {"spb", "low_skill"}}}),
            0u);
  ASSERT_FALSE(cache.IsEmpty());

  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({"vip"}));
  EXPECT_EQ(cache.GetTagsFast(kDriverList), TagSet({"vip"}));

  // "vip" tag duplicated for udid and car_number properties
  cache.UpdateTags({{Entity{kUdid, Type::kUdid}, {"moscow", "vip"}}});
  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({"vip", "moscow"}));
  EXPECT_EQ(cache.GetTagsFast(kDriverList), TagSet({"vip", "moscow"}));

  // effectively removing "vip" tag from udid property
  // through it still remains in car_number property
  // and no buckets should be updated via the call
  ASSERT_EQ(cache.UpdateTags({{Entity{kUdid, Type::kUdid}, {"moscow"}}}), 0u);
  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({"vip", "moscow"}));
  EXPECT_EQ(cache.GetTagsFast(kDriverList), TagSet({"vip", "moscow"}));

  ASSERT_EQ(cache.GetTags(Entities{{Type::kCarNumber, kCarNumberSpb},
                                   {Type::kUdid, kUdid}}),
            TagSet({"spb", "low_skill", "moscow"}));

  // only car_number tag should remain, no buckets copied
  ASSERT_EQ(cache.UpdateTags({{Entity{kUdid, Type::kUdid}, {}}}), 0u);
  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({"vip"}));
  EXPECT_EQ(cache.GetTagsFast(kDriverList), TagSet({"vip"}));

  // driver should lose his last tag
  cache.UpdateTags({{Entity{kCarNumber, Type::kCarNumber}, {}},
                    {Entity{kCarNumberSpb, Type::kCarNumber}, {}}});
  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({}));
  EXPECT_EQ(cache.GetTagsFast(kDriverList), TagSet({}));

  // There are still some names in the cache so it won't be empty anymore
  ASSERT_FALSE(cache.IsEmpty());
}

TEST(TagsCache, GenerationOverflow) {
  const Entity entity{kUdid, Type::kUdid};

  Cache cache = Cache::MakeTestCache(MaxGeneration());
  ASSERT_EQ(cache.GetGeneration(), MaxGeneration());
  ASSERT_EQ(cache.UpdateTags({{entity, {"tag"}}}), 0u);
  ASSERT_EQ(cache.GetTagsFast(kDriver), TagSet({"tag"}));

  Cache copy{cache};
  ASSERT_EQ(copy.GetGeneration(), Gen{0u});
  ASSERT_EQ(copy.GetTagsFast(kDriver), TagSet({"tag"}));

  ASSERT_EQ(copy.UpdateTags({{entity, {"tag", "new"}}}), 1u);
  ASSERT_EQ(copy.GetTagsFast(kDriver), TagSet({"tag", "new"}));
}

TEST(TagsCache, DumpRestoreEmpty) {
  const Cache cache = Cache::MakeTestCache();
  dump::TestWriteReadCycle(cache);
}

TEST(TagsCache, DumpRestore) {
  Cache cache{123};

  cache.UpdateTags({
      {Entity{kCarNumber, Type::kCarNumber}, {"tag0", "tag1"}},
      {Entity{kUdid, Type::kUdid}, {"tag0", "tag2"}},
      {Entity{"park0", Type::kPark}, {}},
      {Entity{"park1", Type::kPark}, {"tag4"}},
      {Entity{"dbid_uuid", Type::kDbidUuid}, {"tag0", "tag5", "tag6"}},
  });
  cache.UpdateRevision(123456);

  dump::TestWriteReadCycle(cache);
}
