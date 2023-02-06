#include "test_yandex_services_info_storage.h"

namespace NMordaBlocks {

    TTestYandexServicesInfoStorage::TTestYandexServicesInfoStorage() {
        SetForTests(this);
    }

    TTestYandexServicesInfoStorage::~TTestYandexServicesInfoStorage() {
        SetForTests(nullptr);
    }

    TString TTestYandexServicesInfoStorage::GetServiceUrl(const TString& id) const {
        const auto& it = Items_.find(id);
        if (it == Items_.end())
            return {};

        return it->second;
    }

    void TTestYandexServicesInfoStorage::SetServiceUrl(const TString& id, const TString& url) {
        Items_[id] = url;
    }

    void TTestYandexServicesInfoStorage::Reset() {
        Items_.clear();
    }

    bool TTestYandexServicesInfoStorage::IsReady() const {
        return true;
    }

    void TTestYandexServicesInfoStorage::Start() {
    }

    void TTestYandexServicesInfoStorage::BeforeShutDown() {
    }

    void TTestYandexServicesInfoStorage::ShutDown() {
    }

    TString TTestYandexServicesInfoStorage::GetServiceName() const {
        return "TestYandexServicesInfoStorage";
    }

} // namespace NMordaBlocks
