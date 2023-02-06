#include "fuzz_helpers.h"

#include <portal/morda/blocks/contexts/request_context_fields.h>
#include <portal/morda/blocks/types/context_types.h>
#include <portal/morda/blocks/utils/json_utils.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <util/generic/vector.h>
#include <util/stream/file.h>

namespace NMordaBlocks {
    namespace {
        constexpr char INTERNAL_NAME_FIELD[] = "_internal_name";
    }  // namespace

    TLocalizationInfo::TLocalizationInfo(const TString& filePath) {
        TFileInput fin(filePath);
        TString line = fin.ReadAll();
        NJson::TJsonValue json;
        NJson::ReadJsonTree(line, &json, true);

        ParseJson(json);
    }

    TLocalizationInfo::TLocalizationInfo(const NJson::TJsonValue& json) {
        ParseJson(json);
    }

    void TLocalizationInfo::ParseJson(const NJson::TJsonValue& json) {
        for (const auto& it : json.GetMap()) {
            Locales_.insert(it.first);

            const TString language = NJsonUtils::GetStringValueOrDefault(it.second, INTERNAL_NAME_FIELD, "");
            if (language) {
                Languages_.insert(language);
            } else {
                Languages_.insert(it.first);
            }
        }

        Y_ASSERT(!Languages_.empty());
        Y_ASSERT(!Locales_.empty());

        Languages_.insert("");
        Languages_.insert("broken_language");
        Locales_.insert("");
        Locales_.insert("broken_locale");
    }

    void TrySetValue(NJson::TJsonValue* json, TStringBuf key, NJson::TJsonValue value) {
        if (value.IsDefined())
            json->InsertValue(key, std::move(value));
    }

    bool ThrowCoin(TMemoryInput& randIn) {
        bool boolValue = false;
        return GetRandBool(randIn, &boolValue) && boolValue;
    }

    // maxLen should be not greater than its default value
    bool GetRandString(TMemoryInput& randIn, TString* output, size_t maxLen) {
        Y_ASSERT(maxLen <= NTest::RAND_STRING_MAX_LEN);

        char c;
        if (!randIn.ReadChar(c))
            return false;

        size_t charsToRead = c % (maxLen + 1);
        if (randIn.Avail() < charsToRead)
            return false;
        TVector<char> buf(charsToRead);
        randIn.LoadOrFail(buf.data(), charsToRead);

        *output = TString(buf.data(), charsToRead);

        return true;
    }

    bool GetRandBool(TMemoryInput& randIn, bool* output) {
        char c;
        if (!randIn.ReadChar(c))
            return false;
        *output = (bool) (c % 2);
        return true;
    }

    NJson::TJsonValue GetStringJsonValue(TMemoryInput& randIn) {
        TString value;
        if (!ThrowCoin(randIn) || !GetRandString(randIn, &value, NTest::RAND_STRING_MAX_LEN)) {
            return {};
        }
        return value;
    }

    NJson::TJsonValue GetIntegerJsonValue(TMemoryInput& randIn) {
        int value;
        if (!ThrowCoin(randIn) || !GetRandInteger(randIn, &value))
            return {};
        return value;
    }

    NJson::TJsonValue GetUIntegerJsonValue(TMemoryInput& randIn) {
        unsigned int value;
        if (!ThrowCoin(randIn) || !GetRandInteger(randIn, &value))
            return {};
        return value;
    }

    NJson::TJsonValue GetBooleanJsonValue(TMemoryInput& randIn) {
        bool value;
        if (!ThrowCoin(randIn) || !GetRandBool(randIn, &value))
            return {};
        return value;
    }

    NJson::TJsonValue GetArrayJsonValue(TMemoryInput& randIn) {
        static constexpr size_t PARAMS_LIMIT = 10;

        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        size_t paramsCnt = 0;
        GetRandInteger(randIn, &paramsCnt);
        paramsCnt %= PARAMS_LIMIT;
        TString value;
        for (size_t i = 0; i < paramsCnt; ++i) {
            if (!GetRandString(randIn, &value))
                break;
            result.AppendValue(value);
        }

        return result;
    }

    NJson::TJsonValue GetMapJsonValue(TMemoryInput& randIn) {
        static constexpr size_t PARAMS_LIMIT = 10;

        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        size_t paramsCnt = 0;
        GetRandInteger(randIn, &paramsCnt);
        paramsCnt %= PARAMS_LIMIT;
        TString key;
        TString value;
        for (size_t i = 0; i < paramsCnt; ++i) {
            if (!GetRandString(randIn, &key) || !GetRandString(randIn, &value))
                break;
            result.InsertValue(key, value);
        }

        return result;
    }

    NJson::TJsonValue GetRegionJsonValue(TMemoryInput& randIn, ERegion defaultRegion, ERegion maxRegionValue) {
        if (!ThrowCoin(randIn))
            return {defaultRegion};
        ui16 intValue = 0;
        if (GetRandInteger(randIn, &intValue))
            return intValue % maxRegionValue + 1;
        return {};
    }

    NJson::TJsonValue GetLocaleJsonValue(TMemoryInput& randIn, const THashSet<TString>& locales, TStringBuf defaultLocale) {
        if (!ThrowCoin(randIn))
            return {defaultLocale};

        ui8 intValue = 0;
        if (locales.empty() || !GetRandInteger(randIn, &intValue))
            return {};

        auto vi = locales.begin();
        std::advance(vi, intValue % locales.size());
        return *vi;
    }

    NJson::TJsonValue GetMordaZoneJsonValue(TMemoryInput& randIn, TStringBuf defaultZone) {
        if (!ThrowCoin(randIn))
            return {defaultZone};
        return GetEnumJsonValue<EMordaZone>(randIn);
    }

    NJson::TJsonValue GetTimeJsonValue(TMemoryInput& randIn, unsigned long long defaultTimestamp) {
        static constexpr unsigned long long SECONDS_PER_DAY = 24 * 60 * 60;

        unsigned long long longValue = 0;
        if (!ThrowCoin(randIn) || !GetRandInteger(randIn, &longValue))
            return defaultTimestamp;

        if (ThrowCoin(randIn))
            return {defaultTimestamp + longValue % SECONDS_PER_DAY};
        return {longValue};
    }

    NJson::TJsonValue GetApiNameJsonValue(TMemoryInput& randIn) {
        ui8 intValue = 0;
        if (!ThrowCoin(randIn) || !GetRandInteger(randIn, &intValue))
            return {};

        if (ThrowCoin(randIn))
            return {"vps"};

        const auto& apis = GetEnumAllValues<EMordaApi>();
        return ToString(apis[intValue % apis.size()]);
    }

    NJson::TJsonValue GetAuthInfoJsonValue(TMemoryInput& randIn) {
        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        TrySetValue(&result, "login", GetStringJsonValue(randIn));
        TrySetValue(&result, "uid", GetStringJsonValue(randIn));
        TrySetValue(&result, "plus_status", GetBooleanJsonValue(randIn));
        return result;
    }

    NJson::TJsonValue GetYCookiesJsonValue(TMemoryInput& randIn) {
        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        TrySetValue(&result, "S", GetStringJsonValue(randIn));
        TrySetValue(&result, "P", GetStringJsonValue(randIn));
        TrySetValue(&result, "C", GetStringJsonValue(randIn));
        return result;
    }

    NJson::TJsonValue GetGeoLocationJsonValue(TMemoryInput& randIn) {
        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        TrySetValue(&result, "lat", GetIntegerJsonValue(randIn));
        TrySetValue(&result, "lon", GetIntegerJsonValue(randIn));
        return result;
    }

    NJson::TJsonValue GetTargetingInfoJsonValue(TMemoryInput& randIn) {
        if (!ThrowCoin(randIn))
            return {};

        NJson::TJsonValue result;
        TrySetValue(&result, "promo-groups", GetArrayJsonValue(randIn));
        return result;
    }

}  // namespace NMordaBlocks
