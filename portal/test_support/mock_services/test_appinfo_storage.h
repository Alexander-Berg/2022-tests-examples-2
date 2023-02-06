#pragma once

#include <portal/morda/blocks/services/appinfo_storage/appinfo_storage.h>

#include <util/generic/hash.h>

#include <memory>

namespace NMordaBlocks {

    class TTestAppInfoStorage : public IAppInfoStorage {
    public:
        TTestAppInfoStorage();
        ~TTestAppInfoStorage() override;

        const TAppPackageItem* GetAppPackageItem(const TString& appName) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        TAppPackageItem* GetOrMakePackageItem(const TString& appName);
        void Reset();

    private:
        THashMap<TString, std::unique_ptr<TAppPackageItem>> Items_;
    };

} // namespace NMordaBlocks
