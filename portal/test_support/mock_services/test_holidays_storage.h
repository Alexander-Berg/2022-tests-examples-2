#pragma once

#include <portal/morda/blocks/services/holidays_storage/holidays_storage.h>

#include <util/generic/set.h>

#include <memory>

namespace NMordaBlocks {

    class THolidayItem;
    class TTestHolidaysStorage : public IHolidaysStorage {
    public:
        TTestHolidaysStorage();
        ~TTestHolidaysStorage() override;

        bool IsHolidayInRegion(ERegion region, const NDatetime::TCivilDay& day) const override;

        bool IsHolidayInExactRegion(ERegion region, const NDatetime::TCivilDay& day) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void Reset();
        void SetHoliday(ERegion region, const NDatetime::TCivilDay& day);

    private:
        TSet<std::pair<ERegion, NDatetime::TCivilDay>> TestHolidays_;
    };

} // namespace NMordaBlocks
