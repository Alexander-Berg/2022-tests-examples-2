#include "test_appinfo_storage.h"

namespace NMordaBlocks {

    TTestAppInfoStorage::TTestAppInfoStorage() {
        SetForTests(this);
    }

    TTestAppInfoStorage::~TTestAppInfoStorage() {
        SetForTests(nullptr);
    }

    const TAppPackageItem* TTestAppInfoStorage::GetAppPackageItem(const TString& appName) const {
        const auto& it = Items_.find(appName);
        if (it == Items_.end())
            return nullptr;

        return it->second.get();
    }

    TAppPackageItem* TTestAppInfoStorage::GetOrMakePackageItem(const TString& appName) {
        std::unique_ptr<TAppPackageItem>& holder = Items_[appName];
        if (!holder) {
            holder = std::make_unique<TAppPackageItem>();
            holder->SetAppName(appName);
        }
        return holder.get();
    }

    void TTestAppInfoStorage::Reset() {
        Items_.clear();
    }

    bool TTestAppInfoStorage::IsReady() const {
        return true;
    }

    void TTestAppInfoStorage::Start() {
    }

    void TTestAppInfoStorage::BeforeShutDown() {
    }

    void TTestAppInfoStorage::ShutDown() {
    }

    TString TTestAppInfoStorage::GetServiceName() const {
        return "TestAppInfoStorage";
    }

} // namespace NMordaBlocks
