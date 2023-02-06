#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <fmt/format.h>
#include <boost/algorithm/string/join.hpp>

#include <userver/utils/datetime.hpp>
#include <userver/utils/invariant_error.hpp>
#include <userver/utils/optionals.hpp>

#include <models/metrics.hpp>
#include <subvention_matcher/impl/impl.hpp>
#include <subvention_matcher/impl/rule_info/property_variants.hpp>
#include <subvention_matcher/match.hpp>

#include "common.hpp"

using namespace subvention_matcher;
using namespace subvention_matcher::impl;
using namespace subvention_matcher::impl::rule_info;

struct DriverPropertiesData {
  MatchParameters driver_info;
  DriverProperties expected;
};

struct ToDriverPropertiesParametrized
    : public ::testing::TestWithParam<DriverPropertiesData> {};

TEST_P(ToDriverPropertiesParametrized, Test) {
  ASSERT_EQ(ToDriverProperties(GetParam().driver_info), GetParam().expected);
}

using PS = PropertySource;
INSTANTIATE_TEST_SUITE_P(
    ToDriverPropertiesParametrized, ToDriverPropertiesParametrized,
    ::testing::ValuesIn({

        DriverPropertiesData{
            MatchParameters{
                {},
                {},
                "zone",
                "class",
                {false, false},
                50,
                {{"tag"}},
                {},
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},
                {ActivityProperty{{50}}, PS::kDriver},
                {TagsProperty{{{"tag"}}}, PS::kDriver},
                {ZoneProperty{{"zone"}}, PS::kDriver},
                {ClassProperty{{"class"}}, PS::kDriver},
            },
        },
    }));

struct FilterPropertiesData {
  DriverProperties original;
  PropertyTypes restrictions;
  DriverProperties expected;
};

struct FilterPropertiesParametrized
    : public ::testing::TestWithParam<FilterPropertiesData> {};

TEST_P(FilterPropertiesParametrized, Test) {
  ASSERT_EQ(FilterProperties(GetParam().original, GetParam().restrictions),
            GetParam().expected);
}

using PT = PropertyType;
INSTANTIATE_TEST_SUITE_P(
    FilterPropertiesParametrized, FilterPropertiesParametrized,
    ::testing::ValuesIn({

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {},
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}}          //
        },

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class11"}}, PS::kDriver},        //
                {ClassProperty{{"class1"}}, PS::kFake}},          //
            {},
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class11"}}, PS::kDriver},        //
                {ClassProperty{{"class1"}}, PS::kFake}},          //
        },

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {PT::kClass},
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver}}            //
        },

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class11"}}, PS::kDriver},        //
                {ClassProperty{{"class1"}}, PS::kFake}},          //
            {PT::kClass},
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver}}            //
        },

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class11"}}, PS::kDriver},        //
                {ClassProperty{{"class1"}}, PS::kFake}},          //
            {PT::kClass, PT::kActivity},
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver}}            //
        },

        FilterPropertiesData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class11"}}, PS::kDriver},        //
                {ClassProperty{{"class1"}}, PS::kFake}},          //
            {PT::kClass, PT::kActivity, PT::kZone, PT::kGeoarea, PT::kBranding,
             PT::kTags},
            DriverProperties{}  //
        }

    }));

struct ToPropertyByTypeData {
  DriverProperties original;
  DriverPropertiesByType expected;
};

struct ToPropertyByTypeDataParametrized
    : public ::testing::TestWithParam<ToPropertyByTypeData> {};

TEST_P(ToPropertyByTypeDataParametrized, Test) {
  ASSERT_EQ(ToPropertyByType(GetParam().original), GetParam().expected);
}

INSTANTIATE_TEST_SUITE_P(
    ToPropertyByTypeDataParametrized, ToPropertyByTypeDataParametrized,
    ::testing::ValuesIn({

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {BrandingProperty{{false, true}}, PS::kDriver},   //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver},
                  {BrandingProperty{{false, true}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {ActivityProperty{{60}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity,
                 {{ActivityProperty{{50}}, PS::kDriver},
                  {ActivityProperty{{60}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {TagsProperty{{{"tag2"}}}, PS::kDriver},          //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags,
                 {{TagsProperty{{{"tag"}}}, PS::kDriver},
                  {TagsProperty{{{"tag2"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ZoneProperty{{"zone2"}}, PS::kDriver},           //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone,
                 {{ZoneProperty{{"zone"}}, PS::kDriver},
                  {ZoneProperty{{"zone2"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {GeoareaProperty{{"geoarea2"}}, PS::kDriver},     //
                {ClassProperty{{"class"}}, PS::kDriver}           //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea,
                 {{GeoareaProperty{{"geoarea"}}, PS::kDriver},
                  {GeoareaProperty{{"geoarea2"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}}},

        ToPropertyByTypeData{
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class2"}}, PS::kDriver}          //
            },
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}}, PS::kDriver}}},
                {PT::kClass,
                 {{ClassProperty{{"class"}}, PS::kDriver},
                  {ClassProperty{{"class2"}}, PS::kDriver}}}}}

    }));

struct GetPropertiesData {
  Rules original;
  PropertyType type;
  DriverProperties expected;
};

struct GetPropertiesParametrized
    : public ::testing::TestWithParam<GetPropertiesData> {};

TEST_P(GetPropertiesParametrized, Test) {
  ASSERT_EQ(GetProperties(GetParam().original, GetParam().type),
            GetParam().expected);
}

namespace {

Rule CreateZoneRule(std::string zone) {
  Rule rule;
  rule.zone = std::move(zone);
  return rule;
}

Rule CreateGeoareaRule(std::string geoarea) {
  Rule rule;
  rule.geoarea = std::move(geoarea);
  return rule;
}

Rule CreateClassRule(std::string tariff_class) {
  Rule rule;
  rule.tariff_class = std::move(tariff_class);
  return rule;
}

namespace bsx = clients::billing_subventions_x;
Rule CreateBrandingRule(bsx::BrandingType type) {
  Rule rule;
  rule.branding_type = std::move(type);
  return rule;
}

Rule CreateActivityRule(int activity) {
  Rule rule;
  rule.activity_points = activity;
  return rule;
}

}  // namespace

INSTANTIATE_TEST_SUITE_P(
    GetPropertiesParametrized, GetPropertiesParametrized,
    ::testing::ValuesIn({
        //***************** ZONE *****************//
        GetPropertiesData{
            Rules{},              //
            PropertyType::kZone,  //
            DriverProperties{}    //
        },

        GetPropertiesData{Rules{CreateZoneRule("zone")},  //
                          PropertyType::kZone,            //
                          DriverProperties{
                              {ZoneProperty{{"zone"}}, PS::kFake},  //
                          }},

        GetPropertiesData{
            Rules{CreateZoneRule("zone"), CreateZoneRule("zone")},  //
            PropertyType::kZone,                                    //
            DriverProperties{
                {ZoneProperty{{"zone"}}, PS::kFake},  //
            }},

        GetPropertiesData{
            Rules{CreateZoneRule("zone"), CreateZoneRule("zone2")},  //
            PropertyType::kZone,                                     //
            DriverProperties{
                {ZoneProperty{{"zone"}}, PS::kFake},   //
                {ZoneProperty{{"zone2"}}, PS::kFake},  //
            }},

        //***************** GEOAREA *****************//
        GetPropertiesData{
            Rules{},                 //
            PropertyType::kGeoarea,  //
            DriverProperties{}       //
        },

        GetPropertiesData{Rules{CreateGeoareaRule("geoarea")},  //
                          PropertyType::kGeoarea,               //
                          DriverProperties{
                              {GeoareaProperty{{"geoarea"}}, PS::kFake},  //
                          }},

        GetPropertiesData{Rules{CreateGeoareaRule("geoarea"),
                                CreateGeoareaRule("geoarea")},  //
                          PropertyType::kGeoarea,               //
                          DriverProperties{
                              {GeoareaProperty{{"geoarea"}}, PS::kFake},  //
                          }},

        GetPropertiesData{Rules{CreateGeoareaRule("geoarea"),
                                CreateGeoareaRule("geoarea2")},  //
                          PropertyType::kGeoarea,                //
                          DriverProperties{
                              {GeoareaProperty{{"geoarea"}}, PS::kFake},   //
                              {GeoareaProperty{{"geoarea2"}}, PS::kFake},  //
                          }},

        //***************** CLASS *****************//
        GetPropertiesData{
            Rules{},               //
            PropertyType::kClass,  //
            DriverProperties{}     //
        },

        GetPropertiesData{Rules{CreateClassRule("class")},  //
                          PropertyType::kClass,             //
                          DriverProperties{
                              {ClassProperty{{"class"}}, PS::kFake},  //
                          }},

        GetPropertiesData{
            Rules{CreateClassRule("class"), CreateClassRule("class")},  //
            PropertyType::kClass,                                       //
            DriverProperties{
                {ClassProperty{{"class"}}, PS::kFake},  //
            }},

        GetPropertiesData{
            Rules{CreateClassRule("class"), CreateClassRule("class2")},  //
            PropertyType::kClass,                                        //
            DriverProperties{
                {ClassProperty{{"class"}}, PS::kFake},   //
                {ClassProperty{{"class2"}}, PS::kFake},  //
            }},

        //***************** BRANDING *****************//
        GetPropertiesData{
            Rules{},                  //
            PropertyType::kBranding,  //
            DriverProperties{}        //
        },

        GetPropertiesData{
            Rules{
                CreateBrandingRule(bsx::BrandingType::kStickerAndLightbox),
            },
            PropertyType::kBranding,
            DriverProperties{
                {BrandingProperty{{true, true}}, PS::kFake},
            },
        },

        GetPropertiesData{
            Rules{
                CreateBrandingRule(bsx::BrandingType::kSticker),
            },
            PropertyType::kBranding,
            DriverProperties{
                {BrandingProperty{{true, false}}, PS::kFake},
                {BrandingProperty{{true, true}}, PS::kFake},
            },
        },

        GetPropertiesData{
            Rules{
                CreateBrandingRule(bsx::BrandingType::kWithoutSticker),
            },
            PropertyType::kBranding,
            DriverProperties{
                {BrandingProperty{{false, true}}, PS::kFake},
                {BrandingProperty{{false, false}}, PS::kFake},
            },
        },

        GetPropertiesData{
            Rules{
                CreateBrandingRule(bsx::BrandingType::kNoFullBranding),
            },
            PropertyType::kBranding,
            DriverProperties{
                {BrandingProperty{{true, false}}, PS::kFake},
                {BrandingProperty{{false, true}}, PS::kFake},
                {BrandingProperty{{false, false}}, PS::kFake},
            },
        },

        //***************** ACTIVITY *****************//
        GetPropertiesData{
            Rules{},
            PropertyType::kActivity,
            DriverProperties{},
        },

        GetPropertiesData{
            Rules{CreateActivityRule(1)},
            PropertyType::kActivity,
            DriverProperties{
                {ActivityProperty{{1}}, PS::kFake},
            },
        },

        GetPropertiesData{
            Rules{CreateActivityRule(1), CreateActivityRule(1)},
            PropertyType::kActivity,
            DriverProperties{
                {ActivityProperty{{1}}, PS::kFake},
            },
        },

        GetPropertiesData{
            Rules{CreateActivityRule(1), CreateActivityRule(2)},
            PropertyType::kActivity,
            DriverProperties{
                {ActivityProperty{{1}}, PS::kFake},
                {ActivityProperty{{2}}, PS::kFake},
            },
        },
    }));

struct MergePropertiesData {
  DriverPropertyMap lhs;
  DriverPropertyMap rhs;
  DriverPropertyMap expected;
};

struct MergePropertiesParametrized
    : public ::testing::TestWithParam<MergePropertiesData> {};

TEST_P(MergePropertiesParametrized, Test) {
  ASSERT_EQ(MergeProperties(DriverPropertyMap(GetParam().lhs),
                            DriverPropertyMap(GetParam().rhs)),
            GetParam().expected);
}

using PT = PropertyType;
using PS = PropertySource;
INSTANTIATE_TEST_SUITE_P(
    MergePropertiesParametrized, MergePropertiesParametrized,
    ::testing::ValuesIn({
        MergePropertiesData{
            DriverPropertyMap{},
            DriverPropertyMap{},
            DriverPropertyMap{},
        },

        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{},
            DriverPropertyMap{},
        },

        MergePropertiesData{
            DriverPropertyMap{},
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{},
        },

        //****************** Equal ******************//
        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
        },

        //****************** Driver - Fake ******************//
        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kFake}},         //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
        },

        //****************** Fake - Driver ******************//
        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},     //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kFake}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},   //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},    //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}  //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
        },

        //************ Minimum branding & activity ************//
        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, true}}, PS::kFake}},        //
                {PT::kActivity, {ActivityProperty{{60}}, PS::kFake}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},   //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},    //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}  //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kDriver}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
        },

        //************ Fake min, but Driver's matched ************//
        MergePropertiesData{
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, false}}, PS::kFake}},       //
                {PT::kActivity, {ActivityProperty{{50}}, PS::kFake}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},   //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},    //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}  //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, true}}, PS::kDriver}},        //
                {PT::kActivity, {ActivityProperty{{60}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
            DriverPropertyMap{
                {PT::kBranding,
                 {BrandingProperty{{false, true}}, PS::kDriver}},        //
                {PT::kActivity, {ActivityProperty{{60}}, PS::kDriver}},  //
                {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
                {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}    //
            },
        },

    }));

struct ExtendPropertyMapData {
  DriverPropertiesByType properties_by_type;
  Rules rules;
  PropertyTypes restrictions;
  DriverPropertiesByType expected;
};

struct ExtendPropertyMapParametrized
    : public BaseTestWithParam<ExtendPropertyMapData> {};

TEST_P(ExtendPropertyMapParametrized, Test) {
  auto result = GetParam().properties_by_type;
  ExtendPropertyMap(result, GetParam().rules, GetParam().restrictions);
  ASSERT_EQ(result, GetParam().expected);
}

INSTANTIATE_TEST_SUITE_P(
    ExtendPropertyMapParametrized, ExtendPropertyMapParametrized,
    ::testing::ValuesIn({
        ExtendPropertyMapData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
            {
                CreateRule("zone", std::nullopt, "class", 10),
            },
            {PT::kActivity},
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{10}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
        },

        ExtendPropertyMapData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{60}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
            {
                CreateRule("zone", std::nullopt, "class", 60),
            },
            {PT::kActivity},
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{60}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
        },

        ExtendPropertyMapData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
            {
                CreateRule("zone", std::nullopt, "class", 60),
            },
            {PT::kActivity},
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity,
                 {{ActivityProperty{{0}}, PS::kDriver},
                  {ActivityProperty{{60}}, PS::kFake}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
        },

        ExtendPropertyMapData{
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
            {
                CreateRule("zone", std::nullopt, "class", 60),
                CreateRule("zone", std::nullopt, "class", 40),
            },
            {PT::kActivity},
            DriverPropertiesByType{
                {PT::kBranding,
                 {{BrandingProperty{{false, false}}, PS::kDriver}}},
                {PT::kActivity,
                 {{ActivityProperty{{40}}, PS::kDriver},
                  {ActivityProperty{{60}}, PS::kFake}}},
                {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},
                {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},
                {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},
            },
        },
    }));

Rule CreateRule(std::string id) {
  Rule rule;
  rule.id = id;
  return rule;
}

ScheduleItem CreateScheduleItem(ScheduleRate rate) {
  ScheduleItem item;
  item.rate = rate;
  return item;
}

const Rule kRule1 = CreateRule("1");
const Rule kRule2 = CreateRule("2");
const Rule kRule3 = CreateRule("3");
const KeyPoint kPoint1 = dt::Stringtime("2022-07-13T12:00:00Z");
const KeyPoint kPoint2 = dt::Stringtime("2022-07-13T13:00:00Z");
const ScheduleItem kItem1 = CreateScheduleItem(123.);
const ScheduleItem kItem2 = CreateScheduleItem(234.);
const ScheduleItem kItem3 = CreateScheduleItem(345.);

struct ReplaceData {
  const KeyPointRuleIdMatches key_point_to_rule_id_matches;
  bool expected_throw;
  const KeyPointRuleMatches expected_key_point_to_rule_matches;
};

struct ReplaceParametrized : public testing::TestWithParam<ReplaceData> {};
TEST_P(ReplaceParametrized, ReplaceParametrized) {
  const Rules rules = {kRule1, kRule2, kRule3};
  auto [key_point_to_rule_id_matches, expected_throw,
        expected_key_point_to_rule_matches] = GetParam();
  if (expected_throw) {
    ASSERT_THROW(subvention_matcher::ReplaceRuleIdWithRule(
                     rules, std::move(key_point_to_rule_id_matches)),
                 std::runtime_error);
  } else {
    const auto result = subvention_matcher::ReplaceRuleIdWithRule(
        rules, std::move(key_point_to_rule_id_matches));
    ASSERT_EQ(result, expected_key_point_to_rule_matches);
  }
}

const std::vector<ReplaceData> kReplaceData{
    {{{}, false, {}},
     {{{kPoint1, {{"1", kItem1}}}}, false, {{kPoint1, {{kRule1, kItem1}}}}},
     {{{kPoint1, {{"1", kItem1}, {"2", kItem2}}}, {kPoint2, {{"3", kItem3}}}},
      false,
      {{kPoint1, {{kRule1, kItem1}, {kRule2, kItem2}}},
       {kPoint2, {{kRule3, kItem3}}}}},
     {{{kPoint1, {{"id_not_from_rule_select", kItem1}}}}, true, {}}}};
INSTANTIATE_TEST_SUITE_P(ReplaceParametrized, ReplaceParametrized,
                         ::testing::ValuesIn(kReplaceData));

struct ComparingData {
  helpers::MatchResult match_result;
  helpers::MatchResult bulk_match_result;
  bool expected_result;
};
struct ComparingParametrized : public testing::TestWithParam<ComparingData> {};
TEST_P(ComparingParametrized, ComparingParametrized) {
  auto [match_result, bulk_match_result, expected_result] = GetParam();
  const auto result = IsMatchResultsEqual(match_result, bulk_match_result);
  ASSERT_EQ(result, expected_result);
}

const KeyPoint kAt1 = dt::Stringtime("2022-07-20T12:00:00Z");
const KeyPoint kAt2 = dt::Stringtime("2022-07-20T13:00:00Z");
const DriverPropertyMap kMap1 = {
    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}}};
const DriverPropertyMap kMap2 = {
    {PT::kClass, {ClassProperty{{"super"}}, PS::kDriver}}};

const std::vector<ComparingData> kComparingData{
    {{}, {}, true},

    {{}, {{}}, false},
    {{{}}, {}, false},

    {{{"id", kAt1, kMap1, 10.}}, {{"ID", kAt2, kMap1, 20.}}, false},
    {{{"id", kAt1, kMap1, 10.}}, {{"ID", kAt1, kMap2, 20.}}, false},
    {{{"id", kAt1, kMap1, 10.}}, {{"ID", kAt2, kMap2, 20.}}, false},

    {{{"id", kAt1, kMap1, 10.}}, {{"id", kAt1, kMap1, 10.}}, true},
    {{{"id", kAt1, kMap1, 10.}}, {{"id", kAt1, kMap1, 20.}}, false},
    {{{"id", kAt1, kMap1, 10.}}, {{"ID", kAt1, kMap1, 10.}}, false},
    {{{"id", kAt1, kMap1, 10.}}, {{"ID", kAt1, kMap1, 20.}}, false},

    {{
         {"id1", kAt1, kMap1, 10.},
         {"id2", kAt2, kMap2, 20.},
     },
     {
         {"id1", kAt1, kMap1, 10.},
         {"id2", kAt2, kMap2, 20.},
     },
     true},

    {{
         {"id1", kAt1, kMap1, 10.},
         {"id2", kAt2, kMap2, 20.},
     },
     {
         {"id1", kAt1, kMap1, 10.},
         {"id3", kAt2, kMap2, 30.},
     },
     false}

};
INSTANTIATE_TEST_SUITE_P(ComparingParametrized, ComparingParametrized,
                         ::testing::ValuesIn(kComparingData));
