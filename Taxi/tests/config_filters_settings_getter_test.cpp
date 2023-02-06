#include <optional>
#include <string>
#include <unordered_map>

#include <userver/decimal64/decimal64.hpp>
#include <userver/dynamic_config/test_helpers.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO.hpp>
#include <taxi_config/variables/EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO_BY_TAGS.hpp>

#include <clients/categories_filters/config_filters_info_getter.hpp>
#include <clients/models/category_filters.hpp>
#include <clients/models/category_v2.hpp>
#include <models/brand.hpp>
#include <models/tag.hpp>

namespace nmn = eats_nomenclature;

namespace {

const std::string ConfigByIdAllFilters = R"({
  "1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      },
      "cultivar": {
      },
      "fat_content": {
      },
      "milk_type": {
      },
      "package_type": {
      },
      "egg_category": {
      },
      "flavour": {
      },
      "volume": {
      },
      "meat_type": {
      },
      "carcass_part": {
      }
    }
  }
})";

const std::string ConfigByIdWithoutBrandOverride = R"({
  "1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    }
  }
})";

const std::string ConfigByIdWithBrandOverride = R"({
  "1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    },
    "777": {
      "cultivar": {
      },
      "fat_content": {
      }
    }
  }
})";

const std::string ConfigByIdWithAnotherBrandOverride = R"({
  "1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    },
    "888": {
      "cultivar": {
      },
      "fat_content": {
      }
    }
  }
})";

const std::string ConfigByIdThatShouldBeIgnored = R"({
  "1": {
    "default_category_settings": {
      "milk_type": {
      },
      "flavour": {
      }
    }
  }
})";

const std::string ConfigByIdWithFilledValues = R"({
  "1": {
    "default_category_settings": {
      "fat_content": {
        "sort_order": 1,
        "overriden_name": "Жирность!",
        "ranges": {
          "10": {
            "from": "10.0",
            "to": "11.0"
          },
          "11+": {
            "from": "11.0",
            "to": "12.5"
          }
        }
      },
      "flavour": {
        "sort_order": 2,
        "overriden_name": "Вкус!"
      }
    }
  }
})";

const std::string ConfigByTagAllFilters = R"({
  "Тег 1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      },
      "cultivar": {
      },
      "fat_content": {
      },
      "milk_type": {
      },
      "package_type": {
      },
      "egg_category": {
      },
      "flavour": {
      },
      "volume": {
      },
      "meat_type": {
      },
      "carcass_part": {
      }
    }
  }
})";

const std::string ConfigByTagWithoutBrandOverride = R"({
  "Тег 1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    }
  }
})";

const std::string ConfigByTagWithBrandOverride = R"({
  "Тег 2": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    },
    "777": {
      "cultivar": {
      },
      "fat_content": {
      }
    }
  }
})";

const std::string ConfigByTagWithAnotherBrandOverride = R"({
  "Тег 1": {
    "default_category_settings": {
      "brand": {
      },
      "country": {
      }
    },
    "888": {
      "cultivar": {
      },
      "fat_content": {
      }
    }
  }
})";

const std::string ConfigByTagWithFilledValues = R"({
  "Тег 1": {
    "default_category_settings": {
      "fat_content": {
        "sort_order": 1,
        "overriden_name": "Жирность!",
        "ranges": {
          "10": {
            "from": "10.0",
            "to": "11.0"
          },
          "11+": {
            "from": "11.0",
            "to": "12.5"
          }
        }
      },
      "flavour": {
        "sort_order": 2,
        "overriden_name": "Вкус!"
      }
    }
  }
})";

const std::string ConfigByTagUnknownTag = R"({
  "Тег 3": {
    "default_category_settings": {
      "flavour": {
      }
    }
  }
})";

const std::string EmptyConfig = R"({})";

const nmn::clients::models::ConfigFiltersSettingsMap
    ExpectedSettingsWithAllFiltersMap = {
        {nmn::clients::models::FilterId{"brand"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"country"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"cultivar"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"fat_content"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"milk_type"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"package_type"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"egg_category"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"flavour"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"volume"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"meat_type"},
         nmn::clients::models::ConfigFilterSettings{}},
        {nmn::clients::models::FilterId{"carcass_part"},
         nmn::clients::models::ConfigFilterSettings{}}};

const nmn::clients::models::ConfigFiltersSettingsMap BrandOverrideResultMap = {
    {nmn::clients::models::FilterId{"cultivar"},
     nmn::clients::models::ConfigFilterSettings{}},
    {nmn::clients::models::FilterId{"fat_content"},
     nmn::clients::models::ConfigFilterSettings{}}};

const nmn::clients::models::ConfigFiltersSettingsMap NoBrandOverrideResultMap =
    {{nmn::clients::models::FilterId{"brand"},
      nmn::clients::models::ConfigFilterSettings{}},
     {nmn::clients::models::FilterId{"country"},
      nmn::clients::models::ConfigFilterSettings{}}};

const nmn::clients::models::ConfigFiltersSettingsMap ResultWithFilledValuesMap =
    {{nmn::clients::models::FilterId{"fat_content"},
      nmn::clients::models::ConfigFilterSettings{
          nmn::clients::models::FilterName{"Жирность!"},
          nmn::clients::models::SortOrder{1},
          {{nmn::clients::models::RangeName{"10"},
            nmn::clients::models::ConfigRange{decimal64::Decimal<2>{"10"},
                                              decimal64::Decimal<2>{"11"}}},
           {nmn::clients::models::RangeName{"11+"},
            nmn::clients::models::ConfigRange{
                decimal64::Decimal<2>{"11"}, decimal64::Decimal<2>{"12.5"}}}}}},
     {nmn::clients::models::FilterId{"flavour"},
      nmn::clients::models::ConfigFilterSettings{
          nmn::clients::models::FilterName{"Вкус!"},
          nmn::clients::models::SortOrder{2},
          {}}}};

dynamic_config::StorageMock CreateConfig(
    const std::string& config_by_id_content,
    const std::string& config_by_tag_content) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO,
        formats::json::FromString(config_by_id_content)},
       {taxi_config::EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO_BY_TAGS,
        formats::json::FromString(config_by_tag_content)}});
}

struct ConfigFiltersSettingsGetterTestParams {
  std::string config_by_id_content;
  std::string config_by_tag_content;
  nmn::clients::models::ConfigFiltersSettingsMap expected_result;
};

class ConfigFiltersSettingsGetterTestBase
    : public ::testing::TestWithParam<ConfigFiltersSettingsGetterTestParams> {
 public:
  void SetUp() override {}
  void TearDown() override {}
};

class FillSettingsFromConfigTest : public ConfigFiltersSettingsGetterTestBase {
};

}  // namespace

namespace {

const nmn::models::BrandId brand_id{777};
const nmn::clients::models::CategoryPublicId category_id{1};
const std::vector<nmn::models::TagName> tags{nmn::models::TagName{"Тег 1"},
                                             nmn::models::TagName{"Тег 2"}};

nmn::clients::models::ConfigFiltersSettingsMap GetConfigFiltersSettingsMap(
    const ConfigFiltersSettingsGetterTestParams& test_param) {
  const auto config_storage_mock = CreateConfig(
      test_param.config_by_id_content, test_param.config_by_tag_content);
  const auto config_snapshot = config_storage_mock.GetSnapshot();

  return nmn::filters::GetConfigFiltersSettingsMap(
      category_id, tags, brand_id,
      config_snapshot
          [taxi_config::EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO],
      config_snapshot
          [taxi_config::EATS_NOMENCLATURE_CATEGORY_BRAND_FILTERS_INFO_BY_TAGS]);
}

}  // namespace

namespace eats_nomenclature::filters::tests {

TEST_P(FillSettingsFromConfigTest, Test) {
  const auto param = GetParam();
  const auto settings_json = ::GetConfigFiltersSettingsMap(param);
  ASSERT_EQ(settings_json, param.expected_result);
}

INSTANTIATE_TEST_SUITE_P(
    FillSettingsFromConfigInst, FillSettingsFromConfigTest,
    ::testing::Values(
        // check all filters
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdAllFilters, ConfigByTagAllFilters,
            ExpectedSettingsWithAllFiltersMap},
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdAllFilters, EmptyConfig,
            ExpectedSettingsWithAllFiltersMap},
        // check settings filling from config with ids
        ConfigFiltersSettingsGetterTestParams{ConfigByIdWithoutBrandOverride,
                                              ConfigByTagUnknownTag,
                                              NoBrandOverrideResultMap},
        ConfigFiltersSettingsGetterTestParams{ConfigByIdWithoutBrandOverride,
                                              EmptyConfig,
                                              NoBrandOverrideResultMap},
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdWithBrandOverride, EmptyConfig, BrandOverrideResultMap},
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdWithAnotherBrandOverride, EmptyConfig,
            NoBrandOverrideResultMap},
        // check settings filling from config with tags
        ConfigFiltersSettingsGetterTestParams{ConfigByIdThatShouldBeIgnored,
                                              ConfigByTagWithoutBrandOverride,
                                              NoBrandOverrideResultMap},
        ConfigFiltersSettingsGetterTestParams{ConfigByIdThatShouldBeIgnored,
                                              ConfigByTagWithBrandOverride,
                                              BrandOverrideResultMap},
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdThatShouldBeIgnored, ConfigByTagWithAnotherBrandOverride,
            NoBrandOverrideResultMap},
        // check filling all filter settings
        ConfigFiltersSettingsGetterTestParams{
            ConfigByIdWithFilledValues, EmptyConfig, ResultWithFilledValuesMap},
        ConfigFiltersSettingsGetterTestParams{EmptyConfig,
                                              ConfigByTagWithFilledValues,
                                              ResultWithFilledValuesMap}));

}  // namespace eats_nomenclature::filters::tests
