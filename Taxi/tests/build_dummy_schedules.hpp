#include <cstdint>
#include <string>
#include <userver/utils/datetime.hpp>

#include <clients/subvention-schedule/definitions.hpp>
#include <common_handlers/schedule_summary/common.hpp>
#include <subvention_matcher/types.hpp>

#include "common.hpp"

using namespace subvention_matcher;
namespace ssch = clients::subvention_schedule;
namespace ch = common_handlers;

static const std::string kTimeFormat = "%Y-%m-%dT%H:%M:%SZ";

inline GroupedRule BuildBasicGroupedRuleWithId(const uint32_t id) {
  return GroupedRule(CreateRuleWithId("dummy_zone", "dummy_geoarea",
                                      "dummy_tariff_class", 42, id));
}

inline GroupedRule BuildGroupedRuleWithIds(const std::vector<uint32_t>& ids) {
  std::optional<GroupedRule> grouped_rule;

  for (const auto id : ids) {
    if (!grouped_rule) {
      grouped_rule = BuildBasicGroupedRuleWithId(id);
    } else {
      grouped_rule->Merge(BuildBasicGroupedRuleWithId(id));
    }
  }

  return *grouped_rule;
}

inline ScheduleItem BuildDummyScheduleItemWithRate(const double rate = 42) {
  PropertySource dummy_property_source = PropertySource::kFake;
  Property dummy_property = ZoneProperty{{"dummy_zone_property"}};
  DriverProperty dummy_driver_property{dummy_property, dummy_property_source};

  PropertyType dummy_property_type = PropertyType::kZone;

  DriverPropertyMap dummy_driver_property_map;
  dummy_driver_property_map[dummy_property_type] = dummy_driver_property;

  ScheduleItem dummy_schedule_item;
  dummy_schedule_item.properties = dummy_driver_property_map;
  dummy_schedule_item.rate = rate;

  return dummy_schedule_item;
}

inline NewScheduleItem BuildDummyNewScheduleItem(const double rate = 42) {
  return {true, true, rate};
}

inline ch::NewSchedule BuildDummySchedule() {
  NewScheduleItem dummy_schedule_item = BuildDummyNewScheduleItem();

  TimeRange dummy_time_range = TimeRange{
      dt::Stringtime("2021-01-28T15:00:00Z", "Europe/Moscow", kTimeFormat),
      dt::Stringtime("2021-02-04T15:00:00Z", "Europe/Moscow", kTimeFormat),
  };
  ch::NewSchedule dummy_schedule;
  dummy_schedule[dummy_time_range] = dummy_schedule_item;

  return dummy_schedule;
}

inline ch::GroupedRuleMatchesNewSchedule BuildRuleToDummySchedule(
    const std::vector<std::vector<uint32_t>>& grouped_rules_ids) {
  ch::GroupedRuleMatchesNewSchedule rule_to_schedule;
  for (const auto& grouped_rule_ids : grouped_rules_ids) {
    rule_to_schedule[BuildGroupedRuleWithIds(grouped_rule_ids)] =
        BuildDummySchedule();
  }

  return rule_to_schedule;
}

struct SchedulePair {
  TimeRange time_range;
  double rate;
};

inline ch::NewSchedule BuildTimeRangeToDummyScheduleItemWithRate(
    const std::vector<SchedulePair>& schedule_pairs) {
  ch::NewSchedule schedule;
  for (const auto& schedule_pair : schedule_pairs) {
    schedule[schedule_pair.time_range] =
        BuildDummyNewScheduleItem(schedule_pair.rate);
  }

  return schedule;
}

struct ScheduleParts {
  TimeRange time_range;
  std::optional<bool> is_activity_satisfied;
  std::optional<bool> is_branding_satisfied;
  double rate;
};

struct GRMSParts {
  std::vector<uint32_t> grouped_rule_ids;
  std::optional<std::vector<ScheduleParts>>
      schedule_parts;  // if {}, build DummySchedule
};

inline ch::NewSchedule BuildFullSchedule(
    const std::vector<ScheduleParts>& schedule_parts) {
  ch::NewSchedule schedule;

  for (const auto& schedule_part : schedule_parts) {
    schedule[schedule_part.time_range] = NewScheduleItem{
        schedule_part.is_activity_satisfied,
        schedule_part.is_branding_satisfied, schedule_part.rate};
  }

  return schedule;
}

inline ch::GroupedRuleMatchesNewSchedule BuildFullGRMS(
    const std::vector<GRMSParts> grms_parts) {
  ch::GroupedRuleMatchesNewSchedule grms;

  for (const auto& grms_part : grms_parts) {
    const auto rule = BuildGroupedRuleWithIds(grms_part.grouped_rule_ids);
    ch::NewSchedule schedule;
    if (grms_part.schedule_parts) {
      schedule = BuildFullSchedule(*grms_part.schedule_parts);
    } else {
      schedule = BuildDummySchedule();
    }

    grms[rule] = schedule;
  }

  return grms;
}

struct TimeRangeAndGRID {
  TimeRange time_range;
  uint32_t gr_id;
  std::string gr_type;
};

inline std::vector<ch::SingleGRScheduleInfo> BuildVectorForMerge(
    const std::vector<TimeRangeAndGRID> source) {
  std::vector<ch::SingleGRScheduleInfo> result;

  for (auto source_item : source) {
    GroupedRule gr(
        CreateExpandedRule("zone_" + std::to_string(source_item.gr_id),
                           "geoarea_" + std::to_string(source_item.gr_id),
                           "tariff_class_" + std::to_string(source_item.gr_id),
                           42, source_item.gr_id, source_item.gr_type));

    result.push_back({source_item.time_range, std::make_shared<GroupedRule>(gr),
                      BuildDummyNewScheduleItem()});
  }

  return result;
}

inline ssch::Schedule BuildSSCHSchedule(
    const std::vector<TimeRangeAndGRID> source) {
  ssch::Schedule result;

  result.type = ssch::RuleType::kSingleRide;

  for (auto source_item : source) {
    ssch::ScheduleItem ssch_item;

    ssch_item.rule_id = std::to_string(source_item.gr_id);
    ssch_item.draft_id = source_item.gr_type;
    ssch_item.time_range =
        ssch::TimeRange{source_item.time_range.from, source_item.time_range.to};
    ssch_item.rate = 42;
    ssch_item.tariff_zone = "zone_" + std::to_string(source_item.gr_id);
    ssch_item.tariff_class =
        "tariff_class_" + std::to_string(source_item.gr_id);
    ssch_item.geoarea = "geoarea_" + std::to_string(source_item.gr_id);

    result.items.push_back(ssch_item);
  }

  return result;
}

struct TimeRangeAndGRIDAndRate {
  TimeRange time_range;
  uint32_t gr_id;
  std::string gr_type;
  double rate;
};

inline ssch::Schedule BuildSSCHScheduleWithRate(
    const std::vector<TimeRangeAndGRIDAndRate> source) {
  ssch::Schedule result;

  result.type = ssch::RuleType::kSingleRide;

  for (auto source_item : source) {
    ssch::ScheduleItem ssch_item;

    ssch_item.rule_id = std::to_string(source_item.gr_id);
    ssch_item.draft_id = source_item.gr_type;
    ssch_item.time_range =
        ssch::TimeRange{source_item.time_range.from, source_item.time_range.to};
    ssch_item.rate = source_item.rate;
    ssch_item.tariff_zone = "zone_" + std::to_string(source_item.gr_id);
    ssch_item.tariff_class =
        "tariff_class_" + std::to_string(source_item.gr_id);
    ssch_item.geoarea = "geoarea_" + std::to_string(source_item.gr_id);

    result.items.push_back(ssch_item);
  }

  return result;
}
