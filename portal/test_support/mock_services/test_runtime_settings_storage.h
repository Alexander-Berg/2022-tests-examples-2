#pragma once

#include <portal/morda/blocks/services/runtime_settings_storage/runtime_settings_storage.h>

#include <util/generic/hash.h>

namespace NMordaBlocks {

    class TTestRuntimeSettingsStorage : public IRuntimeSettingsStorage {
    public:
        TTestRuntimeSettingsStorage();
        ~TTestRuntimeSettingsStorage() override;

        const TRuntimeSettings& Settings() const override {
            return Settings_;
        }

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void Reset();

        TRuntimeSettings& TestSettings() {
            return Settings_;
        }


    private:
        TRuntimeSettings Settings_;
    };

} // namespace NMordaBlocks
