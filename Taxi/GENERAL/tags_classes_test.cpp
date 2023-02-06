#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include "virtual_tariffs_classes.hpp"

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_car/fetch_car.hpp>
#include <filters/infrastructure/fetch_driver/fetch_driver.hpp>
#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>

#include <virtual-tariffs/models/requirements.hpp>
#include <virtual-tariffs/models/virtual_tariffs.hpp>

using candidates::GeoMember;
using namespace candidates::filters;
using namespace candidates::filters::infrastructure;
using namespace candidates::filters::efficiency;
using namespace candidates::filters::corp;
using namespace tags::models;
using namespace virtual_tariffs::models;

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

using TagsByClasses =
    std::unordered_map<std::string, std::vector<std::vector<std::string>>>;

struct TestData {
  TagsByClasses request;
  bool allow = false;
};

class TagsRequiredParametric : public ::testing::TestWithParam<TestData> {};

std::unique_ptr<VirtualTariffs> MakeVirtualTariffs(
    TagsByClasses&& tags_by_classes, const Cache& tags_cache) {
  static const OperationId kOperationId = OperationId::kContainsAll;
  static const RequirementId kRequirementId = RequirementId::kTags;
  static const ContextId kContextId = ContextId::kTags;

  formats::json::ValueBuilder builder;
  formats::json::ValueBuilder tariffs_builder(formats::json::Type::kArray);
  SpecialRequirements special_requirements;
  int counter = 0;
  for (auto&& [key, value] : tags_by_classes) {
    for (auto&& tags : value) {
      formats::json::ValueBuilder builder_sr;
      builder_sr["class"] = key;
      formats::json::ValueBuilder array_builder(formats::json::Type::kArray);
      formats::json::ValueBuilder requirement_builder;
      auto requirement_name = "tags" + std::to_string(counter);
      requirement_builder["id"] = requirement_name;
      special_requirements[requirement_name].requirements = {
          {Requirement(kContextId, kRequirementId, kOperationId,
                       std::move(tags), requirement_name)}};
      array_builder.PushBack(requirement_builder.ExtractValue());
      builder_sr["special_requirements"] = array_builder.ExtractValue();
      tariffs_builder.PushBack(builder_sr.ExtractValue());
      ++counter;
    }
  }
  formats::json::ValueBuilder order;
  order["virtual_tariffs"] = tariffs_builder.ExtractValue();
  builder["order"] = order.ExtractValue();
  auto result_value = builder.ExtractValue();
  std::unique_ptr<VirtualTariffs> result;

  ReplaceFunctor functor = [tags_cache](Requirement& requirement) {
    requirement.ReplaceFunctor<tags::models::IdsVec>(
        [&tags_cache](const std::vector<std::string>& arguments) {
          auto ids = tags_cache.GetTagIds(arguments);
          if (ids.size() != arguments.size())
            throw std::runtime_error("size of arguments " +
                                     std::to_string(arguments.size()) +
                                     " is not equal to size of tag ids " +
                                     std::to_string(ids.size()));
          return ids;
        });
  };

  const ReplaceMap replace_map = {
      {virtual_tariffs::models::RequirementId::kTags, functor}};

  RunInCoro([&result, &result_value, &special_requirements, &replace_map]() {
    result = std::make_unique<VirtualTariffs>(
        result_value, special_requirements, replace_map,
        dynamic_config::GetDefaultSnapshot());
  });
  return result;
}

}  // namespace

TEST_P(TagsRequiredParametric, Test) {
  models::UniqueDriver unique_driver;
  unique_driver.id = "udid";

  models::Car car;
  car.raw_number = "car_number";
  car.park_id = "dbid";
  Context context;
  FetchUniqueDriver::Set(context, std::make_shared<models::UniqueDriver>(
                                      std::move(unique_driver)));
  FetchCar::Set(context, std::make_shared<models::Car>(std::move(car)));
  FetchFinalClasses::Set(context, {"econom", "business"});
  FetchDriver::Set(context, std::make_shared<models::Driver>(models::Driver()));
  const auto member = GeoMember{{0, 0}, "dbid_uuid"};

  static const auto cache = MakeTagsCache(
      {{{"udid", EntityType::kUdid}, {"tag1", "tag2"}},
       {{"car_number", EntityType::kCarNumber}, {"tag3"}},
       {{"dbid", EntityType::kPark}, {"tag4"}},
       {{"dbid_uuid", EntityType::kDbidUuid}, {"tag5", "tag6"}},
       {{"dbid_uuid_unregistered_tags", EntityType::kDbidUuid}, {"tag7"}}});

  FetchTags::Set(context, cache.GetTagIds({
                              "tag1",
                              "tag2",
                              "tag3",
                              "tag4",
                              "tag5",
                              "tag6",
                          }));

  auto tags_required = GetParam();

  auto virtual_tariffs_ptr =
      MakeVirtualTariffs(std::move(tags_required.request), cache);

  VirtualTariffsClasses filter(kEmptyInfo, std::move(virtual_tariffs_ptr));

  EXPECT_EQ(filter.Process(member, context),
            (tags_required.allow ? Result::kAllow : Result::kDisallow))
      << filter.Get().ToString();
}

INSTANTIATE_TEST_SUITE_P(
    TagsRequired, TagsRequiredParametric,
    ::testing::Values(
        TestData{TagsByClasses{}, true},
        TestData{
            TagsByClasses{
                {"econom", {{"tag1", "tag2", "tag3", "tag4", "tag5", "tag6"}}}},
            true},
        TestData{TagsByClasses{{"econom", {{"tag1", "tag2"}}}}, true},
        TestData{TagsByClasses{{"econom", {{"tag3"}}}}, true},
        TestData{TagsByClasses{{"econom", {{"tag4"}}}}, true},
        TestData{TagsByClasses{{"econom", {{"tag5", "tag6"}}}}, true},
        TestData{
            TagsByClasses{
                {"econom",
                 {{"tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"}}},
                {"business",
                 {{"tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7"}}}},
            false},
        TestData{TagsByClasses{{"econom", {{"tag1", "tag2", "tag7"}}},
                               {"business", {{"tag1", "tag2", "tag7"}}}},
                 false},
        TestData{TagsByClasses{{"econom", {{"tag3", "tag7"}}},
                               {"business", {{"tag3", "tag7"}}}},
                 false},
        TestData{TagsByClasses{{"econom", {{"tag4", "tag7"}}},
                               {"business", {{"tag4", "tag7"}}}},
                 false},
        TestData{TagsByClasses{{"econom", {{"tag5", "tag6", "tag7"}}},
                               {"business", {{"tag5", "tag6", "tag7"}}}},
                 false},
        TestData{TagsByClasses{{"business", {{"tag5", "tag6", "tag7"}}},
                               {"econom", {{"tag5", "tag6"}}}},
                 true},
        TestData{TagsByClasses{{"business", {{}}},
                               {"econom", {{"tag5", "tag6", "tag7"}}}},
                 true},
        TestData{TagsByClasses{{"econom", {{"tag7"}}}}, true},
        TestData{TagsByClasses{{"business", {{"tag7"}}},
                               {"econom", {{"tag5", "tag6"}}},
                               {"vip", {{"tag5", "tag6", "tag7"}}}},
                 true},
        TestData{TagsByClasses{{"business", {{"tag7"}}},
                               {"econom", {{"tag5", "tag6", "tag7"}}},
                               {"vip", {{"tag5", "tag6"}}}},
                 false},
        TestData{TagsByClasses{{"business", {{"tag1", "tag7"}}},
                               {"econom", {{"tag5", "tag7"}}}},
                 false}));
