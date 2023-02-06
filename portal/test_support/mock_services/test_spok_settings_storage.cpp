#include "test_spok_settings_storage.h"

namespace NMordaBlocks {

    TTestSpokSettingsStorage::TTestSpokSettingsStorage() {
        SetForTests(this);
    }

    TTestSpokSettingsStorage::~TTestSpokSettingsStorage() {
        SetForTests(nullptr);
    }

    bool TTestSpokSettingsStorage::IsServicesTabsEnabled() const {
        return IsServicesTabsEnabled_;
    }

    void TTestSpokSettingsStorage::Reset() {
        IsServicesTabsEnabled_ = false;
    }

    bool TTestSpokSettingsStorage::IsReady() const {
        return true;
    }

    void TTestSpokSettingsStorage::Start() {
    }

    void TTestSpokSettingsStorage::BeforeShutDown() {
    }

    void TTestSpokSettingsStorage::ShutDown() {
    }

    TString TTestSpokSettingsStorage::GetServiceName() const {
        return "TestSpokSettingsStorage";
    }

} // namespace NMordaBlocks
