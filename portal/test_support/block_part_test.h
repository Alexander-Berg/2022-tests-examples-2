#pragma once

#include "test_with_core.h"

#include <memory>

namespace NJson {
    class TJsonValue;
}

namespace NMordaBlocks {
    namespace NTest {
        class TTestBlockDataProvider;
    }

    class TTestAppInfoStorage;
    class TTestGeoBase;
    class TTestHolidaysStorage;
    class TTestLocalization;
    class TTestUrlGenerator;
    class TUserAgent;
    class TTestYandexServicesInfoStorage;
    class TTestRuntimeSettingsStorage;

    class TBlockPartTest: public TTestWithCore {
    public:
        TBlockPartTest();

        ~TBlockPartTest() override;

        void CreateServices() override;

        void SetUp() override;

        void TearDown() override;

        void SetConfigValue(TStringBuf section, TStringBuf param, const NJson::TJsonValue& value);
        void SetConfigFilePath(TStringBuf section, TStringBuf param, TStringBuf filePath);
        void SetConfigFileData(TStringBuf section, TStringBuf param, TString data);

        using TTestWithCore::GetTestRequestContext;

        NTest::TTestBlockDataProvider* GetTestDataProvider() {
            return DataProvider_.get();
        }

        TTestLocalization* GetTestLocalization() {
            return Localization_.get();
        }

        void LoadTestTranslations();

        TTestGeoBase* GetTestGeoBase() {
            return GeoBase_.get();
        }

        TTestHolidaysStorage* GetTestHolidaysStorage() {
            return HolidaysSrorage_.get();
        }

        TTestAppInfoStorage* GetTestAppInfoStorage() {
            return AppInfos_.get();
        }

        TTestUrlGenerator* GetTestUrlGenerator() {
            return UrlGenerator_.get();
        }

        TTestYandexServicesInfoStorage* GetTestYandexServicesInfoStorage() {
            return YandexServicesInfo_.get();
        }

        TTestRuntimeSettingsStorage* GetTestRuntimeSettingsStorage() {
            return RuntimeSettingsStorage_.get();
        }

    private:
        std::unique_ptr<NTest::TTestBlockDataProvider> DataProvider_;
        std::unique_ptr<TTestLocalization> Localization_;
        std::unique_ptr<TTestGeoBase> GeoBase_;
        std::unique_ptr<TTestHolidaysStorage> HolidaysSrorage_;
        std::unique_ptr<TTestAppInfoStorage> AppInfos_;
        std::unique_ptr<TTestUrlGenerator> UrlGenerator_;
        std::unique_ptr<TTestYandexServicesInfoStorage> YandexServicesInfo_;
        std::unique_ptr<TTestRuntimeSettingsStorage> RuntimeSettingsStorage_;
    };

} // namespace NMordaBlocks
