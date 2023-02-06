#pragma once

#include <portal/morda/blocks/services/localization/localization.h>

#include <util/generic/hash.h>
#include <util/generic/string.h>

#include <utility>

namespace NJson {
    class TJsonValue;
} // namespace NJson

namespace NMordaBlocks {

    class TTestLocalization : public ILocalization {
    public:
        TTestLocalization();
        ~TTestLocalization() override;

        ESupportedLocale FallbackLocale() const override;

        TString GetTranslation(TStringBuf path) const override;
        TString GetPointsAccus(int points, TStringBuf path) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void SetTranslation(TStringBuf path, TStringBuf translation);
        void LoadTranslationsFromFile(const TString& filePath);
        void LoadTranslationsFromFile(const TString& filePath, ESupportedLocale locale);
        void LoadTestTranslations();
        void LoadTestTranslations(ESupportedLocale locale);
        void Clear();

    private:
        void SetTranslationsFromJson(const TString& path, const NJson::TJsonValue& json);

        THashMap<TString, TString> Translations_;
        THashMap<TString, NJson::TJsonValue> PointsAccus_;
    };

} // namespace NMordaBlocks
