#include <gtest/gtest.h>

#include <cstdint>
#include <iostream>
#include <set>
#include <string>
#include <userver/utils/datetime.hpp>

#include <boost/algorithm/string/join.hpp>

#include <common_handlers/schedule_summary/ssch_schedule_merging.hpp>
#include <common_handlers/types.hpp>
#include <subvention_matcher/types.hpp>

#include "build_dummy_schedules.hpp"

using namespace subvention_matcher;
namespace ch = common_handlers;

// clang-format off

namespace {
bool PRINT_TEST_LOGS = true;
} // namespace

void print_test_log(std::string log) {
    if (PRINT_TEST_LOGS) {
        std::cout << log << "\n";
    }
}

void PrintTimeranges(Schedule schedule, std::string prefix) {
    print_test_log(">>>>START PRINTING TIMERANGES");
    for (auto it : schedule) {
        std::string timerange_id = it.first.ToString();
        print_test_log(prefix + "timerange id: " + timerange_id);
    }
    print_test_log(">>>>FINISH PRINTING TIMERANGES");
}

void PrintGR(GroupedRule gr, std::string prefix) {
    print_test_log(">>>>START PRINTING GR");
    print_test_log(prefix + "zones: " + boost::algorithm::join(gr.zones, ", "));
    print_test_log(prefix + "tariff_classes: " + boost::algorithm::join(gr.tariff_classes, ", "));
    print_test_log(prefix + "geoareas: " + boost::algorithm::join(gr.geoareas, ", "));
    print_test_log(">>>>FINISH PRINTING GR");
}

void PrintGRMS(GroupedRuleMatchesSchedule grms) {
    print_test_log(">>START PRINTING GRMS");
    for (auto it : grms) {
        std::string id = it.first.GetDebugId();
        print_test_log("grms id: " + id);
        
        std::string prefix = "for id " + id + ": ";

        PrintGR(it.first, prefix);
        PrintTimeranges(it.second, prefix);
    }
    print_test_log(">>FINISH PRINTING GRMS");
}

bool CheckKeysForGRMS(GroupedRuleMatchesSchedule grms, std::set<std::string> ids) {
    print_test_log("START KEY CHECKING");
    PrintGRMS(grms);

    for (auto it : grms) {
        std::string id = it.first.GetDebugId();
        if (!ids.count(id)) {
            print_test_log("extra id: " + id);
            return false;
        }
        ids.erase(id);
    }

    if (ids.size() > 0) {
        print_test_log("missing ids: " + boost::algorithm::join(ids, ", "));
        return false;
    }

    print_test_log("FINISH KEY CHECKING");
    return true;
}

bool CheckGRMS(ch::GroupedRuleMatchesNewSchedule grms, std::unordered_map<std::string, std::set<std::string>> ids_to_timeranges) {
    print_test_log("START GRMS CHECKING");
    for (auto it : grms) {
        std::string id = it.first.GetDebugId();
        if (ids_to_timeranges.find(id) == ids_to_timeranges.end()) {
            print_test_log("extra id in ids_to_timeranges: " + id);
            return false;
        }

        std::string prefix = "for id " + id + ": ";

        auto& expected_timeranges = ids_to_timeranges[id];
        
        for (auto timerange_it: it.second) {
            std::string timerange_id = timerange_it.first.ToString();

            if (!expected_timeranges.count(timerange_id)) {
                print_test_log(prefix + "extra timerange: " + timerange_id);
                return false;
            }
            expected_timeranges.erase(timerange_id);
        }

        if (expected_timeranges.size() > 0) {
            print_test_log(prefix + "missing timeranges: " + boost::algorithm::join(expected_timeranges, ", "));
            return false;
        }

        ids_to_timeranges.erase(id);
    }

    if (ids_to_timeranges.size() > 0) {
        std::vector<std::string> missing_ids;
        for (auto it: ids_to_timeranges) {
            missing_ids.push_back(it.first);
        }

        print_test_log("missing ids: " + boost::algorithm::join(missing_ids, ", "));
        return false;
    }

    print_test_log("FINISH GRMS CHECKING");
    return true;
}

bool CheckTimerangesAndGRs(std::vector<ch::ManyGRScheduleInfos> vec, std::unordered_map<std::string, std::set<std::string>> timeranges_to_ids) {
    print_test_log("START TIMERANGES AND GRS CHECKING");

    for (auto it: vec) {
        std::string timerange_id = it.time_range.ToString();
        if (timeranges_to_ids.find(timerange_id) == timeranges_to_ids.end()) {
            print_test_log("extra id in ids_to_timeranges: " + timerange_id);
            return false;
        }

        std::string prefix = "for timerange " + timerange_id + ": ";

        auto& expected_grs = timeranges_to_ids[timerange_id];


        for (auto grs_it: it.grouped_rule_matches) {
            std::string id = grs_it.first.GetDebugId();

            if (!expected_grs.count(id)) {
                print_test_log(prefix + "extra gr: " + id);
                return false;
            }
            expected_grs.erase(id);
        }

        if (expected_grs.size() > 0) {
            print_test_log(prefix + "missing grs: " + boost::algorithm::join(expected_grs, ", "));
            return false;
        }

        timeranges_to_ids.erase(timerange_id);
    }


    if (timeranges_to_ids.size() > 0) {
        std::vector<std::string> missing_timeranges;
        for (auto it: timeranges_to_ids) {
            missing_timeranges.push_back(it.first);
        }

        print_test_log("missing timeranges: " + boost::algorithm::join(missing_timeranges, ", "));
        return false;
    }

    print_test_log("FINISH TIMERANGES AND GRS CHECKING");
    return true;
}


TimePoint BuildTimePoint(std::string time_string) {
    return  dt::Stringtime(time_string, "Europe/London", kTimeFormat);
}

/*
Проверка работы мерджинга(MergeTimeRanges) тайм ренджей.
Для проверки используются наполовину-dummy GroupedRules: для проверки имеют значение
только поля gr_id и gr_type. 
gr_id используется только для проверки верности работы,
gr_type указывает на "тип" объекта GroupedRules. 
Если у двух объектов одинаковые gr_type, то их можно мерджить.
*/

struct MergeGroupedRulesTestData {
  std::vector<TimeRangeAndGRID> unmerged_params;

  std::unordered_map<std::string, std::set<std::string>> timerange_to_ids;
};

struct MergeGroupedRulesTestParametrized
    : public BaseTestWithParam<MergeGroupedRulesTestData> {};


TEST_P(MergeGroupedRulesTestParametrized, Test) {
  auto vector = handlers::merging::MergeManyClasses(BuildVectorForMerge(GetParam().unmerged_params));

  ASSERT_EQ(CheckTimerangesAndGRs(vector, GetParam().timerange_to_ids), true);
}

INSTANTIATE_TEST_SUITE_P(
    MergeGroupedRulesTestParametrized, MergeGroupedRulesTestParametrized,
    ::testing::ValuesIn({
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // dummy test
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-02T00:00:00Z")
                    },
                    0,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}}
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // dummy distinguish different types
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "B"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"1"}}
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // simple intersection
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // simple sorting and intersect
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // simple absorption, right side
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // simple absorption, left side
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-02T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0","1"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  // simple equality
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{  
                // medium intersection, full abosrption of middle range
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"1","2"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // medium intersection, with more full absorption
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    2,
                    "A"
                },
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"0"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","1"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-06T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"2"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // simple telescoping
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-08T00:00:00+0000>", {"0","1"}},
                {"<2021-01-08T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"0"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // telescoping, with finding correct place for 0-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","2"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>", {"2"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // intersecting, finding correct place for 1-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"1","2"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-08T00:00:00+0000>", {"2"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // intersecting, finding correct place for 0 and 1-parts' merge result,
                // and correct place for 1-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-07T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-07T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"0","1"}},
                {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>", {"1"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // more hard telescoping and places-finding
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-07T00:00:00+0000>", {"0","2"}},
                {"<2021-01-07T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"0"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // more hard telescoping and places-finding
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"0","2"}},
                {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>", {"2"}},
            }
        },
        MergeGroupedRulesTestData{
            std::vector<TimeRangeAndGRID>{
                // hard telescoping and intersection
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    2,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    3,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    4,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    5,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"0"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"0","1"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","1","2","4","5"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>", {"0","1","3","4","5"}},
                {"<2021-01-06T00:00:00+0000; 2021-01-07T00:00:00+0000>", {"0","1","3","5"}},
                {"<2021-01-07T00:00:00+0000; 2021-01-08T00:00:00+0000>", {"0","1","5"}},
                {"<2021-01-08T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"0","5"}},
                {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>", {"5"}},
            }
        },
        MergeGroupedRulesTestData{
            // hard intersection
            std::vector<TimeRangeAndGRID>{
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    2,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    3,
                    "B"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    4,
                    "B"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    5,
                    "C"
                },
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>", {"0"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"0","1"}},
                {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>", {"0","1","2"}},
                {"<2021-01-06T00:00:00+0000; 2021-01-09T00:00:00+0000>", {"2"}},
                {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", {"3"}},
                {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>", {"3","4"}},
                {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>", {"4"}},
                {"<2021-01-04T00:00:00+0000; 2021-01-06T00:00:00+0000>", {"5"}},
            }
        }
}));

/*
Проверка работы полного цикла мерджинга(ConvertScheduleItemsIntoGRMS)
*/

struct FullMergeTestData {
  std::vector<TimeRangeAndGRID> unmerged_params;

  std::unordered_map<std::string, std::set<std::string>> ids_to_timeranges;
};

struct FullMergeTestParametrized
    : public BaseTestWithParam<FullMergeTestData> {};

TEST_P(FullMergeTestParametrized, Test) {
    auto schedule = BuildSSCHSchedule(GetParam().unmerged_params);

    ASSERT_EQ(CheckGRMS(handlers::merging::ConvertScheduleItemsIntoGRMS(std::move(schedule)), 
              GetParam().ids_to_timeranges), true);
}


INSTANTIATE_TEST_SUITE_P(
    FullMergeTestParametrized, FullMergeTestParametrized,
    ::testing::ValuesIn({
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 0 dummy test
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-02T00:00:00Z")
                    },
                    0,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}}
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 1 dummy distinguish different types
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "B"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1", {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>"}}
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 2 simple intersection
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1", {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 3 simple sorting and intersect
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1", {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 4 simple absorption, right side
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 5 simple absorption, left side
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-02T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0|1", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  // 6 simple equality
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0|1", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{  
                // 7 medium intersection, full abosrption of middle range
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1|2", {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 8 medium intersection, with more full absorption
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    2,
                    "A"
                },
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
                {"0|1", {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>"}},
                {"2", {"<2021-01-06T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 9 simple telescoping
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    1,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>", "<2021-01-08T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-08T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 10 telescoping, with finding correct place for 0-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
                {"0|2", {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"2", {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 11 intersecting, finding correct place for 1-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-04T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1|2", {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
                {"2", {"<2021-01-04T00:00:00+0000; 2021-01-08T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 12 intersecting, finding correct place for 0 and 1-parts' merge result,
                // and correct place for 1-part's right shard
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-03T00:00:00+0000; 2021-01-07T00:00:00+0000>"}},
                {"0|1", {"<2021-01-07T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"1", {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 13 more hard telescoping and places-finding
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>", "<2021-01-07T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"0|2", {"<2021-01-05T00:00:00+0000; 2021-01-07T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 14 more hard telescoping and places-finding
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    2,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"0|2", {"<2021-01-05T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"2", {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            std::vector<TimeRangeAndGRID>{
                // 15 hard telescoping and intersection
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-08T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-03T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    2,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-07T00:00:00Z")
                    },
                    3,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    4,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-10T00:00:00Z")
                    },
                    5,
                    "A"
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"0|1", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-03T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
                {"0|1|2|4|5", {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"0|1|3|4|5", {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>"}},
                {"0|1|3|5", {"<2021-01-06T00:00:00+0000; 2021-01-07T00:00:00+0000>"}},
                {"0|1|5", {"<2021-01-07T00:00:00+0000; 2021-01-08T00:00:00+0000>"}},
                {"0|5", {"<2021-01-08T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"5", {"<2021-01-09T00:00:00+0000; 2021-01-10T00:00:00+0000>"}},
            }
        },
        FullMergeTestData{
            // 16 hard intersection
            std::vector<TimeRangeAndGRID>{
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    0,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    1,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-05T00:00:00Z"),
                        BuildTimePoint("2021-01-09T00:00:00Z")
                    },
                    2,
                    "A"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    3,
                    "B"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-02T00:00:00Z"),
                        BuildTimePoint("2021-01-05T00:00:00Z")
                    },
                    4,
                    "B"
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-04T00:00:00Z"),
                        BuildTimePoint("2021-01-06T00:00:00Z")
                    },
                    5,
                    "C"
                },
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-02T00:00:00+0000; 2021-01-04T00:00:00+0000>"}},
                {"0|1", {"<2021-01-04T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"0|1|2", {"<2021-01-05T00:00:00+0000; 2021-01-06T00:00:00+0000>"}},
                {"2", {"<2021-01-06T00:00:00+0000; 2021-01-09T00:00:00+0000>"}},
                {"3", {"<2021-01-01T00:00:00+0000; 2021-01-02T00:00:00+0000>"}},
                {"3|4", {"<2021-01-02T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"4", {"<2021-01-03T00:00:00+0000; 2021-01-05T00:00:00+0000>"}},
                {"5", {"<2021-01-04T00:00:00+0000; 2021-01-06T00:00:00+0000>"}},
            }
        }
}));


/*
Проверка работы полного цикла мерджинга(ConvertScheduleItemsIntoGRMS),
где при мердже рассматривается rate
*/

struct FullMergeWithRateTestData {
  std::vector<TimeRangeAndGRIDAndRate> unmerged_params;

  std::unordered_map<std::string, std::set<std::string>> ids_to_timeranges;
};

struct FullMergeWithRateTestParametrized
    : public BaseTestWithParam<FullMergeWithRateTestData> {};

TEST_P(FullMergeWithRateTestParametrized, Test) {
    auto schedule = BuildSSCHScheduleWithRate(GetParam().unmerged_params);

    ASSERT_EQ(CheckGRMS(handlers::merging::ConvertScheduleItemsIntoGRMS(std::move(schedule)), 
              GetParam().ids_to_timeranges), true);
}

INSTANTIATE_TEST_SUITE_P(
    FullMergeWithRateTestParametrized, FullMergeWithRateTestParametrized,
    ::testing::ValuesIn({
        FullMergeWithRateTestData{
            std::vector<TimeRangeAndGRIDAndRate>{
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    0,
                    "A",
                    1
                },
                {
                    TimeRange{
                        BuildTimePoint("2021-01-01T00:00:00Z"),
                        BuildTimePoint("2021-01-03T00:00:00Z")
                    },
                    1,
                    "A",
                    2
                }
            },
            std::unordered_map<std::string, std::set<std::string>>{
                {"0", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}},
                {"1", {"<2021-01-01T00:00:00+0000; 2021-01-03T00:00:00+0000>"}}
            }
        }
}));

