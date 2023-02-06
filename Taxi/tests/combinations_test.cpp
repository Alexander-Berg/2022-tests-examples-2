#include <gtest/gtest.h>

#include <subvention_matcher/impl/impl.hpp>

#include "common.hpp"

using namespace subvention_matcher;
using namespace subvention_matcher::impl;

using States = std::vector<Combinations::State>;

States GetAllStates(Combinations& comb) {
  States result;

  Combinations::State state;
  while (comb.Next(state)) {
    result.push_back(std::move(state));
  }

  return result;
}

struct Data {
  Combinations::Dimensions dimm;
  States expected;
};

struct CombinationsParametrized : public ::testing::TestWithParam<Data> {};

TEST_P(CombinationsParametrized, Test) {
  Combinations comb(GetParam().dimm);

  ASSERT_EQ(comb.Count(), GetParam().expected.size());
  ASSERT_EQ(GetAllStates(comb), GetParam().expected);
}

INSTANTIATE_TEST_SUITE_P(
    CombinationsParametrized, CombinationsParametrized,
    ::testing::ValuesIn({
        Data{{1}, {{0}}},                                                //
        Data{{3}, {{0}, {1}, {2}}},                                      //
        Data{{1, 1}, {{0, 0}}},                                          //
        Data{{1, 3}, {{0, 0}, {0, 1}, {0, 2}}},                          //
        Data{{2, 3}, {{0, 0}, {1, 0}, {0, 1}, {1, 1}, {0, 2}, {1, 2}}},  //
        Data{{2, 1, 2}, {{0, 0, 0}, {1, 0, 0}, {0, 0, 1}, {1, 0, 1}}}    //
    }));

struct BuildPropertiesVariantsData {
  DriverPropertiesByType properties_map;
  std::vector<DriverPropertyMap> expected;
};

struct BuildPropertiesVariantsParametrized
    : public ::testing::TestWithParam<BuildPropertiesVariantsData> {};

TEST_P(BuildPropertiesVariantsParametrized, Test) {
  ASSERT_EQ(BuildPropertiesVariants(GetParam().properties_map),
            GetParam().expected);
}

using PS = PropertySource;
using PT = PropertyType;

INSTANTIATE_TEST_SUITE_P(
    BuildPropertiesVariantsParametrized, BuildPropertiesVariantsParametrized,
    ::testing::ValuesIn({
        BuildPropertiesVariantsData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}},
            std::vector<DriverPropertyMap>{
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
            },
        },

        BuildPropertiesVariantsData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kFake}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}},
            std::vector<DriverPropertyMap>{
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kFake}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
            },
        },

        BuildPropertiesVariantsData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver},
                  {BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}},
            std::vector<DriverPropertyMap>{
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
            },
        },

        BuildPropertiesVariantsData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver},
                  {BrandingProperty{{false, true}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}},
            std::vector<DriverPropertyMap>{
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, true}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
            },
        },

        BuildPropertiesVariantsData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver},
                  {BrandingProperty{{false, true}}, PS::kFake}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea,
                 {{GeoareaProperty{{"geoarea"}}, PS::kDriver},
                  {GeoareaProperty{{"geoarea2"}}, PS::kFake}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}},
            std::vector<DriverPropertyMap>{
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, false}}, PS::kDriver}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea2"}}, PS::kFake}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, true}}, PS::kFake}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
                DriverPropertyMap{
                    {PT::kBranding,
                     {BrandingProperty{{false, true}}, PS::kFake}},
                    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},
                    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},
                    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},
                    {PT::kGeoarea, {GeoareaProperty{{"geoarea2"}}, PS::kFake}},
                    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},
                },
            },
        },

    }));
