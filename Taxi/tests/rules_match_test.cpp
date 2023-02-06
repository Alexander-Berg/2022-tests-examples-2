#include <fmt/format.h>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <discounts-match/conditions.hpp>
#include <discounts-match/matched_data.hpp>
#include <models/condition_description.hpp>
#include <models/condition_storage.hpp>
#include <models/exclusions.hpp>
#include <models/hierarchy.hpp>
#include <models/node.hpp>
#include <models/rules_match_impl.hpp>
#include <types/condition_type.hpp>
#include <userver/server/handlers/exceptions.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/boost_uuid4.hpp>

using namespace rules_match;
using namespace rules_match::models;
using namespace rules_match::types;

namespace {
using AnyOtherString = types::AnyOtherType<std::string>;
using AnyOtherTimeRange = types::AnyOtherType<TimeRange>;
using AnyOtherInt = types::AnyOtherType<int64_t>;
using StringVector = std::vector<std::string>;
using IntegerVector = std::vector<int64_t>;
using GeneratedTimeRange = generated::TimeRangeValue;
using GeneratedTimeRangeVector = std::vector<GeneratedTimeRange>;

ConditionDescription MakeConditionDescription(
    const std::string& name, const std::string& type,
    const std::string& _default, const std::vector<ConditionFlags>& flags) {
  const auto& default_json = formats::json::FromString(_default);
  ConditionFlagSet condition_flags{};
  for (auto flag : flags) {
    condition_flags.set(static_cast<size_t>(flag));
  }
  return {name, type, default_json, condition_flags};
}

ConditionDescriptionMap MakeConditionDescriptionMap(
    const std::vector<ConditionDescription>& vec) {
  ConditionDescriptionMap map;
  for (auto item : vec) {
    map[item.GetName()] = std::make_shared<const ConditionDescription>(item);
  }
  return map;
}

template <typename T, typename U>
QueryConditionsVector MakeConditions(const U& value) {
  return QueryConditionsVector{std::vector<T>{T{value}}};
}

template <typename T, typename U>
QueryConditionsVector MakeConditions(const std::vector<U>& value) {
  std::vector<T> vec;
  vec.reserve(value.size());
  for (auto val : value) {
    vec.push_back(T{val});
  }
  return QueryConditionsVector{vec};
}

const auto start = utils::datetime::Stringtime("2019-01-21T15:29:00+0000");
const auto end = utils::datetime::Stringtime("2019-01-21T16:29:00+0000");
const auto due = utils::datetime::Stringtime("2019-01-21T16:09:00+0000");
const auto due1 = utils::datetime::Stringtime("2019-01-21T16:09:01+0000");
constexpr auto MoscowId = 11;
constexpr auto CityAnyId = 55;
constexpr auto TestTagId = 22;
constexpr auto EconomId = 12;
}  // namespace

void CheckSimple(const MatchTree& match_tree, RulesMatch::MatchType match_type,
                 const BaseMatchedData& data) {
  auto res = match_tree.Find(
      {MakeConditions<EntityId>(MoscowId), MakeConditions<EntityId>(EconomId),
       MakeConditions<EntityId>(TestTagId),
       MakeConditions<AnyOtherTimeRange>(
           TimeRange{TimePoint{due, false}, TimePoint{due1, false}})},
      match_type);

  EXPECT_EQ(res.size(), 1);
  const auto& find_path = res.front().path;
  EXPECT_EQ(find_path.size(), 4);
  EXPECT_EQ(std::get<EntityId>(find_path[0]), EntityId{MoscowId});
  EXPECT_EQ(std::get<EntityId>(find_path[1]), EntityId{EconomId});
  EXPECT_EQ(std::get<EntityId>(find_path[2]), EntityId{TestTagId});
  EXPECT_EQ(std::get<AnyOtherTimeRange>(find_path[3]).value(),
            TimeRange(TimePoint{start, false}, TimePoint{end, false}));
  EXPECT_EQ(*match_tree.Find(res.front().data->match_data->data_id), data);
}

void CheckAny(const MatchTree& match_tree, RulesMatch::MatchType match_type,
              const BaseMatchedData& data) {
  auto res = match_tree.Find(
      {MakeConditions<EntityId>(CityAnyId), MakeConditions<EntityId>(EconomId),
       MakeConditions<EntityId>(TestTagId),
       MakeConditions<AnyOtherTimeRange>(
           TimeRange{TimePoint{due, false}, TimePoint{due1, false}})},
      match_type);

  EXPECT_EQ(res.size(), 1);
  const auto& find_path = res.front().path;
  EXPECT_EQ(find_path.size(), 4);
  EXPECT_EQ(std::get<EntityId>(find_path[0]), EntityId{CityAnyId});
  EXPECT_EQ(std::get<EntityId>(find_path[1]), EntityId{EconomId});
  EXPECT_EQ(std::get<EntityId>(find_path[2]), EntityId{TestTagId});
  EXPECT_EQ(std::get<AnyOtherTimeRange>(find_path[3]).value(),
            TimeRange(TimePoint{start, false}, TimePoint{end, false}));
  EXPECT_EQ(*match_tree.Find(res.front().data->match_data->data_id), data);
}

Hierarchy MakeTestHierarchy() {
  auto city = MakeConditionDescription(
      "city", "text", "{\"value_type\": \"Any\"}",
      {ConditionFlags::SupportAny, ConditionFlags::SupportOther});
  auto storage = city.GetStorage();
  storage->Insert(EntityId{MoscowId}, AnyOtherString{"moscow"});
  storage->Insert(EntityId{CityAnyId}, AnyOtherString{AnyOtherValueType::Any});

  auto tag = MakeConditionDescription(
      "tag", "text", "{\"value_type\": \"Any\"}", {ConditionFlags::SupportAny});
  storage = tag.GetStorage();
  storage->Insert(EntityId{TestTagId}, AnyOtherString{"test_tag"});

  auto tariff =
      MakeConditionDescription("tariff", "text", "{\"value\": \"econom\"}", {});
  storage = tariff.GetStorage();
  storage->Insert(EntityId{EconomId}, AnyOtherString{"econom"});

  auto active_time = MakeConditionDescription(
      "active_time", "time_range",
      "{\"value\": "
      "{\"begin\": \"2000-01-01T00:00:00.000+03:00\", \"is_begin_utc\": false, "
      "\"end\": \"2100-01-01T00:00:00.000+03:00\", \"is_end_utc\": false}}",
      {});
  storage = active_time.GetStorage();
  storage->Insert(EntityId{24},
                  AnyOtherTimeRange{TimeRange{TimePoint{start, false},
                                              TimePoint{end, false}}});

  auto condition_description =
      MakeConditionDescriptionMap({city, tag, tariff, active_time});

  Hierarchy hierarchy = {"hierarchy_12",
                         {{"city"}, {"tariff"}, {"tag"}, {"active_time"}},
                         condition_description};
  return hierarchy;
}

UTEST(RulesMatch, SimpleTest) {
  auto hierarchy = MakeTestHierarchy();

  std::vector<RulesMatch::MatchedDataCPtr> data_ptr;
  for (int i = 0; i < 10; ++i) {
    formats::json::ValueBuilder builder{formats::common::Type::kObject};
    builder["other"] = fmt::format("value{}", i);
    data_ptr.push_back(
        std::make_shared<BaseMatchedData>(MatchedData<formats::json::Value>{
            RulesMatchBase::DataId{i}, utils::generators::GenerateBoostUuid(),
            builder.ExtractValue()}));
  }

  MatchTree match_tree{hierarchy};

  {
    Hierarchy::MatchPath path = {
        EntityId{MoscowId}, EntityId{EconomId}, EntityId{TestTagId},
        AnyOtherTimeRange{
            TimeRange{TimePoint{start, false}, TimePoint{end, false}}}};

    match_tree.AddData(RulesMatchBase::DataId{1}, data_ptr[0], {});
    match_tree.AddRule(
        path, {RulesMatchBase::DataId{1}, RulesMatch::Revision{1}, {}});
  }
  CheckSimple(match_tree, RulesMatch::MatchType::StrongMatch, *data_ptr[0]);
  CheckSimple(match_tree, RulesMatch::MatchType::WeakMatch, *data_ptr[0]);
  CheckSimple(match_tree, RulesMatch::MatchType::RegularMatch, *data_ptr[0]);

  {
    Hierarchy::MatchPath path = {
        EntityId{CityAnyId}, EntityId{EconomId}, EntityId{TestTagId},
        AnyOtherTimeRange{
            TimeRange{TimePoint{start, false}, TimePoint{end, false}}}};

    {
      RulesMatch::MatchPath generated_path = {
          {generated::PathConditionAnyOther{
              "city", generated::AnyOtherValueType::kAny}},
          {generated::PathConditionValue{"tariff", "econom"}},
          {generated::PathConditionValue{"tag", "test_tag"}},
          {generated::PathConditionValue{
              "active_time", GeneratedTimeRange{start, false, end, false}}},
      };

      EXPECT_EQ(hierarchy.ConvertToRulesMatchPath(path, nullptr),
                generated_path);
    }

    match_tree.AddData(RulesMatchBase::DataId{2}, data_ptr[1], {});
    match_tree.AddRule(
        path, {RulesMatchBase::DataId{2}, RulesMatch::Revision{2}, {}});
  }
  CheckSimple(match_tree, RulesMatch::MatchType::StrongMatch, *data_ptr[0]);
  CheckSimple(match_tree, RulesMatch::MatchType::WeakMatch, *data_ptr[0]);
  CheckSimple(match_tree, RulesMatch::MatchType::RegularMatch, *data_ptr[0]);
  CheckAny(match_tree, RulesMatch::MatchType::StrongMatch, *data_ptr[1]);
  CheckAny(match_tree, RulesMatch::MatchType::WeakMatch, *data_ptr[1]);
  CheckAny(match_tree, RulesMatch::MatchType::RegularMatch, *data_ptr[1]);

  {
    Hierarchy::Query query = {
        MakeConditions<EntityId>(std::vector<int>{CityAnyId, MoscowId, 0}),
        MakeConditions<EntityId>(EconomId),
        MakeConditions<EntityId>(std::vector<int>{0, TestTagId}),
        MakeConditions<AnyOtherTimeRange>(
            TimeRange{TimePoint{due, false}, TimePoint{due1, false}})};

    {
      rules_match::MatchConditions query_map{
          std::vector<rules_match::MatchConditions::ValueType>{
              {"city", StringVector{"moscow"}},
              {"tariff", StringVector{"econom"}},
              {"active_time", GeneratedTimeRangeVector{GeneratedTimeRange{
                                  due, false, due1, false}}},
              {"tag", StringVector{"test_tag"}}}};

      EXPECT_EQ(hierarchy.ConvertToQuery(query_map,
                                         RulesMatch::MatchType::RegularMatch),
                query);
    }

    auto res = match_tree.Find(query, RulesMatch::MatchType::StrongMatch);
    EXPECT_EQ(res.size(), 2);
    {
      const auto& find_path = res.front().path;
      EXPECT_EQ(find_path.size(), 4);
      EXPECT_EQ(std::get<EntityId>(find_path[0]), EntityId{CityAnyId});
      EXPECT_EQ(std::get<EntityId>(find_path[1]), EntityId{EconomId});
      EXPECT_EQ(std::get<EntityId>(find_path[2]), EntityId{TestTagId});
      EXPECT_EQ(std::get<AnyOtherTimeRange>(find_path[3]).value(),
                (TimeRange{TimePoint{start, false}, TimePoint{end, false}}));
      EXPECT_EQ(*match_tree.Find(res.front().data->match_data->data_id),
                *data_ptr[1]);
    }
    {
      const auto& find_path = res[1].path;
      EXPECT_EQ(find_path.size(), 4);
      EXPECT_EQ(std::get<EntityId>(find_path[0]), EntityId{MoscowId});
      EXPECT_EQ(std::get<EntityId>(find_path[1]), EntityId{EconomId});
      EXPECT_EQ(std::get<EntityId>(find_path[2]), EntityId{TestTagId});
      EXPECT_EQ(std::get<AnyOtherTimeRange>(find_path[3]).value(),
                (TimeRange{TimePoint{start, false}, TimePoint{end, false}}));
      EXPECT_EQ(*match_tree.Find(res.front().data->match_data->data_id),
                *data_ptr[1]);
    }
  }
}

TEST(RulesMatch, SimpleTypeTest) {
  auto type_text = types::ConditionTypeCollection::Find("text");
  EXPECT_TRUE(type_text != nullptr);

  auto type_time_range = types::ConditionTypeCollection::Find("time_range");
  EXPECT_TRUE(type_time_range != nullptr);

  auto type_integer = types::ConditionTypeCollection::Find("integer");
  EXPECT_TRUE(type_integer != nullptr);

  auto type_unknown = types::ConditionTypeCollection::Find("unknown");
  EXPECT_FALSE(type_unknown != nullptr);

  std::variant<int, float> val1;
  std::variant<int, float, std::string> val2;
  val2 = VariantCast(val1);
  // Compilation error
  //  val1 = VariantCast(val2);
}

TEST(RulesMatch, TestTimeRangeStorage) {
  auto time_ranges_type = ConditionTypeCollection::Find("time_range");
  auto storage = time_ranges_type->CreateConditionStorage();
  auto time1 = utils::datetime::Stringtime("2019-01-01T00:00:00+0000");
  auto time2 = utils::datetime::Stringtime("2019-01-02T00:00:00+0000");
  auto time3 = utils::datetime::Stringtime("2019-01-03T00:00:00+0000");
  auto entity_id_1 = EntityId{1};
  auto entity_id_2 = EntityId{2};
  auto range_1 = AnyOtherTimeRange{
      TimeRange{TimePoint{time1, false}, TimePoint{time3, false}}};
  auto range_2 = AnyOtherTimeRange{
      TimeRange{TimePoint{time1, false}, TimePoint{time2, false}}};

  storage->Insert(entity_id_1, range_1);
  storage->Insert(entity_id_2, range_2);

  EXPECT_EQ(std::get<AnyOtherTimeRange>(*storage->Find(entity_id_1)), range_1);
  EXPECT_EQ(std::get<AnyOtherTimeRange>(*storage->Find(entity_id_2)), range_2);

  EXPECT_EQ(storage->Find(range_1), entity_id_1);
  EXPECT_EQ(storage->Find(range_2), entity_id_2);
}

UTEST(RulesMatch, TestIntCondition) {
  const int kNum15 = 15;
  const int kNum25 = 25;
  const int64_t kBigNum15{kNum15};
  const int64_t kBigNum25{kNum25};
  auto number = MakeConditionDescription("number", "integer", "{\"value\": 15}",
                                         {ConditionFlags::ExclusionsForType});
  auto storage = number.GetStorage();
  storage->Insert(EntityId{kNum15}, AnyOtherInt{kBigNum15});
  storage->Insert(EntityId{kNum25}, AnyOtherInt{kBigNum25});

  {
    generated::AnyOtherConditionsVector num_vector = IntegerVector{kBigNum15};
    QueryConditionsVector query = number.QueryConditionsVectorFromGenerated(
        std::cref(num_vector), RulesMatch::MatchType::StrongMatch);
    EXPECT_EQ(std::get<EntityIdsVector>(query),
              EntityIdsVector{EntityId{kNum15}});
  }
  {
    generated::BaseConditionsVector num_vector = IntegerVector{kBigNum25};
    QueryConditionsVector query = number.QueryConditionsVectorFromGenerated(
        std::cref(num_vector), RulesMatch::MatchType::RegularMatch);
    EXPECT_EQ(std::get<EntityIdsVector>(query),
              EntityIdsVector{EntityId{kNum25}});
  }
  {
    ExclusionsPtr exclusions = number.CreateExclusions();
    exclusions->Add(EntityId{kNum25});
    QueryCondition query_condition = EntityId{kNum15};
    generated::PathCondition path_condition =
        number.MakeGeneratedPathCondition(query_condition, exclusions);
    const auto& path_condition_value =
        std::get<generated::PathConditionValue>(path_condition);
    EXPECT_EQ(path_condition_value.condition_name, "number");
    EXPECT_EQ(std::get<int64_t>(path_condition_value.value), kBigNum15);
    EXPECT_EQ(std::get<IntegerVector>(*path_condition_value.exclusions),
              IntegerVector{kBigNum25});
  }
}

TEST(RulesMatch, Invalid) {
  RulesMatch rules_match;
  EXPECT_THROW(rules_match.Check(), server::handlers::InternalServerError);
  EXPECT_THROW(rules_match.GetHierarchyDescriptions(),
               server::handlers::InternalServerError);
  EXPECT_THROW(rules_match.RulesCount(), server::handlers::InternalServerError);
  EXPECT_THROW(auto _ = rules_match.Find("hierarchy_name", (MatchConditions{}),
                                         RulesMatchBase::MatchType::WeakMatch),
               server::handlers::InternalServerError);
  EXPECT_THROW(
      auto _ = rules_match.Find("hierarchy_name", (MatchComplexConditions{}),
                                RulesMatchBase::MatchType::WeakMatch),
      server::handlers::InternalServerError);
  EXPECT_THROW(
      rules_match.IsHierarchyHasCondition("hierarchy_name", "condition_name"),
      server::handlers::InternalServerError);
}
