#include <gtest/gtest.h>

#include "cache.hpp"

namespace {

using Type = tags::models::EntityType;
using Entities = tags::models::Entities;
using Set = tags::models::Set;

const std::string kCarNumber = "A777MP777";
const std::string kCarNumberSpb = "E666KX178";
const std::string kLicense = "EC1000";
const std::string kUdid = "udid";

const Entities kEntities{{Type::kCarNumber, kCarNumber},
                         {Type::kDriverLicense, kLicense},
                         {Type::kUniqueDriverId, kUdid}};

}  // namespace

TEST(TagsCache, Empty) {
  tags::models::Cache cache;

  ASSERT_TRUE(cache.IsEmpty());
  ASSERT_TRUE(cache.GetTags({}).empty());
  ASSERT_TRUE(cache.GetTags(kEntities).empty());

  cache.SetTags(Type::kUniqueDriverId, {{kUdid, {}}});
  ASSERT_TRUE(cache.IsEmpty());

  ASSERT_EQ(cache.GetRevision(), 0);

  cache.UpdateRevision(1);
  ASSERT_FALSE(cache.IsEmpty());
  ASSERT_EQ(cache.GetRevision(), 1);

  cache.UpdateRevision(0);
  ASSERT_TRUE(cache.IsEmpty());
  ASSERT_EQ(cache.GetRevision(), 0);
}

TEST(TagsCache, Tags) {
  tags::models::Cache cache;

  cache.SetTags(Type::kCarNumber,
                {{kCarNumber, {"vip"}}, {kCarNumberSpb, {"spb", "low_skill"}}});
  ASSERT_FALSE(cache.IsEmpty());

  ASSERT_EQ(cache.GetTags(kEntities), Set({"vip"}));

  // "vip" tag duplicated for udid and car_number properties
  cache.SetTags(Type::kUniqueDriverId, {{kUdid, {"moscow", "vip"}}});
  ASSERT_EQ(cache.GetTags(kEntities), Set({"vip", "moscow"}));

  // effectively removing "vip" tag from udid property
  // through it still remains in car_number property
  cache.SetTags(Type::kUniqueDriverId, {{kUdid, {"moscow"}}});
  ASSERT_EQ(cache.GetTags(kEntities), Set({"vip", "moscow"}));

  ASSERT_EQ(cache.GetTags({{Type::kCarNumber, kCarNumberSpb},
                           {Type::kUniqueDriverId, kUdid}}),
            Set({"spb", "low_skill", "moscow"}));

  // only car_number tag should remain
  cache.SetTags(Type::kUniqueDriverId, {{kUdid, {}}});
  ASSERT_EQ(cache.GetTags(kEntities), Set({"vip"}));

  // driver should lose his last tag
  cache.SetTags(Type::kCarNumber, {{kCarNumber, {}}, {kCarNumberSpb, {}}});
  ASSERT_EQ(cache.GetTags(kEntities), Set({}));

  // There are still some names in the cache so it won't be empty anymore
  ASSERT_FALSE(cache.IsEmpty());
}
