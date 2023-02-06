#include "test_localization.h"

#include <portal/morda/blocks/test_resources/test_resource_wrappers.h>

#include <library/cpp/json/json_reader.h>
#include <library/cpp/json/json_value.h>

#include <util/stream/file.h>

namespace NMordaBlocks {
    TTestLocalization::TTestLocalization() {
    }

    TTestLocalization::~TTestLocalization() = default;

    ESupportedLocale TTestLocalization::FallbackLocale() const {
        return ESupportedLocale::LANG_UNK;
    }

    TString TTestLocalization::GetTranslation(TStringBuf path) const {
        if (path.empty())
            return {};

        const auto it = Translations_.find(path);
        if (it != Translations_.end())
            return it->second;

        return TString() + "<" + path + ">";
    }

    TString TTestLocalization::GetPointsAccus(int points, TStringBuf path) const {
        if (path.empty())
            return {};

        const auto it = PointsAccus_.find(path);
        if (it == PointsAccus_.end())
            return TString() + "<" + path + ToString(points) + ">";

        const NJson::TJsonValue* values = &(it->second);
        if (values->GetArray().empty()) {
            return {};
        }

        const NJson::TJsonValue::TArray& array = values->GetArraySafe();

        if (array.size() == 1)
            return array[0].GetStringSafe();

        if (array.size() == 2) {
            if (points == 1)
                return array[0].GetStringSafe();
            return array[1].GetStringSafe();
        }

        if (array.size() == 4 && points == 0) {
            // That's kind of a hack - we may want something special for zero value
            return array.back().GetStringSafe();
        }

        points %= 100;
        if (points >= 20)
            points %= 10;

        if (points == 1)
            return array[0].GetStringSafe();

        if (points > 1 && points < 5)
            return array[1].GetStringSafe();

        return array[2].GetStringSafe();
    }

    void TTestLocalization::SetTranslation(TStringBuf path, TStringBuf translation) {
        Translations_[path] = TString(translation);
    }

    void TTestLocalization::Clear() {
        Translations_.clear();
        PointsAccus_.clear();
    }

    bool TTestLocalization::IsReady() const {
        return true;
    }

    void TTestLocalization::Start() {
    }

    void TTestLocalization::BeforeShutDown() {
    }

    void TTestLocalization::ShutDown() {
    }

    TString TTestLocalization::GetServiceName() const {
        return "TestLocalization";
    }

    void TTestLocalization::LoadTranslationsFromFile(const TString& filePath) {
        LoadTranslationsFromFile(filePath, ESupportedLocale::LANG_RUS);
    }

    void TTestLocalization::LoadTranslationsFromFile(const TString& filePath,
                                                     ESupportedLocale locale) {
        Clear();
        NJson::TJsonValue value;
        NJson::ReadJsonTree(TFileInput(filePath).ReadAll(), /* allowComments = */ true, &value, /* throwOnError = */ true);
        const TString strLocale(LocaleToString(locale));
        for (const auto& it : value[strLocale].GetMapSafe()) {
            SetTranslationsFromJson(it.first, it.second);
        }
    }

    void TTestLocalization::LoadTestTranslations() {
        LoadTestTranslations(ESupportedLocale::LANG_RUS);
    }

    void TTestLocalization::LoadTestTranslations(ESupportedLocale locale) {
        try {
            LoadTranslationsFromFile(NTest::LOCAL_TEST_DATA_PATH / "Lang_auto.json", locale);
        } catch (...) {
        }
    }

    void TTestLocalization::SetTranslationsFromJson(const TString& path,
                                                    const NJson::TJsonValue& json) {
        if (json.IsMap()) {
            for (const auto& it : json.GetMapSafe()) {
                SetTranslationsFromJson(path + "." + it.first, it.second);
            }
        } else if (json.IsString()) {
            SetTranslation(path, json.GetStringSafe());
        } else if(json.IsArray()) {
            PointsAccus_.emplace(path, json);
        }
    }

} // namespace NMordaBlocks
