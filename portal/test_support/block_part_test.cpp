#include "block_part_test.h"

#include "test_request_context.h"

#include <portal/morda/blocks/core/config/config.h>
#include <portal/morda/blocks/test_support/mock_services/test_appinfo_storage.h>
#include <portal/morda/blocks/test_support/mock_services/test_holidays_storage.h>
#include <portal/morda/blocks/test_support/mock_services/test_localization.h>
#include <portal/morda/blocks/test_support/mock_services/test_runtime_settings_storage.h>
#include <portal/morda/blocks/test_support/mock_services/test_url_generator.h>
#include <portal/morda/blocks/test_support/mock_services/test_yandex_services_info_storage.h>
#include <portal/morda/blocks/test_support/test_block_data_provider.h>
#include <portal/morda/blocks/test_support/test_geobase.h>

#include <library/cpp/json/json_value.h>

#include <utility>

namespace NMordaBlocks {

    TBlockPartTest::TBlockPartTest()
        : DataProvider_(std::make_unique<NTest::TTestBlockDataProvider>())
        , Localization_(std::make_unique<TTestLocalization>())
        , GeoBase_(std::make_unique<TTestGeoBase>())
        , HolidaysSrorage_(std::make_unique<TTestHolidaysStorage>())
        , AppInfos_(std::make_unique<TTestAppInfoStorage>())
        , UrlGenerator_(std::make_unique<TTestUrlGenerator>())
        , YandexServicesInfo_(std::make_unique<TTestYandexServicesInfoStorage>())
        , RuntimeSettingsStorage_(std::make_unique<TTestRuntimeSettingsStorage>())
    {
        IBlockDataProvider::SetForTests(DataProvider_.get());
        ILocalization::SetForTests(Localization_.get());
        IGeoBase::SetForTests(GeoBase_.get());
    }

    TBlockPartTest::~TBlockPartTest() {
        StopCore();
        IGeoBase::SetForTests(nullptr);
        ILocalization::SetForTests(nullptr);
        IBlockDataProvider::SetForTests(nullptr);
    }

    void TBlockPartTest::SetUp() {
        TTestWithCore::SetUp();
    }

    void TBlockPartTest::TearDown() {
        TTestWithCore::TearDown();
    }

    void TBlockPartTest::SetConfigValue(TStringBuf section, TStringBuf param,
                                        const NJson::TJsonValue& value) {
        GetTestConfig()->SetValue(section, param, value);
    }

    void TBlockPartTest::SetConfigFilePath(TStringBuf section, TStringBuf param,
                                           TStringBuf filePath) {
        SetConfigValue(section, param, NJson::TJsonValue(filePath));
        GetTestDataProvider()->LoadDataFromFile(TString(filePath), TString(filePath));
    }

    void TBlockPartTest::SetConfigFileData(TStringBuf section, TStringBuf param, TString data) {
        const auto key = TString() + section + "_" + param;
        SetConfigValue(section, param, NJson::TJsonValue(key));
        GetTestDataProvider()->SetData(key, std::move(data));
    }

    void TBlockPartTest::CreateServices() {
        DependsOn(DataProvider_.get());
        DependsOn(Localization_.get());
        DependsOn(GeoBase_.get());
        DependsOn(HolidaysSrorage_.get());
        DependsOn(AppInfos_.get());
        DependsOn(UrlGenerator_.get());
    }

    void TBlockPartTest::LoadTestTranslations() {
        Localization_->LoadTestTranslations();
    }

} // namespace NMordaBlocks
