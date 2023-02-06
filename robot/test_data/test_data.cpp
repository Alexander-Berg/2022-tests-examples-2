#include "test_data.h"

using namespace NZora;
using namespace NRobot;

TTestData::TTestData() {
    Keys = GenerateStrings();
    Values = GenerateStrings();
}

TVector<TString> TTestData::GenerateStrings() const {
    const auto& cfg = TRotorCacheConfig::Get()->GetConfigBase();
    ui32 maxLength = cfg.GetMaxLength();
    ui32 minLength = cfg.GetMinLength();
    ui32 stringCount = cfg.GetStringCount();
    TVector<TString> strings;
    strings.assign(stringCount, "");

    static const char alphabet[] = "abcdefghijklmnopqrstuvwxyz";

    ui32 alphabetSize = sizeof(alphabet);
    for (size_t i = 0; i < strings.size(); i++) {
        srand((unsigned)time(NULL) * i);
        ui32 length = RandomNumber<size_t>(maxLength - minLength) + minLength;
        strings[i].reserve(length);
        for (size_t j = 0; j < length; j++) {
            strings[i] += alphabet[RandomNumber<size_t>(alphabetSize)];
        }
    }
    return strings;
}

const TString& TTestData::GetRandomKey() const {
    ui32 key = RandomNumber<size_t>(Keys.size());
    return Keys[key];
}

const TString& TTestData::GetRandomValue() const {
    ui32 value = RandomNumber<size_t>(Values.size());
    return Values[value];
}

TDuration TTestData::GetRandomTtl() const {
    const auto& cfg = TRotorCacheConfig::Get()->GetConfigBase();
    ui32 maxTtl = cfg.GetMaxTtl();
    ui32 minTtl = cfg.GetMinTtl();
    return TDuration::MilliSeconds(RandomNumber<ui32>(maxTtl - minTtl) + minTtl);
}

TDuration TTestData::GetTimeout() const {
    return Timeout;
}
