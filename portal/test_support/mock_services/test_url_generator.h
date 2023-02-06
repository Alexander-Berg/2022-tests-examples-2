#pragma once

#include <portal/morda/blocks/services/url_generator/url_generator.h>

#include <memory>

namespace NMordaBlocks {

    class TTestUrlGenerator : public IUrlGenerator {
    public:
        TTestUrlGenerator();
        ~TTestUrlGenerator() override;

        TString MakeIconUrl(std::initializer_list<TStringBuf> pathFragments) const override;
        TString MakeIntent(const TString& baseUrl,
                           const TIntentParams& intentParams) const override;
        TString AppendAppSearchHeader(const TString& url) const override;
        TString MakeBrowserDeeplink(const TString& baseUrl, bool noRedir,
                                    bool needAppSearchHeader) const override;
        TString MakeYellowSkinUrl(const TString& url, const TString& blockId) const override;
        TString MakeViewPortUrl(const TString& url) const override;
        TString MakeViewPortUrlFromQuery(const TMap<TString, TString>& query) const override;

        // IService overrides:
        bool IsReady() const override;
        void Start() override;
        void BeforeShutDown() override;
        void ShutDown() override;
        TString GetServiceName() const override;
    };

} // namespace NMordaBlocks
