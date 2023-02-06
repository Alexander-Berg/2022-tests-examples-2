#pragma once

#include <robot/zora/algo/actors/base.h>
#include <robot/samovar/algo/misc/static.h>
#include <robot/zora/rotor/cache/config/config.h>


class TTestData : public NSamovar::TStaticObject<TTestData> {
public:
    TTestData();
    const TString& GetRandomKey() const;
    const TString& GetRandomValue() const;
    TDuration GetRandomTtl() const;
    TDuration GetTimeout() const;

private:
    TVector<TString> GenerateStrings() const;

private:
    TVector<TString> Keys;
    TVector<TString> Values;
    const TDuration Timeout = TDuration::Seconds(10 * 60);
};
