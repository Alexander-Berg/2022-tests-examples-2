#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "fetch_tags_classes.hpp"

#include <dispatch-settings/dispatch_settings.hpp>
#include <dispatch-settings/models/settings_values_serialization.hpp>

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>
#include <utils/mock_dispatch_settings.hpp>

namespace {

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::efficiency;
using namespace tags::models;

unsigned kRandomRev = 1u;

using TagsCache = std::vector<tags::models::EntityWithTags>;

Cache MakeTagsCache(TagsCache&& tags, int64_t revision) {
  Cache tags_cache = Cache::MakeTestCache();
  tags_cache.UpdateTags(std::move(tags));
  tags_cache.UpdateRevision(revision);

  return tags_cache;
}

Context MakeContext(const std::string& udid, const std::string& car_id,
                    const std::string& dbid, const bool need_details = false) {
  models::Driver driver;
  driver.park_id_car_id = dbid + "_car_id";

  models::UniqueDriver unique_driver;
  unique_driver.id = udid;

  models::Car car;
  car.car_id = car_id;
  car.park_id = dbid;

  Context context;
  context.need_details = need_details;
  FetchDriver::Set(context,
                   std::make_shared<models::Driver>(std::move(driver)));
  FetchUniqueDriver::Set(context, std::make_shared<models::UniqueDriver>(
                                      std::move(unique_driver)));
  FetchCar::Set(context, std::make_shared<models::Car>(std::move(car)));
  return context;
}

const candidates::filters::FilterInfo kEmptyInfo;
const std::string kJsonBlockingTags = R"({
    "__default__": {
    },
    "econom": {
      "DISPATCH_DRIVER_TAGS_BLOCK": ["econom_excluded"]
    },
    "comfortplus": {
      "DISPATCH_DRIVER_TAGS_BLOCK": ["bad_driver", "bad_car"]
    }
  })";

const std::string kJsonRequiredTags = R"({
      "__default__": {
        "requires_tag": false,
        "tag": ""
      },
      "econom": {
        "requires_tag": false,
        "tag": ""
      },
      "comfort": {
        "requires_tag": true,
        "tag": "good_car"
      },
      "maybach": {
        "requires_tag": true,
        "tag": "new_car"
      }
  })";

void TestFilter(const Cache& cache,
                models::Classes classes_to_exclude_from_answer,
                const std::string& blocking_tags_json = kJsonBlockingTags,
                const std::string& required_tags_json = kJsonRequiredTags) {
  const auto json_blocking_tags = formats::json::FromString(blocking_tags_json);

  formats::json::ValueBuilder builder;
  builder["__default__"] = json_blocking_tags;

  const auto dispatch_settings =
      std::make_shared<utils::MockDispatchSettings>(builder.ExtractValue());

  const auto blocking_tags = BlockingTags(*dispatch_settings);

  const auto json_required_tags = formats::json::FromString(required_tags_json);
  const auto required_tags = json_required_tags.As<RequiredTags>();

  const auto all_classes = models::Classes::GetAll();

  const auto cache_ptr = std::make_shared<Cache>(cache);

  const FetchTagsClasses filter(
      kEmptyInfo, all_classes, {}, cache_ptr,
      blocking_tags.GetMapForZoneClasses("__default__", all_classes, cache),
      required_tags.GetMapForClasses(all_classes, cache));

  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  // Ensure diagnostic output doesn't spoil the filter itself
  for (bool need_details : {false, true}) {
    auto context = MakeContext("udid", "car_id", "dbid", need_details);

    const FetchTags tags_fetcher(kEmptyInfo, cache_ptr);
    tags_fetcher.Process(member, context);

    EXPECT_EQ(filter.Process(member, context), Result::kAllow);
    EXPECT_EQ(FetchTagsClasses::Get(context).GetNames(),
              (all_classes - classes_to_exclude_from_answer).GetNames());
  }
}

}  // namespace

UTEST(Tags, Allow) {
  const auto tags_cache = MakeTagsCache(
      TagsCache{
          {{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
          {{"dbid_car_id", EntityType::kParkCarId}, {"bad_car"}},
          {{"dbid", EntityType::kPark}, {"tag1", "new_car"}},
          {{"dbid_uuid", EntityType::kDbidUuid}, {"tag5", "econom_excluded"}},
      },
      kRandomRev);
  TestFilter(tags_cache, models::Classes{{"econom", "comfortplus", "comfort"}});
}

TEST(Tags, NoTagsAllow) {
  const auto tags_cache = MakeTagsCache(TagsCache{}, 0u);
  TestFilter(tags_cache, models::Classes{"comfort", "maybach"});
}

TEST(Tags, NoBlocksAllow) {
  const auto tags_cache =
      MakeTagsCache(TagsCache{{{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
                              {{"dbid", EntityType::kPark}, {"tag1"}},
                              {{"dbid_car_id", EntityType::kParkCarId},
                               {"tag5", "econom_excluded", "bad_car"}}},
                    kRandomRev);
  TestFilter(tags_cache, {"comfortplus", "econom", "maybach", "comfort"});
}

TEST(Tags, RequiredAllow) {
  const auto tags_cache = MakeTagsCache(
      TagsCache{{{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
                {{"dbid_car_id", EntityType::kParkCarId}, {"bad_car"}},
                {{"dbid", EntityType::kPark}, {"tag1"}},
                {{"dbid_uuid", EntityType::kDbidUuid}, {"tag5", "new_car"}}},
      kRandomRev);
  TestFilter(tags_cache, {"comfortplus", "comfort"});
}

TEST(Tags, DisallowByBlock) {
  const auto tags_cache = MakeTagsCache(
      TagsCache{
          {{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
          {{"dbid_car_id", EntityType::kParkCarId}, {"bad_car"}},
          {{"dbid", EntityType::kPark}, {"tag1"}},
          {{"dbid_uuid", EntityType::kDbidUuid}, {"tag5", "econom_excluded"}}},
      kRandomRev);
  TestFilter(tags_cache, {"comfortplus", "econom", "comfort", "maybach"});
}

TEST(Tags, DisallowByDefault) {
  const std::string kBlockTags = R"({
    "__default__": {
      "DISPATCH_DRIVER_TAGS_BLOCK": ["default_block"]
    }
  })";
  const std::string kRequireTags = R"({
    "__default__": {
      "requires_tag": false,
      "tag": ""
    }
  })";

  const auto tags_cache = MakeTagsCache(
      TagsCache{{{"udid", EntityType::kUdid}, {"default_block"}}}, kRandomRev);
  TestFilter(tags_cache, models::Classes::GetAll(), kBlockTags, kRequireTags);
}
