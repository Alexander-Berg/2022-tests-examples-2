#pragma once

#include <portal/morda/blocks/types/regions.h>

#include <library/cpp/json/writer/json_value.h>

#include <util/generic/fwd.h>
#include <util/generic/hash_set.h>
#include <util/generic/noncopyable.h>
#include <util/generic/serialized_enum.h>
#include <util/stream/mem.h>
#include <util/string/cast.h>

namespace NMordaBlocks {
    namespace NTest {
        constexpr auto RAND_STRING_MAX_LEN = 10;
    }

    class TLocalizationInfo: public TMoveOnly {
    public:
        TLocalizationInfo(const TString& filePath);
        explicit TLocalizationInfo(const NJson::TJsonValue& json);

        TLocalizationInfo(TLocalizationInfo&&) noexcept = default;
        TLocalizationInfo& operator=(TLocalizationInfo&&) noexcept = default;

        virtual ~TLocalizationInfo() = default;

        // Contains all languages from the file, empty string, and some random (broken) value
        const THashSet<TString>& Languages() const {
            return Languages_;
        }

        // Contains all locales from the file, empty string, and some random (broken) value
        const THashSet<TString>& Locales() const {
            return Locales_;
        }

    private:
        void ParseJson(const NJson::TJsonValue& json);

    private:
        THashSet<TString> Languages_;
        THashSet<TString> Locales_;
    };

    void TrySetValue(NJson::TJsonValue* json, TStringBuf key, NJson::TJsonValue value);
    bool ThrowCoin(TMemoryInput& randIn);

    bool GetRandString(TMemoryInput& randIn, TString* output, size_t maxLen = NTest::RAND_STRING_MAX_LEN);
    bool GetRandBool(TMemoryInput& randIn, bool* output);

    template<class T>
    bool GetRandInteger(TMemoryInput& randIn, T* output) {
        if (randIn.Avail() < sizeof(T))
            return false;

        randIn.LoadOrFail(output, sizeof(T));
        return true;
    }

    // All the following methods have a probability that the corresponding field will be remained
    // unset, even in cases when some default value is required UNLESS its comment says other
    NJson::TJsonValue GetStringJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetIntegerJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetUIntegerJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetBooleanJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetArrayJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetMapJsonValue(TMemoryInput& randIn);

    NJson::TJsonValue GetRegionJsonValue(TMemoryInput& randIn, ERegion defaultRegion, ERegion maxRegionValue);
    NJson::TJsonValue GetLocaleJsonValue(TMemoryInput& randIn, const THashSet<TString>& locales, TStringBuf defaultLocale);
    NJson::TJsonValue GetMordaZoneJsonValue(TMemoryInput& randIn, TStringBuf defaultZone);
    NJson::TJsonValue GetTimeJsonValue(TMemoryInput& randIn, unsigned long long defaultTimestamp);
    NJson::TJsonValue GetApiNameJsonValue(TMemoryInput& randIn);

    template<class EnumType>
    NJson::TJsonValue GetEnumJsonValue(TMemoryInput& randIn) {
        ui8 intValue = 0;
        if (!ThrowCoin(randIn) || !GetRandInteger(randIn, &intValue))
            return {};

        const auto& versions = GetEnumAllValues<EnumType>();
        return NJson::TJsonValue{ToString(versions[intValue % versions.size()])};
    }

    NJson::TJsonValue GetAuthInfoJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetYCookiesJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetGeoLocationJsonValue(TMemoryInput& randIn);
    NJson::TJsonValue GetTargetingInfoJsonValue(TMemoryInput& randIn);

}  // namespace NMordaBlocks
