#pragma once

#include "topnews_config_params.h"

#include <portal/morda/blocks/test_support/block_part_test.h>
#include <portal/morda/blocks/test_support/json_test_utils.h>

namespace NMordaBlocks {

    class TTopnewsBlockPartTest : public TBlockPartTest {
    public:
        TTopnewsBlockPartTest() {
            SetIconsSettingsStorageData(R"({"all": []})");
            SetAgenciesInfoStorageData(R"({"all": []})");
            SetRegionsTitlesStorageData(R"({"all": []})");
            SetTopnewsSettingsStorageData(R"({"all": []})");
            SetSpecialThemesStorageData(R"({"all": []})");
            SetPersonalTabsDataStorageData(R"({})");
            SetTopnewsDataStorageData(R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_DEFAULT_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP0_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP1_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP2_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP3_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP4_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP5_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP6_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP7_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP8_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP9_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP10_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP11_FILE_PATH_PARAM, R"({})");
            SetTopnewsStorageData(CONFIG_TOPNEWS_EXP12_FILE_PATH_PARAM, R"({})");
        }

        ~TTopnewsBlockPartTest() override = default;

        void SetIconsSettingsStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_ICONS_SETTINGS_FILE_PATH_PARAM, data);
        }

        void SetAgenciesInfoStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_AGENCIES_INFO_FILE_PATH_PARAM, data);
        }

        void SetRegionsTitlesStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_REGIONS_TITLES_FILE_PATH_PARAM, data);
        }

        void SetTopnewsSettingsStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_SETTINGS_FILE_PATH_PARAM, data);
        }

        void SetSpecialThemesStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_SPECIAL_THEMES_FILE_PATH_PARAM, data);
        }

        void SetPersonalTabsDataStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_PERSONAL_TABS_DATA_FILE_PATH_PARAM, data);
        }

        void SetTopnewsDataStorageData(const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, CONFIG_TOPNEWS_DATA_FILE_PATH_PARAM, data);
        }

        void SetTopnewsStorageData(const TString& param, const TString& data) {
            SetConfigFileData(CONFIG_TOPNEWS_NAME, param, data);
        }
    };

}  //  namespace NMordaBlocks
