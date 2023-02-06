#include <gtest/gtest.h>

#include <boost/algorithm/string/join.hpp>

#include "common.hpp"
#include "mocked_bsx.hpp"

#include <db/types.hpp>
#include <logic/mask_update.hpp>
#include <models/types.hpp>
#include <ranges/to_container.hpp>

using namespace logic;
using namespace logic::impl;

#include <set>

namespace db {

bool operator==(const MaskInfo& lhs, const MaskInfo& rhs) {
  return std::tie(lhs.rule_type, lhs.zone, lhs.tariff_class, lhs.tags,
                  lhs.active_from, lhs.active_to) ==
         std::tie(rhs.rule_type, rhs.zone, rhs.tariff_class, rhs.tags,
                  rhs.active_from, rhs.active_to);
}

}  // namespace db

namespace logic {

std::ostream& operator<<(std::ostream& os, const MaskTagsRange& data) {
  return os << "active_range: " << data.active_range << "; tags: "
            << (data.tags ? boost::join(*data.tags, ", ")
                          : std::string("none"));
}

bool operator==(const MaskTagsRange& lhs, const MaskTagsRange& rhs) {
  return std::tie(lhs.active_range, lhs.tags) ==
         std::tie(rhs.active_range, rhs.tags);
}

}  // namespace logic

struct UpdateMasksData {
  MasksByTime masks;
  ChangesByTime updates;
  MasksByTime expected;
};

struct UpdateMasksParametrized : public BaseTestWithParam<UpdateMasksData> {};

TEST_P(UpdateMasksParametrized, UpdateMasks) {
  mocks::BSXClient client;
  DefaultTagsUpdateStrategy strategy(client);

  ASSERT_EQ(GetParam().expected,
            UpdateMasks(
                {
                    "test_zone",
                    "test_tariff",
                    models::RuleType::kSingleRide,
                },
                GetParam().masks, GetParam().updates, strategy));
}

INSTANTIATE_TEST_SUITE_P(
    UpdateMasksParametrized, UpdateMasksParametrized,
    ::testing::ValuesIn({
        UpdateMasksData{
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
            },
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    TagsChange{
                        {"t3"},
                        {},
                    },
                },
            },
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3"},
                },
            },
        },

        UpdateMasksData{
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
            },
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    TagsChange{
                        {"t3"},
                        {},
                    },
                },
                {
                    dt::Stringtime("2021-08-02T00:00:00Z"),
                    TagsChange{
                        {"t4"},
                        {},
                    },
                },
            },
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3", "t4"},
                },
            },
        },

        UpdateMasksData{
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-03T00:00:00Z"),
                    },
                    {"t1", "t4"},
                },
            },
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    TagsChange{
                        {"t3"},
                        {},
                    },
                },
            },
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-03T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t3",
                     "t4"},
                },
            },
        },

        UpdateMasksData{
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-03T00:00:00Z"),
                    },
                    {"t1", "t4"},
                },
            },
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    TagsChange{
                        {"t3"},
                        {},
                    },
                },
                {
                    dt::Stringtime("2021-08-02T12:00:00Z"),
                    TagsChange{
                        {"t5"},
                        {},
                    },
                },
            },
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-02T12:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t3",
                     "t4"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T12:00:00Z"),
                        dt::Stringtime("2021-08-03T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t3",
                     "t4", "t5"},
                },
            },
        },

        UpdateMasksData{
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
            },
            {
                {
                    dt::Stringtime("2021-08-02T00:00:00Z"),
                    TagsChange{
                        {"t3"},
                        {},
                    },
                },
            },
            {
                {
                    {
                        dt::Stringtime("2021-08-01T00:00:00Z"),
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                    },
                    {"t1", "t2"},
                },
                {
                    {
                        dt::Stringtime("2021-08-02T00:00:00Z"),
                        dt::Stringtime("2021-08-10T00:00:00Z"),
                    },
                    {"subv_disable_all", "subv_disable_single_ride", "t1", "t2",
                     "t3"},
                },
            },
        },
    }));

struct SelectMasksData {
  std::vector<db::MaskInfo> masks;
  std::vector<db::MaskInfo> expected;
};

struct SelectMasksParametrized : public BaseTestWithParam<SelectMasksData> {};

TEST_P(SelectMasksParametrized, SelectMasks) {
  ASSERT_EQ(GetParam().expected, logic::impl::SelectMasks(GetParam().masks));
}

std::vector<db::MaskInfo> CreateDummyMasks(const std::vector<bool>& active) {
  std::vector<db::MaskInfo> result;
  result.reserve(active.size());
  for (const bool a : active) {
    db::MaskInfo info;
    info.is_active = a;
    result.push_back(std::move(info));
  }
  return result;
}

INSTANTIATE_TEST_SUITE_P(SelectMasksParametrized, SelectMasksParametrized,
                         ::testing::ValuesIn({
                             SelectMasksData{
                                 CreateDummyMasks({false, false}),
                                 CreateDummyMasks({false, false}),
                             },
                             SelectMasksData{
                                 CreateDummyMasks({false, false, true}),
                                 CreateDummyMasks({false, false}),
                             },
                             SelectMasksData{
                                 CreateDummyMasks({false, false, true, true}),
                                 CreateDummyMasks({false, false}),
                             },
                             SelectMasksData{
                                 CreateDummyMasks({false, true, true}),
                                 CreateDummyMasks({false}),
                             },
                             SelectMasksData{
                                 CreateDummyMasks({true, true}),
                                 CreateDummyMasks({true, true}),
                             },
                         }));

struct GetTagsRangesData {
  std::set<models::TimeRange> week_ranges;
  std::vector<db::MaskInfo> masks_data;
  std::vector<MaskTagsRange> expected;
};

struct GetTagsRangesParametrized : public BaseTestWithParam<GetTagsRangesData> {
};

TEST_P(GetTagsRangesParametrized, GetTagsRanges) {
  ASSERT_EQ(GetParam().expected,
            GetTagsRanges(GetParam().week_ranges, GetParam().masks_data));
}

db::MaskInfo CreateMask(std::string from, std::string to,
                        std::set<std::string> tags) {
  db::MaskInfo info;

  info.is_active = false;
  info.active_from = dt::Stringtime(from);
  info.active_to = dt::Stringtime(to);
  info.tags = tags | ranges::ToVector;

  return info;
}

MaskTagsRange CreateMaskTagsRange(std::string from, std::string to,
                                  std::optional<std::set<std::string>> tags) {
  MaskTagsRange info;

  info.active_range.from = dt::Stringtime(from);
  info.active_range.to = dt::Stringtime(to);
  info.tags = tags;

  return info;
}

INSTANTIATE_TEST_SUITE_P(
    GetTagsRangesParametrized, GetTagsRangesParametrized,
    ::testing::ValuesIn({
        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
            },
            {
                CreateMask("2021-08-01T00:00:00Z", "2021-08-10T00:00:00Z",
                           {"t1"}),
            },
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-10T00:00:00Z", {{"t1"}}),
            },
        },
        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
            },
            {},
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-10T00:00:00Z", std::nullopt),
            },
        },

        GetTagsRangesData{
            {},
            {},
            {},
        },

        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
            },
            {
                CreateMask("2021-07-01T00:00:00Z", "2021-08-10T00:00:00Z",
                           {"t1"}),
            },
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-10T00:00:00Z", {{"t1"}}),
            },
        },

        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
            },
            {
                CreateMask("2021-08-01T00:00:00Z", "2021-08-05T00:00:00Z",
                           {"t1"}),
                CreateMask("2021-08-05T00:00:00Z", "2021-08-10T00:00:00Z",
                           {"t2"}),
            },
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-05T00:00:00Z", {{"t1"}}),
                CreateMaskTagsRange("2021-08-05T00:00:00Z",
                                    "2021-08-10T00:00:00Z", {{"t2"}}),
            },
        },

        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                    dt::Stringtime("2021-08-20T00:00:00Z"),
                },
            },
            {
                CreateMask("2021-07-01T00:00:00Z", "2021-08-20T00:00:00Z",
                           {{"t1"}}),
            },
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-10T00:00:00Z", {{"t1"}}),
                CreateMaskTagsRange("2021-08-10T00:00:00Z",
                                    "2021-08-20T00:00:00Z", {{"t1"}}),
            },
        },

        GetTagsRangesData{
            {
                {
                    dt::Stringtime("2021-08-01T00:00:00Z"),
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                },
                {
                    dt::Stringtime("2021-08-10T00:00:00Z"),
                    dt::Stringtime("2021-08-20T00:00:00Z"),
                },
            },
            {
                CreateMask("2021-07-01T00:00:00Z", "2021-08-05T00:00:00Z",
                           {"t1"}),
                CreateMask("2021-08-05T00:00:00Z", "2021-08-15T00:00:00Z",
                           {"t2"}),
                CreateMask("2021-08-15T00:00:00Z", "2021-08-20T00:00:00Z",
                           {"t3"}),
            },
            {
                CreateMaskTagsRange("2021-08-01T00:00:00Z",
                                    "2021-08-05T00:00:00Z", {{"t1"}}),
                CreateMaskTagsRange("2021-08-05T00:00:00Z",
                                    "2021-08-10T00:00:00Z", {{"t2"}}),
                CreateMaskTagsRange("2021-08-10T00:00:00Z",
                                    "2021-08-15T00:00:00Z", {{"t2"}}),
                CreateMaskTagsRange("2021-08-15T00:00:00Z",
                                    "2021-08-20T00:00:00Z", {{"t3"}}),
            },
        },
    }));
