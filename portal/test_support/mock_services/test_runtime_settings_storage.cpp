#include "test_runtime_settings_storage.h"

namespace NMordaBlocks {

    TTestRuntimeSettingsStorage::TTestRuntimeSettingsStorage() {
        SetForTests(this);
    }

    TTestRuntimeSettingsStorage::~TTestRuntimeSettingsStorage() {
        SetForTests(nullptr);
    }

    void TTestRuntimeSettingsStorage::Reset() {
        Settings_.Clear();
    }

    bool TTestRuntimeSettingsStorage::IsReady() const {
        return true;
    }

    void TTestRuntimeSettingsStorage::Start() {
    }

    void TTestRuntimeSettingsStorage::BeforeShutDown() {
    }

    void TTestRuntimeSettingsStorage::ShutDown() {
    }

    TString TTestRuntimeSettingsStorage::GetServiceName() const {
        return "TestRuntimeSettingsStorage";
    }

} // namespace NMordaBlocks
