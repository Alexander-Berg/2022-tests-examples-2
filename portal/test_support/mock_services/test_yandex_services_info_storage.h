#pragma once

#include <portal/morda/blocks/services/yandex_services_info_storage/yandex_services_info_storage.h>

#include <util/generic/map.h>

#include <memory>

namespace NMordaBlocks {

    class TTestYandexServicesInfoStorage : public IYandexServicesInfoStorage {
    public:

        TTestYandexServicesInfoStorage();
        ~TTestYandexServicesInfoStorage() override;

        TString GetServiceUrl(const TString& id) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;

        void SetServiceUrl(const TString& id, const TString& url);
        void Reset();

    private:
        TMap<TString, TString> Items_;
    };

} // namespace NMordaBlocks
