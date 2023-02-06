#pragma once

#include <portal/morda/blocks/services/spok_settings_storage/spok_settings_storage.h>

#include <util/generic/map.h>

#include <memory>

namespace NMordaBlocks {

    class TTestSpokSettingsStorage : public ISpokSettingsStorage {
    public:
        TTestSpokSettingsStorage();
        ~TTestSpokSettingsStorage() override;

        bool IsServicesTabsEnabled() const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void SetServicesTabsEnabled(bool enabled) {
            IsServicesTabsEnabled_ = enabled;
        }

        void Reset();

    private:
        bool IsServicesTabsEnabled_ = false;
    };

} // namespace NMordaBlocks
