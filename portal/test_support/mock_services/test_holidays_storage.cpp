#include "test_holidays_storage.h"

#include <portal/morda/blocks/services/geobase/geobase.h>

#include <util/generic/vector.h>

namespace NMordaBlocks {

    TTestHolidaysStorage::TTestHolidaysStorage() {
        IHolidaysStorage::SetForTests(this);
    }

    TTestHolidaysStorage::~TTestHolidaysStorage() {
        IHolidaysStorage::SetForTests(nullptr);
    }

    bool TTestHolidaysStorage::IsHolidayInRegion(ERegion region,
                                                 const NDatetime::TCivilDay& day) const {
        if (IsHolidayInExactRegion(region, day))
            return true;

        if (TestHolidays_.empty())
            return false;

        const TVector<ERegion> parents = IGeoBase::Get()->GetOnlyParents(region);
        for (auto parentRegion : parents) {
            if (IsHolidayInExactRegion(parentRegion, day))
                return true;
        }

        return false;
    }

    bool TTestHolidaysStorage::IsHolidayInExactRegion(ERegion region,
                                                      const NDatetime::TCivilDay& day) const {
        return TestHolidays_.find(std::make_pair(region, day)) != TestHolidays_.end();
    }

    void TTestHolidaysStorage::Reset() {
        TestHolidays_.clear();
    }

    void TTestHolidaysStorage::SetHoliday(ERegion region, const NDatetime::TCivilDay& day) {
        TestHolidays_.insert(std::make_pair(region, day));
    }

    bool TTestHolidaysStorage::IsReady() const {
        return true;
    }

    void TTestHolidaysStorage::Start() {
    }

    void TTestHolidaysStorage::BeforeShutDown() {
    }

    void TTestHolidaysStorage::ShutDown() {
    }

    TString TTestHolidaysStorage::GetServiceName() const {
        return "TestHolidaysStorage";
    }

} // namespace NMordaBlocks
