#include <gtest/gtest.h>

#include "fetch_tags.hpp"

#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::efficiency;
using namespace tags::models;

namespace {

using TagsCache = std::vector<tags::models::EntityWithTags>;

const candidates::filters::FilterInfo kEmptyInfo;

Cache MakeTagsCache(TagsCache&& tags) {
  Cache tags_cache = Cache::MakeTestCache();
  tags_cache.UpdateTags(std::move(tags));

  static const auto kRevision = 1u;
  tags_cache.UpdateRevision(kRevision);

  return tags_cache;
}

}  // namespace

TEST(FetchTags, Test) {
  models::Driver driver;
  driver.park_id_car_id = "dbid_car_id";

  models::UniqueDriver unique_driver;
  unique_driver.id = "udid";

  models::Car car;
  car.raw_number = "car_number";
  car.park_id = "dbid";
  Context context;
  FetchDriver::Set(context,
                   std::make_shared<models::Driver>(std::move(driver)));
  FetchUniqueDriver::Set(context, std::make_shared<models::UniqueDriver>(
                                      std::move(unique_driver)));
  FetchCar::Set(context, std::make_shared<models::Car>(std::move(car)));
  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  static const auto cache = MakeTagsCache(
      {{{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
       {{"dbid", EntityType::kPark}, {"tag4"}},
       {{"dbid_uuid", EntityType::kDbidUuid}, {"tag5", "tag6"}},
       {{"dbid_uuid_unregistered_tags", EntityType::kDbidUuid}, {"tag7"}}});

  FetchTags filter(kEmptyInfo, std::make_shared<Cache>(cache));

  filter.Process(member, context);
  auto expected = cache.GetTagIds({
      "tag1",
      "tag2",
      "tag3",
      "tag4",
      "tag5",
      "tag6",
  });
  std::sort(expected.begin(), expected.end());
  auto from_context = FetchTags::Get(context);
  std::sort(from_context.begin(), from_context.end());
  EXPECT_EQ(from_context, expected);
}
